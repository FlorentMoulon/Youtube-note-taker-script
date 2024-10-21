import math
from Scrapper import Scrapper
from Generator import Generator




prompt = '''
You are an expert in content structuring and organization. 
Your task is to create a detailed outline from a portion of a video transcript, maintaining time codes and hierarchical structure.

Context:
This is a chunk of a larger video transcript. Previous chunks have already been processed, resulting in the following outline structure (if any):
{{temp_outline}}


Task:
Create a detailed outline for this chunk that:
- Follows the natural progression of topics in the video
- Maintains chronological consistency with any existing outline
- Preserves exact time codes from the transcript
- Uses appropriate hierarchical structure
- Avoids duplicating content from previous chunks


Structural Requirements:

Main Sections (Level 1):
Use ONLY for major, broad topics that encompass multiple related subtopics
Should represent the highest-level organization of content
A main section typically spans several minutes of video
Format: # [HH:MM] Section Title

Subsections (Level 2):
Use for specific topics within main sections
Most content should be organized at this level
Format: ## [HH:MM] Subsection Title

Key Points (Level 3):
Use for specific arguments, examples, or important details
Should be used liberally to capture detailed content
Format: ### [HH:MM] Key Point Description


Hierarchical Organization Guidelines:
Before creating a new main section, consider if it could be a subsection of an existing topic
Group related topics under broader main sections
Main sections should be broad enough to encompass multiple subsections
If a topic is closely related to the previous main section, make it a subsection instead
Aim for a structure where most content is at levels 2 and 3

Overlap Handling:
Check the last 2-3 minutes of time codes from the previous outline
If you encounter content that's already been outlined, skip it
If a section continues from the previous chunk, maintain its hierarchical level

Rules:
- Always include the exact time code [HH:MM] at the start of each line
- Maintain chronological order of time codes
- Keep titles and descriptions concise but descriptive
- Use the exact time code from when the topic/point begins in the transcript
- Do not include explanatory text or commentary
- Do not summarize content, only outline it
- Do not modify or reference time codes from previous chunks

Output Format:
# [HH:MM] Section Title
## [HH:MM] Subsection Title
## [HH:MM] Another Subsection

Please, rescpect carefully this output format

Process the following transcript chunk and provide only the outline, without any additional text:
{{chunk}}
'''



rebalance_prompt = '''
You are an expert in content organization and information architecture.

Your task is to refine and rebalance an existing video outline to ensure optimal hierarchical structure and topic organization.

Input Context:
The following outline was automatically generated from video transcript chunks. While the time codes and content are accurate, the hierarchical structure may need refinement:

{{original_outline}}

Task:
Rewrite the outline to ensure:
1. Logical topic grouping
2. Appropriate hierarchical depth
3. Balanced section scope
4. Clear distinction between main ideas and supporting details

Structural Requirements:

Main Sections (Level 1) must:
- Represent truly significant shifts in topic or theme
- Encompass multiple related subtopics
- Be broad enough to warrant subdivision
- Not be too specific or detail-oriented
- Typically span several minutes of content

Subsections (Level 2) must:
- Represent distinct subtopics within the main theme
- Be specific enough to be meaningful
- Be general enough to potentially contain key points
- Have clear relationships to their parent section

Key Points (Level 3) must:
- Contain specific details, examples, or arguments
- Directly support their parent subsection
- Not be so broad that they could be subsections

Rebalancing Rules:
1. If a Level 1 section contains only one subsection, either:
   - Promote the subsection to Level 1 if it's sufficiently important
   - Or merge it with another related section

2. If a Level 1 section is too specific:
   - Demote it to Level 2 and find an appropriate parent section
   - Or combine it with related sections under a new broader heading

3. If multiple Level 2 sections share a common theme:
   - Create a new Level 1 section to group them
   - Ensure the new section title accurately represents the group

4. If Level 3 points are too broad:
   - Promote them to Level 2
   - Create appropriate parent sections as needed

Format Requirements:
- Maintain all original time codes [HH:MM]
- Preserve chronological order
- Keep section titles concise but descriptive
- Do not add explanatory text or commentary
- Do not modify time codes (it's really important)

Output Format:
# [HH:MM] Main Section Title
## [HH:MM] Subsection Title
### [HH:MM] Key Point

Process the outline and provide only the rebalanced version, without any additional text.
'''







yt_url = "https://www.youtube.com/watch?v=TOvPlPi1rSE"
s= Scrapper(yt_url)
generator = Generator()
t = s.get_transcript(with_chapter=True, with_timestamps=True)


def create_chunks_with_overlap( text: str, chunk_size_in_word: int, overlap: int):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words) - overlap:
        end = start + chunk_size_in_word
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start += chunk_size_in_word - overlap
    return chunks



model_max_tokens = generator.get_model_max_tokens()
estimated_tokens = generator.estimate_token_count(t)
margin = 500 # token

if estimated_tokens >= model_max_tokens//2:  
    # Calculate the chunk size and overlap (in token)
    chunk_size = model_max_tokens//2 - margin
    chunk_size_in_word = math.floor(chunk_size // 1.5)

chunks = create_chunks_with_overlap(t, chunk_size_in_word, math.floor(chunk_size_in_word/10))



def clear_outline(outline):
    # keep the line that start with #
    
    lines = outline.split("\n")
    outline = ""
    for line in lines:
        if line.startswith("#") or line.startswith("##"):
            outline += line + "\n"
    
    return outline



print("nb of chunks : ",len(chunks))

outline = ""

for i in range(0, len(chunks)):
    p = prompt.replace("{{chunk}}", chunks[i]).replace("{{temp_outline}}", outline)
    r = generator.generate_chat_completion("",p)
    r = clear_outline(r)
    
    print("\n---------------------------------------------------\n")
    print(r)
    
    outline += "\n" + r

print("\n---------------------------------------------------\n")    
print(outline)

print("\n---------------------------------------------------\n")
p = rebalance_prompt.replace("{{original_outline}}", outline)
o = generator.generate_chat_completion("",p)

print(o)


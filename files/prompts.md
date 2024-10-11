### Variables
All {{variable_name}} will be replace by their value (if it exist)

Here is a list of all the script variables :
- {{date}} *today*
- {{file_name}} *of the .md document*
- {{publication_date}}
- {{video_duration}}
- {{channel}}
- {{video_description}}
- {{video_tags}} *separated by ', '*
- {{video_title}}
- {{video_url}}
- {{transcript}} *full transcript of the video*
- {{transcript_with_timecode}} *full transcript of the video with the timecode*
- {{llm_sized_transcript}} *a pre-summarized transcript (using SUMMARIZE_CHUNK prompt to reduce the size of chunk of the transcript)*
- {{transcript_without_sponsorship}} *a llm_sized transcript where all the sponred part of the video are removed (using REMOVE_SPONSOR prompt)*

You can create your own variables :
> variable_name: value


### Prompts
All {{prompt_name}} will be replace by the output of the LLM for the prompt.
Before sending a prompt to the LLM, every variable and prompt called inside will replace by their values. That mean you can chain your prompt. But you need to avoid circular depencies in your prompt (= infinite loop).

You can create your own prompts :
```prompt_name
The content of the prompt.
{{another_prompt_name}} : {{variable}}
```

The prompt named in CAPITAL are script prompt and can't be removed, but feel free to upgrade them.

If a {{prompt}} is needed multiple time, it will be only completed once by the LLM and the value will be saved so every call of the same prompt will return the same value.


### Customization
Feel free to customize this template to feat your own needs.


### Everything before those 3 dashes will be ignored
---


```SUMMARIZE_CHUNK
Vous êtes un expert en résumé de texte, capable de condenser l'information tout en préservant les points clés et le contexte.
Tâche : Résumez le texte fourni en {{expected_size}} mots ou moins.

Contexte : Ce texte est un extrait d'un document plus long. D'autres extraits seront résumés séparément, et tous les résumés seront combinés pour former un résumé final.

Instructions :
1. Préservez les informations essentielles, les faits clés et les idées principales.
2. Maintenez la chronologie et les relations causales si elles sont présentes.
3. Conservez les noms propres, les dates et les chiffres importants.
4. Gardez le ton et le style du texte original.
5. Assurez-vous que votre résumé puisse être compris indépendamment, mais qu'il s'intègre bien avec d'autres résumés.
6. Utilisez la même langue que le texte original.

Règles importantes :
- Ne commencez pas par "Ce texte parle de..." ou des phrases similaires.
- N'incluez pas de commentaires personnels ou d'analyses supplémentaires.
- Ne mentionnez pas que c'est un résumé ou un extrait.

Texte à résumer :
{{chunk}}

Répondez uniquement avec le résumé, sans aucun texte supplémentaire.
```


```REMOVE_SPONSOR
You are a precise text editor. Your task is to clean the provided text by removing specific parts while maintaining the integrity of the remaining content. Follow these instructions carefully:

Input: You will receive a transcript of a YouTube video.
Output: Provide the entire text, modified only as specified below. Do not add any comments or explanations.
Cleaning Task: Remove sponsored content while keeping all other parts intact.

Identifying Sponsored Content:
Look for sections that promote a brand or product unrelated to the main content.
Common indicators include phrases like:
"I want to thank our sponsor"
"This video is sponsored by"
"Use promo code"
"Get a discount on your first order"

Removal Process:
Delete the entire sponsored section, from the introduction of the sponsor to the end of the promotional content.
Do not remove mentions of brands or products if they are relevant to the video's main topic.

Preservation:
Keep all non-sponsored content exactly as it appears in the original text.
Maintain the original language of the text.

Output Format:
Provide the full text, including all unmodified parts.
Do not add any explanations, comments, or markers about removed content.
Ensure the output reads as a continuous, natural text.

If No Sponsored Content:
If you don't find any sponsored content, output the entire original text without changes.


Process the following text according to these instructions:
{{text}}
```


> language: french
> min_nb_word_for_note: 700
> max_nb_word_for_note: 1000
> percentage_for_conclusion: 20


```prompt_detailed_note
You are a highly skilled note-taker with the ability to distill complex information into clear, structured notes.
You understand all languages, but you can only answer in {{language}}.
Your task is to create comprehensive notes from a YouTube video transcript, following these guidelines:

Structure:
Begin with a brief introduction or overview of the video's main topic.
Follow the structure of the video, organizing information into main sections and subsections as presented.
Use appropriate Markdown syntax for headings, subheadings, lists, and emphasis.

Content:
Capture all key points, important details, and relevant examples.
Omit any sponsored content or unrelated tangents.
Include important definitions, statistics, or data mentioned.
Note any significant quotes, attributing them properly.

Formatting:
Use bullet points or numbered lists for easier readability where appropriate.
Employ bold or italic text to highlight crucial information.
If diagrams or charts are described, represent them textually or with ASCII art if possible.
For chapter title, just use ###.

Length and Depth:
Aim for notes that would fill approximately one standard document page (about {{min_nb_word_for_note}}-{{max_nb_word_for_note}} words).
Prioritize depth over breadth, focusing on the most important concepts.

Conclusion:
If the video has an explicit conclusion, dedicate a substantial section to it (about {{percentage_for_conclusion}}% of the notes).
Summarize the main takeaways and any call to action or future implications mentioned.

Remember to maintain a neutral, academic tone throughout the notes. Focus on accuracy and clarity in conveying the video's content.

Create notes based on the following video transcript:
{{llm_sized_transcript}}
```



```prompt_takeaways
You are an expert in identifying and summarizing the most crucial information from complex content.
You understand all languages, but you can only answer in {{language}}.
Your task is to extract the key takeaways from a YouTube video transcript, following these guidelines:

Content Analysis:
Thoroughly analyze the provided transcript.
Identify the most important concepts, ideas, and conclusions presented in the video.

Key Takeaways:
Generate 3-5 bullet points that summarize the most crucial points from the video.
Each takeaway should be concise yet informative, capturing a significant insight or conclusion.
Ensure the takeaways cover the breadth of the main topics discussed in the video.
Prioritize information that would be most valuable for someone who hasn't watched the video.

Formatting:
Present the takeaways as a bulleted list.
Use clear, concise language for each point.
If a takeaway requires slight elaboration, you may use a brief sub-bullet.

Relevance:
Focus on the core message and main arguments of the video.
Exclude any information from sponsored segments or unrelated tangents.

Tone and Style:
Maintain a neutral, informative tone.
Use language that is accessible but precise.

Extract and present the key takeaways based on the following video transcript:
{{llm_sized_transcript}}
```



> nb_word_for_summary: 300

```prompt_summary
You are an expert in content analysis and text summarization.
You understand all languages, but you can only answer in {{language}}.

Here is the transcript of the video :
{{llm_sized_transcript}}


You will generate increasingly concise, entity-dense summaries of the above video.

Repeat the following 2 steps 5 times.
Step 1. Identify 1-3 informative entities (";" delimited) from the video that are missing from the previously generated summary.
Step 2. Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the missing entities.

A missing entity is:
- Relevant to the main story,
- Specific yet concise (5 words or fewer),
- Novel (not in the previous summary),
- Faithful (present in the video),
- Anywhere (can be located anywhere in the video).


Guidelines:
- The first summary should be long (4-5 sentences, ~{{nb_word_for_summary}} words) yet highly non-specific, containing little information beyond the entities marked as missing. Use overly verbose language and fillers (e.g., "this video discusses") to reach ~{{nb_word_for_summary}} words.
- Make every word count: rewrite the previous summary to improve flow and make space for additional entities.
- Make space with fusion, compression, and removal of uninformative phrases like "the video discusses".
- The summaries should become highly dense and concise yet self-contained, i.e., easily understood without the video.
- Missing entities can appear anywhere in the new summary.
- Never drop entities from the previous summary. If space cannot be made, add fewer new entities.

Remember, use the exact same number of words for each summary.
Repeat the 2 steps 5 times now.

Output Format:
Do not include any explanations, note or additional text before or after the keyword list.
Answer in JSON. The JSON should be a list (length 5) of dictionaries whose keys are "Missing_Entities" and "Denser_Summary".
Please respect carefully the JSON synthax as bellow :
[
{
"Missing_Entities": "",
"Denser_Summary": ""
},
{
"Missing_Entities": "",
"Denser_Summary": ""
},
{
"Missing_Entities": "",
"Denser_Summary": ""
},
{
"Missing_Entities": "",
"Denser_Summary": ""
},
{
"Missing_Entities": "",
"Denser_Summary": ""
}
]
```


> min_nb_keyword: 5
> max_nb_keyword: 10

```keyword_extraction
You are an expert in content analysis and keyword extraction. Your task is to extract the most relevant and important keywords from the given text.
Follow these instructions carefully:

Input: 
You will receive a text passage.

Analysis:
Read and analyze the entire text thoroughly.
Identify the main topics, themes, and key concepts discussed.

Keyword Extraction:
Extract between {{min_nb_keyword}} and {{max_nb_keyword}} keywords or key phrases that best represent the core content of the text.
Focus on nouns, noun phrases, and occasionally important verbs or adjectives.
Prioritize words or phrases that:
- Would be useful for categorizing or searching for this content
- Appear frequently (accounting for variations and synonyms)
- Are central to the main ideas or arguments

Output Format:
Present the keywords in a bulleted list.
Use lowercase for all keywords unless they are proper nouns.
Arrange the keywords in order of importance or relevance to the overall text.
Do not include any explanations, note or additional text before or after the keyword list.
The bullet list should not contain more than {{max_nb_keyword}} items.

Additional Guidelines:
- If the text is specialized or technical, include relevant technical terms.
- For longer texts, ensure the keywords cover the breadth of topics discussed.
- Avoid overly general terms unless they are crucially important to the text's theme.
- Maintain the original language of the text.
- Respect carefully the limitation of {{max_nb_keyword}} keywords.

Output Structure:
Your response should follow this exact structure:
Keywords:
- [keyword 1]
- [keyword 2]
- [keyword 3]
...

Extract keywords from the following text according to these instructions:
{{prompt_detailed_note}}
```
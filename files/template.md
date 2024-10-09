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


### Prompts
All {{prompt_name}} will be replace by the output of the LLM for the prompt.


### Customization
Feel free to customize this template to feat your own needs.
Keep in mind that everything above the first 3 dashes will be ignored, even if you don't have yaml header.


### Everything before those 3 dashes will be ignored
---
aliases: 
tags: 
date: {{date}}
video_title: {{video_title}}
video_url: {{video_url}}
video_duration: {{video_duration}}
video_publication Date: {{publication_date}}
channel: {{channel}}
---

# Keyword
{{keyword_extraction}}


# Description
{{prompt_summary}}

# Takeaways
{{prompt_takeaways}}

# {{video_title}}
{{prompt_detailed_note}}

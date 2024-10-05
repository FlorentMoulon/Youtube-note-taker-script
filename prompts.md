Everything before the 3 dashes will be ignored

All the prompt are run in the order in which they appear in this file

- {{date}} *today*
- {{file_name}} *of the .md document*
- {{publication_date}}
- {{video_duration}}
- {{channel}}
- {{video_description}}
- {{video_tags}}
- {{video_title}}
- {{video_url}}
- {{transcript}}


- {{transcript_with_timecode}}




```prompt_detailed_note
Writte in french.
Take note about the video like you are a degree student assiting to a lecture using markdown syntax. The note should be consice but should not miss any revelant information.
Here is all the metadata of the video :
- publication_date: {{publication_date}}
- duration: {{duration}}
- channel: {{channel}}
- video_description :{{video_description}}
- tags: {{video_tags}}
- title: {{video_title}}

Here is the transcript of the video :
{{transcript}}
```

```prompt_summary
Writte in french.
Summarize this video in 2 to 3 senteces (this summary should be as usefull as possible to find the note when we look for a information that is inside).

Here is all the metadata of the video :
- publication_date: {{publication_date}}
- duration: {{duration}}
- channel: {{channel}}
- video_description :{{video_description}}
- tags: {{video_tags}}
- title: {{video_title}}

And here is a detailed description of the video :
{{prompt_detailed_note}}
```


---


```prompt_detailed_note
Take note about the video like you are a degree student assiting to a lecture using markdown syntax. The note should be consice but should not miss any revelant information.
Do not talk about the sponsored part of the video if there is one.

Here is all the metadata of the video :
- publication_date: {{publication_date}}
- duration: {{duration}}
- channel: {{channel}}
- video_description :{{video_description}}
- tags: {{video_tags}}
- title: {{video_title}}

Here is the transcript of the video :
{{transcript}}
```


```prompt_summary
Video: 
Here is all the metadata of the video :
- publication_date: {{publication_date}}
- duration: {{video_duration}}
- channel: {{channel}}
- video_description :{{video_description}}
- tags: {{video_tags}}
- title: {{video_title}}

Here is the transcript of the video :
{{transcript}}


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
- The first summary should be long (4-5 sentences, ~200 words) yet highly non-specific, containing little information beyond the entities marked as missing. Use overly verbose language and fillers (e.g., "this video discusses") to reach ~200 words.
- Make every word count: rewrite the previous summary to improve flow and make space for additional entities.
- Make space with fusion, compression, and removal of uninformative phrases like "the video discusses".
- The summaries should become highly dense and concise yet self-contained, i.e., easily understood without the video.
- Missing entities can appear anywhere in the new summary.
- Never drop entities from the previous summary. If space cannot be made, add fewer new entities.
- Do not talk about the sponsored part of the video if there is one.

Remember, use the exact same number of words for each summary.
Repeat the 2 steps 5 times now.
```

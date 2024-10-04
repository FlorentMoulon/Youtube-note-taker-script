Everything before the 3 dashes will be ignored

All the prompt are run in the order in which they appear in this file

- {{date}} *today*
- {{file_name}} *of the .md document*
- {{publication_date}}
- {{duration}}
- {{channel}}
- {{video_description}}
- {{video_tags}}
- {{video_title}}
- {{video_url}}
- {{transcript}}


- {{transcript_with_timecode}}

---



```prompt_detailed_note
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

```test
Raconte un blague drole stp
```
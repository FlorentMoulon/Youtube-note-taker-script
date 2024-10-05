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


```
Second thing to remove : LLM footprint
A LLM footprint is a small sentece that break the text to say something like "Here is a summary of the text in English, under 1000 words:" or "for sure, here is your summary".
They are small and unrealated to the context around them.
```

> variable: value
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


```prompt_detailed_note
Writte in french.
Take note about the video like you are a degree student assiting to a lecture using markdown syntax. The note should be consice but should not miss any revelant information.
Do not talk about the sponsored part of the video if there is one.

Here is the transcript of the video :
{{llm-sized-transcript}}
```


> nb_word_for_summary: 300

```prompt_summary
Writte in french.

Here is the transcript of the video :
{{llm-sized-transcript}}


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

Answer in JSON. The JSON should be a list (length5) of dictionaries whose keys are "Missing_Entities" and "Denser_Summary" .
```

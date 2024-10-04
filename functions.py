import os
import requests
import re
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
from bs4 import BeautifulSoup
from groq import Groq
from dotenv import load_dotenv


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama3-8b-8192"


def generate_note_file(youtube_url, file_name, folder_path, template_path="./template.md"):
  # Get video details
  video_details = get_video_details(youtube_url)

  # Get transcript
  transcript = get_transcript(youtube_url)

  # Generate notes
  completions = generate_notes(video_details, file_name, transcript)
  
  # Save notes to file
  create_markdown_file(video_details, transcript, completions, file_name, folder_path, template_path)



# Function to retrieve YouTube video details using scraping
def get_video_details(youtube_url):
  response = requests.get(youtube_url)
  soup = BeautifulSoup(response.text, 'html.parser')

  # Extract basic info like title, channel, etc.
  title = soup.find('meta', {'name': 'title'})['content']
  channel = soup.find('link', {'itemprop': 'name'})['content']
  publication_date = soup.find('meta', {'itemprop': 'uploadDate'})['content'][0:10]
  video_duration = soup.find('meta', {'itemprop': 'duration'})['content'].replace('PT', '').lower()
  video_tags = soup.find('meta', {'name': 'keywords'})['content']
  video_description = soup.find('meta', {'name': 'description'})['content']

  return {
    'url': youtube_url,
    'title': title,
    'channel': channel,
    'publication_date': publication_date,
    'video_duration': video_duration,
    'video_tags': video_tags,
    'video_description': video_description
  }


# Get video ID from URL
def get_video_id(youtube_url):
  video_id_match = re.search(r'v=([a-zA-Z0-9_-]+)', youtube_url)
  if video_id_match:
    return video_id_match.group(1)
  return None

# Function to fetch transcript in any available language
def get_transcript(video_url):
  try:
    # Get available transcripts for the video
    transcript_list = YouTubeTranscriptApi.list_transcripts(get_video_id(video_url))

    # Try to find a transcript in the preferred languages ('fr' or 'en')
    try:
      transcript = transcript_list.find_transcript(['fr', 'en'])
    except NoTranscriptFound:
      # If not found, use any available transcript
      transcript = transcript_list.find_generated_transcript(['fr', 'en', 'it'])

    # Format transcript to plain text
    formatter = TextFormatter()
    transcript_text = formatter.format_transcript(transcript.fetch())
    return transcript_text

  except NoTranscriptFound as e:
    print(f"Error retrieving transcript: {e}")
    return None


# Function to create a Markdown file
def create_markdown_file(video_details, transcript, completions, file_name, folder_path, template_path):
  # Prepare the markdown content
  md_content =  parse_content_in_template(template_path, video_details, file_name, transcript)
  md_content = replace_completion(md_content, completions)

  # Define the initial filepath and file extension
  base_filepath = os.path.join(folder_path, f"{file_name}.md")
  new_filepath = base_filepath
  counter = 1

  # Check if file already exists and find a unique name
  while os.path.exists(new_filepath):
    print(f"File {new_filepath} already exists. Trying a new name...")
    new_filepath = os.path.join(folder_path, f"{file_name}-{counter}.md")
    counter += 1
  
  # Save to .md file with a unique name
  with open(new_filepath, 'w') as f:
    f.write(md_content)

  print(f"Markdown file saved at {new_filepath}")


def parse_content_in_template(template_path, video_details, file_name, transcript):
  content = ""
  
  # load template
  with open(template_path, 'r') as file:
    content = file.read()
  
  # remove instruction (everything before '---')
  content = "---".join(content.split("---")[1:])
  content = "---" + content
  
  content = replace_variable(content, video_details, file_name, transcript)
  
  return content
  
  
def replace_variable(content, video_details, file_name, transcript):
  content = content.replace("{{date}}", datetime.now().strftime('%Y-%m-%d'))
  content = content.replace("{{file_name}}", file_name)
  content = content.replace("{{publication_date}}", video_details.get('publication_date'))
  content = content.replace("{{video_duration}}", video_details.get('video_duration'))
  content = content.replace("{{channel}}", video_details.get('channel'))
  content = content.replace("{{video_description}}", video_details.get('video_description'))
  content = content.replace("{{video_tags}}", video_details.get('video_tags'))
  content = content.replace("{{video_title}}", video_details.get('title'))
  content = content.replace("{{video_url}}", video_details.get('url'))
  content = content.replace("{{transcript}}", transcript)
  return content

def replace_completion(content, completions):
  for prompt_name in completions:
    content = content.replace("{{"+prompt_name+"}}", completions[prompt_name])
  return content




# ---------------------- LLM Part ---------------------- 

def parse_prompt(video_details, file_name, transcript, prompt_path):
  content = ""
  
  # load template
  with open(prompt_path, 'r') as file:
    content = file.read()
  
  # remove instruction (everything before '---')
  content = "---".join(content.split("---")[1:])
  content = "---" + content
  
  content = replace_variable(content, video_details, file_name, transcript)
  
  content = content.split("```")
  content = [content[i] for i in range(1, len(content), 2)]

  prompts = [{'name':prompt.split("\n")[0], 'prompt': "\n".join(prompt.split("\n")[1:]) }for prompt in content]
  
  return prompts

def generate_notes(video_details, file_name, transcript_text, prompt_path="D:/4.Projet/Youtube-note-taker-script/prompts.md"):
  prompts = parse_prompt(video_details, file_name, transcript_text, prompt_path)
  completions = {}

  for i in range(len(prompts)):
    prompt = prompts[i].get('prompt')
    
    for prompt_name in completions:
      prompt = prompt.replace("{{"+prompt_name+"}}", completions[prompt_name])
    
    completion = generate_chat_completion(
      system_prompt = "Generate notes based on the video transcript.",
      user_prompt = prompt
    )
    
    completions[prompts[i].get('name')] = completion

  return completions


# Function to generate text using Groq API
def generate_chat_completion(system_prompt, user_prompt, model=MODEL):
  client = Groq(api_key=GROQ_API_KEY)
    
  chat_completion = client.chat.completions.create(
    messages = [
      {
        "role": "system",
        "content": system_prompt
      },
      {
        "role": "user",
        "content": user_prompt
      }
    ],

    model = model,
    temperature=0.5,
  )

  return chat_completion.choices[0].message.content

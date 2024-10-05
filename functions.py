import os
import requests
import re
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
from bs4 import BeautifulSoup
from groq import Groq, BadRequestError
from dotenv import load_dotenv
import sys
import math as Math

# Reconfigurer la sortie standard pour utiliser l'encodage 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama3-8b-8192"
#MODEL = "mixtral-8x7b-32768"


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
      transcript = transcript_list.find_transcript(['fr', 'en', 'en-GB', 'en-US', 'it'])
    except NoTranscriptFound:
      # If not found, use any available transcript
      transcript = transcript_list.find_generated_transcript(['fr', 'en', 'en-GB', 'en-US', 'it'])

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

def parse_prompt(prompt_path):
  content = ""
  
  # load template
  with open(prompt_path, 'r') as file:
    content = file.read()
  
  # remove instruction (everything before '---')
  content = "---".join(content.split("---")[1:])
  content = "---" + content
  
  content = content.split("```")
  content = [content[i] for i in range(1, len(content), 2)]

  prompts = [{'name':prompt.split("\n")[0], 'prompt': "\n".join(prompt.split("\n")[1:]) }for prompt in content]
  
  return prompts

def generate_notes(video_details, file_name, transcript_text, prompt_path="D:/4.Projet/Youtube-note-taker-script/prompts.md", model=MODEL):
  prompts = parse_prompt(prompt_path)
  completions = {}
  
  transcript = generate_shorter_transcript(transcript_text, model)
  
  # for i in range(len(prompts)):
  #   print(prompts[i])
  #   print("\n")

  for i in range(len(prompts)):
    prompt = prompts[i].get('prompt')
    
    for prompt_name in completions:
      prompt = prompt.replace("{{"+prompt_name+"}}", completions[prompt_name])
    
    prompt = replace_variable(prompt, video_details, file_name, transcript)
    
    print("\n-----------------------------------\n")
    print("Prompt:", prompt)
    
    completion = generate_chat_completion(
      system_prompt = "Generate notes based on the video transcript.",
      user_prompt = prompt,
      model = model
    )
    
    completions[prompts[i].get('name')] = completion

  return completions


# Function to generate text using Groq API
def generate_chat_completion(system_prompt, user_prompt, model=MODEL, api_key=GROQ_API_KEY):
  client = Groq(api_key=api_key)

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



# --------------- Chunking and Summarization ---------------


def estimate_token_count(prompt, model=MODEL, api_key=GROQ_API_KEY):
  return len(prompt)/3.8   # Rough estimate: 1 token ≈ 3.8 characters

def get_model_max_tokens(model):
  return {
    "mixtral-8x7b-32768": 32768,
    "llama2-70b-4096": 4096,
    "llama3-8b-8192": 8192,
    # Add other models and their token limits here
  }.get(model, 4096)  # Default


def create_chunks_with_overlap(text: str, chunk_size_in_word: int, overlap: int):
  words = text.split()
  chunks = []
  start = 0
  while start < len(words) - overlap:
    end = start + chunk_size_in_word
    chunk = ' '.join(words[start:end])
    chunks.append(chunk)
    start += chunk_size_in_word - overlap
  return chunks

def summarize_chunk(chunk: str, expected_size: int, model: str) -> str:
  return generate_chat_completion(
    system_prompt="",
    user_prompt=f"Summarize the following text in it's own language (if the text is in english, write in english, if it's in french, write in french ...) in less than {expected_size} words : {chunk}",
    model=model
  )

def generate_shorter_transcript(transcript_text: str, model: str) -> str:
  margin = 1000  # Margin to account for additional tokens in the final summary
  
  #model_max_tokens = get_model_max_tokens(model)

  model_max_tokens = 4000
  
  
  
  estimated_tokens = estimate_token_count(transcript_text)
  
  if estimated_tokens <= model_max_tokens - margin:
    return transcript_text
  
  
  # Calculate the chunk size and overlap (in token)
  chunk_size = model_max_tokens - margin
  chunk_size_in_word = Math.floor(chunk_size // 1.5)
  overlap = Math.floor(chunk_size_in_word // 4)
  

  
  print("Estimated tokens:", estimated_tokens)
  print("Model max tokens:", model_max_tokens)
  print("Chunk size in token:", chunk_size)
  print("Chunk size in word:", chunk_size_in_word)
  print("Overlap:", overlap)
  

  # Create chunks with overlap
  chunks = create_chunks_with_overlap(transcript_text, chunk_size_in_word, overlap)
  
  print("---CHUNKS------------------")
  print("")
  print("Number of chunks:", len(chunks))
  for chunk in chunks:
    print("Chunk length:", len(chunk))
    print("Estimated tokens:", estimate_token_count(chunk))
    print(chunk)
    print("----------")
    print("")
    
    
  # Summarize each chunk
  summarize_chunk_size = (model_max_tokens - margin) // len(chunks)
  summarize_chunk_size_inword = Math.floor(summarize_chunk_size // 1.5)
  summaries = [summarize_chunk(chunk, summarize_chunk_size_inword, model) for chunk in chunks]
  print("--SUMMARIES-------------------")
  print("")
  for summary in summaries:
    print("Summary length:", len(summary))
    print("Estimated tokens:", estimate_token_count(summary))
    print(summary)
    print("----------")
    print("")
  
  
  # Combine summaries
  combined_summary = " ".join(summaries)
  
  print("--FINAL-------------------")
  print("")
  print("Combined summary length:", len(combined_summary))
  print("Estimated tokens:", estimate_token_count(combined_summary))
  print(combined_summary)
  
  return combined_summary
  
  # If the combined summary is still too long, recursively summarize
  # if estimate_token_count(combined_summary) > model_max_tokens - margin:
  #   print("\n\nRecursively summarizing...\n\n")
  #   return generate_shorter_transcript(combined_summary, model)
  # else:
  #   return combined_summary

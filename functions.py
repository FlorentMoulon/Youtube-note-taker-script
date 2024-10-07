import os
import requests
import re
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
from bs4 import BeautifulSoup
import sys

from Logger import Logger
from Parser import Parser
from Generator import Generator

# use 'utf-8' for printing to console
sys.stdout.reconfigure(encoding='utf-8')

# Create a generator instance who allow to call the LLM
generator = Generator()
logger = Logger()


def generate_note_file(youtube_url, file_name, folder_path, template_path="./template.md", prompt_path="D:/4.Projet/Youtube-note-taker-script/prompts.md"):
    logger.landmark_log()
    logger.save_log(f"Generating notes for video: {youtube_url} with file name: {file_name} and template: {template_path}")
    
    # Get video details
    video_details = get_video_details(youtube_url)

    # Get transcript
    transcript = get_transcript(youtube_url)

    # Generate notes
    parser = Parser(prompt_path, generator, logger)
    md_content = parser.replace_variable(prepare_content_from_template(template_path), video_details, file_name, transcript)
    
    # Save notes to file
    create_markdown_file(md_content, file_name, folder_path)



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


def get_video_id(youtube_url):
    video_id_match = re.search(r'v=([a-zA-Z0-9_-]+)', youtube_url)
    if video_id_match:
        return video_id_match.group(1)
    return None


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
        transcript_text = transcript_text.replace('[Musique]', '')  # Remove [Musique] tags
        return transcript_text

    except NoTranscriptFound as e:
        print(f"Error retrieving transcript: {e}")
        return None



def create_markdown_file(md_content, file_name, folder_path):
    # Define the initial filepath and file extension
    base_filepath = os.path.join(folder_path, f"{file_name}.md")
    new_filepath = base_filepath
    counter = 1

    info =""

    # Check if file already exists and find a unique name
    while os.path.exists(new_filepath):
        info += f"File {new_filepath} already exists. Trying a new name...\n"
        new_filepath = os.path.join(folder_path, f"{file_name}-{counter}.md")
        counter += 1
    
    # Save to .md file with a unique name
    with open(new_filepath, 'w', encoding="utf-8") as f:
        f.write(md_content)

    info += f"Markdown file saved at {new_filepath}"
    logger.save_log(info)
    print(f"Markdown file saved at {new_filepath}")


def prepare_content_from_template(template_path):
    content = ""

    with open(template_path, 'r') as file:
        content = file.read()
    
    # remove instruction (everything before '---')
    content = "---".join(content.split("---")[1:])
    content = "---" + content
    
    return content

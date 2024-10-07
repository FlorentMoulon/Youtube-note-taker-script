import json
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
logger = Logger(True)


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



def get_transcript_data(video_url):
    try:
        # Get available transcripts for the video
        transcript_list = YouTubeTranscriptApi.list_transcripts(get_video_id(video_url))

        # Try to find a transcript in the preferred languages ('fr' or 'en')
        try:
            transcript = transcript_list.find_transcript(['fr', 'en', 'en-GB', 'en-US', 'it'])
        except NoTranscriptFound:
            # If not found, use any available transcript
            transcript = transcript_list.find_generated_transcript(['fr', 'en', 'en-GB', 'en-US', 'it'])

        return transcript.fetch()
    
    except NoTranscriptFound as e:
        print(f"Error retrieving transcript: {e}")
        return None

def get_transcript(video_url, with_chapter=True ,with_timestamps=False):
    transcript_text =""
    
    if with_chapter:
        chapter_divided_transcript = get_chapter_divided_transcript(video_url, with_timestamps)
        for chapter in chapter_divided_transcript:
            transcript_text += f"\n# {chapter['title']}\n{chapter['content']}\n"
        return transcript_text
        
    if with_timestamps:
        transcript_data = get_transcript_data(video_url)
        formatted_transcript = []
        for entry in transcript_data:
            start_time = int(entry['start'])
            text = entry['text']
            timestamp = f"{start_time // 60:02d}:{start_time % 60:02d}"
            formatted_transcript.append(f"[{timestamp}] {text}")
        transcript_text = "\n".join(formatted_transcript)
    else:
        formatter = TextFormatter()
        transcript_text = formatter.format_transcript(get_transcript_data(video_url))
    
    transcript_text = transcript_text.replace('[Musique]', '')  # Remove [Musique] tags
    return transcript_text



def get_video_description(video_url):
    video_id = get_video_id(video_url)
    if not video_id:
        return ""

    response = requests.get(f"https://www.youtube.com/watch?v={video_id}")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the script tag containing the video data
    scripts = soup.find_all('script')
    for script in scripts:
        if 'attributedDescription' in script.text:
            full_description = script.text.split('"attributedDescription":{"content":"')[1].split('","')[0]
            full_description = full_description.split('","')[0]
            
            return full_description
    return ""


def get_video_chapters(video_url):
    description = get_video_description(video_url)
    chapters = []
    
    # Regular expression to match time stamps (0:00, 1:23, 01:23, 1:23:45 etc.)
    time_pattern = r'^((?:\d{1,2}:)?\d{1,2}:\d{2})\s+(.+)$'
    
    for line in description.split('\\n'):
        match = re.match(time_pattern, line.strip())
        if match:
            time_str, title = match.groups()
            
            chapters.append({
                'time': time_str,
                'title': title.strip()
            })

    return chapters



def get_chapter_divided_transcript(video_url, with_timestamps=False):
    # timestamp are not supported for chapter divided transcript yet
    
    chapters = get_video_chapters(video_url)
    if not chapters or len(chapters) == 0:
        return get_transcript(video_url)
    
    transcript_data = get_transcript_data(video_url)
    chapter_divided_transcript = []
    current_chapter = 0
    current_chapter_text = []
    
    for entry in transcript_data:
        while current_chapter < len(chapters) - 1 and entry['start'] >= format_time_to_seconds(chapters[current_chapter + 1]['time']):
            chapter_divided_transcript.append({
                'title': chapters[current_chapter]['title'],
                'content': "\n".join(current_chapter_text)
            })
            current_chapter += 1
            current_chapter_text = []
        
        current_chapter_text.append(entry['text'])
    
    # Add the last chapter
    chapter_divided_transcript.append({
        'title': chapters[current_chapter]['title'],
        'content': "\n".join(current_chapter_text)
    })
    
    
    for i in range(len(chapter_divided_transcript)):
        chapter_divided_transcript[i]['content'] = chapter_divided_transcript[i]['content'].replace('[Musique]', '')
        chapter_divided_transcript[i]['content'] = chapter_divided_transcript[i]['content'].replace('  ', ' ')
        chapter_divided_transcript[i]['content'] = chapter_divided_transcript[i]['content'].replace(' ', ' ')
        
        
    return chapter_divided_transcript



# Function to format seconds into HH:MM:SS
def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Function to format HH:MM:SS into seconds
def format_time_to_seconds(time_str):
    time_parts = time_str.split(':')
    total_seconds = 0
    if len(time_parts) == 2:
        minutes, seconds = map(int, time_parts)
        total_seconds = minutes * 60 + seconds
    elif len(time_parts) == 3:
        hours, minutes, seconds = map(int, time_parts)
        total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds



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
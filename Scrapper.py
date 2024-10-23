import math
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
from bs4 import BeautifulSoup
import requests
import re
from Logger import Logger


from pprint import pprint




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

def get_video_id(youtube_url):    
    if "youtu.be" in youtube_url :
        video_id_match = re.search(r'youtu.be/([a-zA-Z0-9_-]+)', youtube_url)
    else:
        video_id_match = re.search(r'v=([a-zA-Z0-9_-]+)', youtube_url)
    
    if video_id_match:
        if video_id_match.group(1) == None:
            print("Error, no id found, check you URL !")
        return video_id_match.group(1)
    return None
    
    
    
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

    return {
        'url': youtube_url,
        'title': title,
        'channel': channel,
        'publication_date': publication_date,
        'video_duration': video_duration,
        'video_tags': video_tags
    }


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



def get_sponsor_segments(video_id):
    # SponsorBlock API endpoint
    base_url = "https://sponsor.ajay.app/api"
    
    # Convert video ID to URL-safe format
    url_safe_video_id = video_id.replace('/', '_').replace('+', '-')
    
    try:
        # Request sponsored segments
        response = requests.get(
            f"{base_url}/skipSegments",
            params={
                "videoID": url_safe_video_id,
                # Category types to fetch:
                # sponsor: Sponsored content
                # selfpromo: Self promotion
                # interaction: Like/Subscribe reminders
                # intro: Intro animations
                # outro: Outro animations
                # preview: Preview/recap of content
                # musicofftopic: Music section in non-music videos
                "categories": '["sponsor", "selfpromo", "interaction", "intro", "outro", "preview"]'
            }
        )
        
        if response.status_code == 200:
            segments = response.json()
            # Extract start and end times from segments
            return [(segment["segment"][0], segment["segment"][1]) for segment in segments]
        elif response.status_code == 404:
            # No segments found
            return []
        else:
            print(f"Error accessing SponsorBlock API: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error accessing SponsorBlock API: {e}")
        return []

def filter_transcript(transcript_data, sponsor_segments):
    if not sponsor_segments or len(sponsor_segments) == 0:
        return transcript_data
        
    filtered_transcript = []
    
    for entry in transcript_data:
        # Check if current transcript entry falls within any sponsor segment
        is_sponsored = any(
            start_time <= entry['start'] <= end_time
            for start_time, end_time in sponsor_segments
        )
        
        if not is_sponsored:
            filtered_transcript.append(entry)
    
    return filtered_transcript



def get_timestamp_of_entry(entry, with_hours=True, with_minutes=True, with_seconds=False):
    start_time = int(entry['start'])
    hours = start_time // 3600
    minutes = (start_time % 3600) // 60
    seconds = start_time % 60
    text = entry['text']
    timestamp = ""
    if with_hours:
        timestamp += f"{hours:02d}"
    if with_minutes:
        timestamp += ":" if timestamp!="" else ""
        timestamp += f"{minutes:02d}"
    if with_seconds:
        timestamp += ":" if timestamp!="" else ""
        timestamp += f"{seconds:02d}"
    return (f"[{timestamp}]")

def get_transcript(video_url, with_chapter=True, selected_chapters=[] ,with_timestamps=False, only_one_timestamp_per_minute=True):
    transcript_text =""
    
    if with_chapter and len(get_video_chapters(video_url))>0:
        chapter_divided_transcript = get_chapter_divided_transcript(video_url, with_timestamps)
        
        filtered_chapters = chapter_divided_transcript
        if len(selected_chapters)>0:
            selected_titles = [chap['title'] for chap in selected_chapters]
            filtered_chapters = [chapter for chapter in chapter_divided_transcript if chapter['title'] in selected_titles]

        for chapter in filtered_chapters:
            if with_timestamps:
                timestamp_chapter = chapter['content'][chapter['content'].find("["):chapter['content'].find("]")+1]
            transcript_text += f"\n{timestamp_chapter} Chapter title : {chapter['title']}\n{chapter['content']}\n"
        return transcript_text
    
        
    if with_timestamps:
        old_timestamp = ""
        transcript_data = get_transcript_data(video_url)
        formatted_transcript = []
        
        for entry in transcript_data:
            curent_timestamp = get_timestamp_of_entry(entry)
            timestamp = ""
            if not only_one_timestamp_per_minute:
                timestamp = curent_timestamp
            elif curent_timestamp != old_timestamp :
                old_timestamp = curent_timestamp
                timestamp = curent_timestamp
                
            formatted_transcript.append(f"{timestamp} {entry['text'].strip()}")

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
    
    # Remove everything before the '00:00' timestamp
    description = description[description.find('00:00'):]
    
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


def get_chapter_divided_transcript(video_url, with_timestamps=False, only_one_timestamp_per_minute=True):
    chapters = get_video_chapters(video_url)
    if not chapters or len(chapters) == 0:
        return get_transcript(video_url, with_chapter=False, with_timestamps=with_timestamps)
    
    transcript_data = get_transcript_data(video_url)
    chapter_divided_transcript = []
    current_chapter = 0
    current_chapter_text = []
    old_timestamp = ""
    
    for entry in transcript_data:
        while current_chapter < len(chapters) - 1 and entry['start'] >= format_time_to_seconds(chapters[current_chapter + 1]['time']):
            chapter_divided_transcript.append({
                'title': chapters[current_chapter]['title'],
                'content': "\n".join(current_chapter_text)
            })
            current_chapter += 1
            current_chapter_text = []
        
        if with_timestamps:
            curent_timestamp = get_timestamp_of_entry(entry)
            timestamp = ""
            if not only_one_timestamp_per_minute:
                timestamp = curent_timestamp
            elif curent_timestamp != old_timestamp :
                old_timestamp = curent_timestamp
                timestamp = curent_timestamp
                
            current_chapter_text.append(f"{timestamp} {entry}")
        else:
            current_chapter_text.append(entry['text'].strip())
    
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

class Scrapper:
    def __init__(self, youtube_url, logger = Logger()):
        self.youtube_url = youtube_url
        self.logger = logger
        self.video_id = get_video_id(youtube_url)
        self.video_details = None
        self.transcript = {}
        self.video_description = None
        self.chapters = None
        
    def get_video_details(self):
        if not self.video_details:
            self.video_details = get_video_details(self.youtube_url)
        return self.video_details
    
    def get_video_description(self):
        if not self.video_description:
            self.video_description = get_video_description(self.youtube_url)
        return self.video_description
    
    def get_transcript(self, with_chapter=True, selected_chapters=[], with_timestamps=False):
        if not self.transcript.get(with_chapter):
            self.transcript[with_chapter] = {}
        if not self.transcript.get(with_chapter).get(with_timestamps):
            self.transcript[with_chapter, with_timestamps] = get_transcript(self.youtube_url, with_chapter, selected_chapters, with_timestamps)
            
        return self.transcript[with_chapter, with_timestamps]
    
    
    def get_chapters(self):
        if not self.chapters:
            self.chapters = get_video_chapters(self.youtube_url)
        return self.chapters
    
    def get_chapters_text(self):
        chapters = self.get_chapters()
        return [f"{chapter['time']} {chapter['title']}" for chapter in chapters]


def save_test_transcript(youtube_url="https://www.youtube.com/watch?v=AmQlEcuJrFw"):
    s = Scrapper(youtube_url)
    a = s.get_transcript(with_timestamps=True)

    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(a)




def create_chunks_with_overlap(text: str, chunk_size_in_character: int, overlap: int):
    char = text.split('')
    chunks = []
    start = 0
    while start < len(char) - overlap:
        end = start + chunk_size_in_character
        chunk = ' '.join(char[start:end])
        chunks.append(chunk)
        start += chunk_size_in_character - overlap
    return chunks



def get_chapter_divided_transcript_data(transcript_data, chapters):
    chapter_divided_transcript = []
    current_chapter = 0
    current_chapter_entries = []
    for entry in transcript_data:
        while current_chapter < len(chapters) - 1 and entry['start'] >= format_time_to_seconds(chapters[current_chapter + 1]['time']):
            # if current_chapter_entries is empty, ie. everything have been revomed by sponsor_blocks, we don't add the chapter
            if current_chapter_entries != []:
                chapter_divided_transcript.append({
                    'title': chapters[current_chapter]['title'],
                    'entries': current_chapter_entries
                })
            current_chapter += 1
            current_chapter_entries = []
        current_chapter_entries.append(entry)

    return chapter_divided_transcript



def get_chapter_divided_text(chapter_divided_transcript, chapter_title_label="Chapter title: "):
    chapter_divided_text = []
    for chapter in chapter_divided_transcript:
        first_timestamp = get_timestamp_of_entry(chapter['entries'][0])
        chapter_text = first_timestamp
        chapter_text += chapter_title_label + chapter['title'] + "\n"
        
        old_timestamp = first_timestamp
        for entry in chapter['entries']:
            curent_timestamp = get_timestamp_of_entry(entry)
            timestamp = ""
            if curent_timestamp != old_timestamp :
                old_timestamp = curent_timestamp
                timestamp = f"{curent_timestamp} "
            
            chapter_text += f"{timestamp}{entry['text']}\n"
        
        chapter_divided_text.append(chapter_text)
    return chapter_divided_text


def get_chunked_transcript(video_url, chunk_size_in_character=1000, chunk_overlap=0):
    video_id = get_video_id(video_url)
    
    transcript_data = get_transcript_data(video_url)
    
    # Cleaning :
    sponsor_blocks = get_sponsor_segments(video_id)
    transcript_data = filter_transcript(transcript_data, sponsor_blocks)
    #TODO : add more cleaning and triming
    
    # Chunking :
    chunks = [""]
    
    chapters = get_video_chapters(video_url)
    
    # Chunking without chapters
    if len(chapters) == 0:
        return [] #TODO

    
    # Chunking with chapters
    chapter_divided_transcript = get_chapter_divided_transcript_data(transcript_data, chapters)
    chapter_divided_text = get_chapter_divided_text(chapter_divided_transcript)
    
    i = 0
    for chapter_text in chapter_divided_text:
        if len(chapter_text) > chunk_size_in_character:
            # we need to split the chapter text into chunks and add them to the list
            chapter_chunks = create_chunks_with_overlap(chapter_text, chunk_size_in_character, chunk_overlap)
            for chunk in chapter_chunks:
                chunks[i] += chunk + "\n"
                chunks.append("")
                i += 1
        elif len(chapter_text) + len(chunks[i]) > chunk_size_in_character:
            # we add a new chunk with the chapter text inside
            chunks.append(chapter_text + "\n")
            i += 1
        else:
            # we add the chapter text to the current chunk
            chunks[i] += chapter_text + "\n"

    if len(chunks)>0 and chunks[-1] == "":
        chunks.pop()

    return chunks


url = "https://www.youtube.com/watch?v=GTl-rBo94rw" 
# s = Scrapper(url)
# t = get_transcript_data(url)
# print(a)

from Generator import Generator
g = Generator(Logger(is_active=True))

margin = 1500 # tokens
max_token_chunk = g.get_model_max_tokens() - margin
max_char_chunk = g.token_to_char(max_token_chunk)
max_word_model = g.token_to_word(max_token_chunk)

print("max_token_chunk: ",max_token_chunk)
print("max_char_chunk: ",max_char_chunk)



chunks = get_chunked_transcript(url, max_char_chunk, math.floor(max_char_chunk/10))


print("\n---------")
for chunk in chunks:
    print("chunk length: ", len(chunk))
    print("chunk tokens: ", g.estimate_token_count(chunk))
    print(chunk[:100])
    print("\n---------")


prompt_chunk = '''
You are an expert in text summarization, capable of condensing information while preserving key points and context. Task: Summarize the provided text in {{expected_size}} words or less.

Context: This text is an excerpt from a longer document. Other excerpts will be summarized separately, and all summaries will be combined to form a final summary.

Rescpect carefully theses instructions :
1. Preserve essential information, key facts, and main ideas.
    If there is chapter title in the original text, you must keep them in your summary.
2. Maintain chronology and causal relationships if present.
    There is timestamp like [HH:mm] in the original text, you must keep them in your summary.
3. Keep proper names, dates, and important figures.
4. Retain the tone and style of the original text.
5. Ensure your summary can be understood independently but integrates well with other summaries.
6. Use the same language as the original text.

Important Rules:
- Do not begin with "Here is your summary", "This text is about..." or similar phrases.
- Do not include personal comments or additional analysis.
- Do not mention that it is a summary or an excerpt.

Text to summarize: {{chunk}}

Respond only with the summary, without any additional text.
'''

summary = []
expected_size = f"{math.floor(0.75 * max_word_model/len(chunks))}"

print("\n---------")
print("expected_size: ", expected_size)

for chunk in chunks:
    summary.append(g.generate_chat_completion("", prompt_chunk.replace("{{expected_size}}", expected_size).replace("{{chunk}}", chunk)))

print("\n---------")
print("\n---------")
print("\n---------")
for s in summary:
    print(s)
    print("\n---------")
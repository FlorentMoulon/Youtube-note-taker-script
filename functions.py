
import os
import sys

from Logger import Logger
from Parser import Parser
from Generator import Generator
from Scrapper import Scrapper

# use 'utf-8' for printing to console
sys.stdout.reconfigure(encoding='utf-8')

logger = Logger(True)


def get_chapters(youtube_url):
    scrapper = Scrapper(youtube_url, logger)
    return scrapper.get_chapters_text()

def get_chapters_data(youtube_url):
    scrapper = Scrapper(youtube_url, logger)
    return scrapper.get_chapters()


def generate_note_file(youtube_url, file_name, folder_path, template_path, prompt_path, selected_chapters=[]):
    logger.landmark_log()
    logger.save_log(f"Generating notes for video: {youtube_url} with file name: {file_name} and template: {template_path}")
    
    generator = Generator()
    
    # Get video details
    scrapper = Scrapper(youtube_url, logger)

    # Generate notes
    parser = Parser(prompt_path, scrapper, selected_chapters, generator, logger)
    md_content = parser.replace_variable(prepare_content_from_template(template_path), file_name)
    
    # Save notes to file
    create_markdown_file(md_content, file_name, folder_path)


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
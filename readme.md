# YouTube Notes Generator

Generate comprehensive markdown notes from YouTube videos using LLM-powered (Groq API) summarization.

## Description
This Python application allows users to create detailed notes from YouTube videos. It fetches video information, transcripts, and chapters, then uses LLM to generate structured notes based on the content. The app features a graphical user interface for easy interaction.


## Features
- Fetch video details, transcript, and chapters from YouTube URLs
- AI-powered summarization and note generation
- Customizable note templates and prompts
- Chunking of huge transcript to overcome LLM window limit
- Chapter selection for focused note-taking
- Simple GUI with input history


## Prerequisites
- Python 3.7+
- Required Python packages (install via `pip install -r requirements.txt`):
  - tkinter
  - youtube_transcript_api
  - beautifulsoup4
  - requests
  - groq
  - python-dotenv
- A [Groq API key](https://console.groq.com/keys) to use Groc LLM computation. (a free plan is available)


## Installation
1. Clone the repository:
   ```
   git clone https://github.com/FlorentMoulon/Youtube-note-taker-script
   cd youtube-notes-generator
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your [Groq API key](https://console.groq.com/keys) :
   ```
   GROQ_API_KEY="your_groq_api_key_here"
   ```

## Usage
1. Run the application:
   ```
   python interface.py
   ```
2. In the GUI:
   - Enter a YouTube URL
   - Select output folder and options
   - Click "Create" to generate notes
3. Find the generated markdown file in your specified output folder


## Project Structure
- `interface.py`: Main GUI application
- `functions.py`: Core functionality and helper functions
- `Parser.py`: Handles parsing of templates and prompts
- `Scrapper.py`: YouTube data extraction
- `Generator.py`: AI-powered text generation using Groq
- `Logger.py`: Logging functionality
- `files/`:
  - `prompt.md`: Customizable prompts for AI generation
  - `template.md`: Note template
  - `saved_fields.json`: Input history
  - `log.md`: Application logs


## Customization
The `template.md` and `prompts.md` files are made to be customize to feat your needs.
Here is short description of how they work, you can find more informations directly in the files.

### Variables
A variable are define in `prompts.md` and can be used in `template.md`, `prompts.md` and file name.
All {{variable_name}} used inside those 2 files will be replace by their value (if it exist) during the computation

The app give you access to a bunch of basic informations like {{video_name}} or {{transcript}}. You can also create your own variables.

### Prompts
Prompts used by the LLM are define in `prompts.md` and can be used in `template.md` and `prompts.md`.
All {{prompt_name}} will be replace by the output of the LLM for the prompt.
Before sending a prompt to the LLM, every variable and prompt called inside will replace by their values. That mean you can chain your prompt.

In the file `prompt_functions.py` you can create functions linked to prompts to perform automated task on the LLM completions before inserting them. You can use them to clean the returned text or work with JSON output for example.

You'll find some basic prompts int the prompts.md file, but can also create your own prompts.


## Contributing
Contributions are welcome! Please feel free to submit a Pull Request or send a message.


## License
This project is open source and available under the [MIT License](LICENSE).
import datetime
import math
from Generator import Generator
from Logger import Logger
from Scrapper import Scrapper

def get_file_content(path):
    with open(path, 'r') as file:
        return file.read()


class Parser:
    def __init__(self, prompt_path, scrapper, selected_chapters= [], generator=Generator(), logger=Logger()):
        self.generator = generator
        self.logger = logger
        self.scrapper = scrapper
        self.selected_chapters = selected_chapters
        self.prompts = {}
        self.variables = {}
        self.short_transcript = {}
        self.clened_transcript = {}
        self.parse_prompt_file(prompt_path)
        
    def get_variable(self, name):
        return self.variables.get(name)
    
    def get_prompt(self, name):
        return self.prompts.get(name)

    def replace_variable(self, content, file_name):
        content = content.replace("{{date}}", datetime.datetime.now().strftime('%Y-%m-%d'))
        content = content.replace("{{file_name}}", file_name)
        
        video_details = self.scrapper.get_video_details()
        content = content.replace("{{publication_date}}", video_details.get('publication_date'))
        content = content.replace("{{video_duration}}", video_details.get('video_duration'))
        content = content.replace("{{channel}}", video_details.get('channel'))
        content = content.replace("{{video_tags}}", video_details.get('video_tags'))
        content = content.replace("{{video_title}}", video_details.get('title'))
        content = content.replace("{{video_url}}", video_details.get('url'))
        
        content = content.replace("{{video_description}}", self.scrapper.get_video_description())
        
        content = self.replace_trasncript(content)

        for variable in self.variables:
            content = content.replace("{{"+variable+"}}", self.variables[variable])
        
        for prompt in self.prompts:
            if content.find("{{"+prompt+"}}") != -1:
                # parse prompt
                prompt_text = self.prompts[prompt]
                prompt_text = self.replace_variable(prompt_text, file_name)

                # generate completion
                completion = self.generator.generate_chat_completion(
                    system_prompt = "",
                    user_prompt = prompt_text,
                    name = prompt
                )
                content = content.replace("{{"+prompt+"}}", completion)
        
        return content

    def replace_trasncript(self, content):
        if content.find("{{transcript}}") != -1:
            content = content.replace("{{transcript}}", self.scrapper.get_transcript(selected_chapters=self.selected_chapters))
            
        if content.find("{{transcript_with_timecode}}") != -1:
            content = content.replace("{{transcript_with_timecode}}", self.scrapper.get_transcript(selected_chapters=self.selected_chapters, with_timecode=True))
            
        if content.find("{{llm_sized_transcript}}") != -1:
            shorter_transcript = self.get_shorter_transcript(self.scrapper.get_transcript(selected_chapters=self.selected_chapters))
            content = content.replace("{{llm_sized_transcript}}", shorter_transcript)
            
        if content.find("{{transcript_without_sponsorship}}") != -1:
            cleaned_transcript = self.get_transcript_without_sponsorship(self.scrapper.get_transcript(selected_chapters=self.selected_chapters))
            content = content.replace("{{transcript_without_sponsorship}}", cleaned_transcript)
            
        return content
    


# ---------------------- Parsing ----------------------
        
    def parse_variables(self, content):
        variables = {}
        content = content.split("\n")
        
        for i in range(len(content)):
            if content[i].startswith(">"):
                ligne = content[i].replace(">", "")
                ligne = ligne.split(":")
                variables[ligne[0].strip()] = ligne[1].strip()
        
        self.variables = variables
        return variables

    def parse_prompts(self, content):
        content = content.split("```")
        content = [content[i] for i in range(1, len(content), 2)]

        for prompt in content:
            self.prompts[prompt.split("\n")[0]] = "\n".join(prompt.split("\n")[1:])
    
        return self.prompts
    
    def parse_prompt_file(self, prompt_path):
        content = get_file_content(prompt_path)
        
        # remove instruction (everything before '---')
        content = "---".join(content.split("---")[1:])
        content = "---" + content
        
        # get vairables
        variables = self.parse_variables(content)
        
        # get prompts
        prompts = self.parse_prompts(content)
        
        return prompts, variables



# --------------- Chunking and Summarization ---------------

    def get_shorter_transcript(self, transcript: str) -> str:
        if self.short_transcript.get(transcript) is None:
            self.short_transcript[transcript] = self.generate_shorter_transcript(transcript)
            
        return self.short_transcript.get(transcript)

    def generate_shorter_transcript(self, transcript: str) -> str:
        margin = 1000  # Margin to account for additional tokens in the final summary
        
        model_max_tokens = self.generator.get_model_max_tokens()
        estimated_tokens = self.generator.estimate_token_count(transcript)
        
        if estimated_tokens <= model_max_tokens - margin:
            return transcript
        
        # Calculate the chunk size and overlap (in token)
        chunk_size = model_max_tokens - margin
        chunk_size_in_word = math.floor(chunk_size // 1.5)
        overlap = math.floor(chunk_size_in_word // 4)

        # Create chunks with overlap
        chunks = self.create_chunks_with_overlap(transcript, chunk_size_in_word, overlap)
            
        # Summarize each chunk
        summarize_chunk_size = (model_max_tokens - margin) // len(chunks)
        summarize_chunk_size_inword = math.floor(summarize_chunk_size // 1.5)
        summaries = [self.summarize_chunk(self.generate_transcript_without_sponsorship(chunk), summarize_chunk_size_inword) for chunk in chunks]
        
        # Combine summaries
        combined_summary = " ".join(summaries)
        
        

        # save logs
        info = "--CHUNKS--\n"
        info += f"Number of chunks: {len(chunks)}\n"
        for chunk in chunks:
            info += f"Chunk length: {len(chunk)}\n"
            info += f"Estimated tokens: {self.generator.estimate_token_count(chunk)}\n"
        self.logger.save_log(info)
        
        info = "--SUMMARIES--\n"
        for summary in summaries:
            info += f"Summary length: {len(summary)}\n"
            info += f"Estimated tokens: {self.generator.estimate_token_count(summary)}\n"
        self.logger.save_log(info)
        
        info = "--COMBINED SUMMARY--\n"
        info += f"Combined summary length: {len(combined_summary)}\n"
        info += f"Estimated tokens: {self.generator.estimate_token_count(combined_summary)}\n"
        self.logger.save_log(info)

        
        # If the combined summary is still too long, recursively summarize
        # if estimate_token_count(combined_summary) > model_max_tokens - margin:
        #   print("\n\nRecursively summarizing...\n\n")
        #   return generate_shorter_transcript(combined_summary, model)
        # else:
        #   return combined_summary

        return combined_summary


    def create_chunks_with_overlap(self, text: str, chunk_size_in_word: int, overlap: int):
        words = text.split()
        chunks = []
        start = 0
        while start < len(words) - overlap:
            end = start + chunk_size_in_word
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            start += chunk_size_in_word - overlap
        return chunks


    def summarize_chunk(self, chunk: str, expected_size: int, generator=Generator()) -> str:
        return generator.generate_chat_completion(
            system_prompt = "",
            user_prompt = self.prompts["SUMMARIZE_CHUNK"].replace("{{chunk}}", chunk).replace("{{expected_size}}", str(expected_size))
        )



# ---------------------- Cleaning ----------------------

    def remove_sponsorship(self, text: str) -> str:
        # a= self.prompts["REMOVE_SPONSOR"].replace("{{text}}", text)
        # print("/////")
        # print(len(a))
        # print(self.generator.estimate_token_count(a))
        # print("/////")
        return self.generator.generate_chat_completion(
            system_prompt = "",
            user_prompt = self.prompts["REMOVE_SPONSOR"].replace("{{text}}", text)
        )
        
    def get_transcript_without_sponsorship(self, transcript: str) -> str:
        if self.clened_transcript.get(transcript) is None:
            self.clened_transcript[transcript] = self.generate_transcript_without_sponsorship(transcript)
        return self.clened_transcript.get(transcript)

    def generate_transcript_without_sponsorship(self, transcript_text: str) -> str:
        margin = 200
        model_max_tokens = self.generator.get_model_max_tokens()
        estimated_tokens = self.generator.estimate_token_count(transcript_text)
        
        if estimated_tokens >= model_max_tokens//2:  
            # Calculate the chunk size and overlap (in token)
            chunk_size = model_max_tokens//2 - margin
            chunk_size_in_word = math.floor(chunk_size // 1.5)
            
            # print("---")
            # print(chunk_size)
            # print(chunk_size_in_word)
            # print("---")

            # Create chunks
            chunks = self.create_chunks_with_overlap(transcript_text, chunk_size_in_word, 0)
            # for chunk in chunks:
            #     print(len(chunk))
            #     print(self.generator.estimate_token_count(chunk))
            #     print("---")
            
            # Remove sponsorship from each chunk
            cleaned_chunks = [self.remove_sponsorship(chunk) for chunk in chunks]
            
            # Combine summaries
            cleaned_text = " ".join(cleaned_chunks)
        
        else:
            cleaned_text = self.remove_sponsorship(transcript_text)
            
        return cleaned_text
    

from groq import Groq, BadRequestError
from dotenv import load_dotenv
import os

from Logger import Logger

DEFAULT_MODEL = "llama3-8b-8192"

class Generator:
    def __init__(self):
        load_dotenv()
        self.logger = Logger()
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key)
        self.model = DEFAULT_MODEL
        self.historic = {}
        
    def set_model(self, model=DEFAULT_MODEL):
        self.model = model

    def generate_chat_completion(self, system_prompt, user_prompt, name=None):
        if name is not None:
            if name in self.historic:
                return self.historic[name]
            else:
                self.historic[name] = self.generate_chat_completion(system_prompt, user_prompt)
                return self.historic[name]
        
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            model=self.model,
            temperature=0.5,
        )
        
        self.logger.save_log(f"Prompt:\n {user_prompt} \n\n Completion:\n {chat_completion.choices[0].message.content}")

        return chat_completion.choices[0].message.content
    
    def get_model_max_tokens(self):
        return {
            "mixtral-8x7b-32768": 32768,
            "llama2-70b-4096": 4096,
            "llama3-8b-8192": 8192,
            # Add other models and their token limits here
        }.get(self.model, 4096)  # Default

    def estimate_token_count(self, prompt: str) -> int:
        return len(prompt)/3.8   # Rough estimate: 1 token ≈ 3.8 characters

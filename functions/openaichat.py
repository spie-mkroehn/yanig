from typing import List, Dict
from openai import OpenAI
import os
from functions import BaseChat


'''
this function provides an ollama endpoint to chat with
'''
class OpenAIChat(BaseChat):
    language_model:str="gpt-4o"  # "gpt-3.5-turbo"
    temperature:float=0.0

    def invoke(self, history: List[Dict[str, str]])->str:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            messages=history,
            model=self.language_model,
            stream=False
        )
        return response.choices[0].message.content

    def stream(self, history: List[Dict[str, str]])->str:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        return client.chat.completions.create(
            messages=history,
            model=self.language_model,
            stream=True
        )

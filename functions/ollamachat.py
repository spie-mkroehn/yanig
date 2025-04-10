from typing import Any, List, Dict
import ollama
from functions.basechat import BaseChat
from globals import Globals
import json


'''
this function provides an ollama endpoint to chat with
'''
class OllamaChat(BaseChat):
    language_model:str=Globals.ollama_medium_model
    temperature:float=Globals.temperature
    structured_response: Dict[str, Any] = None

    def invoke(self, history: List[Dict[str, str]])->str:
        if not any(self.language_model in model["model"] for model in ollama.list()["models"]):
            raise TypeError(f"ollama: {self.language_model} model not found") 
        if self.structured_response is None:  
            response = ollama.chat(
                model=self.language_model,
                messages=history,
                options = {
                    'temperature': self.temperature
                },
                stream=False,
            )
        else:
            response = ollama.chat(
                model=self.language_model,
                messages=history,
                options = {
                    'temperature': self.temperature
                },
                stream=False,
                format=self.structured_response,
            )
        return response['message']['content']
    
    def stream(self, history: List[Dict[str, str]]):
        if not any(self.language_model in model["model"] for model in ollama.list()["models"]):
            raise TypeError(f"ollama: {self.language_model} model not found")       
        return ollama.chat(
                model=self.language_model,
                messages=history,
                options = {
                    'temperature': self.temperature
                },
                stream=True,
            )
        
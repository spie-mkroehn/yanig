from typing import Dict, List, Optional
from functions.basechat import BaseChat
import os
from huggingface_hub import InferenceClient


class HuggingFaceChat(BaseChat):
    language_model: str = "mistralai/Mistral-7B-Instruct-v0.3"  # Default model
    temperature: float = 0.0
    
    def invoke(self, history: List[Dict[str, str]])->str:
        # Create an InferenceClient using the Hugging Face API token
        client = InferenceClient(token=os.getenv("HUGGINGFACE_API_TOKEN"))
        
        # Convert the chat history to the format expected by Hugging Face
        # Most Hugging Face chat models expect a format similar to OpenAI's
        formatted_messages = []
        for message in history:
            formatted_messages.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        # Make the API call to the Hugging Face model
        response = client.chat_completion(
            model=self.language_model,  # This will use the model specified during instantiation
            messages=formatted_messages,
            temperature=self.temperature,
            stream=False
        )
        
        # Extract and return the response content
        return response.choices[0].message.content

    def stream(self, history: List[Dict[str, str]])->str:
        # Create an InferenceClient using the Hugging Face API token
        client = InferenceClient(token=os.getenv("HUGGINGFACE_API_TOKEN"))
        
        # Convert the chat history to the format expected by Hugging Face
        formatted_messages = []
        for message in history:
            formatted_messages.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        # Make the streaming API call
        return client.chat_completion(
            model=self.language_model,  # This will use the model specified during instantiation
            messages=formatted_messages,
            temperature=self.temperature,
            stream=True
        )

from typing import Dict, List
from functions.basechat import BaseChat


class HuggingFaceChat(BaseChat):
    language_model: str
    temperature: float = 0.0
    
    #TODO: implement huggingface chat functionality
    def invoke(self, history: List[Dict[str, str]])->str:
        pass

    def stream(self, history: List[Dict[str, str]])->str:
        pass

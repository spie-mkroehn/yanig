from typing import List, Dict
from pydantic import BaseModel
from abc import ABC, abstractmethod

'''
Chat-Function base class. 
'''
class BaseChat(ABC,BaseModel):
    @abstractmethod
    def invoke(self, history: List[Dict[str, str]])->str:
        pass

    @abstractmethod
    def stream(self, history: List[Dict[str, str]])->str:
        pass
 
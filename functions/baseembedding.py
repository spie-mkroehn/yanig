from typing import List, Dict
from pydantic import BaseModel
from abc import ABC, abstractmethod

'''
Embedding-Function base class. 
'''
class BaseEmbedding(ABC,BaseModel):
    @abstractmethod
    def invoke(self, chunk: str)->List[float]:
        pass

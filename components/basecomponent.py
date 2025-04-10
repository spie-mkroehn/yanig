from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List
from core import ComponentResultObject


'''
this is somehow the "contract" for each component
has no other functionality yet
'''
class BaseComponent(ABC,BaseModel):
    @abstractmethod
    def invoke(self, input:List[ComponentResultObject])->List[ComponentResultObject]:
        pass

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List
from core import ComponentResultObject


'''
this is somehow the "contract" for each api
has no other functionality yet
api's provide read/write-operations
'''
class BaseApi(ABC,BaseModel):
    @abstractmethod
    def retrieve(self, input:List[ComponentResultObject])->List[ComponentResultObject]:
        pass

    @abstractmethod
    def write(self, output:List[ComponentResultObject]):
        pass

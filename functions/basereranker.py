from abc import abstractmethod
from typing import List
from pydantic import BaseModel
from core import ComponentResultObject


class BaseReranker(BaseModel):
    @abstractmethod
    def invoke(self, question: str, data: List[ComponentResultObject])->List[ComponentResultObject]:
        pass

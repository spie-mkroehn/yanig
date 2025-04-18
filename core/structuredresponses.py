from typing import List
from pydantic import BaseModel


class QuestionStructure(BaseModel):
    questions: List[str]

class ComparatorStructure(BaseModel):
    score: float
    summary: str

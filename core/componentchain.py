from typing import List
from pydantic import BaseModel
from core import ComponentResultObject


class ComponentChain(BaseModel):
    def invoke(data: List[ComponentResultObject], *funcs) -> List[ComponentResultObject]:
        for func in funcs:
            data = func.invoke(data)
        return data

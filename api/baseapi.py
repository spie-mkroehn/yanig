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

    def __create_cro_from_database_entry(self, id:str, rank:int, d:float, md:Dict[str, Any])->ComponentResultObject:
        cro = ComponentResultObject()
        cro["unique_id"] = id
        cro["source"] = md["source"]
        cro["content"]["publish_date"] = md["publish_date"]
        cro["content"]["original_text"] = md["original_text"]
        cro["content"]["page_number"] = md["page_number"]
        cro["preprocessing"]["result_text"] = md["result_text"]
        cro["preprocessing"]["summary"] = md["summary"]
        cro["preprocessing"]["keywords"] = md["keywords"]
        cro["preprocessing"]["category"] = md["category"]
        cro["retrieval"]["rank"] = rank + 1
        cro["retrieval"]["distance"] = d
        return cro
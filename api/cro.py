import datetime
import random
import string
import json
from typing import Any, List, Union
from core import ComponentResultObject
from api import BaseApi
from globals import Globals


class Cro(BaseApi):
    def retrieve(self, input:List[ComponentResultObject])->List[ComponentResultObject]:
        result = []
        for infile in input:
            with open(infile["source"], "r", encoding="utf-8") as f:
                result.append(self.__fix_deprecate__(json.load(f)))
                result[-1]["source"] = infile["source"]
                result[-1]["unique_id"] = self.__verify_unique_id__(result[-1])
        return result
            
    def write(self, output:List[ComponentResultObject]):
        for outfile in output:
            with open(outfile["target"], "w") as fp:
                json.dump(outfile.dictionary , fp)

    '''
    This provides compatibility to spierina componentresultobjects
    '''    
    def __fix_deprecate__(self, deprecate:ComponentResultObject)->ComponentResultObject:
        if "version" in deprecate.keys():
            return deprecate
        return ComponentResultObject(dictionary={
            "unique_id": self.__read_cro__(deprecate, "unique_id"),
            "source": None,
            "content": {
                "original_text": self.__read_cro__(deprecate, "original_text"),
                "page_number": self.__read_cro__(deprecate, "page_number"),
                "raw_image_data": self.__read_cro__(deprecate, "images"),
                "raw_audio_data": self.__read_cro__(deprecate, "raw_media_data"),
                "sampling_rate": self.__read_cro__(deprecate, "sampling_rate"),
            },           
            "preprocessing": {
                "result_text": self.__read_cro__(deprecate, "text"),
                "summary": self.__read_cro__(deprecate, "summary"),
                "keywords": self.__read_cro__(deprecate, "keywords"),
                "category": None,
                "embedding": {
                    "standard": self.__read_cro__(deprecate, "standard_embedding"),
                    "enhanced": self.__read_cro__(deprecate, "enhanced_embedding"),
                },
            },
            "target": None,
            "version": Globals.cro_version                        
            }
        )
    
    def __read_cro__(self, cro:ComponentResultObject, key:str)->Union[int, str, List[Any], None]:
        if key in cro.keys():
            return cro[key]
        else:
            return None

    def __verify_unique_id__(self, cro:ComponentResultObject)->str:
        if cro["unique_id"] is None:
            current_microseconds = f"{datetime.datetime.now().microsecond}"
            random_number = random.randint(1000, 9999)
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
            return f"{current_microseconds}_{random_number}_{random_string}"
        else:
            return cro["unique_id"]

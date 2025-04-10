from typing import List

import pdfplumber
from core import ComponentResultObject
from api import BaseApi


class PdfReader(BaseApi):

    #read compares cro (standard and enhanced embedding) with vectordb
    def retrieve(self, input:List[ComponentResultObject])->List[ComponentResultObject]:
        if input is None:
            raise KeyError("PdfReaderComponent: input is None.")        
        results = []
        for pdf in input:
            with pdfplumber.open(pdf["source"]) as f:
                for number, page in enumerate(f.pages, 1):
                    result = ComponentResultObject()
                    result["source"] = pdf["source"]
                    result["content"]["original_text"] = page.extract_text()
                    result["page_number"] = number
                    results.append(result)
        return results

    def write(self, output:List[ComponentResultObject]):
        raise KeyError("PdfReader API: write-function not implemented.")

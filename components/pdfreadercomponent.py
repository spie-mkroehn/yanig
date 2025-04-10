from components import BaseComponent
from typing import Any, Dict, List
from core import ComponentResultObject
from api import PdfReader


class PdfReaderComponent(BaseComponent):
    delimiter: str = ' '
    divider: str = '.....'
    depth: int = 3
    toc_headline_prefix: str = "Inhalt"
    toc_page_start: int = 1

    def invoke(self, input:List[ComponentResultObject])->List[ComponentResultObject]:
        if input is None:
            raise KeyError("PdfReaderComponent: input is None.")
        processed = []     
        for pdf in input:
            pages = self.__get_pdf__(pdf)
            toc = self.__extract_toc__(pdf, pages)
            chapters = self.__generate_chapters__(toc, pdf, pages)
            for chapter in chapters:
                processed.append(chapter)
        return processed
        
    def __get_pdf__(self, source: str)->List[ComponentResultObject]:
        pdfreader = PdfReader()
        return pdfreader.retrieve([source])
    
    def __extract_toc__(self, pdf: ComponentResultObject, pages: List[ComponentResultObject])->List[Dict[str,Any]]:
        toc = []
        for i in range(pdf["content"]["page_number"] - 1, 
                        pdf["content"]["page_number"] + pdf["content"]["page_count"] - 1):
            multiline = False
            for line in pages[i]["content"]["original_text"].split("\n")[self.toc_page_start:]:
                if not multiline:
                    line_prefix = line.split(self.delimiter)[0]
                if self.toc_headline_prefix in line_prefix:
                    continue
                line_suffix = line.split(self.delimiter)[-1]
                if line_prefix.count('.') < self.depth:
                    if self.divider in line:
                        toc.append({
                            "chapter": line_prefix,
                            "page_number": line_suffix
                        })
                        multiline = False
                    else:
                        multiline = True
        return toc

    def __generate_chapters__(
            self, 
            toc: List[Dict[str,Any]], 
            pdf: ComponentResultObject, 
            pages:List[ComponentResultObject]
        ):
        chapters = []
        for i in range(len(toc)-1):
            chapter = ComponentResultObject()
            chapter["source"] = pdf["source"]
            chapter["content"]["chapter"] = toc[i]["chapter"]
            chapter["content"]["page_number"] = int(toc[i]["page_number"])
            chapter["content"]["page_count"] = int(toc[i+1]["page_number"]) - int(toc[i]["page_number"]) + 1
            chapters.append(chapter)
        for i in range(len(chapters)-1):
            txt = pages[chapters[i]["content"]["page_number"] - 1]["content"]["original_text"]
            txt = f"{chapters[i]["content"]["chapter"]} {txt.split(f"{chapters[i]["content"]["chapter"]} ")[1:]}"
            if chapters[i]["content"]["page_count"] > 1:
                for j in range(chapters[i]["content"]["page_count"] - 1):
                    txt += pages[chapters[i]["content"]["page_number"] + j]["content"]["original_text"]
            txt = txt.split(f"{chapters[i+1]["content"]["chapter"]} ")[0:-1]
            chapters[i]["content"]["original_text"] = txt
        return chapters

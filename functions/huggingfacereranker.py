from typing import List
from functions import BaseReranker
from core import ComponentResultObject
from mxbai_rerank import MxbaiRerankV2


class HuggingFaceReranker(BaseReranker):
    rerank_model: str = "mixedbread-ai/mxbai-rerank-large-v2"
    reranker: MxbaiRerankV2 = None

    def invoke(self, question: str, data: List[ComponentResultObject])->List[ComponentResultObject]:
        if self.reranker is None:
            self.reranker = MxbaiRerankV2("mixedbread-ai/mxbai-rerank-base-v2")
        documents = []
        for res in data:
            documents.append(res["content"]["original_text"])
        documents_reranked = self.reranker.rank(question, documents)
        results = []
        # sort the original crs list
        results = [data[i.index] for i in documents_reranked]
        return results

    # Konfigurationsoptionen für Pydantic
    class Config:
        arbitrary_types_allowed = True

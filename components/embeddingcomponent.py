from typing import List
from functions import BaseEmbedding, OllamaEmbedding, HuggingFaceEmbedding
from components import BaseComponent
from core import ComponentResultObject
from globals import Globals


'''
this component calculates standard and enhanced embeddings for a given chunk
it calculates the embedding on base of the inital chunk and on summary and keywords
(i.e. standard_embedding and enhanced_embedding)
the modell is prefixed by "huggingface:" or "ollama:".
this determines the function called for processing the embedding task.
'''
class EmbeddingComponent(BaseComponent):
    embedding_model: str = Globals.ollama_embedding_model
    em: BaseEmbedding = None

    def invoke(self, input:List[ComponentResultObject])->List[ComponentResultObject]:
        if self.em is None:
            self.em = self.__prepare_embedding__(self.embedding_model)       
        for i in range(len(input)):
            input[i]["preprocessing"]["embedding"]["standard"] = self.__calculate_standard_embedding__(input[i], self.em)
            if input[i]["preprocessing"]["summary"] is not None:
                input[i]["preprocessing"]["embedding"]["enhanced"] = self.__calculate_enhanced_embedding__(input[i], self.em)
        return input
    
    def __prepare_embedding__(self, model: str)->BaseEmbedding:
        if "ollama:" in model:
            return OllamaEmbedding(embedding_model=self.embedding_model.split(":")[1])
        elif "huggingface:" in model:
            return HuggingFaceEmbedding(embedding_model=self.embedding_model.split(":")[1])
        else:
            raise TypeError("EmbeddingComponent: embedding model name invalid")
    
    def __calculate_standard_embedding__(self, inp:ComponentResultObject, em:BaseEmbedding)->List[float]:
        chunk = f'{inp["content"]["original_text"]}'
        return em.invoke(chunk)
    
    def __calculate_enhanced_embedding__(self, inp:ComponentResultObject, em:BaseEmbedding)->List[float]:
        chunk = f'{inp["preprocessing"]["summary"]} (Keywords: {inp["preprocessing"]["keywords"]})'
        return em.invoke(chunk)

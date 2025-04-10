from typing import ClassVar, List
from functions.baseembedding import BaseEmbedding
import ollama


'''
this function provides an ollama endpoint for calculating embeddings
'''
class OllamaEmbedding(BaseEmbedding):
    client:ClassVar[ollama.Client] = ollama.Client(host='http://localhost:11434')
    embedding_model:str

    def invoke(self, chunk: str)->List[float]:
        if not any(self.embedding_model in m["model"] for m in ollama.list()["models"]):
            raise TypeError(f"ollama: {self.embedding_model} model not found")
        result = ollama.embeddings(
            model=self.embedding_model,
            prompt=chunk,
        )
        return result["embedding"]

from typing import List
from functions.baseembedding import BaseEmbedding
from transformers import AutoTokenizer, AutoModel
from FlagEmbedding import FlagLLMModel, BGEM3FlagModel
import torch


class HuggingFaceEmbedding(BaseEmbedding):
    embedding_model:str = "baai/bge-m3"

    def invoke(self, chunk: str)->List[float]:        
        if "bge-m3" in self.embedding_model:
            model_original = BGEM3FlagModel('BAAI/bge-m3',use_fp16=True)
            result = model_original.encode_corpus(chunk)["dense_vecs"]
        elif "bge-multilingual-gemma2" in self.embedding_model:
            model_original = FlagLLMModel('BAAI/bge-multilingual-gemma2',use_fp16=True)
            result = model_original.encode_corpus(chunk)
        else:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model_original = AutoModel.from_pretrained(self.embedding_model)
            tokenizer = AutoTokenizer.from_pretrained(self.embedding_model)
            inputs = tokenizer(chunk, return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = model_original(**inputs)
            result = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
        return result

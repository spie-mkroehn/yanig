from pydantic import BaseModel
from typing import ClassVar


class Globals(BaseModel):
    cro_version: ClassVar[str] = "APOFIS v1"
    
    max_vectordb_results: ClassVar[int] = 5

    ollama_big_model: ClassVar[str] = 'ollama:llama3.1:latest'
    ollama_medium_model: ClassVar[str] = 'ollama:llama3.2:3b'
    ollama_small_model: ClassVar[str] = 'ollama:llama3.2:1b'
    openai_model: ClassVar[str] = 'openai:gpt-4o'
    temperature: ClassVar[float] = 0.0

    ollama_embedding_model: ClassVar[str] = "ollama:mxbai-embed-large"
    #ollama_embedding_model: ClassVar[str] = "ollama:bge-m3"

from typing import Any, Dict
from functions import BaseChat, OllamaChat, HuggingFaceChat, OpenAIChat


def __prepare_llm__(
    model: str, 
    temperature: float, 
    structured_response: Dict[str, Any])->BaseChat:
    if "ollama:" in model:
        if structured_response is None:
            return OllamaChat(
                language_model=model[7:],
                temperature=temperature
            )
        else:
            return OllamaChat(
                language_model=model[7:],
                temperature=temperature,
                structured_response=structured_response,
            )                
    elif "huggingface:" in model:
        return HuggingFaceChat(
            language_model=model[12:],
            temperature=temperature
        )
    elif "openai:" in model:
        return OpenAIChat(
            language_model=model[7:],
            temperature=temperature                
        )
    else:
        raise TypeError("__prepare_llm__: chat model name invalid")

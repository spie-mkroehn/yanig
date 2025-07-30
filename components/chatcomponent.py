from typing import Any, Dict, List
from functions import BaseChat, OllamaChat, HuggingFaceChat, OpenAIChat
from components import BaseStreamingComponent
from core import ComponentResultObject
import core.settings as settings
import core.commons as commons


class ChatComponent(BaseStreamingComponent):
    llm: BaseChat = None
    language_model: str = settings.ollama_model
    temperature: float = 0.0
    structured_response: Dict[str, Any] = None

    #input contains whole chat including initial system prompt
    def invoke(self, input:List[ComponentResultObject])->List[ComponentResultObject]:
        if self.llm is None:
            self.llm = commons._prepare_llm(
                    model=self.language_model,
                    temperature=self.temperature,
                    structured_response=self.structured_response
                )
        history = self._prepare_messages(input)
        answer = ComponentResultObject()
        answer["source"] = "assistant"
        answer["content"]["original_text"] = self.llm.invoke(history)
        input.append(answer) 
        return input
    
    #input contains whole chat including initial system prompt
    def stream(self, input:List[ComponentResultObject]):
        if self.llm is None:
            self.llm = commons._prepare_llm(
                    model=self.language_model,
                    temperature=self.temperature,
                    structured_response=self.structured_response
                )
        history = self._prepare_messages(input)
        return self.llm.stream(history)
    
    def _prepare_messages(self, msgs:List[ComponentResultObject])->List[Dict[str, str]]:
        history = []
        for item in msgs:
            history.append(
                {
                    "role": item["source"],
                    "content": item["content"]["original_text"]
                }
            )
        return history

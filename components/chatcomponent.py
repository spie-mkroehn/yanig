from typing import Any, Dict, List, Type
from functions import BaseChat, OllamaChat, HuggingFaceChat, OpenAIChat
from components import BaseStreamingComponent
from core import ComponentResultObject
from globals import Globals

'''
This component performs an llm operation given the complete chat history
(In this way it is possible to not only do conversation with user but also analyse chats)
'''
class ChatComponent(BaseStreamingComponent):
    llm: BaseChat = None
    language_model: str = Globals.ollama_medium_model
    temperature: float = 0.0
    structured_response: Dict[str, Any] = None

    #input contains whole chat including initial system prompt
    def invoke(self, input:List[ComponentResultObject])->List[ComponentResultObject]:
        if self.llm is None:
            self.llm = self.__prepare_llm__(
                    self.language_model,
                    self.temperature,
                    self.structured_response
                )
        history = self.__prepare_messages__(input)
        answer = ComponentResultObject()
        answer["source"] = "assistant"
        answer["content"]["original_text"] = self.llm.invoke(history)
        input.append(answer) 
        return input
    
    #input contains whole chat including initial system prompt
    def stream(self, input:List[ComponentResultObject]):
        if self.llm is None:
            self.llm = self.__prepare_llm__(
                    self.language_model,
                    self.temperature,
                    self.structured_response
                )
        history = self.__prepare_messages__(input)
        return self.llm.stream(history)
    
    def __prepare_llm__(
            self, 
            model: str, 
            temperature: float, 
            structured_response: Dict[str, Any])->BaseChat:
        if "ollama:" in model:
            if structured_response is None:
                return OllamaChat(
                    language_model=self.language_model[7:],
                    temperature=self.temperature
                )
            else:
                return OllamaChat(
                    language_model=self.language_model[7:],
                    temperature=self.temperature,
                    structured_response=self.structured_response,
                )                
        elif "huggingface:" in model:
            return HuggingFaceChat(
                language_model=self.language_model[12:],
                temperature=self.temperature
            )
        elif "openai:" in model:
            return OpenAIChat(
                language_model=self.language_model[7:],
                temperature=self.temperature                
            )
        else:
            raise TypeError("ChatComponent: chat model name invalid")
    
    def __prepare_messages__(self, msgs:List[ComponentResultObject])->List[Dict[str, str]]:
        history = []
        for item in msgs:
            history.append(
                {
                    "role": item["source"],
                    "content": item["content"]["original_text"]
                }
            )
        return history

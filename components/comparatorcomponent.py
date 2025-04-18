import json
from typing import Any, Dict, List
from functions import BaseChat
from components.basecomponent import BaseComponent
from core import ComponentResultObject, ComparatorStructure
import core.settings as settings
import core.commons as commons


class ComparatorComponent(BaseComponent):
    llm: BaseChat = None
    language_model: str = settings.ollama_model
    temperature: float = 0.0
    structured_response: Dict[str, Any] = ComparatorStructure.model_json_schema()

    def invoke(self, input:List[ComponentResultObject])->List[ComponentResultObject]:       
        systxt = '''
            Your task is to compare two texts regarding contents.
            The second text is the german translation of the first text.
            Ideally it should state the exact same points.

            Analyse the two and estimate a matching score between 0 and 1.
            1: perfect match
            0: completely different content

            Also, if there are differences summarize them in one sentence.
            The summary has to be in GERMAN.

            Your output has to be in JSON format like this:
            {
                "score": <the matching score>,
                "summary": <summarize differences>
            }
        '''

        if self.llm is None:
            self.llm = commons.__prepare_llm__(
                    model=self.language_model,
                    temperature=self.temperature,
                    structured_response=self.structured_response
                )

        for data in input:
            engtxt = data["content"]["original_text"]
            gertxt = data["preprocessing"]["result_text"]
            history = []
            history.append(
                {
                    "role": "system",
                    "content": systxt
                }
            )
            history.append(
                {
                    "role": "user",
                    "content": f"Text 1 (english):\n{engtxt}\n\nText 2 (german)\n{gertxt}"
                }
            )
            answer = json.loads(self.llm.invoke(history))
            data["preprocessing"]["score"] = answer["score"]
            data["preprocessing"]["summary"] = answer["summary"]

        return input


    # def __prepare_llm__(
    #         self, 
    #         model: str, 
    #         temperature: float, 
    #         structured_response: Dict[str, Any])->BaseChat:
    #     if "ollama:" in model:
    #         if structured_response is None:
    #             return OllamaChat(
    #                 language_model=model[7:],
    #                 temperature=temperature
    #             )
    #         else:
    #             return OllamaChat(
    #                 language_model=model[7:],
    #                 temperature=self.temperature,
    #                 structured_response=structured_response,
    #             )                
    #     elif "huggingface:" in model:
    #         return HuggingFaceChat(
    #             language_model=model[12:],
    #             temperature=temperature
    #         )
    #     elif "openai:" in model:
    #         return OpenAIChat(
    #             language_model=model[7:],
    #             temperature=temperature                
    #         )
    #     else:
    #         raise TypeError("__prepare_llm__: chat model name invalid")
           
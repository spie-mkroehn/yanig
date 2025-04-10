from os.path import join
import json
from typing import Any, Dict, List
from pydantic import BaseModel
from api import VectorDB
from core import ComponentResultObject, QuestionStructure
from components import ChatComponent, EmbeddingComponent


class MRR(BaseModel):
    dbpath:str = None

    system_texts: Dict[str, str] = {
        "role_question_generator": """
            You are a candidate of the Jeopardy Quizshow.
            You are given a text.
            Generate three specific questions regarding the content of this text.
            Return the result in JSON format:
            { questions: [<question_1>, <question_2>, <question_3>] }
            Use exactly this format. 
            The language of the questions must be the same as the language of the text.
            Return only the JSON result.
        """
    }


    def invoke(self):
        mrr_score = 0.0
        ec = EmbeddingComponent()
        vdb = VectorDB(
            client_path=join(self.dbpath),
            client_collection="wiki"
        )
        datas = vdb.get_all()
        questions = self.__generate_questions__(datas, QuestionStructure.model_json_schema())
        for cnt in range(len(questions)):
            orig_id = datas[cnt]["unique_id"]
            for i in range(len(questions[cnt])):
                question = ComponentResultObject()
                question["content"]["original_text"] = questions[cnt][i]
                question = ec.invoke([question])[0]
                matches = vdb.retrieve([question])
                for j in range(len(matches)):
                    if orig_id in matches[j]["unique_id"]:
                        mrr_score += (len(matches) - j)/len(matches)
        return mrr_score / len(questions) / len(questions[0])
        
    def __generate_questions__(self, datas:List[ComponentResultObject], structured_response: Dict[str,Any])->List[List[str]]:
        questions = []
        chatbot = ChatComponent(structured_response=QuestionStructure.model_json_schema())
        for data in datas:
            chathistory = self.__create_chat_history__(self.system_texts["role_question_generator"],
                                                        data["content"]["original_text"])           
            res = chatbot.invoke(chathistory)[-1]["content"]["original_text"]
            res = json.loads(res)
            questions.append(res["questions"])
        return questions

    def __get_ranking__(self, vdb:VectorDB)->List[ComponentResultObject]:
        vdb = VectorDB(
            client_path=join(self.dbpath),
            client_collection="wiki"
        )        
    
    def __create_chat_history__(self, systxt, qntxt):
        sysprompt = ComponentResultObject()
        sysprompt["source"] = "system"
        sysprompt["content"]["original_text"] = systxt
        qnprompt = ComponentResultObject()
        qnprompt["source"] = "user"
        qnprompt["content"]["original_text"] = f"Quizmaster: \n{qntxt}\n\nCandidate:\n"
        return [sysprompt, qnprompt]

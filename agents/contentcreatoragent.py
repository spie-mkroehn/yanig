from typing import List
from agents import BaseAgent
from components import ChatComponent, WebSearchComponent
from api import JourneyDBManager
from core import ComponentResultObject
import core.settings as settings
import json


'''
Content Creator Agent
Input: String containing the user's search keywords
Output: List of ComponentResultObject with question and answers for multiple choice
'''
class ContentCreatorAgent(BaseAgent):
    language_model: str = settings.ollama_model
    temperature: float = 0.3
    max_search_results: int = 3

    chat_prompt: str = """Du bist ein Experte für Multiple-Choice-Fragen.
        Deine Aufgabe ist es, aus einem Textabschnitt präzise und klare Multiple-Choice-Fragen zu einem vorgegebenen Thema zu generieren.
        Jede Frage soll 4 Antwortmöglichkeiten haben, von denen nur eine korrekt ist.
        Achte darauf, dass die Fragen:
        - klar und verständlich formuliert sind
        - sich auf den Inhalt des Textes beziehen
        - eine korrekte Antwort haben
        - die anderen Antworten plausibel, aber falsch sind
        Gib die Fragen im folgenden JSON-Format zurück:
        [
            {
                "question": "Deine Frage hier?",
                "answers": [
                    {"text": "Antwort A", "is_correct": false},
                    {"text": "Antwort B", "is_correct": true},
                    {"text": "Antwort C", "is_correct": false},
                    {"text": "Antwort D", "is_correct": false}
                ]
            },
            ...
        ]
        Gib nur die das JSON zurück. Kein weiterer Text. Nur das JSON."""
    
    def run(self, topic: str) -> None:
        if not topic:
            raise ValueError("question cannot be empty")
        
        # Step 1: Retrieve original text
        datas = self._perform_web_search(topic)

        # Step 2: Preprocess datas (generate single ComponentResultObject with all texts)
        datas_preproc = [ComponentResultObject()]
        datas_preproc[0]["content"]["original_text"] = topic
        datas_preproc[0]["preprocessing"]["result_text"] = ""
        for data in datas:
            datas_preproc[0]["preprocessing"]["result_text"] += data["content"]["original_text"] + "\n"

        # Step 3: Generate multiple choice questions
        questions = self._generate_multiple_choice_questions(datas_preproc)

        # Step 4: Save questions to SQLite
        self._create_database_entries(questions)

    def _generate_multiple_choice_questions(self, data_preproc: List[ComponentResultObject]) -> List[ComponentResultObject]:
        chat = ChatComponent(language_model=self.language_model, temperature=self.temperature)
        system_prompt = self.chat_prompt

        user_prompt = f"Formuliere Fragen und Antworten zu folgendem Thema: {data_preproc[0]["content"]["original_text"]}."
        user_prompt += f"\n\nVerwende folgende Hintergrundinformationen bei der Erstellung:\n\n{data_preproc[0]["preprocessing"]["result_text"]}"

        input_cros = [
            self._create_message_cro("system", system_prompt),
            self._create_message_cro("user", user_prompt)
        ]  

        result = chat.invoke(input_cros)
        response = result[-1]["content"]["original_text"]

        return self._parse_multiple_choice_questions(data_preproc[0]["content"]["original_text"], response)

    def _create_message_cro(self, role: str, content: str) -> ComponentResultObject:
        """Helper to create message ComponentResultObject"""
        cro = ComponentResultObject()
        cro["source"] = role
        cro["content"]["original_text"] = content
        return cro
        
    def _parse_multiple_choice_questions(self, topic: str, response: str) -> List[ComponentResultObject]:
        try:
            questions = json.loads(response)
            results = []
            for question in questions:
                if "answers" not in question or len(question["answers"]) != 4:
                    raise ValueError("each question must have exactly 4 answers")
                result = ComponentResultObject()
                result["content"]["original_text"] = topic
                result["preprocessing"]["questions"] = question["question"]
                result["preprocessing"]["answers"] = question["answers"]
                results.append(result)
            return results
        except json.JSONDecodeError:
            print("Failed to parse multiple choice questions.")
            return []

    def _perform_web_search(self, search_term: str) -> List[ComponentResultObject]:
        """Perform Wikipedia search for evidence"""
        websearch = WebSearchComponent(max_results=self.max_search_results)
        
        search_input = ComponentResultObject()
        search_input["content"]["original_text"] = search_term
        search_input["content"]["page_count"] = self.max_search_results
        
        results = websearch.invoke([search_input])
        print(f"📚 Found {len(results)} Wikipedia articles")
        return results
    
    def _create_database_entries(self, questions):
        journey_db_manager = JourneyDBManager()
        journey_db_manager.create_all()
        for question in questions:
            question_data = {
                "question": question["preprocessing"]["questions"],
                "answers": json.dumps(question["preprocessing"]["answers"]),
                "correct_answer": next((i for i, ans in enumerate(question["preprocessing"]["answers"]) if ans["is_correct"]), None)
            }
            if question_data["correct_answer"] is None:
                raise ValueError("Each question must have exactly one correct answer")
            journey_db_manager.create_quest(question_data)

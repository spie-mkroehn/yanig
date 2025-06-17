from typing import Dict, List
from agents import BaseAgent
from components import ChatComponent, WebSearchComponent
from core import ComponentResultObject
import core.settings as settings


'''
Dialectical Reasoning Agent implementing Hegel's dialectical method:
These -> Antithese -> Synthese

Input: Dict with "question" key containing the user's question
Output: Dict with structured reasoning including these, antithese, arguments, and synthese

This agent performs sophisticated reasoning by:
1. Generating these and antithese from the question
2. Searching for evidence supporting each position
3. Formulating arguments for both sides
4. Creating a dialectical synthese that transcends both positions
'''
class DialecticalReasoningAgent(BaseAgent):
    language_model: str = settings.ollama_model
    temperature: float = 0.3  # Slightly creative but focused
    max_search_results: int = 3
    
    def run(self, context: Dict[str, str]) -> Dict[str, str]:
        question = context.get("question", "")
        if not question:
            return {"error": "No question provided"}
        
        print(f"🤔 Starting dialectical reasoning for: {question}")
        
        # Step 1: Generate These and Antithese
        these_antithese = self._generate_these_antithese(question)
        
        # Step 2: Research and argue for These
        these_search_term = self._generate_search_term(these_antithese["these"], "supporting")
        these_evidence = self._perform_web_search(these_search_term)
        these_argumentation = self._formulate_argument(these_antithese["these"], these_evidence, "supporting")
        
        # Step 3: Research and argue for Antithese  
        antithese_search_term = self._generate_search_term(these_antithese["antithese"], "opposing")
        antithese_evidence = self._perform_web_search(antithese_search_term)
        antithese_argumentation = self._formulate_argument(these_antithese["antithese"], antithese_evidence, "supporting")
        
        # Step 4: Dialectical Synthese
        synthese = self._create_synthese(
            question, 
            these_antithese["these"], 
            these_antithese["antithese"],
            these_argumentation,
            antithese_argumentation
        )
        
        return {
            "original_question": question,
            "these": these_antithese["these"],
            "antithese": these_antithese["antithese"],
            "these_search_term": these_search_term,
            "antithese_search_term": antithese_search_term,
            "these_argumentation": these_argumentation,
            "antithese_argumentation": antithese_argumentation,
            "synthese": synthese
        }
    
    def _generate_these_antithese(self, question: str) -> Dict[str, str]:
        """Generate dialectical these and antithese from user question"""
        chat = ChatComponent(language_model=self.language_model, temperature=self.temperature)
        
        system_prompt = """Du bist ein Philosoph, der nach Hegels dialektischer Methode arbeitet. 
        Deine Aufgabe ist es, aus einer Frage eine klare THESE und eine dazu passende ANTITHESE zu formulieren.
        
        Wichtige Prinzipien:
        - These und Antithese müssen echte Gegenpositionen sein
        - Beide sollen als Aussagesätze formuliert werden
        - Sie sollen spezifisch und argumentierbar sein
        - Vermeide Extrempositionen, wähle ausgewogene Standpunkte
        
        Antworte im Format:
        THESE: [Deine These hier]
        ANTITHESE: [Deine Antithese hier]"""
        
        user_prompt = f"Frage: {question}\n\nFormuliere eine These und eine Antithese zu dieser Frage."
        
        input_cros = [
            self._create_message_cro("system", system_prompt),
            self._create_message_cro("user", user_prompt)
        ]
        
        result = chat.invoke(input_cros)
        response = result[-1]["content"]["original_text"]
        
        print(f"📝 Generated these/antithese: {response[:100]}...")
        
        return self._parse_these_antithese(response)
    
    def _generate_search_term(self, statement: str, perspective: str) -> str:
        """Convert statement into Wikipedia search term"""
        chat = ChatComponent(language_model=self.language_model, temperature=0.1)
        
        system_prompt = """Du wandelst Aussagen in optimale Wikipedia-Suchbegriffe um.
        
        Regeln:
        - Extrahiere die 2-3 wichtigsten Begriffe aus der Aussage
        - Entferne zeitliche Wörter wie "wird", "einmal", "nie", "zukünftig"
        - Fokussiere auf die Kernkonzepte
        - Verwende englische Begriffe für bessere Wikipedia-Ergebnisse
        
        Beispiele:
        "KI wird Menschen überlegen sein" → "artificial intelligence superintelligence"
        "Klimawandel ist gefährlich" → "climate change global warming"
        
        Antworte NUR mit dem Suchbegriff, keine weiteren Erklärungen."""
        
        user_prompt = f"Aussage: {statement}\n\nSuchbegriff:"
        
        input_cros = [
            self._create_message_cro("system", system_prompt),
            self._create_message_cro("user", user_prompt)
        ]
        
        result = chat.invoke(input_cros)
        search_term = result[-1]["content"]["original_text"].strip()
        
        # Fallback if LLM gives weird response
        if len(search_term) < 3 or "keine" in search_term.lower() or "perspektive" in search_term.lower():
            # Extract keywords manually as fallback
            search_term = self._extract_keywords_fallback(statement)
        
        print(f"🔍 Generated search term: {search_term}")
        return search_term
    
    def _perform_web_search(self, search_term: str) -> List[ComponentResultObject]:
        """Perform Wikipedia search for evidence"""
        websearch = WebSearchComponent(max_results=self.max_search_results)
        
        search_input = ComponentResultObject()
        search_input["content"]["original_text"] = search_term
        search_input["content"]["page_count"] = self.max_search_results
        
        results = websearch.invoke([search_input])
        print(f"📚 Found {len(results)} Wikipedia articles")
        return results
    
    def _formulate_argument(self, position: str, evidence: List[ComponentResultObject], stance: str) -> str:
        """Formulate argument for position based on evidence"""
        chat = ChatComponent(language_model=self.language_model, temperature=self.temperature)
        
        # Prepare evidence text
        evidence_text = ""
        for i, cro in enumerate(evidence):
            title = cro["content"]["title"]
            content = cro["content"]["original_text"][:1000]  # Limit content length
            evidence_text += f"\nQuelle {i+1}: {title}\n{content}\n"
        
        system_prompt = f"""Du bist ein erfahrener akademischer Philosoph und Argumentationsexperte, 
        der objektive wissenschaftliche Analysen durchführt. 
        
        Deine Aufgabe ist eine rein akademische Argumentation für Forschungs- und Bildungszwecke.
        Du analysierst verschiedene Standpunkte sachlich und neutral, ohne persönliche Meinungen.
        
        Prinzipien:
        - Nutze nur Informationen aus den gegebenen Quellen
        - Formuliere logische, nachvollziehbare Argumente  
        - Bleibe sachlich und ausgewogen
        - Zitiere relevante Fakten aus den Quellen
        - Strukturiere deine Argumentation klar
        - Dies ist eine akademische Diskussion verschiedener Standpunkte
        
        Position zu analysieren: {position}"""
        
        user_prompt = f"Verfügbare Quellen:\n{evidence_text}\n\nFormuliere eine fundierte Argumentation für die gegebene Position basierend auf diesen Quellen."
        
        input_cros = [
            self._create_message_cro("system", system_prompt),
            self._create_message_cro("user", user_prompt)
        ]
        
        result = chat.invoke(input_cros)
        argumentation = result[-1]["content"]["original_text"]
        
        print(f"⚖️ Formulated argument for: {position[:50]}...")
        return argumentation
    
    def _create_synthese(self, question: str, these: str, antithese: str, 
                          these_arg: str, antithese_arg: str) -> str:
        """Create dialectical synthese transcending both positions"""
        chat = ChatComponent(language_model=self.language_model, temperature=0.4)
        
        system_prompt = """Du bist ein Philosoph, der nach Hegels dialektischer Methode eine Synthese erstellt.
        
        Die Synthese ist NICHT ein Kompromiss oder Mittelweg, sondern eine höhere Erkenntnis, 
        die sowohl These als auch Antithese aufhebt und auf einer neuen Ebene verbindet.
        
        Prinzipien der Synthese:
        - Erkenne die Wahrheitskerne in beiden Positionen
        - Zeige die Begrenztheit beider Standpunkte auf
        - Entwickle eine übergeordnete Perspektive
        - Integriere die Erkenntnisse auf einer neuen Ebene
        - Beantworte die ursprüngliche Frage differenziert
        
        WICHTIG: Die Synthese soll präzise und knapp sein - maximal 3-5 Sätze.
        Keine Wiederholungen oder ausschweifende Erklärungen."""
        
        user_prompt = f"""Ursprüngliche Frage: {question}

THESE: {these}
Argumentation: {these_arg}

ANTITHESE: {antithese}  
Argumentation: {antithese_arg}

Erstelle eine dialektische Synthese, die über beide Positionen hinausgeht und eine höhere Erkenntnis formuliert."""
        
        input_cros = [
            self._create_message_cro("system", system_prompt),
            self._create_message_cro("user", user_prompt)
        ]
        
        result = chat.invoke(input_cros)
        synthese = result[-1]["content"]["original_text"]
        
        print("🎯 Created dialectical synthese")
        return synthese
    
    def _create_message_cro(self, role: str, content: str) -> ComponentResultObject:
        """Helper to create message ComponentResultObject"""
        cro = ComponentResultObject()
        cro["source"] = role
        cro["content"]["original_text"] = content
        return cro
    
    def _parse_these_antithese(self, response: str) -> Dict[str, str]:
        """Parse these and antithese from LLM response"""
        lines = response.split('\n')
        these = ""
        antithese = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("THESE:"):
                these = line.replace("THESE:", "").strip()
            elif line.startswith("ANTITHESE:"):
                antithese = line.replace("ANTITHESE:", "").strip()
        
        # Fallback parsing if format is different
        if not these and not antithese:
            parts = response.split("ANTITHESE:")
            if len(parts) == 2:
                these_part = parts[0].replace("THESE:", "").strip()
                antithese_part = parts[1].strip()
                these = these_part
                antithese = antithese_part
        
        return {"these": these, "antithese": antithese}

    def _extract_keywords_fallback(self, statement: str) -> str:
        """Fallback keyword extraction if LLM fails"""
        # Simple keyword mapping for common topics
        statement_lower = statement.lower()
        
        if "künstliche intelligenz" in statement_lower or "ki" in statement_lower:
            return "artificial intelligence"
        elif "klimawandel" in statement_lower:
            return "climate change"
        elif "demokratie" in statement_lower:
            return "democracy"
        elif "wirtschaft" in statement_lower:
            return "economics"
        elif "technologie" in statement_lower:
            return "technology"
        else:
            # Extract first meaningful words
            words = statement.split()
            keywords = []
            skip_words = ["wird", "ist", "sind", "war", "waren", "hat", "haben", "ein", "eine", "der", "die", "das", "und", "oder", "aber", "so", "sehr", "einmal", "nie", "immer"]
            
            for word in words:
                clean_word = word.lower().strip(".,!?;:")
                if len(clean_word) > 3 and clean_word not in skip_words:
                    keywords.append(clean_word)
                    if len(keywords) >= 2:
                        break
            
            return " ".join(keywords) if keywords else "artificial intelligence"

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import asyncio
import sys
import os

# Füge das übergeordnete Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import JourneyDBManager


# Server-Instanz erstellen
server = Server("journey-mcp-server")
journey_db_manager = JourneyDBManager()
journey_db_manager.create_all()

@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    Liste aller verfügbaren Tools
    """
    return [
        Tool(
            name="create_character",
            description="Erstellt einen neuen Standard-Charakter",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name des Charakters"},
                    "desc": {"type": "string",
                              "description": "Beschreibung des Charakters"}
                },
                "required": ["name", "desc"]
            }
        ),
        Tool(
            name="get_character",
            description="Liefert einen Charakter anhand des Namens",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name des Charakters"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="modify_character",
            description="Modifiziert einen Charakter",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name des Charakters"
                    },
                    "xp": {
                        "type": "integer",
                        "description": "Neue Erfahrungspunkte des Charakters"
                    },
                    "hp": {
                        "type": "integer",
                        "description": "Neue Lebenspunkte des Charakters"
                    },
                    "str": {
                        "type": "integer",
                        "description": "Neue Stärke des Charakters"
                    },
                    "int": {
                        "type": "integer",
                        "description": "Neue Intelligenz des Charakters"
                    },
                    "dex": {
                        "type": "integer",
                        "description": "Neue Geschicklichkeit des Charakters"
                    }
                },
                "required": ["name", "xp", "hp", "str", "int", "dex"]
            }
        ),
        Tool(
            name="get_random_quest",
            description="Liefert eine zufällige Quest aus der Datenbank",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="create_quest",
            description="Erstellt eine neue Quest/Frage in der Datenbank",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Die Frage"
                    },
                    "answer1": {
                        "type": "string",
                        "description": "Antwortmöglichkeit 1"
                    },
                    "answer2": {
                        "type": "string", 
                        "description": "Antwortmöglichkeit 2"
                    },
                    "answer3": {
                        "type": "string",
                        "description": "Antwortmöglichkeit 3"
                    },
                    "answer4": {
                        "type": "string",
                        "description": "Antwortmöglichkeit 4"
                    },
                    "correct_answer": {
                        "type": "integer",
                        "description": "Index der richtigen Antwort (1-4)",
                        "minimum": 1,
                        "maximum": 4
                    }
                },
                "required": ["question", "answer1", "answer2", "answer3", "answer4", "correct_answer"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    try:
        if name == "create_character":
            if not arguments or "name" not in arguments or "desc" not in arguments:
                raise ValueError("Name und Beschreibung sind erforderlich")
            character = journey_db_manager.create_character(arguments)
            return [TextContent(type="text", text=f"Charakter '{character.name}' erstellt.")]
        elif name == "get_character":
            if not arguments or "name" not in arguments:
                raise ValueError("Name ist erforderlich")
            character = journey_db_manager.get_character(arguments["name"])
            if character:
                return [TextContent(type="text", text=f"Charakter: {character.name}, Beschreibung: {character.desc}, "
                                    f"XP: {character.xp}, HP: {character.hp}, "
                                    f"Str: {character.str}, Int: {character.int}, Dex: {character.dex}")]
            else:
                return [TextContent(type="text", text="Charakter nicht gefunden.")]
        elif name == "modify_character":
            if not arguments or "name" not in arguments:
                raise ValueError("Name ist erforderlich")
            character = journey_db_manager.modify_character(arguments["name"], arguments)
            if character:
                return [TextContent(type="text", text=f"Charakter '{character.name}' modifiziert.")]
            else:
                return [TextContent(type="text", text="Charakter nicht gefunden.")]
        elif name == "get_random_quest":
            quest = journey_db_manager.get_random_quest()
            if quest:
                return [TextContent(type="text", text=f"Quest: {quest.question}, Antworten: {quest.answers}, "
                                    f"Richtige Antwort: {quest.correct_answer}")]
            else:
                return [TextContent(type="text", text="Keine Quests in der Datenbank vorhanden. Bitte erstellen Sie zuerst einige Quests.")]
        elif name == "create_quest":
            if not arguments or not all(key in arguments for key in ["question", "answer1", "answer2", "answer3", "answer4", "correct_answer"]):
                raise ValueError("Alle Felder (question, answer1-4, correct_answer) sind erforderlich")
            
            import json
            # Create answers array in the expected format
            answers = [
                {"text": arguments["answer1"], "is_correct": arguments["correct_answer"] == 1},
                {"text": arguments["answer2"], "is_correct": arguments["correct_answer"] == 2},
                {"text": arguments["answer3"], "is_correct": arguments["correct_answer"] == 3},
                {"text": arguments["answer4"], "is_correct": arguments["correct_answer"] == 4}
            ]
            
            quest_data = {
                "question": arguments["question"],
                "answers": json.dumps(answers),
                "correct_answer": arguments["correct_answer"] - 1  # Convert to 0-based index
            }
            
            quest = journey_db_manager.create_quest(quest_data)
            return [TextContent(type="text", text=f"Quest '{quest.question[:50]}...' wurde erfolgreich erstellt!")]
        else:
            return [TextContent(type="text", text=f"Unbekanntes Tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Fehler: {str(e)}")]

async def main():
    """
    Main function to start the server
    """
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

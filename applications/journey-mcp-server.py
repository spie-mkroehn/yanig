from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import asyncio
from api import JourneyDBManager


# Server-Instanz erstellen
server = Server("journey-mcp-server")
journey_db_manager = JourneyDBManager()

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
            description="Liefert eine zufällige Quest",
            inputSchema={
                "type": "object",
                "properties": {
                    "random_number": {
                        "type": "integer",
                        "description": "Zufallszahl für die Quest"
                    }
                },
                "required": ["random_number"]
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
            return [TextContent(f"Charakter '{character.name}' erstellt.")]
        elif name == "get_character":
            if not arguments or "name" not in arguments:
                raise ValueError("Name ist erforderlich")
            character = journey_db_manager.get_character(arguments["name"])
            if character:
                return [TextContent(f"Charakter: {character.name}, Beschreibung: {character.desc}, "
                                    f"XP: {character.xp}, HP: {character.hp}, "
                                    f"Str: {character.str}, Int: {character.int}, Dex: {character.dex}")]
            else:
                return [TextContent("Charakter nicht gefunden.")]
        elif name == "modify_character":
            if not arguments or "name" not in arguments:
                raise ValueError("Name ist erforderlich")
            character = journey_db_manager.modify_character(arguments["name"], arguments)
            if character:
                return [TextContent(f"Charakter '{character.name}' modifiziert.")]
            else:
                return [TextContent("Charakter nicht gefunden.")]
        elif name == "get_random_quest":
            if not arguments or "random_number" not in arguments:
                raise ValueError("Zufallszahl ist erforderlich")
            quest = journey_db_manager.get_random_quest(arguments["random_number"])
            if quest:
                return [TextContent(f"Quest: {quest.question}, Antworten: {quest.answers}, "
                                    f"Richtige Antwort: {quest.correct_answer}")]
            else:
                return [TextContent("Keine Quest gefunden.")]
        else:
            return [TextContent(f"Unbekanntes Tool: {name}")]
    except Exception as e:
        return [TextContent(f"Fehler: {str(e)}")]

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

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import asyncio
import sys
import os

# Füge das übergeordnete Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import CrmDBManager

# Server-Instanz erstellen
server = Server("crm-mcp-server")
crm_db_manager = CrmDBManager()
crm_db_manager.create_all()

@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    Liste aller verfügbaren Tools
    """
    return [
        Tool(
            name="create_entry",
            description="Erstellt eine neue Besprechungsnotiz",
            inputSchema={
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "Name der Firma, mit der gesprochen wurde."
                    },
                    "name": {
                        "type": "string",
                        "description": "Name des Gesprächspartners"
                    },
                    "occasion": {
                        "type": "string",
                        "description": "Art des Gesprächs: Telefongespräch, Besprechung, Privates Treffen etc."
                    },
                    "date": {
                        "type": "string",
                        "description": "Datum, wann das Gespräch stattgefunden hat"
                    },
                    "content": {
                        "type": "string",
                        "description": "Zusammenfassung des Gesprächs"
                    }
                },
                "required": ["company", "date", "content"]
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    try:
        if name == "create_entry":
            if not arguments or "company" not in arguments or "date" not in arguments or "content" not in arguments:
                raise ValueError("Es fehlen erforderliche Parameter (Erforderlich: company, date, content)")
            entry = crm_db_manager.create_character(arguments)
            return [TextContent(type="text", text=f"Gesprächsnotitz für Gespräch mit Firma '{entry.company}' vom '{entry.date} erstellt.")]
        
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

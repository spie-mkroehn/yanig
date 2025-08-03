# YaniG - Yet Another Natural Intelligence Gedöns

> *"Gedöns"* ist ein liebevolles deutsches Wort für eine Sammlung von Dingen zwischen Schnickschnack und organisiertem Chaos.

Ein modulares Python-Framework für KI-Anwendungen mit Fokus auf komponentenbasierte Architektur, Agenten-basierte Systeme und nahtlose Integration verschiedener AI-Services.

## 🚀 Features

### 🏗️ **Modulare Architektur**
- **Components**: Wiederverwendbare KI-Komponenten (Chat, Embedding, Web Search, PDF Reader, etc.)
- **Agents**: Intelligente Agenten für komplexe Aufgaben (Content Creator, Dialectical Reasoning)
- **APIs**: Datenbankmanagement und Datenverarbeitung
- **Functions**: Abstrakte Basis-Klassen für verschiedene AI-Provider

### 🤖 **AI-Provider Integration**
- **OpenAI**: Chat, Embeddings, Reranking
- **Ollama**: Lokale LLM-Integration
- **Hugging Face**: Transformers und Modelle
- **ElevenLabs**: Text-to-Speech

### 🎮 **MCP (Model Context Protocol) Server**
- **Journey MCP Server**: Direktintegration mit Claude Desktop
- **Character Management**: RPG-ähnliche Charakterverwaltung
- **Quest System**: Multiple-Choice Fragen und Quiz-System
- **Real-time Interaction**: Asynchrone Tool-Integration

### 📊 **Datenverarbeitung**
- **Vector Database**: Chromadb für semantische Suche
- **SQLite Integration**: Strukturierte Datenspeicherung
- **PDF Processing**: Automatische Dokumentenverarbeitung
- **Web Search**: Wikipedia und andere Quellen

## 📁 Projektstruktur

```
yanig/
├── agents/               # KI-Agenten
│   ├── baseagent.py     # Basis-Agent Klasse
│   ├── contentcreatoragent.py
│   └── dialecticalreasoningagent.py
├── api/                 # Datenbank und API Layer
│   ├── journeydbmanager.py
│   ├── journeydbschema.py
│   ├── vectordb.py
│   └── pdfreader.py
├── applications/        # Hauptanwendungen
│   ├── journey-mcp-server.py  # MCP Server für Claude Desktop
│   └── examples.py
├── components/          # Wiederverwendbare KI-Komponenten
│   ├── chatcomponent.py
│   ├── embeddingcomponent.py
│   ├── websearchcomponent.py
│   └── pdfreadercomponent.py
├── core/               # Kern-Framework
│   ├── componentchain.py
│   ├── componentresultobject.py
│   └── settings.py
├── functions/          # AI-Provider Implementierungen
│   ├── openaichat.py
│   ├── ollamachat.py
│   └── huggingfacechat.py
└── data/              # Datenverzeichnisse
    ├── db/           # Datenbanken
    ├── pdf/          # PDF-Dokumente
    └── json/         # JSON-Daten
```

## 🛠️ Installation

### Voraussetzungen
- Python 3.12.x
- Virtual Environment (empfohlen)

### Setup
```bash
# Repository klonen
git clone <repository-url>
cd yanig

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt
```

### Umgebungsvariablen
Erstellen Sie eine `.env`-Datei im Hauptverzeichnis:
```env
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_KEY=your_hf_api_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

## 🎮 MCP Server für Claude Desktop

### Konfiguration
Fügen Sie zu Ihrer `claude-desktop-config.json` hinzu:
```json
{
  "mcpServers": {
    "journey-mcp-server": {
      "command": "python",
      "args": [
        "c:\\path\\to\\yanig\\applications\\journey-mcp-server.py"
      ],
      "cwd": "c:\\path\\to\\yanig"
    }
  }
}
```

### Verfügbare Tools
- **`create_character`**: Erstelle RPG-Charaktere
- **`get_character`**: Charaktere abrufen
- **`modify_character`**: Charaktere modifizieren
- **`create_quest`**: Multiple-Choice Fragen erstellen
- **`get_random_quest`**: Zufällige Quiz-Fragen abrufen

## 💡 Verwendungsbeispiele

### Basic Chat Component
```python
from components import ChatComponent
from functions import OpenAIChat

chat = ChatComponent()
chat.set_chat_function(OpenAIChat())

response = chat.invoke("Erkläre mir Quantenphysik")
```

### Agent-basierte Contenterstellung
```python
from agents import ContentCreatorAgent

agent = ContentCreatorAgent()
result = agent.invoke("Erstelle Fragen zum Thema Schwarze Löcher")
```

### Datenbank-Integration
```python
from api import JourneyDBManager

db = JourneyDBManager()
character = db.create_character({
    "name": "Gandalf",
    "desc": "Ein weiser Zauberer"
})
```

## 🏗️ Architektur-Prinzipien

### Component Pattern
Alle KI-Funktionalitäten sind als wiederverwendbare Komponenten implementiert:
- **Eingabe**: `ComponentResultObject`
- **Verarbeitung**: Spezifische Logik
- **Ausgabe**: `List[ComponentResultObject]`

### Provider Abstraction
Verschiedene AI-Services werden durch einheitliche Interfaces abstrahiert:
- `BaseChat`, `BaseEmbedding`, `BaseReranker`
- Einfacher Wechsel zwischen OpenAI, Ollama, Hugging Face

### Asynchrone Verarbeitung
- Event-driven Architecture
- Non-blocking I/O Operations
- Concurrent Task Processing

## 🧪 Testing

```bash
# Alle Tests ausführen
python -m pytest

# Spezifische Tests
python test_character_creation.py
python test_mcp_tools.py
```

## 📚 Dokumentation

Weitere Dokumentation finden Sie in:
- `docs/YaniG Documentation.md` - Detaillierte Architektur-Dokumentation
- `docs/diagrams/` - UML-Diagramme und Architektur-Übersichten

## 🤝 Contributing

1. Fork des Repositories
2. Feature Branch erstellen (`git checkout -b feature/amazing-feature`)
3. Änderungen committen (`git commit -m 'Add amazing feature'`)
4. Branch pushen (`git push origin feature/amazing-feature`)
5. Pull Request erstellen

## 📄 Lizenz

Siehe `LICENSE` Datei für Details.

## 🎯 Roadmap

- [ ] Erweiterte Agent-Funktionalitäten
- [ ] Weitere AI-Provider Integration
- [ ] Web-Interface
- [ ] Docker-Containerisierung
- [ ] Mehr MCP-Tools

---

> *"Intelligence is not about having all the answers, but about building systems that can find them."* 🧠✨

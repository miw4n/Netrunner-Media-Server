🌐 Netrunner-Media-Server

    A high-performance, open-standard MCP media server with database AI-tagged works for local AI assistants.

Netrunner-Media-Server is a localized brain for media discovery. It turns any AI assistant into an expert cinephile by providing access to a massive database of 20,000+ Movies, TV Shows, and Animes.

Unlike standard databases, every entry has been processed by a local LLM (3B model) to extract "mood tags," allowing your assistant to understand the soul of a film rather than just its genre.
✨ Key Features

    🧠 AI-Powered Database: A database of 20,000+ synopses tagged one-by-one by a local AI for metadata.

    📡 MCP Standard: Built on the Model Context Protocol (MCP), making it instantly compatible with Claude, Ollama, and specialized hardware like the Xiaozhi (ESP32) box.

    🌍 Multilingual Support: While mood_tags are stored in French, modern LLMs can query the server in English, Chinese, or any other language without issues.

    🎯 Smart Profiling: The server analyzes your "Liked" history (user_rating = 1) to suggest new content based on your personal taste.

    ⚡ Ultra-Lightweight: Optimized for Raspberry Pi using SQLite with WAL mode for near-instant responses.

🛠️ The Backstory (The Marathon)

To ensure privacy and quality, this database was built during a local processing:

    AI Model: Llama-based 3B model via Ollama.

    Result: A local metadata layer that captures atmospheres like "Dark," "Epic," "Misty," or "Psychological."

🚀 Getting Started
1. Requirements

    A Raspberry Pi (or any Linux/Python server).

    Python 3.11+.

    The Xiaozhi.db file (provided in the /database folder).

2. Installation

Clone this repository and install the MCP dependencies:
Bash

pip install mcp fastmcp sqlite3

3. Launch the Server

Run the MCP server script:
Bash

python netrunner_server.py

4. Configuration

    Importing Data: If you use the provided scripts to import your own list, ensure you update your TMDB API Key in the .bat or configuration file.

    AI Persona: Use the provided PROMPT.md to give your assistant its "Netrunner" personality and ruleset.

🗣️ Voice Interaction Examples

    "Netrunner, recommend a dark sci-fi movie from the 90s I haven't seen."

    "Find me an anime with a survival vibe released after 2022."

    "I loved 'Inception', update my rating and suggest something similar."

📂 Repository Structure

    /database: SQLite schema and the pre-tagged AI metadata.

    /server: The core FastMCP Python script for your Raspberry Pi.

    /tools: The original tagging scripts and import batch files.

    PROMPT.md: The 2000-character optimized system prompt for the AI.

⚖️ License

This project is licensed under the MIT License. You are free to use, modify, and distribute it as long as the original credits are maintained.

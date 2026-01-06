# ⚡ Netrunner Media Database & AI Recommender

> "Data is the new currency. Let's rob the TMDB bank." — Lucy

[FR] Ce projet est un écosystème complet pour gérer votre bibliothèque média. Il extrait les données de TMDB, les enrichit via une IA locale (Ollama) et permet à une IA de vous faire des recommandations basées sur vos goûts.

Choix du serveur : Si vous utilisez le prompt en Français, configurez votre MCP sur server_mcp_Fr.py. Pour le prompt Anglais, utilisez server_mcp_En.py. Cela garantit que l'IA reçoit des réponses techniques dans la même langue que sa personnalité.

[EN] This project is a complete ecosystem to manage your media library. It extracts TMDB data, enriches it via local AI (Ollama), and allows an AI to give you personalized recommendations.

Server Choice: If you use the French prompt, point your MCP config to server_mcp_Fr.py. For the English prompt, use server_mcp_En.py. This ensures the AI receives technical feedback in the same language as its personality.
---

📡 NAVIGATION & EXPLORATION (Catalogue)

    -Simple Search | Recherche simple : * "Search for the movie Inception in the catalog."

        "Cherche le film Inception dans le catalogue."

    -Status Check | Vérification de statut : * "Have I already watched Matrix?"

        "Est-ce que j'ai déjà vu Matrix ?"

    -Technical Intel | Détails techniques : * "Give me the synopsis and rating for Blade Runner 2049."

        "Donne-moi le synopsis et la note de Blade Runner 2049."

    -Ambiguity Management | Gestion d'ambiguïté : * "Check if there are multiple versions of Batman."

        "Regarde s'il y a plusieurs versions de Batman."

🧠 INTELLIGENCE & PROFILE (Analysis | Analyse)

    -Profile Analysis | Analyse de profil : * "Analyze my user profile."

        "Analyse mon profil utilisateur."

    -Taste-Based Recommendation | Recommandation par goûts : * "Find a recent movie that matches my tastes."

        "Trouve-moi un film récent qui correspond à mes goûts."

    -Genre Exploration | Exploration par genre : * "Suggest a Cyberpunk-type anime that I haven't watched yet."

        "Propose-moi un anime de type Cyberpunk que je n'ai pas vu."

    -Classics & Mood | Classiques et Humeur : * "I'm in the mood for something dark, what do you have in stock?"

        "Je suis d'humeur pour quelque chose de sombre, qu'est-ce que tu as en stock ?"
        
    -Streaming Location | Localisation Streaming : * "Where can I watch the series Arcane?" 

        "Sur quelle plateforme puis-je voir la série Arcane ?"

💾 UPDATES (Feedback)

    -Positive Feedback | Avis Positif : * "I loved the movie Interstellar, update my database."

        "J'ai aimé le film Interstellar, mets à jour ma base."

    -Neutral Log | Marquage Neutre : * "Mark the series Dark as watched."

        "Marque la série Dark comme vue."

    -Negative Feedback | Avis Négatif : * "The movie [Title] was awful, record that."

        "Le film [Titre] était nul, enregistre ça."

🛠️ COMPLEX QUERIES (Multi-Filters)

    -Time & Type | Temps et Type : * "Find me a recent Thriller anime released between 2020 and 2025."

        "Trouve-moi un anime récent de type Thriller entre 2020 et 2025."

    -Similarity | Similitude : * "I want to see a movie similar to Inception from my unwatched list."

        "Je veux voir un film similaire à Inception parmi les œuvres non vues."

    -Random Scan | Scan Aléatoire : * "Suggest 5 random media, mix movies and series."

        "Suggère-moi 5 médias aléatoires, mélange films et séries."
        
---

## 🧠 MCP Integration / Intégration MCP

[FR] Ce projet est conçu pour fonctionner avec le standard **Model Context Protocol (MCP)**. La base de données `Netrun.db` est structurée pour être lue par un serveur MCP, permettant à n'importe quelle IA (Xiaozhi, Claude, etc.) d'accéder à vos médias, d'analyser vos goûts et de vous recommander du contenu en temps réel.

[EN] This project is designed to work with the **Model Context Protocol (MCP)** standard. The `Netrun.db` database is structured to be read by an MCP server, allowing any AI (Xiaozhi, Claude, etc.) to access your media, analyze your tastes, and recommend content in real-time.

---

## 🔗 MCP Server Configuration / Configuration du Serveur MCP

[FR] Connexion à l'IA : Pour que l'IA puisse accéder à la base de données, vous devez déclarer le serveur dans votre application MCP. Modifiez le chemin vers server_mcp.py dans votre configuration.
>{
  "mcpServers": {
    "netrunner": {
      "command": "python",
      "args": ["C:/PUT_YOUR_PATH/scripts/server_mcp_Fr.py"]
    }
  }
}

[EN] Connecting to AI: To allow the AI to access the database, you must declare the server in your MCP app. Update the path to server_mcp.py in your configuration.
>{
  "mcpServers": {
    "netrunner": {
      "command": "python",
      "args": ["C:/PUT_YOUR_PATH/scripts/server_mcp_En.py"]
    }
  }
}

---

## 🛠️ Project Structure / Structure du Projet

- `run_export.bat`: [EN] Entry point for TMDB extraction / [FR] Point d'entrée pour l'extraction TMDB.
- `tagging.bat`: [EN] Launches AI Tagger & Stats Monitor / [FR] Lance le tagueur IA et le moniteur de stats.
- `scripts/`: [EN] Core Python logic / [FR] Cœur du réacteur (Python).
- `Netrun.db`: [EN] SQLite database / [FR] Base de données SQLite.
- `role_prompt_En.txt` & `role_prompt_Fr.txt` : [EN] System prompts for the AI / [FR] Prompts système pour l'IA.
- `database French Tagged/` : [FR] Contient la base `Netrun.db` déjà pré-extraite et tagguée en français.
- `scripts/server_mcp_En.py` : [EN] MCP Server (English logs & tools) / [FR] Serveur MCP (Logs et outils en Anglais).
- `scripts/server_mcp_Fr.py` : [EN] MCP Server (French logs & tools) / [FR] Serveur MCP (Logs et outils en Français).
---

## 🚀 Setup & Configuration

### 1. Requirements / Prérequis
- **Python 3.10+**
- **Ollama**: [ollama.com](https://ollama.com) (Model: `qwen2.5:3b`)
- **TMDB API Key**: [themoviedb.org](https://www.themoviedb.org/settings/api)

### 2. Personality Training / Entraînement (Important!)
[FR] **Très important :** Pour que l'IA comprenne vos goûts, vous devez remplir manuellement quelques lignes dans la colonne `user_rating` de la table `media` :
- `1` : Aimé / Liked
- `0` : Neutre / Neutral
- `-1` : Détesté / Disliked

[EN] **Crucial Step:** For the AI to understand your tastes, you must manually rate a few titles in the `user_rating` column:
- `1` : Liked
- `0` : Neutral
- `-1` : Disliked

### 3. Streaming Configuration
[FR] Pour la fonction verifier_streaming, assurez-vous d'avoir configuré votre TMDB_API_KEY dans le script serveur. La région est réglée sur FR par défaut dans le code pour garantir des résultats locaux.

[EN] For the check_streaming function, ensure your TMDB_API_KEY is set in the server script. The region is set to FR by default but can be modified to US, GB, etc., in line 256.

---

### [FR] Mode d'emploi
1. **Extraction** : Lancez `run_export.bat` (Éditez-le d'abord pour ajouter votre clé API TMDB).
2. **Tagging IA** : Vérifiez qu'Ollama est lancé (`ollama serve`), puis lancez `tagging.bat` pour enrichir la base.
3. **Base de données** : Vous pouvez copier la base pré-remplie depuis `database French Tagged/` à la racine pour sauter les étapes 1 et 2.
4. **Activation IA (MCP)** : 
   - Choisissez votre langue (`server_mcp_Fr.py` ou `_En.py`).
   - Ajoutez le chemin du script dans votre configuration MCP (ex: Claude Desktop).
   - Injectez le contenu de `role_prompt_Fr.txt` (ou En) dans votre assistant pour activer la personnalité de Lucie.

### [EN] Instructions
1. **Extraction**: Run `run_export.bat` (Edit it first to add your TMDB API Key).
2. **AI Tagging**: Ensure Ollama is running (`ollama serve`), then launch `tagging.bat` to enrich the database.
3. **Database**: You can copy the pre-filled database from `database French Tagged/` to the root folder to skip steps 1 and 2.
4. **AI Activation (MCP)**: 
   - Pick your language (`server_mcp_En.py` or `_Fr.py`).
   - Add the script path to your MCP configuration (e.g., Claude Desktop).
   - Inject the content of `role_prompt_En.txt` (or Fr) into your assistant to trigger Lucy's personality.
  
---

## 🛡️ Security Note
> "Don't share your API Key on the grid. Keep it safe."
> « Ne partagez pas votre clé API. Gardez-la en lieu sûr. »

---

## ❤️ Support
If you enjoy this tool, consider buying me a bubble tea 🧋  
Si cet outil vous plaît, pensez à m'offrir un bubble tea 🧋

[**Buy Me a Coffee**](https://www.buymeacoffee.com/miw4n)

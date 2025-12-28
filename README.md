# ⚡ Netrunner Media Database & AI Recommender

> "Data is the new currency. Let's rob the TMDB bank." — Lucie

[FR] Ce projet est un écosystème complet pour gérer votre bibliothèque média. Il extrait les données de TMDB, les enrichit via une IA locale (Ollama) et permet à une IA de vous faire des recommandations basées sur vos goûts.

[EN] This project is a complete ecosystem to manage your media library. It extracts TMDB data, enriches it via local AI (Ollama), and allows an AI to give you personalized recommendations.

---

## 🧠 MCP Integration / Intégration MCP

[FR] Ce projet est conçu pour fonctionner avec le standard **Model Context Protocol (MCP)**. La base de données `Netrun.db` est structurée pour être lue par un serveur MCP, permettant à n'importe quelle IA (Xiaozhi, Claude, etc.) d'accéder à vos médias, d'analyser vos goûts et de vous recommander du contenu en temps réel.

[EN] This project is designed to work with the **Model Context Protocol (MCP)** standard. The `Netrun.db` database is structured to be read by an MCP server, allowing any AI (Xiaozhi, Claude, etc.) to access your media, analyze your tastes, and recommend content in real-time.

---

## 🛠️ Project Structure / Structure du Projet

- `run_export.bat`: [EN] Entry point for TMDB extraction / [FR] Point d'entrée pour l'extraction TMDB.
- `tagging.bat`: [EN] Launches AI Tagger & Stats Monitor / [FR] Lance le tagueur IA et le moniteur de stats.
- `scripts/`: [EN] Core Python logic / [FR] Cœur du réacteur (Python).
- `Netrun.db`: [EN] SQLite database / [FR] Base de données SQLite.
- `role_prompt_En.txt` & `role_prompt_Fr.txt` : [EN] System prompts for the AI / [FR] Prompts système pour l'IA.
- `database French Tagged/` : [FR] Contient la base `Netrun.db` déjà pré-extraite et tagguée en français.

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

---

## 🛰️ How to Use / Mode d'Emploi

### [FR] Mode d'emploi
1. **Extraction** : Lancez `run_export.bat` (Éditez-le d'abord pour ajouter votre clé API).
2. **Tagging IA** : Vérifiez qu'Ollama est lancé (`ollama serve`), puis lancez `tagging.bat`.
3. **Base de données** : Vous pouvez utiliser la base pré-remplie dans `database French Tagged/` pour sauter l'étape de scan.

### [EN] Instructions
1. **Extraction**: Run `run_export.bat` (Edit it first to add your API Key).
2. **AI Tagging**: Ensure `ollama serve` is running, then launch `tagging.bat`.
3. **Database**: You can use the pre-tagged database in `database French Tagged/` to skip the AI processing time.

---

## 🛡️ Security Note
> "Don't share your API Key on the grid. Keep it safe."
> « Ne partagez pas votre clé API. Gardez-la en lieu sûr. »

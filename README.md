# ⚡ Netrunner Media Database & AI Recommender

> "Data is the new currency. Let's rob the TMDB bank." — Lucie

[FR] Ce projet est un écosystème complet pour gérer votre bibliothèque média. Il extrait les données de TMDB, les enrichit via une IA locale (Ollama) et permet à un assistant (Xiaozhi ou autre/Lucie) de vous faire des recommandations basées sur vos goûts.

[EN] This project is a complete ecosystem to manage your media library. It extracts TMDB data, enriches it via local AI (Ollama), and allows an assistant (Xiaozhi or another/Lucie) to give you personalized recommendations.

---

## 🛠️ Project Structure / Structure du Projet

- `run_export.bat`: [EN] Entry point for TMDB extraction / [FR] Point d'entrée pour l'extraction TMDB.
- `tagging.bat`: [EN] Launches AI Tagger & Stats Monitor / [FR] Lance le tagueur IA et le moniteur de stats.
- `scripts/`: [EN] Core Python logic / [FR] Cœur du réacteur (Python).
- `Netrun.db`: [EN] SQLite database / [FR] Base de données SQLite.

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

1. **Extraction**: Run `run_export.bat` (Edit it first to add your API Key). / Exécutez `run_export.bat` (Modifiez-le d'abord pour ajouter votre clé API).
2. **AI Tagging**: Ensure `ollama serve` is running, then launch `tagging.bat`. / Assurez-vous que `ollama serve` est en cours d'exécution, puis lancez `tagging.bat`.
3. **Enjoy**: Your database is now ready for the AI prompt! / Votre base de données est maintenant prête pour l'IA !

---

## 🛡️ Security Note
> "Don't share your API Key on the grid. Keep it safe."
> « Ne partagez pas votre clé API. Gardez-la en lieu sûr. »

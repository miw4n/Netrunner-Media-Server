import os
import sqlite3
import asyncio
import sys
from mcp.server.fastmcp import FastMCP

# Force les logs en temps réel
sys.stdout.reconfigure(line_buffering=True)

# ------------------------
# Configuration
# ------------------------
BASE_DIR = "/PUT_YOUR_PATH/Your_Folder"
# VERIFIE BIEN LE NOM ICI : Xiaozhi.db ou media.db ?
DB_PATH = os.path.join(BASE_DIR, "Netrun.db") 

# ------------------------
# Initialisation MCP
# ------------------------
mcp = FastMCP("Netrunner-Media-Server")

# ------------------------
# Utilitaires
# ------------------------
def get_db_connection():
    """Crée une connexion sécurisée à la base SQLite."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA wal_autocheckpoint = 10;") 
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

# ------------------------
# Tools MCP
# ------------------------

@mcp.tool()
def consulter_catalogue(titre: str) -> str:
    """Recherche les détails d'une œuvre (titre, synopsis, notes...)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT id, title, year, rating_tmdb, synopsis, user_rating, watched, mood_tags FROM media WHERE title LIKE ? OR original_title LIKE ? LIMIT 1"
        cursor.execute(query, (f'%{titre}%', f'%{titre}%'))
        row = cursor.fetchone()
        conn.close()

        if row:
            status = "Vu" if row[6] == 1 else "À voir"
            return (f"Titre: {row[1]} ({row[2]}) | Note TMDB: {row[3]}/10 | "
                    f"Ton Avis: {row[5]} | Statut: {status} | Tags: {row[7]} | Synopsis: {row[4]}")
        return f"Je n'ai pas trouvé '{titre}' dans la bibliothèque."
    except Exception as e:
        return f"Erreur technique : {str(e)}"

@mcp.tool()
def film_vu_aime_ou_pas(titre: str, avis: str = None, vu: bool = None) -> str:
    """Met à jour un film (vu/note) par son titre uniquement."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Recherche du film
        cursor.execute("SELECT id, title FROM media WHERE title LIKE ? LIMIT 1", (f"%{titre}%",))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return f"Désolé, je n'ai pas trouvé '{titre}' dans ta liste."
        
        film_id, film_titre = row
        updates, params = [], []

        # 2. Logique de notation (Correction pour accepter les chiffres directs)
        if avis is not None:
            # Dictionnaire de mots-clés
            notes_mots = {
                "aimé": 1, "bien": 1, "génial": 1, "top": 1, "adore": 1,
                "neutre": 0, "moyen": 0, "passable": 0,
                "pas aimé": -1, "nul": -1, "détesté": -1, "mauvais": -1
            }
            
            valeur = None
            
            # Cas 1 : L'IA envoie un chiffre sous forme de string ("1", "0", "-1")
            if str(avis) in ["1", "0", "-1"]:
                valeur = int(avis)
            # Cas 2 : L'IA envoie un mot ("aimé", "nul")
            else:
                valeur = notes_mots.get(avis.lower())

            if valeur is not None:
                updates.append("user_rating = ?")
                params.append(valeur)
                # Si on donne un avis, on considère que c'est vu (sauf si c'est neutre 0)
                if valeur != 0:
                    updates.append("watched = 1")
                    

        # 3. Logique de visionnage explicite (Correction pour 0 et 1)
        if vu is not None:
            # On convertit en 1 ou 0 peu importe ce que l'IA envoie (booléen ou int)
            valeur_vu = 1 if (vu is True or vu == 1) else 0
            
            # On n'ajoute l'update que si watched=1 n'est pas déjà prévu par la note
            if "watched = 1" not in updates:
                updates.append("watched = ?")
                params.append(valeur_vu)

        if not updates:
            conn.close()
            return f"Rien à modifier pour '{film_titre}'."

        # 4. Exécution
        sql = f"UPDATE media SET {', '.join(updates)} WHERE id = ?"
        params.append(film_id)
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
        
        return f"C'est noté ! '{film_titre}' a été mis à jour."

    except Exception as e:
        return f"Erreur de mise à jour : {str(e)}"

@mcp.tool()
def recommander_media(mood: str = None, type_media: str = None, annee_min: int = None, annee_max: int = None, genre_similaire: str = None) -> str:
    """
    Recherche aléatoire de médias non vus selon des filtres.
    type_media peut être 'movie', 'tv' ou 'anime'.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base de la requête
        query = "SELECT title, year, genres, rating_tmdb, mood_tags, type FROM media WHERE watched = 0"
        params = []

        if type_media:
            query += " AND type = ?"; params.append(type_media.lower())
        
        if annee_min:
            query += " AND year >= ?"; params.append(annee_min)
        
        if annee_max:
            query += " AND year <= ?"; params.append(annee_max)
        
        if mood:
            query += " AND (mood_tags LIKE ? OR genres LIKE ?)"
            params.append(f'%{mood}%')
            params.append(f'%{mood}%')
            
        if genre_similaire:
            query += " AND genres LIKE ?"
            params.append(f'%{genre_similaire}%')

        query += " ORDER BY RANDOM() LIMIT 5"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        if not rows: return "Je n'ai rien trouvé qui corresponde exactement, essaie d'élargir tes critères !"
        
        res = "📡 Voici ce que j'ai déniché pour toi :\n" 
        for r in rows:
            type_label = "🎬 Film" if r[5] == 'movie' else "📺 Série/Anime"
            res += f"- {r[0]} ({r[1]}) | {type_label} | Tags: {r[4]}\n"
        return res
    except Exception as e:
        return f"Erreur de scan : {str(e)}"

@mcp.tool()
def analyser_profil_utilisateur() -> str:
    """Analyse les tags des films que Miwan a noté 'aimé' (1)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT mood_tags FROM media WHERE user_rating = 1")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows: return "Tu n'as pas encore noté de films."
        
        all_tags = []
        for r in rows:
            if r[0]: all_tags.extend([t.strip().capitalize() for t in r[0].split(",")])
        
        from collections import Counter
        top_tags = [t for t, c in Counter(all_tags).most_common(5)]
        return f"Tes thèmes favoris sont : {', '.join(top_tags)}."
    except Exception as e:
        return f"Erreur profil : {str(e)}"

# ------------------------
# Lancement
# ------------------------
if __name__ == "__main__":
    mcp.run(transport="stdio")
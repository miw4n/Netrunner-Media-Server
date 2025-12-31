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
    """Recherche les détails d'une œuvre. Retourne une liste si plusieurs matchs."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # On passe à LIMIT 10 pour attraper toutes les suites/versions
        query = """
            SELECT title, year, rating_tmdb, synopsis, user_rating, watched, mood_tags 
            FROM media 
            WHERE title LIKE ? OR original_title LIKE ? 
            ORDER BY year ASC
            LIMIT 10
        """
        cursor.execute(query, (f'%{titre}%', f'%{titre}%'))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"Cible '{titre}' introuvable dans le Datalake."

        # Si un seul film : on donne tout
        if len(rows) == 1:
            r = rows[0]
            status = "Vu" if r[5] == 1 else "À voir"
            return (f"Titre: {r[0]} ({r[1]}) | Note TMDB: {r[2]}/10 | "
                    f"Ton Avis: {r[4]} | Statut: {status} | Tags: {r[6]} | Synopsis: {r[3]}")

        # Si plusieurs films (ex: Deadpool 1, 2, 3) : Format compact
        res = "📡 Multiples signatures détectées :\n"
        for r in rows:
            res += f"- {r[0]} ({r[1]}) note {r[2]}/10\n"
        res += "Lequel souhaites-tu sélectionner ?"
        return res

    except Exception as e:
        return f"Erreur système : {str(e)}"
        

@mcp.tool()
def film_vu_aime_ou_pas(titre: str, avis: str = None, vu: bool = None) -> str:
    """Met à jour un film (vu/note) par son titre uniquement."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # On récupère jusqu'à 5 correspondances triées par pertinence
        cursor.execute("""
            SELECT id, title, year FROM media 
            WHERE title LIKE ? 
            ORDER BY ABS(LENGTH(title) - LENGTH(?)) ASC 
            LIMIT 5
        """, (f"%{titre}%", titre))
        rows = cursor.fetchall()

        # CAS 1 : Introuvable
        if not rows:
            conn.close()
            return f"Désolé , je n'ai pas trouvé '{titre}' dans la bibliothèque."

        # CAS 2 : Ambiguïté (Plusieurs films avec des noms proches)
        # Si on a plusieurs résultats et que le premier n'est pas EXACTEMENT le titre tapé
        if len(rows) > 1 and rows[0][1].lower() != titre.lower():
            conn.close()
            options = "\n".join([f"- {r[1]} ({r[2]})" for r in rows])
            return (f"Plusieurs cibles correspondent à '{titre}'. "
                    f"Laquelle dois-je mettre à jour ?\n{options}")

        # CAS 3 : Match trouvé (Exact ou le seul disponible)
        film_id, film_titre, film_annee = rows[0]
        updates, params = [], []

        if avis is not None:
            notes_mots = {
                "aimé": 1, "bien": 1, "génial": 1, "top": 1, "adore": 1,
                "neutre": 0, "moyen": 0, "passable": 0,
                "pas aimé": -1, "nul": -1, "détesté": -1, "mauvais": -1
            }
            valeur = int(avis) if str(avis) in ["1", "0", "-1"] else notes_mots.get(avis.lower())
            
            if valeur is not None:
                updates.append("user_rating = ?")
                params.append(valeur)
                if valeur != 0:
                    updates.append("watched = 1")

        if vu is not None:
            valeur_vu = 1 if (vu is True or vu == 1) else 0
            if "watched = 1" not in updates:
                updates.append("watched = ?")
                params.append(valeur_vu)

        if not updates:
            conn.close()
            return f"Aucune instruction de mise à jour pour '{film_titre}'."

        sql = f"UPDATE media SET {', '.join(updates)} WHERE id = ?"
        params.append(film_id)
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
        
        return f"C'est noté ! '{film_titre} ({film_annee})' a été mis à jour dans le système."

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
    """Analyse les tags des films noté 'aimé' (1)."""
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

import os
import sqlite3
import asyncio
import sys
from mcp.server.fastmcp import FastMCP

# Force real-time logging
sys.stdout.reconfigure(line_buffering=True)

# ------------------------
# Configuration
# ------------------------
BASE_DIR = "/PUT_YOUR_PATH/Your_Folder"
# DOUBLE CHECK THE NAME HERE: Netrun.db
DB_PATH = os.path.join(BASE_DIR, "Netrun.db") 

# ------------------------
# MCP Initialization
# ------------------------
mcp = FastMCP("Netrunner-Media-Server")

# ------------------------
# Utilities
# ------------------------
def get_db_connection():
    """Creates a secure connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA wal_autocheckpoint = 10;") 
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

# ------------------------
# MCP Tools
# ------------------------

@mcp.tool()
def consulter_catalogue(titre: str) -> str:
    """Search for media details. Returns a list if multiple matches found."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # LIMIT 10 to catch all sequels/versions
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
            return f"Target '{titre}' not found in the Datalake."

        # If single match: return full details
        if len(rows) == 1:
            r = rows[0]
            status = "Watched" if r[5] == 1 else "To watch"
            return (f"Title: {r[0]} ({r[1]}) | TMDB Rating: {r[2]}/10 | "
                    f"Your Rating: {r[4]} | Status: {status} | Tags: {r[6]} | Synopsis: {r[3]}")

        # If multiple matches: Compact format
        res = "📡 Multiple signatures detected:\n"
        for r in rows:
            res += f"- {r[0]} ({r[1]}) rating {r[2]}/10\n"
        res += "Which one do you want to select?"
        return res

    except Exception as e:
        return f"System Error: {str(e)}"
        

@mcp.tool()
def film_vu_aime_ou_pas(titre: str, avis: str = None, vu: bool = None) -> str:
    """Update a movie (watched/rating) by its title."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Retrieve matches sorted by relevance
        cursor.execute("""
            SELECT id, title, year FROM media 
            WHERE title LIKE ? 
            ORDER BY ABS(LENGTH(title) - LENGTH(?)) ASC 
            LIMIT 5
        """, (f"%{titre}%", titre))
        rows = cursor.fetchall()

        # CASE 1: Not found
        if not rows:
            conn.close()
            return f"Sorry, I couldn't find '{titre}' in the library."

        # CASE 2: Ambiguity
        if len(rows) > 1 and rows[0][1].lower() != titre.lower():
            conn.close()
            options = "\n".join([f"- {r[1]} ({r[2]})" for r in rows])
            return (f"Multiple targets match '{titre}'. "
                    f"Which one should I update?\n{options}")

        # CASE 3: Match found
        film_id, film_titre, film_annee = rows[0]
        updates, params = [], []

        if avis is not None:
            # English keyword mapping
            notes_mots = {
                "liked": 1, "good": 1, "great": 1, "top": 1, "love": 1,
                "neutral": 0, "okay": 0, "average": 0,
                "disliked": -1, "bad": -1, "hated": -1, "awful": -1
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
            return f"No update instructions for '{film_titre}'."

        sql = f"UPDATE media SET {', '.join(updates)} WHERE id = ?"
        params.append(film_id)
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
        
        return f"Acknowledge! '{film_titre} ({film_annee})' has been updated in the system."

    except Exception as e:
        return f"Update Error: {str(e)}"

@mcp.tool()
def recommander_media(mood: str = None, type_media: str = None, annee_min: int = None, annee_max: int = None, genre_similaire: str = None) -> str:
    """
    Random search for unwatched media based on filters.
    type_media can be 'movie', 'tv' or 'anime'.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query
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

        if not rows: return "I found nothing matching these criteria, try widening your search!"
        
        res = "📡 Here is what I extracted for you:\n" 
        for r in rows:
            type_label = "🎬 Movie" if r[5] == 'movie' else "📺 Series/Anime"
            res += f"- {r[0]} ({r[1]}) | {type_label} | Tags: {r[4]}\n"
        return res
    except Exception as e:
        return f"Scan Error: {str(e)}"

@mcp.tool()
def analyser_profil_utilisateur() -> str:
    """Analyze tags from media rated as 'liked' (1)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT mood_tags FROM media WHERE user_rating = 1")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows: return "You haven't rated any movies yet."
        
        all_tags = []
        for r in rows:
            if r[0]: all_tags.extend([t.strip().capitalize() for t in r[0].split(",")])
        
        from collections import Counter
        top_tags = [t for t, c in Counter(all_tags).most_common(20)]
        return f"Your favorite themes are: {', '.join(top_tags)}."
    except Exception as e:
        return f"Profile Error: {str(e)}"

# ------------------------
# Launch
# ------------------------
if __name__ == "__main__":
    mcp.run(transport="stdio")


import os
import sqlite3
import asyncio
import sys
from collections import Counter
from mcp.server.fastmcp import FastMCP

# Force real-time logging for the MCP pipe
sys.stdout.reconfigure(line_buffering=True)

# ------------------------
# Configuration
# ------------------------
BASE_DIR = "/PUT_YOUR_PATH/Your_Folder"
DB_PATH = os.path.join(BASE_DIR, "..", "Netrun.db") 

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
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA wal_autocheckpoint = 10;") 
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

# ------------------------
# MCP Tools (English Version)
# ------------------------

@mcp.tool()
def consulter_catalogue(title: str) -> str:
    """Search for media details (title, synopsis, ratings, tags)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT title, year, rating_tmdb, synopsis, user_rating, watched, mood_tags FROM media WHERE title LIKE ? OR original_title LIKE ? LIMIT 1"
        cursor.execute(query, (f'%{title}%', f'%{title}%'))
        row = cursor.fetchone()
        conn.close()

        if row:
            status = "Watched" if row['watched'] == 1 else "Plan to Watch"
            return (f"Title: {row['title']} ({row['year']}) | TMDB Rating: {row['rating_tmdb']}/10 | "
                    f"User Rating: {row['user_rating']} | Status: {status} | Tags: {row['mood_tags']} | Synopsis: {row['synopsis']}")
        return f"Database search failed: '{title}' not found in the grid."
    except Exception as e:
        return f"Technical glitch: {str(e)}"

@mcp.tool()
def film_vu_aime_ou_pas(title: str, feedback: str = None, watched: bool = None) -> str:
    """Update a movie/show status (watched/rating) using its title."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM media WHERE title LIKE ? LIMIT 1", (f"%{title}%",))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return f"Access denied: '{title}' not found in your logs."
        
        media_id, media_title = row['id'], row['title']
        updates, params = [], []

        if feedback is not None:
            # Multi-language keyword mapping
            rating_map = {
                "liked": 1, "loved": 1, "great": 1, "good": 1, "aimé": 1, "top": 1,
                "neutral": 0, "okay": 0, "average": 0, "neutre": 0, "moyen": 0,
                "disliked": -1, "bad": -1, "hated": -1, "nul": -1, "détesté": -1
            }
            
            value = None
            if str(feedback) in ["1", "0", "-1"]:
                value = int(feedback)
            else:
                value = rating_map.get(feedback.lower())

            if value is not None:
                updates.append("user_rating = ?")
                params.append(value)
                if value != 0: # If rated (liked or disliked), it's obviously watched
                    updates.append("watched = 1")

        if watched is not None:
            watched_val = 1 if (watched is True or watched == 1) else 0
            if "watched = 1" not in updates:
                updates.append("watched = ?")
                params.append(watched_val)

        if not updates:
            conn.close()
            return f"No modifications requested for '{media_title}'."

        sql = f"UPDATE media SET {', '.join(updates)} WHERE id = ?"
        params.append(media_id)
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
        return f"Uplink successful: '{media_title}' has been updated."
    except Exception as e:
        return f"Write error: {str(e)}"

@mcp.tool()
def recommander_media(mood: str = None, media_type: str = None, year_min: int = None, year_max: int = None, similar_genre: str = None) -> str:
    """Random search for unwatched media based on filters (movie, tv, or anime)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT title, year, genres, rating_tmdb, mood_tags, type FROM media WHERE watched = 0"
        params = []

        if media_type:
            query += " AND type = ?"; params.append(media_type.lower())
        if year_min:
            query += " AND year >= ?"; params.append(year_min)
        if year_max:
            query += " AND year <= ?"; params.append(year_max)
        if mood:
            query += " AND (mood_tags LIKE ? OR genres LIKE ?)"
            params.extend([f'%{mood}%', f'%{mood}%'])
        if similar_genre:
            query += " AND genres LIKE ?"
            params.append(f'%{similar_genre}%')

        query += " ORDER BY RANDOM() LIMIT 5"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        if not rows: return "No data matches your query. Try broadening the search parameters."
        
        res = "📡 Incoming signal! I've found these for you:\n" 
        for r in rows:
            label = "🎬 Movie" if r['type'] == 'movie' else "📺 Show/Anime"
            res += f"- {r['title']} ({r['year']}) | {label} | Tags: {r['mood_tags']}\n"
        return res
    except Exception as e:
        return f"Scan failed: {str(e)}"

@mcp.tool()
def analyser_profil_utilisateur() -> str:
    """Analyze the tags of media rated as 'Liked' (1) to find user preferences."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT mood_tags FROM media WHERE user_rating = 1")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows: return "Profile is empty. Rate some media first (1 = Liked)."
        
        all_tags = []
        for r in rows:
            if r['mood_tags']: 
                all_tags.extend([t.strip().capitalize() for t in r['mood_tags'].split(",")])
        
        top_tags = [t for t, c in Counter(all_tags).most_common(5)]
        return f"User preferences detected. Top themes: {', '.join(top_tags)}."
    except Exception as e:
        return f"Profile analysis error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
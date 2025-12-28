import os
import sys
import requests
import time
import sqlite3
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==========================
# CONFIGURATION
# ==========================
# Get API KEY from CLI arguments
if len(sys.argv) < 2:
    print("Usage: python extractor.py <YOUR_TMDB_API_KEY>")
    sys.exit(1)

API_KEY = sys.argv[1]
BASE_URL = "https://api.themoviedb.org/3"
LANG = "en-US"  # Primary language for metadata

# Scrapping Range
START_YEAR = 1985
END_YEAR   = 2025

# Limits per category/year
MOVIES_PER_YEAR = 500
SERIES_PER_YEAR = 500
ANIME_PER_YEAR  = 500

MAX_WORKERS = 20
DB_FILE = "Netrun.db"

# ==========================
# SQLITE INITIALIZATION
# ==========================
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tmdb_id INTEGER UNIQUE,
    type TEXT,
    title TEXT,
    original_title TEXT,
    year INTEGER,
    genres TEXT,
    duration INTEGER,
    rating_tmdb REAL,
    synopsis TEXT,
    mood_tags TEXT DEFAULT NULL, -- To be populated by AI enrichment script
    user_rating INTEGER DEFAULT 0,
    watched INTEGER DEFAULT 0,
    rewatchable INTEGER DEFAULT 0
)
""")
conn.commit()

# ==========================
# API UTILS
# ==========================
def get_json(url, params):
    params["api_key"] = API_KEY
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def fetch_details(item_id, item_type):
    endpoint = "tv" if item_type == "tv" else "movie"
    return get_json(f"{BASE_URL}/{endpoint}/{item_id}", {"language": LANG})

INSERT_SQL = """
INSERT OR IGNORE INTO media (
    tmdb_id, type, title, original_title, year,
    genres, duration, rating_tmdb, synopsis
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

# ==========================
# CORE EXTRACTION LOGIC
# ==========================
def process_year(year, item_type, limit):
    page = 1
    collected = 0

    with tqdm(total=limit, desc=f"{item_type.upper()} {year}") as bar:
        while collected < limit:
            params = {
                "language": LANG,
                "sort_by": "vote_average.desc",
                "vote_count.gte": 50,
                "page": page
            }

            if item_type == "tv":
                params["first_air_date_year"] = year
                url = f"{BASE_URL}/discover/tv"
            else:
                params["primary_release_year"] = year
                url = f"{BASE_URL}/discover/movie"
                if item_type == "anime":
                    params["with_genres"] = 16 # Animation genre id

            try:
                data = get_json(url, params)
            except: 
                break
            
            results = data.get("results", [])
            if not results: 
                break

            with ThreadPoolExecutor(MAX_WORKERS) as executor:
                futures = {executor.submit(fetch_details, r["id"], item_type): r for r in results}

                for future in as_completed(futures):
                    if collected >= limit: 
                        break
                    r = futures[future]
                    try:
                        d = future.result()
                        
                        title = r.get("title") or r.get("name") or ""
                        orig_title = r.get("original_title") or r.get("original_name") or ""
                        
                        date_str = (r.get("release_date") or r.get("first_air_date") or "")[:4]
                        year_val = int(date_str) if date_str.isdigit() else None

                        # Handling duration (minutes)
                        ep_times = d.get("episode_run_time") or []
                        duration = d.get("runtime") or (sum(ep_times)//len(ep_times) if ep_times else None)

                        genres = "|".join(g["name"] for g in d.get("genres", []))
                        synopsis = r.get("overview", "")
                        rating = r.get("vote_average", 0.0)

                        cur.execute(INSERT_SQL, (
                            r["id"], item_type, title, orig_title, year_val,
                            genres, duration, rating, synopsis
                        ))
                        conn.commit()
                        collected += 1
                        bar.update(1)
                    except:
                        continue
            page += 1

# ==========================
# MAIN EXECUTION
# ==========================
if __name__ == "__main__":
    print(f"--- Netrun Database Extractor ---")
    print(f"Targeting: {START_YEAR} to {END_YEAR}")
    
    for year in range(START_YEAR, END_YEAR + 1):
        process_year(year, "movie", MOVIES_PER_YEAR)
        process_year(year, "tv", SERIES_PER_YEAR)
        process_year(year, "anime", ANIME_PER_YEAR)

    conn.close()
    print("\n[SUCCESS] Extraction complete. Data is ready for AI tagging.")
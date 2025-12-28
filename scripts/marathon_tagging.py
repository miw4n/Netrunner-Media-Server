import sqlite3
import ollama
from tqdm import tqdm
import os
import sys
import signal

# --- CONFIGURATION ---
DB_PATH = "Netrun.db" 
MODEL_NAME = "qwen2.5:3b" # Modèle ultra-rapide 
LOG_FILE = "marathon_log.txt"

# Gestion du Ctrl+C
def signal_handler(sig, frame):
    print("\n\n[!] Interruption . Saving / Closing...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

import re

import re

def get_mood_tags(title, synopsis):
    prompt = f"""Task: Give 5 simple keywords in English for the following film.
Rule: Only words, separated by commas. No numbers, no sentences.
Example: Adventure, Future, Action, Romance, Comedy

Film: {title}
Synopsis: {synopsis}
Tags:"""

    try:
        response = ollama.generate(
            model=MODEL_NAME, 
            prompt=prompt, 
            options={"num_predict": 35, "temperature": 0.2}
        )
        
        raw_tags = response.get('response', '').strip()

        # 1. On supprime les chiffres suivis de points ou d'espaces (ex: "1. ", "1 ")
        clean_tags = re.sub(r'\d+[\s\.]*', '', raw_tags)
        
        # 2. On sépare par les virgules et on nettoie chaque mot
        tags_list = []
        for t in clean_tags.split(','):
            word = t.strip().lower()
            # On ne garde que si c'est un vrai mot (pas de ponctuation seule)
            word = re.sub(r'[^\w\s-]', '', word) 
            if len(word) > 1:
                tags_list.append(word.capitalize())

        # 3. On ne garde que les 5 premiers et on recrée la chaîne
        final_tags = ", ".join(tags_list[:5])
        
        return final_tags if len(tags_list) >= 2 else None
    except:
        return None
        

def run_marathon():
    if not os.path.exists(DB_PATH):
        print(f"ERREUR : {DB_PATH} not found."); return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Vérification des colonnes (pour être SÛR à 100%)
    cursor.execute("PRAGMA table_info(media)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'mood_tags' not in columns or 'tagdone' not in columns:
        print("⚠️ Colonnes manquantes détectées. Création...")
        if 'mood_tags' not in columns: cursor.execute("ALTER TABLE media ADD COLUMN mood_tags TEXT")
        if 'tagdone' not in columns: cursor.execute("ALTER TABLE media ADD COLUMN tagdone INTEGER DEFAULT 0")
        conn.commit()

    # Option Reset
    choix = input("Reset tags (tagdone = 0) ? (oui/non) : ").lower()
    if choix == 'oui':
        cursor.execute("UPDATE media SET tagdone = 0, mood_tags = NULL")
        conn.commit()
        if os.path.exists(LOG_FILE): os.remove(LOG_FILE)

    # Récupération des films
    cursor.execute("SELECT id, title, synopsis FROM media WHERE tagdone = 0 AND synopsis IS NOT NULL AND synopsis != ''")
    films = cursor.fetchall()
    
    if not films:
        print("✓ Aucun film à traiter."); return

    print(f"🚀 MARATHON CPU-SPEED ({MODEL_NAME}) - {len(films)} films.")
    
    pbar = tqdm(total=len(films), desc="Progression", unit="film")
    
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        try:
            for i, (film_id, title, synopsis) in enumerate(films):
                tags = get_mood_tags(title, synopsis)
                
                if tags:
                    # Sauvegarde SQL
                    cursor.execute("UPDATE media SET mood_tags = ?, tagdone = 1 WHERE id = ?", (tags, film_id))
                    
                    # Log et Affichage
                    ligne = f"ID: {film_id:<5} | {title[:25]:<25} | Tags: {tags}"
                    tqdm.write(ligne) # Affiche dans la fenêtre sans casser la barre
                    log.write(ligne + "\n")
                    log.flush()
                
                # Sauvegarde sur disque tous les 5 films
                if i % 5 == 0:
                    conn.commit()
                
                pbar.update(1)

        finally:
            conn.commit()
            conn.close()
            pbar.close()
            print(f"\n✅ Finish. Logs : {LOG_FILE}")

if __name__ == "__main__":
    run_marathon()
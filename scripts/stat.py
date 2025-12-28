import time
import os
from collections import Counter

LOG_FILE = "marathon_log.txt"

def show_stats():
    os.system("") 

    if not os.path.exists(LOG_FILE):
        print(f"En attente de {LOG_FILE}...")
        return

    while True:
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            all_tags = []
            num_films = 0
            for line in lines:
                if "Tags:" in line:
                    num_films += 1
                    tags_part = line.split("Tags:")[1].strip()
                    tags = [t.strip().strip('.').capitalize() for t in tags_part.split(",") if t.strip()]
                    all_tags.extend(tags)

            if num_films > 0:
                counts = Counter(all_tags)
                most_common = counts.most_common(20)
                
                os.system('cls')
                print("="*55)
                print(f"📊 MONITORING - {num_films} FILMS")
                print(f"Dernière MAJ : {time.strftime('%H:%M:%S')}")
                print("="*55)
                print(f"{'TAG':<18} | {'FREQ':>6} | {'% FILMS'}")
                print("-" * 55)
                
                for tag, count in most_common:
                    percentage = (count / num_films) * 100 
                    bar_size = int(min(percentage, 100) / 4)
                    bar = "█" * bar_size
                    print(f"{tag:<18} | {count:>6} | {percentage:>5.1f}% {bar}")
                
                print("-" * 55)
                
                # --- LE TIMER VISUEL ---
                for i in range(10, 0, -1):
                    # \r permet de réécrire sur la même ligne
                    print(f"  Next Update in {i}s...   ", end="\r")
                    time.sleep(1)
            else:
                print("Waiting...", end="\r")
                time.sleep(2)
            
        except Exception as e:
            print(f"\nErreur : {e}")
            time.sleep(5)

if __name__ == "__main__":
    show_stats()
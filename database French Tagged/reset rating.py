import sqlite3

conn = sqlite3.connect('Netrun.db')
cursor = conn.cursor()

# On remet tout à zéro
print("Nettoyage de la base de données...")
cursor.execute("UPDATE media SET user_rating = 0, watched = 0, rewatchable = 0")

conn.commit()
conn.close()
print("Terminé ! Tous les compteurs sont à zéro.")
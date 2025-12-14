import sqlite3

conn = sqlite3.connect('data/tvseries.db')
c = conn.cursor()

# Vérifier les séries en commun entre alice (41) et les autres
c.execute("""
SELECT r2.user_id, u2.username, COUNT(*) as common_series
FROM ratings r1
JOIN ratings r2 ON r1.serie_id = r2.serie_id
JOIN users u2 ON r2.user_id = u2.id
WHERE r1.user_id = 41 AND r2.user_id != 41
GROUP BY r2.user_id, u2.username
ORDER BY common_series DESC
""")

print("Séries en commun avec alice:")
for row in c.fetchall():
    print(f"  {row[1]} (ID {row[0]}): {row[2]} séries communes")

conn.close()

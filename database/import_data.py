"""
Script d'import des données JSON vers MySQL
"""
import mysql.connector
import json
import os
import joblib
from tqdm import tqdm

# Configuration MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # À modifier selon votre config
    'database': 'tvseries'
}

def connect_db():
    """Connexion à la base de données."""
    return mysql.connector.connect(**DB_CONFIG)

def import_series_and_keywords():
    """Importer les séries et leurs mots-clés depuis les fichiers."""
    print("📚 Import des séries et mots-clés...")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Charger les métadonnées
    meta = joblib.load('./data/index/meta.joblib')
    titles = meta['titles']
    
    # Charger les mots-clés
    keywords_dir = './data/keywords'
    
    for title in tqdm(titles, desc="Séries"):
        # Déterminer la langue
        language = 'vf' if title.lower().endswith('_vf') else 'vo'
        
        # Insérer la série
        cursor.execute(
            "INSERT IGNORE INTO series (title, language) VALUES (%s, %s)",
            (title, language)
        )
        serie_id = cursor.lastrowid
        
        # Si la série existait déjà, récupérer son ID
        if serie_id == 0:
            cursor.execute("SELECT id FROM series WHERE title = %s", (title,))
            serie_id = cursor.fetchone()[0]
        
        # Importer les mots-clés
        keywords_file = os.path.join(keywords_dir, f'{title}_keywords.json')
        if os.path.exists(keywords_file):
            with open(keywords_file, 'r', encoding='utf-8') as f:
                keywords_data = json.load(f)
            
            # Prendre les top 50 mots-clés pour ne pas surcharger la BD
            for kw, score in keywords_data[:50]:
                cursor.execute(
                    "INSERT INTO keywords (serie_id, keyword, score) VALUES (%s, %s, %s)",
                    (serie_id, kw, score)
                )
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ {len(titles)} séries importées avec leurs mots-clés")

def import_ratings():
    """Importer les notations depuis ratings.json."""
    print("\n⭐ Import des notations...")
    
    ratings_file = './data/ratings.json'
    if not os.path.exists(ratings_file):
        print("⚠️ Pas de fichier ratings.json trouvé")
        return
    
    with open(ratings_file, 'r', encoding='utf-8') as f:
        ratings_data = json.load(f)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Map username -> user_id
    cursor.execute("SELECT id, username FROM users")
    user_map = {username: uid for uid, username in cursor.fetchall()}
    
    # Map title -> serie_id
    cursor.execute("SELECT id, title FROM series")
    serie_map = {title: sid for sid, title in cursor.fetchall()}
    
    count = 0
    for username, user_ratings in ratings_data.items():
        if username not in user_map:
            # Créer l'utilisateur s'il n'existe pas
            cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
                (username, 'a' * 64, f'{username}@example.com')
            )
            user_map[username] = cursor.lastrowid
        
        user_id = user_map[username]
        
        for serie_title, rating in user_ratings.items():
            if serie_title in serie_map:
                serie_id = serie_map[serie_title]
                cursor.execute(
                    """INSERT INTO ratings (user_id, serie_id, rating) 
                       VALUES (%s, %s, %s)
                       ON DUPLICATE KEY UPDATE rating = %s""",
                    (user_id, serie_id, rating, rating)
                )
                count += 1
    
    conn.commit()
    
    # Mettre à jour les statistiques des séries
    print("\n📊 Calcul des statistiques...")
    cursor.execute("""
        UPDATE series s
        LEFT JOIN (
            SELECT 
                serie_id,
                AVG(rating) as avg_rating,
                COUNT(*) as num_ratings,
                AVG(rating) * LOG(1 + COUNT(*)) as popularity_score
            FROM ratings
            GROUP BY serie_id
        ) r ON s.id = r.serie_id
        SET 
            s.average_rating = COALESCE(r.avg_rating, 0),
            s.num_ratings = COALESCE(r.num_ratings, 0),
            s.popularity_score = COALESCE(r.popularity_score, 0)
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ {count} notations importées")

def verify_import():
    """Vérifier l'import."""
    print("\n🔍 Vérification de l'import...")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Compter les données
    cursor.execute("SELECT COUNT(*) FROM users")
    num_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM series")
    num_series = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM keywords")
    num_keywords = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ratings")
    num_ratings = cursor.fetchone()[0]
    
    print(f"\n📈 Statistiques de la base de données:")
    print(f"   👥 Utilisateurs: {num_users}")
    print(f"   📺 Séries: {num_series}")
    print(f"   🏷️  Mots-clés: {num_keywords}")
    print(f"   ⭐ Notations: {num_ratings}")
    
    # Afficher les séries les mieux notées
    print(f"\n🌟 Top 5 des séries (VF):")
    cursor.execute("""
        SELECT title, average_rating, num_ratings, popularity_score
        FROM series
        WHERE language = 'vf'
        ORDER BY popularity_score DESC
        LIMIT 5
    """)
    
    for i, (title, avg, num, pop) in enumerate(cursor.fetchall(), 1):
        print(f"   {i}. {title} - Note: {avg:.2f} ({num} votes) - Pop: {pop:.2f}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("Import des données dans MySQL")
    print("=" * 60)
    
    try:
        import_series_and_keywords()
        import_ratings()
        verify_import()
        print("\n✅ Import terminé avec succès!")
    except mysql.connector.Error as e:
        print(f"\n❌ Erreur MySQL: {e}")
        print("\n💡 Vérifiez que:")
        print("   - MySQL est installé et démarré")
        print("   - Le fichier schema.sql a été exécuté")
        print("   - Les identifiants dans DB_CONFIG sont corrects")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

"""
Script pour mettre à jour uniquement les utilisateurs et ratings
"""
import json
import hashlib
from database.db_sqlite import get_connection

def hash_password(password):
    """Hasher un mot de passe avec SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def update_users_and_ratings():
    """Mettre à jour les utilisateurs et leurs ratings depuis example_ratings.json"""
    
    with open('example_ratings.json', 'r', encoding='utf-8') as f:
        ratings_data = json.load(f)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # D'abord, supprimer les anciennes données
        print("🗑️  Suppression des anciennes données...")
        cursor.execute("DELETE FROM ratings")
        cursor.execute("DELETE FROM users")
        print("✅ Anciennes données supprimées")
        print()
        
        # Créer les utilisateurs
        print("👥 Création des utilisateurs...")
        users_created = 0
        
        for username in ratings_data.keys():
            # Mot de passe = username + "123"
            password = f"{username}123"
            password_hash = hash_password(password)
            
            # Déterminer la langue préférée basée sur les ratings
            user_ratings = ratings_data[username]
            vf_count = sum(1 for title in user_ratings.keys() if title.endswith('_vf'))
            vo_count = sum(1 for title in user_ratings.keys() if title.endswith('_vo'))
            preferred_language = 'vf' if vf_count > vo_count else 'vo'
            
            cursor.execute(
                "INSERT INTO users (username, password_hash, language_preference) VALUES (?, ?, ?)",
                (username, password_hash, preferred_language)
            )
            users_created += 1
            print(f"  ✅ {username} (mot de passe: {password}, préférence: {preferred_language.upper()})")
        
        print(f"✅ {users_created} utilisateurs créés")
        print()
        
        # Créer les ratings
        print("⭐ Création des ratings...")
        ratings_created = 0
        ratings_skipped = 0
        
        for username, user_ratings in ratings_data.items():
            # Récupérer l'ID de l'utilisateur
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_row = cursor.fetchone()
            
            if not user_row:
                print(f"⚠️  Utilisateur {username} non trouvé")
                continue
            
            user_id = user_row[0]
            
            for series_title, rating in user_ratings.items():
                # Trouver l'ID de la série
                cursor.execute("SELECT id FROM series WHERE title = ?", (series_title,))
                series_row = cursor.fetchone()
                
                if not series_row:
                    ratings_skipped += 1
                    continue
                
                serie_id = series_row[0]
                
                # Insérer le rating
                cursor.execute(
                    "INSERT INTO ratings (user_id, serie_id, rating) VALUES (?, ?, ?)",
                    (user_id, serie_id, rating)
                )
                ratings_created += 1
        
        print(f"✅ {ratings_created} ratings créés")
        if ratings_skipped > 0:
            print(f"⚠️  {ratings_skipped} ratings ignorés (séries non trouvées)")
        print()
        
        # Statistiques
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ratings")
        total_ratings = cursor.fetchone()[0]
        
        print("=" * 60)
        print("📊 STATISTIQUES FINALES")
        print("=" * 60)
        print(f"👥 Utilisateurs : {total_users}")
        print(f"⭐ Ratings      : {total_ratings}")
        print()
        print("✅ Mise à jour terminée !")

if __name__ == '__main__':
    update_users_and_ratings()

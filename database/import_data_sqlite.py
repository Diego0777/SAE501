"""
Script d'import des données dans la base de données SQLite
"""
import os
import json
import hashlib
from datetime import datetime
from db_sqlite import init_db, get_connection, get_db_stats

def hash_password(password):
    """Hasher un mot de passe avec SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def import_series():
    """Importer toutes les séries depuis les fichiers cleaned."""
    print("📺 Import des séries...")
    
    cleaned_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cleaned')
    
    if not os.path.exists(cleaned_dir):
        print("❌ Répertoire cleaned/ introuvable")
        return 0
    
    series_data = []
    
    for filename in os.listdir(cleaned_dir):
        if filename.endswith('.txt'):
            # Extraire le nom de la série
            parts = filename.replace('.txt', '').split('_')
            
            if len(parts) == 2:
                series_name = parts[0]
                language = parts[1].lower()  # vf ou vo
                
                # Format: seriesname_vf ou seriesname_vo
                title = f"{series_name}_{language}"
                series_data.append((title, language))
    
    # Insérer dans la base de données
    with get_connection() as conn:
        cursor = conn.cursor()
        
        inserted = 0
        for title, language in series_data:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO series (title, language) VALUES (?, ?)",
                    (title, language)
                )
                if cursor.rowcount > 0:
                    inserted += 1
            except Exception as e:
                print(f"❌ Erreur import {title}: {e}")
    
    print(f"✅ {inserted} séries importées")
    return inserted

def import_keywords():
    """Importer les mots-clés depuis les fichiers JSON."""
    print("🔑 Import des mots-clés...")
    
    keywords_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'keywords')
    
    if not os.path.exists(keywords_dir):
        print("❌ Répertoire keywords/ introuvable")
        return 0
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        inserted = 0
        
        for filename in os.listdir(keywords_dir):
            if filename.endswith('.json'):
                # Format: lost_vf_keywords.json → lost_vf
                title = filename.replace('_keywords.json', '')
                
                # Trouver l'ID de la série
                cursor.execute(
                    "SELECT id FROM series WHERE title = ?",
                    (title,)
                )
                row = cursor.fetchone()
                
                if not row:
                    print(f"⚠️ Série {title} non trouvée")
                    continue
                
                serie_id = row[0]
                
                # Lire les mots-clés
                filepath = os.path.join(keywords_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        keywords_list = json.load(f)
                    
                    # Insérer les mots-clés (max 200)
                    for kw_data in keywords_list[:200]:
                        keyword = kw_data.get('keyword', '')
                        score = kw_data.get('score', 0.0)
                        
                        cursor.execute(
                            "INSERT INTO keywords (serie_id, keyword, score) VALUES (?, ?, ?)",
                            (serie_id, keyword, score)
                        )
                        inserted += 1
                
                except Exception as e:
                    print(f"❌ Erreur lecture {filename}: {e}")
        
        print(f"✅ {inserted} mots-clés importés")
        return inserted

def import_ratings():
    """Importer les notes depuis ratings.json."""
    print("⭐ Import des notes...")
    
    ratings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'ratings.json')
    
    if not os.path.exists(ratings_file):
        print("❌ Fichier ratings.json introuvable")
        return 0
    
    with open(ratings_file, 'r', encoding='utf-8') as f:
        ratings_data = json.load(f)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        inserted = 0
        
        # ratings.json format: {"alice": {"lost_vf": 5, ...}, ...}
        for username, user_ratings in ratings_data.items():
            # Trouver ou créer l'utilisateur
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            
            if not row:
                print(f"⚠️ Utilisateur {username} non trouvé (ignoré)")
                continue
            
            user_id = row[0]
            
            for series_title, rating in user_ratings.items():
                # Trouver l'ID de la série
                cursor.execute(
                    "SELECT id FROM series WHERE title = ?",
                    (series_title,)
                )
                row = cursor.fetchone()
                
                if row:
                    serie_id = row[0]
                    
                    try:
                        cursor.execute(
                            """INSERT OR REPLACE INTO ratings 
                               (user_id, serie_id, rating, created_at) 
                               VALUES (?, ?, ?, datetime('now'))""",
                            (user_id, serie_id, rating)
                        )
                        inserted += 1
                    except Exception as e:
                        print(f"❌ Erreur import note user {username}, série {series_title}: {e}")
                else:
                    print(f"⚠️ Série {series_title} non trouvée")
        
        print(f"✅ {inserted} notes importées")
        return inserted

def main():
    """Fonction principale d'import."""
    print("=" * 60)
    print("🚀 IMPORT DES DONNÉES DANS LA BASE DE DONNÉES SQLITE")
    print("=" * 60)
    print()
    
    # Initialiser la base de données
    print("📋 Initialisation de la base de données...")
    try:
        init_db()
        print("✅ Base de données initialisée")
        print()
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        return
    
    # Import des données
    total_series = import_series()
    print()
    
    total_keywords = import_keywords()
    print()
    
    total_ratings = import_ratings()
    print()
    
    # Statistiques finales
    print("=" * 60)
    print("📊 STATISTIQUES DE LA BASE DE DONNÉES")
    print("=" * 60)
    
    stats = get_db_stats()
    
    print(f"👥 Utilisateurs : {stats['users']}")
    print(f"📺 Séries      : {stats['series']}")
    print(f"🔑 Mots-clés   : {stats['keywords']}")
    print(f"⭐ Notes       : {stats['ratings']}")
    print(f"🔐 Sessions    : {stats['sessions']}")
    print()
    
    print("✅ Import terminé avec succès!")

if __name__ == '__main__':
    main()

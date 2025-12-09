"""
Script pour télécharger toutes les images de posters localement
"""
import requests
import sqlite3
import os
from pathlib import Path
from database.db_sqlite import get_connection
import time

# Créer le dossier pour les posters
POSTERS_DIR = Path("web/posters")
POSTERS_DIR.mkdir(parents=True, exist_ok=True)

def download_poster(url, filename):
    """Télécharger une image de poster."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        filepath = POSTERS_DIR / filename
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return f"posters/{filename}"
    except Exception as e:
        print(f"   ❌ Erreur téléchargement: {e}")
        return None

def download_all_posters():
    """Télécharger tous les posters et mettre à jour la BD."""
    print("📥 Téléchargement des posters localement...")
    print("=" * 60)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Récupérer toutes les séries avec leur poster_url
        cursor.execute(
            "SELECT id, title, poster_url FROM series WHERE poster_url IS NOT NULL"
        )
        series = cursor.fetchall()
    
    print(f"📊 {len(series)} séries à traiter\n")
    
    downloaded = 0
    failed = 0
    
    for serie_id, title, poster_url in series:
        # Extraire l'extension de l'URL
        ext = poster_url.split('.')[-1].split('?')[0]
        if ext not in ['jpg', 'jpeg', 'png', 'webp']:
            ext = 'jpg'
        
        filename = f"{title}.{ext}"
        
        print(f"📥 {title:<35} → {filename}")
        
        # Télécharger l'image
        local_path = download_poster(poster_url, filename)
        
        if local_path:
            # Mettre à jour la BD avec le chemin local
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE series SET poster_url = ? WHERE id = ?",
                    (local_path, serie_id)
                )
            
            print(f"   ✅ Sauvegardé: {local_path}")
            downloaded += 1
        else:
            failed += 1
        
        # Pause pour ne pas surcharger le serveur
        time.sleep(0.1)
    
    print("\n" + "=" * 60)
    print(f"✅ Téléchargement terminé !")
    print(f"   Réussis: {downloaded}")
    print(f"   Échoués: {failed}")
    print(f"   Total: {len(series)}")
    print(f"\n📁 Images stockées dans: {POSTERS_DIR.absolute()}")

if __name__ == '__main__':
    download_all_posters()

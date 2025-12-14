"""
Script pour optimiser les posters : 
- Garder une seule image par série (supprimer les doublons VF/VO)
- Stocker les images en BLOB dans la base de données
"""
import sqlite3
from pathlib import Path
from database.db_sqlite import get_connection

POSTERS_DIR = Path("web/posters")

def optimize_posters():
    """Optimiser le stockage des posters."""
    print("🔧 Optimisation des posters...")
    print("=" * 60)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Ajouter la colonne poster_data si elle n'existe pas
        try:
            cursor.execute("ALTER TABLE series ADD COLUMN poster_data BLOB")
            print("✅ Colonne poster_data ajoutée")
        except:
            print("ℹ️  Colonne poster_data existe déjà")
        
        # Récupérer toutes les séries
        cursor.execute("SELECT id, title, poster_url FROM series WHERE poster_url IS NOT NULL")
        series = cursor.fetchall()
    
    print(f"📊 {len(series)} séries à traiter\n")
    
    # Grouper par nom de base (sans _vf/_vo)
    series_groups = {}
    for serie_id, title, poster_url in series:
        base_name = title.replace('_vf', '').replace('_vo', '')
        if base_name not in series_groups:
            series_groups[base_name] = []
        series_groups[base_name].append((serie_id, title, poster_url))
    
    processed = 0
    
    for base_name, group in series_groups.items():
        # Utiliser le premier poster du groupe
        first_serie = group[0]
        poster_path = POSTERS_DIR / f"{first_serie[1]}.jpg"
        
        # Vérifier si le fichier existe
        if not poster_path.exists():
            # Essayer avec d'autres extensions
            for ext in ['jpg', 'jpeg', 'png', 'webp']:
                alt_path = POSTERS_DIR / f"{first_serie[1]}.{ext}"
                if alt_path.exists():
                    poster_path = alt_path
                    break
        
        if poster_path.exists():
            # Lire l'image
            with open(poster_path, 'rb') as f:
                poster_data = f.read()
            
            # Mettre à jour toutes les séries du groupe avec la même image
            with get_connection() as conn:
                cursor = conn.cursor()
                for serie_id, title, _ in group:
                    cursor.execute(
                        "UPDATE series SET poster_data = ?, poster_url = ? WHERE id = ?",
                        (poster_data, f"blob:{base_name}", serie_id)
                    )
            
            print(f"✅ {base_name:<30} → {len(poster_data):>8} bytes ({len(group)} séries)")
            processed += 1
            
            # Supprimer les fichiers dupliqués (garder le premier)
            for i, (_, title, _) in enumerate(group):
                if i > 0:  # Ne pas supprimer le premier
                    for ext in ['jpg', 'jpeg', 'png', 'webp']:
                        dup_path = POSTERS_DIR / f"{title}.{ext}"
                        if dup_path.exists():
                            dup_path.unlink()
                            print(f"   🗑️  Supprimé: {title}.{ext}")
        else:
            print(f"⚠️  {base_name:<30} → Fichier non trouvé")
    
    print("\n" + "=" * 60)
    print(f"✅ Optimisation terminée !")
    print(f"   Séries traitées: {processed}")
    print(f"   Groupes: {len(series_groups)}")

if __name__ == '__main__':
    optimize_posters()

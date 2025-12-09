"""
Script pour basculer automatiquement de JSON vers MySQL
"""
import os

serve_api_file = './serve_api.py'

# Lire le fichier actuel
with open(serve_api_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacer les imports
replacements = [
    ('from api_users import users_bp', 'from api_users_mysql import users_bp'),
    ('from api_ratings import ratings_bp, init_ratings_data', 'from api_ratings_mysql import ratings_bp, init_ratings_data'),
    ('from api_series import series_bp, init_series_data', 'from api_series_mysql import series_bp, init_series_data'),
    ('from api_recommend import recommend_bp', 'from api_recommend_mysql import recommend_bp'),
]

for old, new in replacements:
    content = content.replace(old, new)

# Ajouter l'import de la DB au début
if 'from database.db import test_connection' not in content:
    # Trouver la ligne après les imports Flask
    lines = content.split('\n')
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.startswith('from flask'):
            insert_pos = i + 1
        elif insert_pos > 0 and line.startswith('import'):
            insert_pos = i + 1
        elif insert_pos > 0 and not line.startswith(('from', 'import', '#', '')):
            break
    
    lines.insert(insert_pos, 'from database.db import test_connection, init_pool')
    content = '\n'.join(lines)

# Sauvegarder
with open(serve_api_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ serve_api.py mis à jour pour utiliser MySQL")
print("\nModifications effectuées :")
for old, new in replacements:
    print(f"  - {old.split()[1]} → {new.split()[1]}")

print("\n📝 Prochaines étapes :")
print("  1. Installer MySQL : mysql --version")
print("  2. Créer la base : mysql -u root -p < database/schema.sql")
print("  3. Installer le driver : pip install mysql-connector-python")
print("  4. Configurer DB_PASSWORD dans database/db.py")
print("  5. Importer les données : python database/import_data.py")
print("  6. Redémarrer le serveur : python serve_api.py")

# Configuration MySQL pour TV Series

## Installation de MySQL

### Windows
1. Télécharger MySQL depuis https://dev.mysql.com/downloads/installer/
2. Installer MySQL Server (version 8.0 ou supérieure)
3. Configurer le mot de passe root pendant l'installation

### Vérifier l'installation
```bash
mysql --version
```

## Configuration de la base de données

### 1. Créer la base de données
```bash
# Se connecter à MySQL
mysql -u root -p

# Ou via PowerShell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
```

### 2. Exécuter le script de création
```sql
SOURCE C:/Users/Diego/Desktop/COURS/SAE501/database/schema.sql;
```

Ou directement :
```bash
mysql -u root -p < database/schema.sql
```

### 3. Installer le connecteur Python
```bash
pip install mysql-connector-python
```

### 4. Configurer les identifiants

Créer un fichier `.env` à la racine du projet :
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_NAME=tvseries
```

Ou modifier directement dans `database/db.py` :
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'VOTRE_MOT_DE_PASSE',  # ← Modifier ici
    'database': 'tvseries'
}
```

### 5. Importer les données
```bash
python database/import_data.py
```

Cela va :
- Importer les 250 séries
- Importer les mots-clés (top 50 par série)
- Importer les notations utilisateurs
- Calculer les statistiques

## Structure de la base

### Tables
- `users` - Utilisateurs (6 de base + nouveaux)
- `series` - 250 séries (VF/VO)
- `keywords` - ~12,500 mots-clés (50 par série)
- `ratings` - Notations utilisateurs
- `sessions` - Sessions d'authentification

### Vue
- `series_stats` - Statistiques en temps réel

## Basculer vers MySQL

### Mode JSON (actuel)
```python
# serve_api.py utilise :
from api_users import users_bp
from api_ratings import ratings_bp
from api_series import series_bp
from api_recommend import recommend_bp
```

### Mode MySQL (nouveau)
```python
# serve_api.py doit utiliser :
from api_users_mysql import users_bp
from api_ratings_mysql import ratings_bp
from api_series_mysql import series_bp
from api_recommend_mysql import recommend_bp
```

Un script `switch_to_mysql.py` est fourni pour faire la bascule automatiquement.

## Vérification

```bash
# Tester la connexion
python -c "from database.db import test_connection; print(test_connection())"

# Vérifier les données
mysql -u root -p tvseries -e "SELECT COUNT(*) FROM series; SELECT COUNT(*) FROM keywords; SELECT COUNT(*) FROM ratings;"
```

## Avantages de MySQL

✅ **Performance** - Pool de connexions, index optimisés
✅ **Scalabilité** - Gère facilement 100k+ séries
✅ **Intégrité** - Contraintes de clés étrangères
✅ **Requêtes complexes** - JOINs, agrégations, vues
✅ **Concurrent** - Plusieurs utilisateurs simultanés
✅ **Backup** - Facilement sauvegardable

## Requêtes utiles

```sql
-- Top 10 séries par popularité
SELECT title, average_rating, num_ratings, popularity_score 
FROM series 
WHERE language = 'vf' 
ORDER BY popularity_score DESC 
LIMIT 10;

-- Mots-clés d'une série
SELECT keyword, score 
FROM keywords k
JOIN series s ON k.serie_id = s.id
WHERE s.title = 'lost_vf'
ORDER BY score DESC
LIMIT 20;

-- Notations d'un utilisateur
SELECT u.username, s.title, r.rating
FROM ratings r
JOIN users u ON r.user_id = u.id
JOIN series s ON r.serie_id = s.id
WHERE u.username = 'alice'
ORDER BY r.rating DESC;

-- Utilisateurs actifs
SELECT u.username, COUNT(r.id) as num_ratings
FROM users u
LEFT JOIN ratings r ON u.id = r.user_id
GROUP BY u.id, u.username
ORDER BY num_ratings DESC;
```

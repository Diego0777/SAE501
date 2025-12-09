# Base de données SQLite - Documentation

## 📊 Vue d'ensemble

Le projet utilise maintenant **SQLite** comme base de données, un système de gestion de base de données relationnel léger, intégré à Python, ne nécessitant aucune installation.

### Avantages de SQLite

- ✅ **Aucune installation requise** - Intégré à Python 3.x
- ✅ **Base de données fichier unique** - `data/tvseries.db`
- ✅ **Portable** - Fichier facilement déplaçable/sauvegardable
- ✅ **Performant** - Parfait pour 250 séries + 50k mots-clés
- ✅ **SQL standard** - Requêtes SQL classiques
- ✅ **Transactions ACID** - Intégrité des données garantie

## 🗂️ Structure de la base de données

### Tables

#### `users` - Utilisateurs
- `id` : Identifiant unique (auto-incrémenté)
- `username` : Nom d'utilisateur (unique)
- `password_hash` : Mot de passe hashé (SHA256)
- `email` : Adresse email
- `language_preference` : Préférence VF/VO
- `created_at` : Date de création

#### `series` - Séries TV
- `id` : Identifiant unique
- `title` : Titre complet (ex: `lost_vf`, `lost_vo`)
- `language` : Langue (`vf` ou `vo`)
- `average_rating` : Note moyenne
- `num_ratings` : Nombre de notes
- `popularity_score` : Score de popularité

#### `keywords` - Mots-clés
- `id` : Identifiant unique
- `serie_id` : Référence à la série
- `keyword` : Mot-clé extrait
- `score` : Score TF-IDF du mot-clé

#### `ratings` - Notes des utilisateurs
- `id` : Identifiant unique
- `user_id` : Référence à l'utilisateur
- `serie_id` : Référence à la série
- `rating` : Note (1-5)
- `created_at` : Date de création
- `updated_at` : Date de modification

#### `sessions` - Sessions utilisateur
- `id` : Identifiant unique
- `user_id` : Référence à l'utilisateur
- `token` : Token de session
- `created_at` : Date de création
- `expires_at` : Date d'expiration (7 jours)

### Vue

#### `series_stats` - Statistiques des séries
Vue calculée automatiquement :
- Agrège les notes moyennes
- Compte le nombre de notes
- Calcule le score de popularité

## 🚀 Utilisation

### 1. Initialiser la base de données

```powershell
python database/import_data_sqlite.py
```

**Résultat attendu :**
```
✅ 6 utilisateurs
✅ 250 séries
✅ 50 000 mots-clés
✅ 37 notes
```

### 2. Lancer le serveur API SQLite

```powershell
python serve_api_sqlite.py
```

Le serveur démarre sur `http://127.0.0.1:5000`

### 3. Tester les endpoints

#### Recherche
```bash
GET http://127.0.0.1:5000/api/search?q=crash+avion+ile&limit=5
```

#### Détails d'une série
```bash
GET http://127.0.0.1:5000/api/series/lost_vf
```

#### Statistiques
```bash
GET http://127.0.0.1:5000/api/series/stats
```

#### Recommandations populaires
```bash
GET http://127.0.0.1:5000/api/recommend/popularity?limit=10
```

## 📁 Fichiers du projet

```
database/
├── schema_sqlite.sql       # Schéma de la base
├── db_sqlite.py           # Module de connexion
└── import_data_sqlite.py  # Script d'import

api_*_sqlite.py            # Modules API SQLite
serve_api_sqlite.py        # Serveur Flask SQLite

data/
└── tvseries.db            # Base de données SQLite
```

## 🔧 Module de connexion

Le module `database/db_sqlite.py` fournit :

### Fonctions principales

```python
from database.db_sqlite import get_connection, execute_query, init_db

# Context manager
with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM series WHERE title = ?", ("lost_vf",))
    result = cursor.fetchone()

# Requête simplifiée
result = execute_query(
    "SELECT * FROM series WHERE title = ?",
    ("lost_vf",),
    fetchone=True
)

# Initialiser la BD
init_db()
```

## 📊 Données importées

### Utilisateurs de test (mot de passe: `password123`)
- alice (VF)
- bob (VF)
- charlie (VO)
- diana (VF)
- eve (VO)
- frank (VF)

### Séries
- 250 séries (126 VF, 124 VO)
- 128 titres différents

### Mots-clés
- 50 000 mots-clés au total
- 200 mots-clés par série
- Scores TF-IDF normalisés

### Notes
- 37 notes d'utilisateurs réels
- Importées depuis `data/ratings.json`
- Note moyenne : 4.41/5

## 🔍 Requêtes SQL utiles

### Séries les mieux notées
```sql
SELECT title, average_rating, num_ratings
FROM series_stats
WHERE num_ratings >= 3
ORDER BY average_rating DESC
LIMIT 10;
```

### Mots-clés d'une série
```sql
SELECT keyword, score
FROM keywords k
JOIN series s ON k.serie_id = s.id
WHERE s.title = 'lost_vf'
ORDER BY score DESC
LIMIT 20;
```

### Notes d'un utilisateur
```sql
SELECT s.title, r.rating, r.created_at
FROM ratings r
JOIN series s ON r.serie_id = s.id
JOIN users u ON r.user_id = u.id
WHERE u.username = 'alice'
ORDER BY r.created_at DESC;
```

### Utilisateurs ayant noté une série
```sql
SELECT u.username, r.rating
FROM ratings r
JOIN users u ON r.user_id = u.id
JOIN series s ON r.serie_id = s.id
WHERE s.title = 'lost_vf';
```

## 🛠️ Maintenance

### Sauvegarder la base de données
```powershell
Copy-Item data/tvseries.db data/tvseries_backup.db
```

### Réinitialiser la base
```powershell
Remove-Item data/tvseries.db
python database/import_data_sqlite.py
```

### Vérifier l'intégrité
```python
from database.db_sqlite import test_connection, get_db_stats

# Test de connexion
success, message = test_connection()
print(message)  # "SQLite 3.50.4"

# Statistiques
stats = get_db_stats()
print(stats)  # {'users': 6, 'series': 250, ...}
```

## 🔄 Migration depuis les fichiers JSON

Les anciennes API utilisant `data/ratings.json` sont **toujours fonctionnelles** via `serve_api.py`.

Pour utiliser la version SQLite :
```powershell
# Ancienne version (JSON)
python serve_api.py

# Nouvelle version (SQLite)
python serve_api_sqlite.py
```

## 📈 Performance

### Temps de chargement
- Initialisation BD : ~2 secondes
- Import complet : ~5 secondes
- Recherche TF-IDF : <100ms
- Détails série : <50ms

### Capacité
- ✅ 250 séries actuellement
- ✅ Scalable jusqu'à 10 000+ séries
- ✅ 50k mots-clés (200 par série)
- ✅ Support illimité d'utilisateurs et notes

## ⚙️ Configuration avancée

### Activer le mode WAL (Write-Ahead Logging)
Améliore les performances en lecture/écriture simultanées :

```python
import sqlite3
conn = sqlite3.connect('data/tvseries.db')
conn.execute('PRAGMA journal_mode=WAL')
```

### Optimiser les performances
```sql
-- Analyser les requêtes
EXPLAIN QUERY PLAN SELECT * FROM series_stats WHERE language = 'vf';

-- Reconstruire les index
REINDEX;

-- Nettoyer l'espace
VACUUM;
```

## 🎯 Cas d'utilisation

### Recherche "crash avion ile"
```python
import requests
r = requests.get('http://127.0.0.1:5000/api/search?q=crash+avion+ile&limit=3')
results = r.json()['results']
print(results[0]['title'])  # "lost_vf" ✅
```

### Recommandations pour un utilisateur
```python
r = requests.get('http://127.0.0.1:5000/api/recommend/hybrid/1')
recs = r.json()['recommendations']
for rec in recs[:5]:
    print(f"{rec['title']} - Note: {rec['average_rating']}")
```

### Ajouter une note
```python
import requests
requests.post('http://127.0.0.1:5000/api/ratings', json={
    'user_id': 1,
    'series_title': 'lost_vf',
    'rating': 5
})
```

## 📚 Ressources

- [Documentation SQLite](https://www.sqlite.org/docs.html)
- [Python sqlite3 module](https://docs.python.org/3/library/sqlite3.html)
- [SQL Tutorial](https://www.w3schools.com/sql/)

---

**Version** : 2.0 (SQLite)  
**Date** : Décembre 2024  
**Projet** : SAE501 - Recherche et recommandation de séries TV

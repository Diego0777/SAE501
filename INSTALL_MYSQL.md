# 🗄️ Installation MySQL pour TV Series

## Guide rapide d'installation

### Étape 1 : Installer MySQL
```powershell
# Télécharger depuis https://dev.mysql.com/downloads/installer/
# Ou avec Chocolatey :
choco install mysql

# Vérifier l'installation
mysql --version
```

### Étape 2 : Installer le driver Python
```powershell
pip install mysql-connector-python
```

### Étape 3 : Créer la base de données
```powershell
# Option A : Depuis PowerShell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p

# Option B : Depuis MySQL Workbench (GUI)
# Ouvrir MySQL Workbench → Ouvrir schema.sql → Exécuter

# Option C : En ligne de commande
mysql -u root -p < database/schema.sql
```

### Étape 4 : Configurer le mot de passe
Modifier `database/db.py` ligne 9 :
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'VOTRE_MOT_DE_PASSE_ICI',  # ← Modifier ici
    'database': 'tvseries'
}
```

### Étape 5 : Tester la connexion
```powershell
python database/test_mysql.py
```

Si ça fonctionne, vous verrez :
```
✅ TOUS LES TESTS RÉUSSIS
```

### Étape 6 : Importer les données
```powershell
python database/import_data.py
```

Cela prend environ 2-3 minutes et importe :
- 250 séries (VF + VO)
- ~12 500 mots-clés
- Toutes les notations

### Étape 7 : Basculer les APIs vers MySQL
```powershell
python database/switch_to_mysql.py
```

### Étape 8 : Redémarrer le serveur
```powershell
# Arrêter le serveur actuel (Ctrl+C)
# Relancer
python serve_api.py
```

## Vérification finale

Tester l'API :
```powershell
python test_api.py
```

Résultat attendu :
```
=== Test recherche: crash avion ile ===
1. lost_vf - Score: 159.31

✅ Toutes les APIs fonctionnent correctement !
```

## Troubleshooting

### ❌ "Can't connect to MySQL server"
- Vérifier que MySQL est démarré :
  ```powershell
  net start MySQL80
  ```

### ❌ "Access denied for user 'root'"
- Vérifier le mot de passe dans `database/db.py`
- Réinitialiser le mot de passe MySQL si nécessaire

### ❌ "Unknown database 'tvseries'"
- Exécuter le script de création :
  ```powershell
  mysql -u root -p < database/schema.sql
  ```

### ❌ "No module named 'mysql.connector'"
- Installer le driver :
  ```powershell
  pip install mysql-connector-python
  ```

## Commandes MySQL utiles

```sql
-- Se connecter
mysql -u root -p

-- Voir les bases
SHOW DATABASES;

-- Utiliser la base
USE tvseries;

-- Voir les tables
SHOW TABLES;

-- Compter les séries
SELECT COUNT(*) FROM series;

-- Top 10 séries
SELECT title, average_rating, num_ratings 
FROM series 
ORDER BY popularity_score DESC 
LIMIT 10;

-- Chercher une série
SELECT * FROM series WHERE title LIKE '%lost%';
```

## Avantages de MySQL

| Aspect | JSON | MySQL |
|--------|------|-------|
| **Performance** | Lent avec beaucoup de données | Rapide avec index |
| **Recherche** | Scan complet | Index optimisés |
| **Concurrent** | Problèmes de verrouillage | Multi-utilisateurs |
| **Intégrité** | Aucune | Contraintes FK |
| **Backup** | Copier les fichiers | Dump SQL |
| **Requêtes complexes** | Difficile | JOINs, agrégations |

## Structure complète

```
tvseries/
├── users (6+ utilisateurs)
├── series (250 séries)
├── keywords (~12 500 mots-clés)
├── ratings (toutes les notations)
└── sessions (tokens d'auth)
```

## Support

En cas de problème :
1. Vérifier `database/test_mysql.py`
2. Consulter `database/README.md`
3. Vérifier les logs MySQL

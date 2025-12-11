# 📺 SAE501 - TV Series Recommendation System

Système de recommandation de séries TV avec recherche intelligente TF-IDF, base de données SQLite et interface web moderne.

## 🎯 Fonctionnalités

- **Recherche intelligente** : TF-IDF sur les sous-titres (50k+ mots-clés)
- **Recommandations** : Collaboratives, par popularité et hybrides
- **Base de données** : SQLite avec 250 séries, utilisateurs et notations
- **Interface moderne** : Design responsive avec posters et filtres VF/VO
- **Authentification** : Système de comptes utilisateurs avec sessions
- **Notation** : Système d'étoiles pour noter les séries

## 📊 Données

- **250 séries TV** (VF et VO)
- **50 000+ mots-clés** extraits des sous-titres
- **6 utilisateurs de test** + possibilité de créer des comptes
- **42 notations** utilisateurs
- **Posters** : Images stockées en BLOB dans la BD (250 posters)

---

## 🚀 Installation et Démarrage (Guide Complet)

### ⚙️ Prérequis

- **Python 3.8+** (testé avec Python 3.13)
- **pip** (gestionnaire de paquets Python)
- **Git** (pour cloner le projet)

---

## 🎯 GUIDE RAPIDE (Si vous avez cloné depuis Git)

**Votre ami a déjà cloné le projet Git ? Suivez ces 4 étapes uniquement :**

### 📥 ÉTAPE 1 : Ouvrir le projet

```powershell
cd SAE501
```

---

### 🐍 ÉTAPE 2 : Créer et activer l'environnement virtuel

```powershell
# Créer le venv
python -m venv venv

# Activer le venv
.\venv\Scripts\Activate.ps1
```

**✅ Vérification :** Le prompt doit afficher `(venv)` devant

---

### 📦 ÉTAPE 3 : Installer les dépendances

```powershell
pip install -r requirements.txt
```

**Packages installés :**
- Flask, scikit-learn, joblib, requests

---

### 💾 ÉTAPE 4 : Créer la base de données

```powershell
python database/import_data_sqlite.py
```

**✅ Ce script va :**
1. Créer `data/tvseries.db` (SQLite)
2. Importer 250 séries depuis `data/keywords/`
3. Créer 6 utilisateurs de test
4. Importer les notations
5. Télécharger 250 posters depuis TVmaze API
6. Stocker les posters en BLOB dans la BD

**⏱️ Durée :** ~2-3 minutes

**📊 Vérification :**
```powershell
python -c "import sqlite3; conn = sqlite3.connect('data/tvseries.db'); print('Séries:', conn.execute('SELECT COUNT(*) FROM series').fetchone()[0]); conn.close()"
```

**Résultat attendu :** `Séries: 250`

---

### 🚀 ÉTAPE 5 : Lancer le serveur

```powershell
python serve_api_sqlite.py
```

**✅ Sortie attendue :**
```
============================================================
🚀 Serveur API TV Series - Version SQLite
============================================================
📊 Base de données : SQLite (data/tvseries.db)
🌐 URL : http://127.0.0.1:5000
============================================================

 * Running on http://127.0.0.1:5000
```

---

### 🌐 ÉTAPE 6 : Ouvrir le site

Ouvrir dans un navigateur : **http://127.0.0.1:5000**

**✅ Vous devez voir :**
- La page d'accueil avec hero section
- Les séries populaires avec posters
- Le bouton VF/VO dans la navbar

---

## 📝 RÉSUMÉ COMMANDES (Pour votre ami)

```powershell
# 1. Aller dans le dossier
cd SAE501

# 2. Créer et activer venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Créer la base de données
python database/import_data_sqlite.py

# 5. Lancer le serveur
python serve_api_sqlite.py

# 6. Ouvrir http://127.0.0.1:5000
```

---

## 🔍 GUIDE COMPLET (Si installation from scratch)

### 📥 ÉTAPE 1 : Cloner le projet

```powershell
# Cloner depuis GitHub
git clone https://github.com/Diego0777/SAE501.git
cd SAE501
```

---

### 🐍 ÉTAPE 2 : Créer l'environnement virtuel

**Windows (PowerShell) :**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD) :**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

**✅ Vérifier l'activation :** Le prompt doit afficher `(venv)` devant

---

### 📦 ÉTAPE 3 : Installer les dépendances

```powershell
pip install -r requirements.txt
```

**Packages installés :**
- Flask (serveur web)
- scikit-learn (TF-IDF)
- joblib (sérialisation)
- requests (API externe)

---

### 🔧 ÉTAPE 4 : Préparer les données (OPTIONNEL - Déjà dans Git)

**⚠️ CES ÉTAPES SONT DÉJÀ FAITES SI VOUS AVEZ CLONÉ LE GIT**

#### 4.1 - Prétraiter les sous-titres

```powershell
python preprocess.py
```

📁 **Résultat :** Fichiers nettoyés dans `data/cleaned/`

#### 4.2 - Extraire les mots-clés

```powershell
python indexer.py
```

📁 **Résultat :** 
- `data/keywords/*.txt` (50k+ mots-clés)
- `data/index/tfidf_matrix.joblib` (index TF-IDF)
- `data/index/meta.joblib` (métadonnées)

---

### 💾 ÉTAPE 5 : Créer et remplir la base de données

```powershell
python database/import_data_sqlite.py
```

**✅ Ce script va :**
1. Créer `data/tvseries.db` (SQLite)
2. Créer les tables (series, users, ratings, keywords, posters)
3. Importer 250 séries
4. Importer 50k+ mots-clés
5. Créer 6 utilisateurs de test
6. Importer 42 notations
7. Télécharger et stocker 250 posters (BLOB)

**⏱️ Durée :** ~2-3 minutes

**📊 Vérification :**
```powershell
# Compter les séries importées
python -c "import sqlite3; conn = sqlite3.connect('data/tvseries.db'); print('Séries:', conn.execute('SELECT COUNT(*) FROM series').fetchone()[0]); conn.close()"
```

**Résultat attendu :** `Séries: 250`

---

### 🚀 ÉTAPE 6 : Lancer le serveur

```powershell
python serve_api_sqlite.py
```

**✅ Sortie attendue :**
```
============================================================
🚀 Serveur API TV Series - Version SQLite
============================================================
📊 Base de données : SQLite (data/tvseries.db)
🌐 URL : http://127.0.0.1:5000
📖 Documentation : http://127.0.0.1:5000/api
============================================================

 * Running on http://127.0.0.1:5000
```

---

### 🌐 ÉTAPE 7 : Accéder au site

Ouvrir dans un navigateur : **http://127.0.0.1:5000**

#### Pages disponibles

| Page | URL | Description |
|------|-----|-------------|
| **Accueil** | `/` ou `/index.html` | Séries populaires + Hero section |
| **Recherche** | `/search.html` | Recherche TF-IDF ("crash avion île" → Lost) |
| **Séries** | `/series.html` | Liste complète avec tri et filtre VF/VO |
| **Recommandations** | `/recommendations.html` | Suggestions basées sur les notes |
| **Détails** | `/series-details.html?series=lost_vf` | Page série avec poster et notation |
| **Profil** | `/profile.html` | Connexion + historique notations |

---

### 👤 Comptes de test

| Utilisateur | Mot de passe | Séries notées |
|-------------|--------------|---------------|
| alice       | password123  | 8 séries      |
| bob         | password123  | 7 séries      |
| charlie     | password123  | 7 séries      |
| diana       | password123  | 7 séries      |
| eve         | password123  | 7 séries      |
| frank       | password123  | 6 séries      |

---

## 🛠️ Dépannage

### ❌ Problème : Pas de séries affichées sur le site

**Solution :**
```powershell
# 1. Vérifier que la BD existe
Test-Path data/tvseries.db
# Résultat attendu: True

# 2. Vérifier le nombre de séries
python -c "import sqlite3; conn = sqlite3.connect('data/tvseries.db'); print('Séries:', conn.execute('SELECT COUNT(*) FROM series').fetchone()[0]); conn.close()"
# Résultat attendu: Séries: 250

# 3. Si 0 série → Réimporter
python database/import_data_sqlite.py
```

### ❌ Problème : Erreur "Table series doesn't exist"

**Cause :** Base de données non créée

**Solution :**
```powershell
# Supprimer l'ancienne BD
Remove-Item data/tvseries.db -ErrorAction SilentlyContinue

# Recréer avec import
python database/import_data_sqlite.py
```

### ❌ Problème : "Lost" n'apparaît pas dans la recherche "crash avion île"

**Cause :** Index TF-IDF manquant

**Solution :**
```powershell
# 1. Vérifier si l'index existe
Test-Path data/index/tfidf_matrix.joblib
# Si False:

# 2. Recréer l'index
python preprocess.py
python indexer.py
```

### ❌ Problème : Posters ne s'affichent pas

**Cause :** Posters non téléchargés ou manquants

**Solution :**
```powershell
# Vérifier les posters dans la BD
python -c "import sqlite3; conn = sqlite3.connect('data/tvseries.db'); print('Posters:', conn.execute('SELECT COUNT(*) FROM series WHERE poster_url IS NOT NULL').fetchone()[0]); conn.close()"
# Résultat attendu: Posters: 250

# Si 0 → Réimporter (import_data_sqlite.py télécharge les posters)
python database/import_data_sqlite.py
```

### ❌ Problème : Port 5000 déjà utilisé

**Solution :**
```powershell
# Trouver et tuer le processus
Get-Process -Name python | Stop-Process -Force

# Ou changer le port dans serve_api_sqlite.py (ligne finale)
# app.run(debug=True, host='0.0.0.0', port=8080)
```

### ❌ Problème : Module 'flask' introuvable

**Solution :**
```powershell
# Vérifier l'activation du venv (doit afficher (venv))
# Si pas activé:
.\venv\Scripts\Activate.ps1

# Réinstaller les dépendances
pip install -r requirements.txt
```

---

## 📖 Utilisation avancée

### 🔍 Tester la recherche TF-IDF

```powershell
# Recherche "crash avion île" → Lost doit être #1
python -c "import recommend; results = recommend.search_series('crash avion île'); print('\n'.join([f'{r[\"title\"]}: {r[\"score\"]:.3f}' for r in results[:3]]))"
```

**Résultat attendu :**
```
lost_vf: 1.125
lost_vo: 1.125
...
```

### 📊 Statistiques de la base

```powershell
python -c "import sqlite3; conn = sqlite3.connect('data/tvseries.db'); print('Séries:', conn.execute('SELECT COUNT(*) FROM series').fetchone()[0]); print('Users:', conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]); print('Ratings:', conn.execute('SELECT COUNT(*) FROM ratings').fetchone()[0]); print('Keywords:', conn.execute('SELECT COUNT(*) FROM keywords').fetchone()[0]); conn.close()"
```

### 🎨 Filtre VF/VO

Le bouton **VF/VO** dans la navbar change de couleur :
- **Violet** : Toutes les séries
- **Vert** : VF uniquement
- **Bleu** : VO uniquement

Préférence sauvegardée dans `localStorage`.

---

## 📁 Structure du projet

```
SAE501/
├── data/                      # Données et base de données
│   ├── tvseries.db           # Base SQLite (250 séries + posters BLOB)
│   ├── ratings.json          # Notations utilisateurs
│   ├── cleaned/              # Sous-titres nettoyés
│   ├── index/                # Index TF-IDF sérialisé
│   └── keywords/             # Mots-clés extraits (50k+)
├── database/                  # Schéma et connexion BD
│   └── db_sqlite.py          # Connexion SQLite
├── web/                       # Interface web
│   ├── index.html            # Page d'accueil (hero + stats)
│   ├── search.html           # Recherche TF-IDF
│   ├── series.html           # Liste des séries
│   ├── recommendations.html  # Recommandations
│   ├── profile.html          # Profil utilisateur
│   ├── series-details.html   # Détails + notation
│   ├── style.css             # Styles CSS
│   └── app.js                # Fonctions JS (filtre VF/VO)
├── sous-titres/              # Sous-titres .srt (15k+ fichiers)
├── api_*.py                  # Blueprints API Flask
├── serve_api_sqlite.py       # Serveur Flask principal
├── database/
│   └── import_data_sqlite.py # Import complet (BD + posters)
├── preprocess.py             # Nettoyage sous-titres
├── indexer.py                # Création index TF-IDF
├── recommend.py              # Système de recommandation
├── requirements.txt          # Dépendances Python
├── .gitignore                # Fichiers exclus du Git
└── README.md                 # Documentation
```

## 🔧 API Endpoints

### Séries
- `GET /api/series` - Liste toutes les séries
- `GET /api/series/<title>` - Détails d'une série
- `GET /api/series/search?query=` - Recherche par nom

### Recherche
- `GET /api/search?q=<query>` - Recherche TF-IDF

### Recommandations
- `GET /api/recommend/popularity` - Par popularité
- `GET /api/recommend/collaborative/<user_id>` - Collaboratives
- `GET /api/recommend/hybrid/<user_id>` - Hybrides

### Utilisateurs
- `POST /api/users/register` - Créer un compte
- `POST /api/users/login` - Se connecter
- `GET /api/users/verify` - Vérifier la session
- `GET /api/users/profile` - Profil utilisateur

### Notations
- `POST /api/ratings` - Noter une série (body: `{user_id, series_title, rating}`)
- `GET /api/ratings/<user_id>` - Notations d'un utilisateur

### Posters
- `GET /posters/<series_name>` - Image du poster (BLOB)

---

## 🎓 Exigences SAE501

### ✅ Validation du projet

**Critère 1 : Recherche TF-IDF fonctionnelle**
```powershell
# Test : "crash avion île" doit retourner Lost en premier
python -c "import recommend; r = recommend.search_series('crash avion île'); print('Test SAE501:', 'PASS ✅' if r[0]['title'].startswith('lost') and r[0]['score'] > 1.0 else 'FAIL ❌')"
```

**Critère 2 : Base de données complète**
- 250 séries ✅
- Utilisateurs + notations ✅
- Mots-clés indexés ✅
- Posters stockés ✅

**Critère 3 : Interface web fonctionnelle**
- Recherche interactive ✅
- Affichage des résultats ✅
- Système de notation ✅
- Authentification ✅

---

## 📝 Notes techniques

### TF-IDF
- **Vectorizer** : `TfidfVectorizer` de scikit-learn
- **Max features** : 5000 mots-clés par série
- **Stopwords** : Français (liste personnalisée)
- **N-grams** : 1-2 (unigrams + bigrams)

### Base de données
- **Engine** : SQLite 3.x
- **Taille** : ~100 MB (avec posters BLOB)
- **Tables** : 5 (series, users, ratings, keywords, posters)
- **Index** : Sur series_id, user_id, title

### Recommandations
- **Collaborative** : Similarité cosinus entre utilisateurs
- **Popularité** : Moyenne des notes × nombre de votes
- **Hybride** : 70% collaborative + 30% popularité

---

## 👨‍💻 Auteur

**Projet SAE501 - IUT Informatique**  
Système de recommandation de séries TV avec recherche TF-IDF

---

## 📜 Licence

Projet académique - 2025

### Utilisateurs
- `POST /register` - Créer un compte
- `POST /login` - Se connecter
- `GET /profile` - Obtenir le profil (authentifié)

### Notations
- `POST /rate` - Noter une série
- `GET /user/<user_id>/ratings` - Notes d'un utilisateur

## 🎨 Fonctionnalités avancées

### Filtre VF/VO
Bouton en haut à droite permettant de filtrer tout le site :
- 🌍 **Tous** : Toutes les séries
- 🇫🇷 **VF** : Séries françaises uniquement
- 🇺🇸 **VO** : Versions originales uniquement

La préférence est sauvegardée dans le navigateur.

### Recherche intelligente
Le système utilise **TF-IDF** (Term Frequency-Inverse Document Frequency) pour :
- Analyser les sous-titres de chaque série
- Extraire les mots-clés les plus pertinents
- Trouver les séries correspondant à une requête

**Exemple** : Rechercher "crash avion île" retourne **Lost** en premier résultat.

### Système de notation
- Notes de 1 à 5 étoiles
- Mise à jour automatique des statistiques
- Calcul de la popularité : `moyenne × log(1 + nombre_notes)`

## 🛠️ Technologies utilisées

- **Backend** : Python 3, Flask, SQLite
- **Frontend** : HTML5, CSS3, JavaScript Vanilla
- **Traitement** : scikit-learn (TF-IDF), joblib
- **API externe** : TVmaze (récupération des posters)

## 📝 Notes importantes

- Les posters sont stockés en **BLOB** dans la base de données (optimisation)
- Les images VF et VO partagent le même poster (économie d'espace)
- L'index TF-IDF est sauvegardé en `.joblib` pour des performances optimales
- Les sessions utilisateurs expirent après 30 jours

## 🐛 Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier que le port 5000 est libre
netstat -ano | findstr :5000

# Ou changer le port dans serve_api_sqlite.py
app.run(debug=True, port=5001)
```

### Base de données vide
```bash
# Réimporter les données
python import_to_sqlite.py
```

### Images ne s'affichent pas
```bash
# Re-télécharger les posters
python fetch_posters.py
python optimize_posters.py
```

## 👥 Auteur

Projet SAE501 - IUT / Université

## 📄 Licence

Projet académique - Utilisation libre pour l'enseignement


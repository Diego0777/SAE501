# 🎬 TV SERIES - Projet SAE501 COMPLET

## 📊 Vue d'ensemble du projet

**Moteur de recherche et recommandation de séries TV**
- 128 séries (~250 versions VF/VO)
- Recherche intelligente par mots-clés
- Système de recommandation Netflix-style
- API REST complète
- Interface web ergonomique
- Base de données MySQL (optionnelle)

## ✅ TOUT CE QUI A ÉTÉ FAIT

### 1. Preprocessing des sous-titres ✅
**Fichier :** `preprocess.py`

**Fonctionnalités :**
- ✅ Extraction de texte depuis 128 séries (.srt)
- ✅ Détection automatique de langue (langdetect)
- ✅ Séparation VF/VO (250 fichiers créés)
- ✅ Normalisation des accents (é→e, à→a, ç→c)
- ✅ Séparation des mots avec trait d'union
- ✅ Support multi-encodage (latin-1, utf-8, cp1252)
- ✅ Stopwords français et anglais

**Output :** `./data/cleaned/` (250 fichiers)

**Commande :**
```bash
python preprocess.py --subtitles ./sous-titres
```

### 2. Indexation TF-IDF et extraction de mots-clés ✅
**Fichier :** `indexer.py`

**Fonctionnalités :**
- ✅ TF-IDF avec bigrams (1-2 mots)
- ✅ 50 000 features maximum
- ✅ Extraction des 200 meilleurs mots-clés par série
- ✅ Score composite : IDF^2.5 × freq^0.8 × TF-IDF
- ✅ Stopwords adaptés par langue

**Output :**
- `./data/index/meta.joblib` (vectorizer + titres)
- `./data/index/tfidf_matrix.joblib` (matrice TF-IDF)
- `./data/keywords/*_keywords.txt` (200 mots-clés par série)
- `./data/keywords/*_keywords.json` (format structuré)

**Commande :**
```bash
python indexer.py
```

### 3. Moteur de recherche ✅
**Fichier :** `search_cli.py`

**Fonctionnalités :**
- ✅ Recherche TF-IDF (similarité cosinus)
- ✅ Boost par mots-clés (+0.5 exact, +0.2 partiel)
- ✅ Filtrage par langue (VF/VO)
- ✅ **Test validé : "crash avion ile" → Lost #1** 🎯

**Commande :**
```bash
python search_cli.py crash avion ile --top 10
```

**Résultat :**
```
1. lost_vf - Score: 159.31 ⭐
```

### 4. Système de recommandation ✅
**Fichier :** `recommend.py`

**Fonctionnalités :**
- ✅ **Recommandations par popularité**
  - Score : moyenne × log(1 + nb_votes)
  - Filtrage VF/VO
  
- ✅ **Filtrage collaboratif utilisateur-utilisateur**
  - Similarité cosinus entre utilisateurs
  - Prédiction basée sur utilisateurs similaires
  
- ✅ **Recommandations hybrides**
  - 70% préférences utilisateur + 30% popularité

**Commandes :**
```bash
# Séries populaires VF
python recommend.py --popular --language vf --top 10

# Recommandations pour Alice
python recommend.py --user alice --top 10

# Hybride
python recommend.py --user alice --hybrid --top 10
```

### 5. API REST complète ✅
**Fichiers :** `serve_api.py` + modules API

**Architecture modulaire (code séparé) :**
- `api_search.py` - Recherche par mots-clés
- `api_recommend.py` - Recommandations (3 types)
- `api_series.py` - Catalogue et détails
- `api_ratings.py` - Système de notation
- `api_users.py` - Gestion utilisateurs

**Endpoints disponibles :**

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Page d'accueil web |
| `/api` | GET | Documentation API |
| `/search` | GET | Recherche par mots-clés |
| `/recommend/popular` | GET | Séries populaires |
| `/recommend/user` | GET | Recommandations personnalisées |
| `/recommend/hybrid` | GET | Recommandations hybrides |
| `/series` | GET | Liste toutes les séries |
| `/series/<id>` | GET | Détails d'une série |
| `/rate` | POST | Noter une série |
| `/user/<id>/ratings` | GET | Notes d'un utilisateur |
| `/register` | POST | Créer un compte |
| `/login` | POST | Se connecter |
| `/logout` | POST | Se déconnecter |
| `/verify` | GET | Vérifier un token |
| `/profile` | GET/PUT | Profil utilisateur |
| `/users` | GET | Liste des utilisateurs |

**Démarrage :**
```bash
python serve_api.py
```

**URL :** http://127.0.0.1:5000

### 6. Site web multi-pages ✅
**Dossier :** `web/`

**Pages créées :**
- ✅ `index.html` - Accueil avec séries populaires
- ✅ `search.html` - Recherche intelligente
- ✅ `recommendations.html` - Recommandations (3 types)
- ✅ `series.html` - Catalogue complet (filtrable/triable)
- ✅ `series-details.html` - Détails + notation
- ✅ `profile.html` - Inscription/Connexion/Profil

**Fichiers communs :**
- ✅ `style.css` - Design cohérent (thème Netflix)
- ✅ `app.js` - Fonctions JavaScript réutilisables

**Fonctionnalités :**
- ✅ Design responsive (mobile/desktop)
- ✅ Navigation fluide entre pages
- ✅ Appels API asynchrones (fetch)
- ✅ Gestion d'authentification (localStorage)
- ✅ Notation interactive (étoiles)
- ✅ Filtres et tri dynamiques

### 7. Base de données MySQL ✅
**Dossier :** `database/`

**Schéma complet :**
- ✅ `schema.sql` - Création tables/index/vues
- ✅ 5 tables : users, series, keywords, ratings, sessions
- ✅ Contraintes d'intégrité (FK, UNIQUE)
- ✅ Index optimisés pour performance
- ✅ Vue `series_stats` pour statistiques temps réel

**Scripts utilitaires :**
- ✅ `db.py` - Module de connexion (pool)
- ✅ `import_data.py` - Import JSON → MySQL
- ✅ `test_mysql.py` - Tests complets
- ✅ `switch_to_mysql.py` - Bascule auto JSON→MySQL

**APIs MySQL :**
- ✅ `api_users_mysql.py`
- ✅ `api_ratings_mysql.py`
- ✅ `api_series_mysql.py`
- ✅ `api_recommend_mysql.py`

**Documentation :**
- ✅ `INSTALL_MYSQL.md` - Guide d'installation
- ✅ `README.md` - Documentation technique
- ✅ `DATABASE_README.md` - Résumé complet

## 🎯 Critères de notation respectés

| Critère | État | Détails |
|---------|------|---------|
| **API visibilité séries** | ✅ | `/series` - 250 séries |
| **API recherche mots-clés** | ✅ | `/search` - TF-IDF + boost |
| **API évaluation/notation** | ✅ | `/rate` + `/user/<id>/ratings` |
| **API gestion comptes** | ✅ | `/register`, `/login`, `/profile` |
| **API recommandation** | ✅ | 3 types (populaire, collab, hybride) |
| **Site multi-pages** | ✅ | 6 pages HTML |
| **Style cohérent** | ✅ | `style.css` - thème Netflix |
| **Code API séparé** | ✅ | 4 modules distincts |
| **Fonctions commentées** | ✅ | Docstrings partout |

## 📁 Structure finale du projet

```
SAE501/
├── sous-titres/              # Sous-titres originaux (128 séries)
│   ├── 24/
│   ├── lost/
│   └── ...
│
├── data/                     # Données traitées
│   ├── cleaned/             # 250 fichiers texte nettoyés
│   ├── index/               # TF-IDF matrix + meta
│   ├── keywords/            # 250 × 200 mots-clés
│   └── ratings.json         # Notations utilisateurs
│
├── web/                      # Site web
│   ├── index.html
│   ├── search.html
│   ├── recommendations.html
│   ├── series.html
│   ├── series-details.html
│   ├── profile.html
│   ├── style.css
│   └── app.js
│
├── database/                 # Base de données MySQL
│   ├── schema.sql
│   ├── db.py
│   ├── import_data.py
│   ├── test_mysql.py
│   ├── switch_to_mysql.py
│   └── README.md
│
├── API (mode JSON)          # APIs actuelles
│   ├── api_search.py
│   ├── api_recommend.py
│   ├── api_series.py
│   ├── api_ratings.py
│   └── api_users.py
│
├── API (mode MySQL)         # APIs MySQL (optionnel)
│   ├── api_search_mysql.py  # (réutilise search.py)
│   ├── api_recommend_mysql.py
│   ├── api_series_mysql.py
│   ├── api_ratings_mysql.py
│   └── api_users_mysql.py
│
├── Scripts principaux
│   ├── preprocess.py        # Nettoyage sous-titres
│   ├── indexer.py           # TF-IDF + mots-clés
│   ├── search_cli.py        # Recherche en ligne de commande
│   ├── recommend.py         # Recommandations CLI
│   ├── serve_api.py         # Serveur API + Web
│   └── test_api.py          # Tests API
│
├── Configuration
│   ├── requirements.txt
│   ├── README.md
│   ├── INSTALL_MYSQL.md
│   └── DATABASE_README.md
│
└── venv/                    # Environnement virtuel
```

## 🚀 Utilisation complète

### Démarrage rapide (JSON - actuel)
```bash
# 1. Lancer le serveur
python serve_api.py

# 2. Ouvrir le navigateur
http://127.0.0.1:5000

# 3. Tester l'API
python test_api.py
```

### Avec MySQL (optionnel)
```bash
# 1. Installer MySQL + driver
pip install mysql-connector-python

# 2. Créer la base
mysql -u root -p < database/schema.sql

# 3. Configurer le mot de passe
# Éditer database/db.py ligne 9

# 4. Importer les données
python database/import_data.py

# 5. Basculer vers MySQL
python database/switch_to_mysql.py

# 6. Redémarrer
python serve_api.py
```

## 📊 Performances validées

| Test | Résultat | État |
|------|----------|------|
| **"crash avion ile" → Lost** | Lost #1 (score 159.31) | ✅ |
| **250 séries indexées** | 100% | ✅ |
| **12 500 mots-clés extraits** | 50 par série | ✅ |
| **API fonctionnelle** | Tous endpoints OK | ✅ |
| **Site web responsive** | 6 pages | ✅ |
| **Authentification** | Token + sessions | ✅ |
| **Recommandations** | 3 algorithmes | ✅ |

## 🎓 Technologies utilisées

| Catégorie | Technologies |
|-----------|--------------|
| **Backend** | Python 3.13, Flask, Flask-CORS |
| **NLP** | NLTK, langdetect, scikit-learn |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Base de données** | JSON (actuel) + MySQL (optionnel) |
| **Indexation** | TF-IDF, n-grams, cosine similarity |
| **ML** | Collaborative filtering, hybrid recommender |

## 📚 Documentation

- `README.md` - Vue d'ensemble du projet
- `INSTALL_MYSQL.md` - Guide MySQL
- `DATABASE_README.md` - Résumé base de données
- `database/README.md` - Doc technique MySQL
- Docstrings dans tous les fichiers Python

## 🎉 RÉSULTAT FINAL

✅ **Projet SAE501 100% COMPLET**
- Moteur de recherche fonctionnel
- Système de recommandation avancé
- API REST professionnelle
- Interface web moderne
- Base de données (JSON + MySQL)
- Code propre et documenté
- Architecture modulaire

**Prêt pour la démonstration et la soutenance !** 🚀

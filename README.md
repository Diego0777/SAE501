# 📺 S5C.01 - Système de Recommandation de Séries TV

> Plateforme web moderne de recherche et recommandation de séries TV avec algorithmes intelligents TF-IDF et filtrage collaboratif.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table des matières

- [Aperçu](#-aperçu)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Installation Rapide](#-installation-rapide)
- [Guide d'utilisation](#-guide-dutilisation)
- [API Documentation](#-api-documentation)
- [Structure du projet](#-structure-du-projet)
- [Technologies](#-technologies)
- [Déploiement](#-déploiement)
- [Contributeurs](#-contributeurs)

---

## 🎯 Aperçu

S5C.01 est une plateforme complète de découverte de séries TV offrant:

- **Recherche intelligente** par mots-clés extraits de 50 000+ sous-titres
- **Recommandations personnalisées** basées sur vos goûts et ceux d'utilisateurs similaires
- **Interface moderne** responsive avec filtres VF/VO
- **Base de données riche** : 250 séries, posters TVmaze, système de notation

### 📊 Statistiques

- **250 séries TV** (VF et VO)
- **50 000+ mots-clés** indexés (TF-IDF)
- **10+ utilisateurs** de test
- **200+ notations** utilisateurs
- **250 posters** haute qualité (TVmaze API)

---

## ✨ Fonctionnalités

### 🔍 Recherche Avancée

- **Recherche TF-IDF** : Trouvez des séries par mots-clés sémantiques
  - Exemple: "crash avion île" → *Lost*
  - Exemple: "drogue professeur chimie" → *Breaking Bad*
- **Recherche par titre** : Autocomplétion et correspondance exacte
- **Filtres** : Langue (VF/VO), nombre de résultats (10/20/50)
- **Fusion intelligente** : Combine TF-IDF et titre pour des résultats pertinents

### 💡 Recommandations

1. **Par popularité**
   - Score = `note_moyenne × log(1 + nb_votes)`
   - Équilibre entre qualité et consensus

2. **Filtrage collaboratif**
   - Trouve des utilisateurs aux goûts similaires
   - Recommande leurs séries préférées (≥4/5)
   - Personnalisé par langue préférée

3. **Hybride**
   - Combine popularité et filtrage collaboratif
   - Moyenne pondérée des deux scores

### 👤 Gestion Utilisateur

- Création de compte et authentification
- Profil personnalisé avec statistiques
- Système de notation 1-5 étoiles
- Historique des séries notées
- Préférence de langue (VF/VO)

### 🎨 Interface Utilisateur

- Design moderne et responsive
- Mode sombre élégant
- Posters haute qualité
- Filtres inline intuitifs
- Navigation fluide entre pages

---

## 🏗️ Architecture

### Stack Technique

```
Frontend (SPA)
├── HTML5/CSS3/JavaScript
├── Design responsive mobile-first
└── API REST consumption

Backend (Flask)
├── Flask 3.x (Python 3.8+)
├── SQLite 3 (embedded database)
├── scikit-learn (TF-IDF)
├── Flask-CORS (cross-origin)
└── RESTful API architecture

Data Processing
├── TF-IDF vectorization
├── Collaborative filtering
├── TVmaze API integration
└── Poster management (BLOB)
```

### Diagramme d'Architecture

```
┌─────────────┐     HTTP      ┌──────────────┐
│   Browser   │ ────────────> │ Flask Server │
│  (Client)   │               │   (API)      │
└─────────────┘               └──────┬───────┘
                                     │
                   ┌─────────────────┼─────────────────┐
                   │                 │                 │
              ┌────▼─────┐     ┌────▼─────┐    ┌─────▼────┐
              │ Search   │     │ Recommend│    │ Series   │
              │ Module   │     │ Module   │    │ Module   │
              └────┬─────┘     └────┬─────┘    └────┬─────┘
                   │                 │               │
                   └─────────────────┼───────────────┘
                                     │
                              ┌──────▼──────┐
                              │  SQLite DB  │
                              │ (250 series)│
                              └─────────────┘
```

---

## 🚀 Installation Rapide

### Prérequis

- **Python 3.8+** ([Télécharger](https://www.python.org/downloads/))
- **Git** ([Télécharger](https://git-scm.com/downloads))
- **pip** (inclus avec Python)

### Installation en 5 minutes

```powershell
# 1. Cloner le projet
git clone https://github.com/Diego0777/SAE501.git
cd SAE501

# 2. Créer et activer l'environnement virtuel
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# source venv/bin/activate   # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer la base de données (2-3 minutes)
python database/import_data_sqlite.py

# 5. Lancer le serveur
python serve_api_sqlite.py
```

**🎉 C'est prêt !** Ouvrez http://127.0.0.1:5000

---

## 📖 Guide d'utilisation

### Démarrage du serveur

```powershell
# S'assurer que le venv est activé
.\venv\Scripts\Activate.ps1

# Lancer le serveur de développement
python serve_api_sqlite.py
```

**Sortie attendue:**
```
============================================================
Serveur API TV Series - Version SQLite
============================================================
Base de données : SQLite (data/tvseries.db)
URL : http://127.0.0.1:5000
Documentation : http://127.0.0.1:5000/api
============================================================

 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Vérification de la base de données

```powershell
python -c "import sqlite3; conn = sqlite3.connect('data/tvseries.db'); print('Séries:', conn.execute('SELECT COUNT(*) FROM series').fetchone()[0]); print('Users:', conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]); print('Ratings:', conn.execute('SELECT COUNT(*) FROM ratings').fetchone()[0]); conn.close()"
```

**Résultat attendu:**
```
Séries: 250
Users: 10
Ratings: 200+
```

### Comptes de test disponibles

| Username | Mot de passe | Langue | Notes |
|----------|-------------|--------|-------|
| alice    | alice123    | VF     | 15    |
| bob      | bob123      | VO     | 12    |
| carol    | carol123    | VF     | 8     |

---

## 🔌 API Documentation

### Base URL

```
http://127.0.0.1:5000
```

### Endpoints principaux

#### Recherche

```http
GET /api/search?q=lost&top=20&language=vf
```

**Paramètres:**
- `q` (string, requis) : Mots-clés de recherche
- `top` (int, optionnel) : Nombre de résultats (défaut: 20)
- `language` (string, optionnel) : 'vf', 'vo' ou vide

**Réponse:**
```json
{
  "query": "lost",
  "total_results": 5,
  "results": [
    {
      "title": "Lost_vf",
      "score": 1000,
      "language": "vf",
      "average_rating": 4.5,
      "num_ratings": 25,
      "poster_url": "/posters/Lost_vf.jpg"
    }
  ]
}
```

#### Recommandations

```http
GET /api/recommend/collaborative/1?limit=10
```

**Paramètres:**
- `user_id` (int, path) : ID de l'utilisateur
- `limit` (int, optionnel) : Nombre de recommandations (défaut: 10)

**Réponse:**
```json
{
  "method": "collaborative",
  "recommendations": [
    {
      "title": "Breaking Bad_vf",
      "score": 4.8,
      "language": "vf",
      "average_rating": 4.9,
      "num_ratings": 42
    }
  ]
}
```

#### Notation

```http
POST /api/ratings
Content-Type: application/json
Authorization: <token>

{
  "serie_id": 1,
  "rating": 5
}
```

**Réponse:**
```json
{
  "success": true,
  "rating_id": 123,
  "message": "Note enregistrée"
}
```

### Documentation complète

Consultez `/api` pour la documentation interactive complète de l'API.

---

## 📁 Structure du projet

```
SAE501/
├── web/                          # Frontend (HTML/CSS/JS)
│   ├── index.html               # Page d'accueil
│   ├── search.html              # Recherche
│   ├── recommendations.html     # Recommandations
│   ├── series.html              # Catalogue
│   ├── series-details.html      # Détails d'une série
│   ├── profile.html             # Profil utilisateur
│   ├── style.css                # Styles globaux
│   └── app.js                   # Logique frontend
│
├── database/                     # Gestion de la base de données
│   ├── db_sqlite.py             # Connexion SQLite
│   └── import_data_sqlite.py    # Import initial + posters
│
├── data/                         # Données
│   ├── tvseries.db              # Base SQLite (généré)
│   ├── keywords/                # Mots-clés par série
│   └── cleaned/                 # Données nettoyées
│
├── sous-titres/                  # Sous-titres originaux
│   ├── 24/
│   ├── lost/
│   └── ... (250 séries)
│
├── api_*.py                      # Modules API
│   ├── api_search_sqlite.py     # Recherche TF-IDF
│   ├── api_recommend_sqlite.py  # Recommandations
│   ├── api_series_sqlite.py     # Gestion séries
│   ├── api_ratings_sqlite.py    # Système de notation
│   └── api_users_sqlite.py      # Authentification
│
├── serve_api_sqlite.py          # Serveur Flask principal
├── indexer.py                   # Indexation TF-IDF
├── preprocess.py                # Prétraitement sous-titres
├── fetch_posters.py             # Téléchargement posters
├── requirements.txt             # Dépendances Python
├── Procfile                     # Configuration Render
├── start.sh                     # Script de démarrage
├── README.md                    # Ce fichier
└── .gitignore                   # Fichiers ignorés par Git
```

---

## 🛠️ Technologies

### Backend

| Technologie | Version | Usage |
|-------------|---------|-------|
| Python | 3.8+ | Langage principal |
| Flask | 3.0+ | Framework web |
| SQLite | 3 | Base de données |
| scikit-learn | 1.3+ | TF-IDF, ML |
| joblib | 1.3+ | Sérialisation |
| requests | 2.31+ | API externe |
| flask-cors | 4.0+ | CORS |

### Frontend

| Technologie | Usage |
|-------------|-------|
| HTML5 | Structure |
| CSS3 | Styles modernes |
| JavaScript | Logique client |
| Fetch API | Requêtes HTTP |

### Données

| Source | Usage |
|--------|-------|
| Sous-titres SRT | Extraction mots-clés |
| TVmaze API | Posters haute qualité |
| SQLite | Stockage persistant |

---

## 🌐 Déploiement

### Déploiement sur Render.com (Gratuit)

Le projet est configuré pour un déploiement automatique sur Render.

**Fichiers de configuration:**
- `Procfile` : Commande de démarrage
- `start.sh` : Script d'initialisation
- `requirements.txt` : Dépendances

**URL de production:** https://sae501-afj1.onrender.com

### Étapes de déploiement

1. **Push sur GitHub**
   ```powershell
   git add .
   git commit -m "Ready for deploy"
   git push origin main
   ```

2. **Render Dashboard**
   - Créer un nouveau Web Service
   - Connecter le repository GitHub
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `bash start.sh`

3. **Variables d'environnement**
   - `PORT` : Auto-configuré par Render
   - Pas besoin de configuration supplémentaire

---

## 👥 Contributeurs

### Équipe SAE501

- **Diego** - Lead Developer & Architecture
- **Projet** - SAE501 - IUT Informatique

### Contributions

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.

---

## 📝 License

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- **TVmaze API** pour les posters de qualité
- **scikit-learn** pour les algorithmes TF-IDF
- **Flask** pour le framework web minimaliste
- **Render.com** pour l'hébergement gratuit

---

## 📞 Support

- **Issues GitHub**: [Signaler un bug](https://github.com/Diego0777/SAE501/issues)
- **Documentation API**: http://127.0.0.1:5000/api
- **Email**: Contactez l'équipe

---

<div align="center">

**Made with ❤️ for SAE501**

[⬆ Retour en haut](#--s5c01---système-de-recommandation-de-séries-tv)

</div>

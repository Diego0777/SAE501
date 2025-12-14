# SAE501 - Système de Recommandation de Séries TV

Projet de recherche et recommandation de séries TV utilisant TF-IDF et filtrage collaboratif.

## Description

Application web permettant de rechercher des séries TV et d'obtenir des recommandations personnalisées. Le système utilise les sous-titres pour extraire des mots-clés et recommande des séries basées sur les notes des utilisateurs.

## Fonctionnalités principales

- Recherche de séries par mots-clés (TF-IDF sur sous-titres)
- Recommandations par popularité et filtrage collaboratif
- Gestion de comptes utilisateurs et notation des séries
- Interface web responsive
- API REST

**Lien de démo** : https://sae501-afj1.onrender.com (premier démarrage lent)

**Données** : 250 séries indexées avec 50 000+ mots-clés

## Détails techniques

### Recherche
- Recherche TF-IDF sur mots-clés extraits des sous-titres
- Recherche par titre
- Filtres langue (VF/VO)

### Recommandations
- Par popularité (note moyenne × log(nb votes))
- Par filtrage collaboratif (utilisateurs similaires)
- Hybride (combinaison des deux)

### Utilisateurs
- Création de compte
- Notation des séries (1-5 étoiles)
- Profil avec historique

## Technologies

- **Backend** : Python 3.8+, Flask 3.0, SQLite 3
- **Frontend** : HTML/CSS/JavaScript
- **ML** : scikit-learn (TF-IDF)
- **Données** : TVmaze API pour les posters


## Installation

```powershell
# Cloner le projet
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

Accéder à http://127.0.0.1:5000

## Utilisation

```powershell
python serve_api_sqlite.py
```

Comptes de test : alice/alice123, bob/bob123

## API

Endpoints principaux :
- `GET /api/search?q=...` - Recherche
- `GET /api/recommend/{type}/{user_id}` - Recommandations
- `POST /api/ratings` - Noter une série
- `GET /api/series` - Liste des séries

Doc complète : http://127.0.0.1:5000/api

## Structure

```
SAE501/
├── web/                     # Frontend HTML/CSS/JS
├── database/                # Gestion base SQLite
├── data/                    # Base de données et index
├── sous-titres/             # Fichiers SRT (250 séries)
├── docs/                    # Documentation
├── scripts/                 # Scripts utilitaires
├── tests/                   # Tests
├── api_*.py                 # Modules API REST
├── serve_api_sqlite.py      # Serveur Flask
└── requirements.txt         # Dépendances
```



## Déploiement

Déployé sur Render : https://sae501-afj1.onrender.com

## Auteurs

Diego Massat & Shun Von Lunen - Groupe 17 - SAE501 IUT Informatique

GitHub : https://github.com/Diego0777/SAE501

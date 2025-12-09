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
- **37+ notations** utilisateurs
- **Posters** : Images stockées en BLOB dans la BD

## 🚀 Installation

### Prérequis

- Python 3.8+
- pip

### Étapes

1. **Cloner le dépôt**
```bash
git clone <url-du-repo>
cd SAE501
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
```

3. **Activer l'environnement virtuel**

Windows (PowerShell) :
```powershell
.\venv\Scripts\Activate.ps1
```

Windows (CMD) :
```cmd
venv\Scripts\activate.bat
```

Linux/Mac :
```bash
source venv/bin/activate
```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

5. **Importer les données dans SQLite**
```bash
python import_to_sqlite.py
```

6. **Télécharger les posters (optionnel)**
```bash
python fetch_posters.py
python optimize_posters.py
```

## 🎮 Utilisation

### Démarrer le serveur

```bash
python serve_api_sqlite.py
```

Le serveur sera accessible sur : **http://127.0.0.1:5000**

### Pages disponibles

- **Accueil** : `/` - Vue d'ensemble avec séries populaires
- **Recherche** : `/search.html` - Recherche TF-IDF par mots-clés
- **Séries** : `/series.html` - Liste complète avec tri
- **Recommandations** : `/recommendations.html` - Suggestions personnalisées
- **Profil** : `/profile.html` - Connexion et gestion du compte

### Comptes de test

| Utilisateur | Mot de passe |
|-------------|--------------|
| alice       | password123  |
| bob         | password123  |
| charlie     | password123  |
| diana       | password123  |
| eve         | password123  |
| frank       | password123  |

## 📁 Structure du projet

```
SAE501/
├── data/                      # Données et base de données
│   ├── tvseries.db           # Base SQLite
│   ├── ratings.json          # Notations utilisateurs
│   ├── cleaned/              # Données nettoyées
│   ├── index/                # Index TF-IDF
│   └── keywords/             # Mots-clés extraits
├── database/                  # Schéma et connexion BD
│   ├── schema.sql            # Schéma MySQL (référence)
│   └── db_sqlite.py          # Connexion SQLite
├── web/                       # Interface web
│   ├── index.html            # Page d'accueil
│   ├── search.html           # Recherche
│   ├── series.html           # Liste des séries
│   ├── recommendations.html  # Recommandations
│   ├── profile.html          # Profil utilisateur
│   ├── series-details.html   # Détails d'une série
│   ├── style.css             # Styles
│   ├── app.js                # Utilitaires JavaScript
│   └── posters/              # Images des posters
├── sous-titres/              # Sous-titres des séries
├── api_*.py                  # Blueprints API Flask
├── serve_api_sqlite.py       # Serveur Flask
├── import_to_sqlite.py       # Import des données
├── preprocess.py             # Prétraitement TF-IDF
├── indexer.py                # Indexation
├── recommend.py              # Système de recommandation
├── fetch_posters.py          # Récupération des posters
├── optimize_posters.py       # Optimisation des images
├── requirements.txt          # Dépendances Python
└── README.md                 # Ce fichier
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


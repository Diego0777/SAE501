# 🤝 Guide de Contribution - S5C.01

Merci de votre intérêt pour contribuer au projet S5C.01 ! Ce guide vous aidera à comprendre nos conventions et processus.

---

## 📋 Table des matières

- [Code de conduite](#code-de-conduite)
- [Comment contribuer](#comment-contribuer)
- [Standards de code](#standards-de-code)
- [Conventions de nommage](#conventions-de-nommage)
- [Documentation](#documentation)
- [Tests](#tests)
- [Workflow Git](#workflow-git)

---

## 🤝 Code de conduite

- Respectez les autres contributeurs
- Soyez constructif dans vos critiques
- Acceptez les feedbacks avec ouverture
- Maintenez un environnement professionnel et inclusif

---

## 🚀 Comment contribuer

### 1. Fork et Clone

```powershell
# Forker le repo sur GitHub, puis:
git clone https://github.com/VOTRE_USERNAME/SAE501.git
cd SAE501
```

### 2. Créer une branche

```powershell
# Créer une branche pour votre fonctionnalité
git checkout -b feature/nom-de-la-feature

# Ou pour un bugfix
git checkout -b fix/nom-du-bug
```

### 3. Faire vos modifications

- Suivre les standards de code (voir ci-dessous)
- Tester localement
- Documenter vos changements

### 4. Commit et Push

```powershell
git add .
git commit -m "feat: ajouter fonctionnalité X"
git push origin feature/nom-de-la-feature
```

### 5. Créer une Pull Request

- Décrire clairement les changements
- Référencer les issues liées
- Ajouter des screenshots si pertinent

---

## 💻 Standards de code

### Python

#### Style général

- **PEP 8**: Suivre les conventions Python standard
- **Longueur de ligne**: Maximum 88 caractères (Black formatter)
- **Encodage**: UTF-8 pour tous les fichiers
- **Indentation**: 4 espaces (pas de tabs)

#### Docstrings

Utiliser le format Google docstring pour toutes les fonctions:

```python
def calculate_score(rating, num_votes):
    """
    Calculer un score de popularité pour une série.
    
    Le score combine la note moyenne avec le nombre de votes en utilisant
    une fonction logarithmique pour équilibrer qualité et consensus.
    
    Args:
        rating (float): Note moyenne de la série (0-5)
        num_votes (int): Nombre total de votes
        
    Returns:
        float: Score de popularité calculé
        
    Raises:
        ValueError: Si rating est hors de la plage [0, 5]
        
    Example:
        >>> calculate_score(4.5, 100)
        20.8
    """
    if not 0 <= rating <= 5:
        raise ValueError("Rating must be between 0 and 5")
    
    return rating * math.log(1 + num_votes)
```

#### Imports

Organiser les imports dans cet ordre:

```python
# 1. Imports standard library
import os
import sys
from datetime import datetime

# 2. Imports third-party
from flask import Flask, request, jsonify
import numpy as np

# 3. Imports locaux
from database.db_sqlite import get_connection
from utils.helpers import format_title
```

#### Commentaires

```python
# Commentaires de code: expliquer le "pourquoi", pas le "quoi"
# ❌ Mauvais
x = x + 1  # Incrémenter x

# ✅ Bon
x = x + 1  # Compenser l'index 0-based pour l'affichage utilisateur

# Sections de code: séparer logiquement
# ============================================================================
# ALGORITHME DE RECOMMANDATION
# ============================================================================

def recommend_series():
    # Étape 1: Récupérer les préférences utilisateur
    preferences = get_user_preferences()
    
    # Étape 2: Calculer les scores de similarité
    scores = calculate_similarity(preferences)
    
    # Étape 3: Trier et filtrer les résultats
    return filter_recommendations(scores)
```

### HTML/CSS/JavaScript

#### HTML

- **Indentation**: 2 espaces
- **Attributs**: Utiliser des doubles quotes `"`
- **Sémantique**: Utiliser les balises appropriées (`<nav>`, `<section>`, `<article>`)

```html
<!-- ✅ Bon -->
<section class="hero">
  <h1>Titre principal</h1>
  <p class="subtitle">Sous-titre descriptif</p>
</section>

<!-- ❌ Mauvais -->
<div class="hero">
  <div class="title">Titre principal</div>
</div>
```

#### CSS

- **BEM notation** pour les classes complexes
- **Variables CSS** pour les couleurs et valeurs réutilisables
- **Mobile-first** approach pour le responsive

```css
/* Variables */
:root {
  --primary-color: #6366f1;
  --surface: #1e293b;
}

/* BEM notation */
.series-card {}
.series-card__title {}
.series-card__rating {}
.series-card--featured {}

/* Responsive */
@media (max-width: 768px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
}
```

#### JavaScript

- **ES6+**: Utiliser les fonctionnalités modernes
- **Async/await**: Préférer à `.then()` pour les promises
- **Arrow functions**: Pour les callbacks courts

```javascript
// ✅ Bon - Async/await
async function loadSeries() {
  try {
    const data = await apiRequest('/api/series');
    displaySeries(data);
  } catch (error) {
    showError(error.message);
  }
}

// ✅ Bon - Arrow function
const filterSeries = (series) => {
  return series.filter(s => s.rating >= 4);
};

// ❌ Mauvais - Callback hell
apiRequest('/api/series').then((data) => {
  return processData(data);
}).then((processed) => {
  displaySeries(processed);
}).catch((error) => {
  showError(error);
});
```

---

## 🏷️ Conventions de nommage

### Python

| Type | Convention | Exemple |
|------|------------|---------|
| Variables | snake_case | `user_rating`, `total_score` |
| Fonctions | snake_case | `calculate_score()`, `get_user_data()` |
| Classes | PascalCase | `SeriesRecommender`, `DatabaseConnection` |
| Constantes | UPPER_SNAKE_CASE | `MAX_RESULTS`, `API_BASE_URL` |
| Fichiers | snake_case | `api_search_sqlite.py`, `db_helpers.py` |

### JavaScript

| Type | Convention | Exemple |
|------|------------|---------|
| Variables | camelCase | `userName`, `totalScore` |
| Fonctions | camelCase | `loadSeries()`, `displayResults()` |
| Classes | PascalCase | `ApiClient`, `SeriesCard` |
| Constantes | UPPER_SNAKE_CASE | `API_BASE_URL`, `MAX_RETRIES` |
| Fichiers | kebab-case ou camelCase | `app.js`, `api-client.js` |

### CSS

| Type | Convention | Exemple |
|------|------------|---------|
| Classes | kebab-case | `.series-card`, `.btn-primary` |
| IDs | kebab-case | `#search-input`, `#user-profile` |
| Variables | kebab-case | `--primary-color`, `--font-size-lg` |

---

## 📚 Documentation

### README

- Mettre à jour le README pour toute nouvelle fonctionnalité
- Inclure des exemples d'utilisation
- Ajouter des captures d'écran si pertinent

### Code comments

**Quand commenter:**
- Algorithmes complexes
- Décisions de design non évidentes
- Workarounds ou hacks temporaires
- Formules mathématiques

**Quand NE PAS commenter:**
- Code évident
- Répéter ce que le code fait déjà
- Commentaires obsolètes

```python
# ❌ Mauvais - évident
# Créer une liste
my_list = []

# ✅ Bon - explique le "pourquoi"
# Utiliser une liste au lieu d'un set pour préserver l'ordre d'insertion
# nécessaire pour l'affichage chronologique
my_list = []
```

### Docstrings

- **Toutes les fonctions publiques** doivent avoir une docstring
- Inclure Args, Returns, Raises
- Ajouter un exemple si la fonction est complexe

---

## 🧪 Tests

### Structure des tests

```
tests/
├── test_api/
│   ├── test_search.py
│   ├── test_recommend.py
│   └── test_ratings.py
├── test_algorithms/
│   ├── test_tfidf.py
│   └── test_collaborative.py
└── test_database/
    └── test_queries.py
```

### Écrire des tests

```python
import pytest
from api_recommend_sqlite import calculate_popularity_score

def test_popularity_score_with_votes():
    """Test du calcul de score avec des votes."""
    score = calculate_popularity_score(4.5, 100)
    assert score > 0
    assert isinstance(score, float)

def test_popularity_score_no_votes():
    """Test du calcul de score sans votes."""
    score = calculate_popularity_score(0, 0)
    assert score == 0

def test_popularity_score_invalid_rating():
    """Test avec une note invalide."""
    with pytest.raises(ValueError):
        calculate_popularity_score(6.0, 100)
```

### Lancer les tests

```powershell
# Tous les tests
pytest

# Tests spécifiques
pytest tests/test_api/test_search.py

# Avec couverture
pytest --cov=. --cov-report=html
```

---

## 🌿 Workflow Git

### Convention de nommage des branches

| Type | Format | Exemple |
|------|--------|---------|
| Feature | `feature/description` | `feature/add-user-profile` |
| Bugfix | `fix/description` | `fix/search-encoding-error` |
| Hotfix | `hotfix/description` | `hotfix/security-patch` |
| Refactor | `refactor/description` | `refactor/improve-api-structure` |
| Docs | `docs/description` | `docs/update-readme` |

### Messages de commit

Suivre la convention **Conventional Commits**:

```
<type>(<scope>): <description courte>

[corps optionnel du message]

[footer optionnel]
```

**Types:**
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation uniquement
- `style`: Changements de style (formatting, etc.)
- `refactor`: Refactorisation du code
- `perf`: Amélioration des performances
- `test`: Ajout ou modification de tests
- `chore`: Tâches de maintenance (build, deps, etc.)

**Exemples:**

```powershell
# Feature
git commit -m "feat(search): ajouter recherche par acteurs"

# Bugfix
git commit -m "fix(api): corriger l'encodage UTF-8 dans la recherche"

# Documentation
git commit -m "docs(readme): ajouter guide de déploiement Render"

# Refactor
git commit -m "refactor(recommend): extraire logique en fonctions helpers"

# Avec corps de message
git commit -m "feat(ratings): implémenter système d'étoiles

- Ajouter endpoint POST /api/ratings
- Créer interface de notation dans series-details.html
- Mettre à jour le calcul de note moyenne"
```

### Workflow de développement

```powershell
# 1. Récupérer les dernières modifications
git checkout main
git pull origin main

# 2. Créer une branche de travail
git checkout -b feature/ma-feature

# 3. Faire des commits réguliers
git add .
git commit -m "feat: première partie de la feature"
# ... travailler ...
git commit -m "feat: compléter la feature X"

# 4. Mettre à jour avec main avant de push
git checkout main
git pull origin main
git checkout feature/ma-feature
git rebase main

# 5. Pousser et créer une PR
git push origin feature/ma-feature
```

### Pull Requests

#### Checklist avant de soumettre

- [ ] Le code compile et fonctionne localement
- [ ] Tous les tests passent
- [ ] La documentation est à jour
- [ ] Les commentaires sont ajoutés pour le code complexe
- [ ] Le code suit les conventions du projet
- [ ] Pas de console.log() ou print() de debug
- [ ] Les dépendances sont à jour dans requirements.txt

#### Template de PR

```markdown
## Description
[Décrire les changements apportés]

## Type de changement
- [ ] Nouvelle fonctionnalité
- [ ] Correction de bug
- [ ] Refactorisation
- [ ] Documentation

## Tests effectués
- [ ] Tests locaux
- [ ] Tests sur navigateurs multiples
- [ ] Tests responsive

## Captures d'écran (si applicable)
[Ajouter des screenshots]

## Checklist
- [ ] Code compile sans erreurs
- [ ] Tests ajoutés/mis à jour
- [ ] Documentation mise à jour
- [ ] Pas de conflits avec main
```

---

## 🔍 Review Process

### Pour les reviewers

- Vérifier la logique du code
- Tester localement si possible
- Suggérer des améliorations
- Approuver ou demander des modifications

### Pour les contributeurs

- Répondre aux commentaires de review
- Faire les modifications demandées
- Re-push les changements
- Demander une nouvelle review si nécessaire

---

## 📞 Questions ?

- **Issues GitHub**: Pour signaler des bugs ou proposer des features
- **Discussions GitHub**: Pour poser des questions générales
- **Email**: Contacter l'équipe pour des questions privées

---

## 🙏 Remerciements

Merci d'avoir lu ce guide ! Vos contributions font la différence. 🚀

---

<div align="center">

**Happy Coding! 🎉**

[⬆ Retour en haut](#-guide-de-contribution---s5c01)

</div>

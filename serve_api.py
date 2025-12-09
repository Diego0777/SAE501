"""
Serveur API REST pour le moteur de recherche et recommandation de séries TV.

Architecture modulaire avec séparation des API :
    - api_search.py : Recherche par mots-clés
    - api_recommend.py : Recommandations (popularité, utilisateur, hybride)
    - api_series.py : Gestion des séries (liste, détails)
    - api_ratings.py : Gestion des notations utilisateur

Endpoints disponibles:
    - GET / : Documentation de l'API
    - GET /search : Recherche par mots-clés
    - GET /recommend/popular : Séries populaires
    - GET /recommend/user : Recommandations personnalisées
    - GET /recommend/hybrid : Recommandations hybrides
    - GET /series : Liste des séries
    - GET /series/<id> : Détails d'une série
    - POST /rate : Noter une série
    - GET /user/<id>/ratings : Notes d'un utilisateur
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import joblib

# Importer les blueprints des différentes API
from api_search import search_bp, init_search_engine
from api_recommend import recommend_bp
from api_series import series_bp, init_series_data
from api_ratings import ratings_bp, init_ratings_data
from api_users import users_bp

app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)

# Initialisation des modules
model_dir = './data/index'
meta_path = os.path.join(model_dir, 'meta.joblib')
meta = joblib.load(meta_path)
titles = meta['titles']

# Initialiser chaque module avec ses données
init_search_engine(model_dir)
init_series_data(model_dir)
init_ratings_data(titles)

# Enregistrer les blueprints
app.register_blueprint(search_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(series_bp)
app.register_blueprint(ratings_bp)
app.register_blueprint(users_bp)


# ============================================================================
# ENDPOINT D'ACCUEIL
# ============================================================================

@app.route('/')
def home():
    """Rediriger vers le site web."""
    return app.send_static_file('index.html')

@app.route('/api')
def index():
    """Documentation de l'API."""
    return jsonify({
        'name': 'TV Series Search & Recommendation API',
        'version': '1.0',
        'architecture': 'Modulaire - Code séparé par fonctionnalité',
        'modules': {
            'api_search.py': 'Recherche par mots-clés',
            'api_recommend.py': 'Recommandations (popularité, utilisateur, hybride)',
            'api_series.py': 'Gestion des séries (liste, détails)',
            'api_ratings.py': 'Gestion des notations utilisateur',
            'api_users.py': 'Gestion des utilisateurs (inscription, connexion, profil)'
        },
        'endpoints': {
            'search': '/search?q=keywords&top=10&language=vf',
            'popular': '/recommend/popular?top=10&language=vf',
            'user_recommendations': '/recommend/user?user_id=alice&top=10',
            'hybrid_recommendations': '/recommend/hybrid?user_id=alice&top=10',
            'series_list': '/series?language=vf',
            'series_details': '/series/<serie_id>',
            'rate_series': 'POST /rate (JSON: user_id, serie_id, rating)',
            'user_ratings': '/user/<user_id>/ratings',
            'register': 'POST /register (JSON: username, password, email)',
            'login': 'POST /login (JSON: username, password)',
            'logout': 'POST /logout (Header: Authorization: Bearer token)',
            'verify_token': '/verify (Header: Authorization: Bearer token)',
            'profile': '/profile (GET/PUT, Header: Authorization: Bearer token)',
            'list_users': '/users'
        }
    })


# ============================================================================
# LANCEMENT DU SERVEUR
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

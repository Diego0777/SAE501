"""
Serveur API Flask pour le système de recommandation de séries TV.

Ce module principal configure le serveur Flask avec tous les blueprints nécessaires
pour gérer les recherches, recommandations, séries, notations et utilisateurs.
Utilise SQLite comme base de données.

Routes principales:
    - / : Page d'accueil
    - /api : Documentation de l'API
    - /register, /login, /verify : Authentification simplifiée
    - /profile : Profil utilisateur
    - /rate : Notation de séries
    - /user/<id>/ratings : Notes d'un utilisateur
    - /posters/<name> : Images de posters
"""
from flask import Flask, send_from_directory, request, jsonify, Response
from flask_cors import CORS
from io import BytesIO

# Importer les blueprints SQLite pour chaque fonctionnalité
from api_search_sqlite import api_search_sqlite
from api_recommend_sqlite import api_recommend_sqlite
from api_series_sqlite import api_series_sqlite
from api_ratings_sqlite import api_ratings_sqlite
from api_users_sqlite import api_users_sqlite
from database.db_sqlite import get_connection

# Configuration de l'application Flask
app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)  # Activer CORS pour les requêtes cross-origin

# Enregistrer tous les blueprints de l'API
app.register_blueprint(api_search_sqlite)
app.register_blueprint(api_recommend_sqlite)
app.register_blueprint(api_series_sqlite)
app.register_blueprint(api_ratings_sqlite)
app.register_blueprint(api_users_sqlite)


# ============================================================================
# ROUTES PRINCIPALES
# ============================================================================

@app.route('/')
def index():
    """
    Servir la page d'accueil HTML.
    
    Returns:
        HTML: Page index.html du dossier web/
    """
    return app.send_static_file('index.html')


# ============================================================================
# HELPERS D'AUTHENTIFICATION
# ============================================================================

def verify_token(token):
    """
    Vérifier la validité d'un token de session.
    
    Args:
        token (str): Token de session à vérifier
        
    Returns:
        tuple: (user_id, error) où user_id est l'ID utilisateur si valide,
               None sinon. error contient un message d'erreur si applicable.
    """
    if not token:
        return None, "Token manquant"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM sessions WHERE token = ?", (token,))
        result = cursor.fetchone()
        
        if result:
            return result[0], None
        return None, "Token invalide"


def get_user_profile_data(user_id):
    """
    Récupérer les données complètes du profil d'un utilisateur.
    
    Args:
        user_id (int): ID de l'utilisateur
        
    Returns:
        dict: Dictionnaire contenant les informations du profil, ou None si non trouvé
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Récupérer les informations utilisateur
        cursor.execute(
            """SELECT id, username, email, language_preference, created_at
               FROM users WHERE id = ?""",
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            return None
        
        # Compter le nombre de notations
        cursor.execute("SELECT COUNT(*) FROM ratings WHERE user_id = ?", (user_id,))
        num_ratings = cursor.fetchone()[0]
        
        return {
            'id': user[0],
            'user_id': user[0],
            'username': user[1],
            'email': user[2],
            'language_preference': user[3],
            'created_at': user[4],
            'num_ratings': num_ratings
        }


# ============================================================================
# ENDPOINTS D'AUTHENTIFICATION SIMPLIFIÉS
# ============================================================================
# ============================================================================
# ENDPOINTS D'AUTHENTIFICATION SIMPLIFIÉS
# ============================================================================

@app.route('/register', methods=['POST'])
def register_simple():
    """
    Créer un nouveau compte utilisateur (alias simplifié).
    
    Cette route est un alias pour /api/users/register, permettant un accès
    plus direct depuis le frontend.
    
    Returns:
        JSON: Résultat de la création du compte
    """
    from api_users_sqlite import register
    return register()


@app.route('/login', methods=['POST'])
def login_simple():
    """
    Authentifier un utilisateur (alias simplifié).
    
    Cette route est un alias pour /api/users/login, permettant un accès
    plus direct depuis le frontend.
    
    Returns:
        JSON: Token de session si authentification réussie
    """
    from api_users_sqlite import login
    return login()


@app.route('/verify', methods=['GET'])
def verify_simple():
    """
    Vérifier la validité d'un token de session.
    
    Headers requis:
        Authorization (str): Token de session
    
    Returns:
        JSON: {'success': True} si token valide, erreur 401 sinon
    """
    token = request.headers.get('Authorization')
    user_id, error = verify_token(token)
    
    if user_id:
        return {'success': True}
    
    return {'error': error}, 401


@app.route('/profile', methods=['GET'])
def profile_simple():
    """
    Obtenir le profil complet de l'utilisateur connecté.
    
    Headers requis:
        Authorization (str): Token de session
    
    Returns:
        JSON: Profil utilisateur avec statistiques, ou erreur 401
    """
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({'error': 'Non authentifié'}), 401
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT u.id FROM users u
               JOIN sessions s ON u.id = s.user_id
               WHERE s.token = ?""",
            (token,)
        )
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'Session invalide'}), 401
        
        user_data = get_user_profile_data(result[0])
        if not user_data:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        return jsonify(user_data)


@app.route('/rate', methods=['POST'])
def rate_simple():
    """
    Noter une série (alias simplifié pour /api/ratings).
    
    Body JSON:
        serie_id (str): ID de la série
        rating (int): Note de 1 à 5
    
    Returns:
        JSON: Confirmation de la notation
    """
    from api_ratings_sqlite import add_rating
    return add_rating()


# ============================================================================
# GESTION DES NOTATIONS UTILISATEUR
# ============================================================================# ============================================================================
# GESTION DES NOTATIONS UTILISATEUR
# ============================================================================

@app.route('/user/<int:user_id>/ratings', methods=['GET'])
def user_ratings_simple(user_id):
    """
    Récupérer toutes les notations d'un utilisateur.
    
    Args:
        user_id (int): ID de l'utilisateur
    
    Returns:
        JSON: Liste des notations avec détails des séries
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT s.title, r.rating, r.created_at
               FROM ratings r
               JOIN series s ON r.serie_id = s.id
               WHERE r.user_id = ?
               ORDER BY r.created_at DESC""",
            (user_id,)
        )
        ratings = cursor.fetchall()
    
    return jsonify({
        'total': len(ratings),
        'ratings': [{
            'serie_id': r[0],
            'rating': r[1],
            'created_at': r[2]
        } for r in ratings]
    })


# ============================================================================
# GESTION DES POSTERS
# ============================================================================

def find_poster_in_db(series_name):
    """
    Chercher un poster dans la base de données.
    
    Essaye plusieurs stratégies de recherche:
    1. Correspondance exacte du titre
    2. Recherche par nom de base (sans _vf/_vo)
    
    Args:
        series_name (str): Nom de la série (peut contenir .jpg, .png, etc.)
        
    Returns:
        bytes: Données binaires du poster, ou None si non trouvé
    """
    # Nettoyer le nom (enlever les extensions)
    base_name = series_name.replace('.jpg', '').replace('.png', '').replace('.webp', '')
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Stratégie 1: Recherche exacte
        cursor.execute(
            "SELECT poster_data FROM series WHERE title = ? AND poster_data IS NOT NULL",
            (base_name,)
        )
        result = cursor.fetchone()
        
        if result and result[0]:
            return result[0]
        
        # Stratégie 2: Recherche par nom de base (sans suffixe VF/VO)
        clean_name = base_name.replace('_vf', '').replace('_vo', '')
        cursor.execute(
            """SELECT poster_data FROM series 
               WHERE (title LIKE ? OR title LIKE ?) 
               AND poster_data IS NOT NULL 
               LIMIT 1""",
            (f"{clean_name}_vf", f"{clean_name}_vo")
        )
        result = cursor.fetchone()
        
        if result and result[0]:
            return result[0]
    
    return None


@app.route('/posters/<series_name>')
def get_poster(series_name):
    """
    Servir une image de poster depuis la base de données.
    
    Les posters sont stockés en BLOB dans SQLite pour éviter la gestion
    de fichiers sur le système de fichiers.
    
    Args:
        series_name (str): Nom de la série (avec ou sans extension)
    
    Returns:
        Response: Image JPEG, ou erreur 404 si non trouvée
    """
    poster_data = find_poster_in_db(series_name)
    
    if poster_data:
        return Response(poster_data, mimetype='image/jpeg')
    
    # Retourner 404 si aucun poster trouvé
    return Response(status=404)


# ============================================================================
# DOCUMENTATION API
# ============================================================================# ============================================================================
# DOCUMENTATION API
# ============================================================================

@app.route('/api')
def api_doc():
    """
    Documentation complète de l'API REST.
    
    Fournit une vue d'ensemble de tous les endpoints disponibles organisés
    par catégorie (recherche, séries, recommandations, notations, utilisateurs).
    
    Returns:
        JSON: Documentation structurée de l'API
    """
    return {
        'name': 'TV Series API - SQLite',
        'version': '2.0',
        'database': 'SQLite',
        'description': 'API REST pour recherche et recommandation de séries TV',
        'endpoints': {
            'search': {
                'GET /api/search': 'Rechercher des séries (TF-IDF + keywords)',
                'GET /api/search/keyword': 'Rechercher par mot-clé uniquement',
                'POST /api/search/advanced': 'Recherche avancée avec filtres'
            },
            'series': {
                'GET /api/series': 'Liste de toutes les séries',
                'GET /api/series/<title>': 'Détails d\'une série',
                'GET /api/series/<title>/keywords': 'Mots-clés d\'une série',
                'GET /api/series/popular': 'Séries populaires',
                'GET /api/series/top_rated': 'Séries les mieux notées',
                'GET /api/series/stats': 'Statistiques générales'
            },
            'recommendations': {
                'GET /api/recommend/popularity': 'Recommandations par popularité',
                'GET /api/recommend/collaborative/<user_id>': 'Filtrage collaboratif',
                'GET /api/recommend/hybrid/<user_id>': 'Recommandations hybrides',
                'GET /api/recommend/similar/<title>': 'Séries similaires'
            },
            'ratings': {
                'GET /api/ratings': 'Toutes les notes (filtrable par user_id)',
                'GET /api/ratings/<title>': 'Notes d\'une série',
                'POST /api/ratings': 'Ajouter/modifier une note',
                'DELETE /api/ratings/<id>': 'Supprimer une note',
                'GET /api/ratings/user/<user_id>/series/<title>': 'Note d\'un utilisateur'
            },
            'users': {
                'POST /api/users/register': 'Créer un compte',
                'POST /api/users/login': 'Se connecter',
                'POST /api/users/logout': 'Se déconnecter',
                'GET /api/users/profile': 'Profil (avec token)',
                'GET /api/users/<user_id>': 'Info utilisateur',
                'GET /api/users': 'Liste des utilisateurs'
            }
        }
    }


# ============================================================================
# POINT D'ENTRÉE DE L'APPLICATION
# ============================================================================

def print_startup_banner(port):
    """
    Afficher une bannière d'information au démarrage du serveur.
    
    Args:
        port (int): Port d'écoute du serveur
    """
    print("=" * 60)
    print("Serveur API TV Series - Version SQLite")
    print("=" * 60)
    print("Base de données : SQLite (data/tvseries.db)")
    print(f"URL : http://127.0.0.1:{port}")
    print(f"Documentation : http://127.0.0.1:{port}/api")
    print("=" * 60)
    print()


if __name__ == '__main__':
    import os
    
    # Récupérer le port depuis les variables d'environnement (Render, Heroku, etc.)
    # ou utiliser 5000 par défaut
    port = int(os.environ.get('PORT', 5000))
    
    # Afficher les informations de démarrage
    print_startup_banner(port)
    
    # Lancer le serveur Flask
    # debug=True : Mode développement avec rechargement automatique
    # host='0.0.0.0' : Accepter les connexions de toutes les interfaces réseau
    app.run(debug=True, host='0.0.0.0', port=port)

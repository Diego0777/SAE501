"""
Serveur API Flask avec base de données SQLite
"""
from flask import Flask, send_from_directory
from flask_cors import CORS

# Importer les blueprints SQLite
from api_search_sqlite import api_search_sqlite
from api_recommend_sqlite import api_recommend_sqlite
from api_series_sqlite import api_series_sqlite
from api_ratings_sqlite import api_ratings_sqlite
from api_users_sqlite import api_users_sqlite

app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)

# Enregistrer les blueprints
app.register_blueprint(api_search_sqlite)
app.register_blueprint(api_recommend_sqlite)
app.register_blueprint(api_series_sqlite)
app.register_blueprint(api_ratings_sqlite)
app.register_blueprint(api_users_sqlite)

@app.route('/')
def index():
    """Page d'accueil."""
    return app.send_static_file('index.html')

# Endpoint simplifié pour profile.html
@app.route('/register', methods=['POST'])
def register_simple():
    """Créer un compte (alias pour /api/users/register)."""
    from api_users_sqlite import register
    return register()

@app.route('/login', methods=['POST'])
def login_simple():
    """Se connecter (alias pour /api/users/login)."""
    from api_users_sqlite import login
    return login()

@app.route('/verify', methods=['GET'])
def verify_simple():
    """Vérifier le token."""
    from flask import request
    token = request.headers.get('Authorization')
    if not token:
        return {'error': 'Non authentifié'}, 401
    
    from database.db_sqlite import get_connection
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM sessions WHERE token = ?", (token,))
        if cursor.fetchone():
            return {'success': True}
    return {'error': 'Token invalide'}, 401

@app.route('/profile', methods=['GET'])
def profile_simple():
    """Obtenir le profil (alias pour /api/users/profile)."""
    from flask import request, jsonify
    from database.db_sqlite import get_connection
    
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Non authentifié'}), 401
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT u.id, u.username, u.email, u.language_preference, u.created_at
               FROM users u
               JOIN sessions s ON u.id = s.user_id
               WHERE s.token = ?""",
            (token,)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'Session invalide'}), 401
        
        cursor.execute("SELECT COUNT(*) FROM ratings WHERE user_id = ?", (user[0],))
        num_ratings = cursor.fetchone()[0]
    
    return jsonify({
        'id': user[0],
        'user_id': user[0],
        'username': user[1],
        'email': user[2],
        'language_preference': user[3],
        'created_at': user[4],
        'num_ratings': num_ratings
    })

@app.route('/rate', methods=['POST'])
def rate_simple():
    """Noter une série (alias simplifié pour /api/ratings)."""
    from api_ratings_sqlite import add_rating
    return add_rating()

@app.route('/user/<int:user_id>/ratings', methods=['GET'])
def user_ratings_simple(user_id):
    """Obtenir les notes d'un utilisateur."""
    from database.db_sqlite import get_connection
    from flask import jsonify
    
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

@app.route('/posters/<series_name>')
def get_poster(series_name):
    """Servir une image de poster depuis la BD."""
    from flask import send_file, Response
    from io import BytesIO
    from database.db_sqlite import get_connection
    
    # Extraire le nom de base (sans extension)
    base_name = series_name.replace('.jpg', '').replace('.png', '').replace('.webp', '')
    
    with get_connection() as conn:
        cursor = conn.cursor()
        # Chercher d'abord par titre exact
        cursor.execute("SELECT poster_data FROM series WHERE title = ? AND poster_data IS NOT NULL", (base_name,))
        result = cursor.fetchone()
        
        if not result:
            # Chercher par nom de base (sans _vf/_vo)
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
        return Response(result[0], mimetype='image/jpeg')
    
    # Image par défaut si non trouvée
    return Response(status=404)

@app.route('/api')
def api_doc():
    """Documentation de l'API."""
    return {
        'name': 'TV Series API - SQLite',
        'version': '2.0',
        'database': 'SQLite',
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
                'GET /api/recommend/popularity': 'Recommandations populaires',
                'GET /api/recommend/collaborative/<user_id>': 'Recommandations collaboratives',
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

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("🚀 Serveur API TV Series - Version SQLite")
    print("=" * 60)
    print("📊 Base de données : SQLite (data/tvseries.db)")
    print(f"🌐 URL : http://0.0.0.0:{port}")
    print("📖 Documentation : http://127.0.0.1:5000/api")
    print("=" * 60)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=port)

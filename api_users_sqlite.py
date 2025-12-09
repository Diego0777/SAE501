"""
API SQLite pour la gestion des utilisateurs
"""
from flask import Blueprint, request, jsonify
import hashlib
import secrets
from datetime import datetime
from database.db_sqlite import get_connection

api_users_sqlite = Blueprint('api_users_sqlite', __name__)

def hash_password(password):
    """Hasher un mot de passe avec SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    """Générer un token de session."""
    return secrets.token_urlsafe(32)

@api_users_sqlite.route('/api/users/register', methods=['POST'])
def register():
    """Enregistrer un nouvel utilisateur."""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    language_preference = data.get('language_preference', 'vf')
    
    if not username or not password:
        return jsonify({'error': 'Username et password requis'}), 400
    
    password_hash = hash_password(password)
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, email, language_preference) VALUES (?, ?, ?, ?)",
                (username, password_hash, email, language_preference)
            )
            user_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'username': username,
            'message': 'Utilisateur créé avec succès'
        }), 201
    
    except Exception as e:
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'Nom d\'utilisateur déjà utilisé'}), 400
        return jsonify({'error': str(e)}), 500

@api_users_sqlite.route('/api/users/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur."""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username et password requis'}), 400
    
    password_hash = hash_password(password)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, language_preference FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'Identifiants invalides'}), 401
        
        # Créer une session (expire dans 30 jours)
        from datetime import datetime, timedelta
        token = generate_token()
        expires_at = (datetime.now() + timedelta(days=30)).isoformat()
        cursor.execute(
            "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user[0], token, expires_at)
        )
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'id': user[0],
            'username': user[1],
            'language_preference': user[2]
        }
    })

@api_users_sqlite.route('/api/users/logout', methods=['POST'])
def logout():
    """Déconnexion d'un utilisateur."""
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'Token requis'}), 400
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
    
    return jsonify({'success': True, 'message': 'Déconnexion réussie'})

@api_users_sqlite.route('/api/users/profile', methods=['GET'])
def get_profile():
    """Obtenir le profil d'un utilisateur."""
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({'error': 'Token requis'}), 401
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Vérifier la session
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
        
        # Compter les notes
        cursor.execute("SELECT COUNT(*) FROM ratings WHERE user_id = ?", (user[0],))
        num_ratings = cursor.fetchone()[0]
    
    return jsonify({
        'id': user[0],
        'username': user[1],
        'email': user[2],
        'language_preference': user[3],
        'created_at': user[4],
        'num_ratings': num_ratings
    })

@api_users_sqlite.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obtenir les informations d'un utilisateur."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, language_preference, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Compter les notes
        cursor.execute("SELECT COUNT(*) FROM ratings WHERE user_id = ?", (user_id,))
        num_ratings = cursor.fetchone()[0]
    
    return jsonify({
        'id': user[0],
        'username': user[1],
        'language_preference': user[2],
        'created_at': user[3],
        'num_ratings': num_ratings
    })

@api_users_sqlite.route('/api/users', methods=['GET'])
def list_users():
    """Lister tous les utilisateurs."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT u.id, u.username, u.language_preference, u.created_at,
                      COUNT(r.id) as num_ratings
               FROM users u
               LEFT JOIN ratings r ON u.id = r.user_id
               GROUP BY u.id
               ORDER BY u.created_at DESC"""
        )
        users = cursor.fetchall()
    
    return jsonify([{
        'id': user[0],
        'username': user[1],
        'language_preference': user[2],
        'created_at': user[3],
        'num_ratings': user[4]
    } for user in users])

"""
API de gestion des utilisateurs avec MySQL
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import hashlib
import secrets
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db import execute_query

users_bp = Blueprint('users', __name__)

def hash_password(password):
    """Hasher un mot de passe."""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    """Générer un token de session."""
    return secrets.token_urlsafe(32)

@users_bp.route('/register', methods=['POST'])
def register():
    """Créer un nouveau compte utilisateur."""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    username = data['username'].lower().strip()
    password = data['password']
    email = data.get('email', '')
    
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    
    if len(password) < 4:
        return jsonify({'error': 'Password must be at least 4 characters'}), 400
    
    # Vérifier si l'utilisateur existe
    existing = execute_query(
        "SELECT id FROM users WHERE username = %s",
        (username,),
        fetchone=True
    )
    
    if existing:
        return jsonify({'error': 'Username already exists'}), 409
    
    # Créer l'utilisateur
    user_id = execute_query(
        "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
        (username, hash_password(password), email),
        commit=True
    )
    
    return jsonify({
        'success': True,
        'message': f'User {username} created successfully',
        'user_id': username
    }), 201

@users_bp.route('/login', methods=['POST'])
def login():
    """Se connecter et obtenir un token de session."""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    username = data['username'].lower().strip()
    password = data['password']
    
    # Vérifier les credentials
    user = execute_query(
        "SELECT id, username, password_hash FROM users WHERE username = %s",
        (username,),
        fetchone=True
    )
    
    if not user or user['password_hash'] != hash_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Créer une session
    token = generate_token()
    expires_at = datetime.now() + timedelta(days=7)
    
    execute_query(
        "INSERT INTO sessions (token, user_id, expires_at) VALUES (%s, %s, %s)",
        (token, user['id'], expires_at),
        commit=True
    )
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'token': token,
        'user_id': user['username']
    })

@users_bp.route('/logout', methods=['POST'])
def logout():
    """Se déconnecter (invalider le token)."""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header[7:]
    
    execute_query(
        "DELETE FROM sessions WHERE token = %s",
        (token,),
        commit=True
    )
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

@users_bp.route('/verify', methods=['GET'])
def verify():
    """Vérifier si un token est valide."""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header[7:]
    
    session = execute_query(
        """SELECT s.token, s.user_id, s.expires_at, u.username
           FROM sessions s
           JOIN users u ON s.user_id = u.id
           WHERE s.token = %s""",
        (token,),
        fetchone=True
    )
    
    if not session:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    # Vérifier l'expiration
    if datetime.now() > session['expires_at']:
        execute_query("DELETE FROM sessions WHERE token = %s", (token,), commit=True)
        return jsonify({'error': 'Token expired'}), 401
    
    return jsonify({
        'valid': True,
        'user_id': session['username'],
        'expires_at': session['expires_at'].isoformat()
    })

@users_bp.route('/profile', methods=['GET'])
def get_profile():
    """Obtenir le profil de l'utilisateur connecté."""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header[7:]
    
    result = execute_query(
        """SELECT u.username, u.email, u.language_preference, u.created_at
           FROM sessions s
           JOIN users u ON s.user_id = u.id
           WHERE s.token = %s AND s.expires_at > NOW()""",
        (token,),
        fetchone=True
    )
    
    if not result:
        return jsonify({'error': 'Invalid token'}), 401
    
    return jsonify({
        'user_id': result['username'],
        'email': result['email'] or '',
        'created_at': result['created_at'].isoformat(),
        'preferences': {
            'language': result['language_preference']
        }
    })

@users_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Mettre à jour le profil utilisateur."""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header[7:]
    data = request.get_json()
    
    # Récupérer l'utilisateur
    session = execute_query(
        """SELECT user_id FROM sessions 
           WHERE token = %s AND expires_at > NOW()""",
        (token,),
        fetchone=True
    )
    
    if not session:
        return jsonify({'error': 'Invalid token'}), 401
    
    user_id = session['user_id']
    
    # Mettre à jour les champs
    if 'email' in data:
        execute_query(
            "UPDATE users SET email = %s WHERE id = %s",
            (data['email'], user_id),
            commit=True
        )
    
    if 'preferences' in data and 'language' in data['preferences']:
        lang = data['preferences']['language']
        if lang in ['vf', 'vo']:
            execute_query(
                "UPDATE users SET language_preference = %s WHERE id = %s",
                (lang, user_id),
                commit=True
            )
    
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully'
    })

@users_bp.route('/users', methods=['GET'])
def list_users():
    """Liste tous les utilisateurs."""
    users = execute_query(
        "SELECT username, email, created_at FROM users ORDER BY username",
        fetchall=True
    )
    
    user_list = [{
        'user_id': u['username'],
        'email': u['email'] or '',
        'created_at': u['created_at'].isoformat()
    } for u in users]
    
    return jsonify({
        'total': len(user_list),
        'users': user_list
    })

"""
API de gestion des utilisateurs
"""
from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime, timedelta
import hashlib
import secrets

users_bp = Blueprint('users', __name__)

# Fichiers de données
USERS_FILE = './data/users.json'
SESSIONS_FILE = './data/sessions.json'

def load_users():
    """Charger les utilisateurs depuis le fichier JSON."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Sauvegarder les utilisateurs dans le fichier JSON."""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def load_sessions():
    """Charger les sessions depuis le fichier JSON."""
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_sessions(sessions):
    """Sauvegarder les sessions dans le fichier JSON."""
    os.makedirs(os.path.dirname(SESSIONS_FILE), exist_ok=True)
    with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, indent=2, ensure_ascii=False)

def hash_password(password):
    """Hasher un mot de passe."""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    """Générer un token de session."""
    return secrets.token_urlsafe(32)


@users_bp.route('/register', methods=['POST'])
def register():
    """
    Créer un nouveau compte utilisateur.
    
    Body (JSON):
        {
            "username": "alice",
            "password": "motdepasse123",
            "email": "alice@example.com"
        }
    
    Returns:
        JSON: Confirmation de création
    """
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    username = data['username'].lower().strip()
    password = data['password']
    email = data.get('email', '')
    
    # Validation
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    
    if len(password) < 4:
        return jsonify({'error': 'Password must be at least 4 characters'}), 400
    
    # Charger les utilisateurs existants
    users = load_users()
    
    if username in users:
        return jsonify({'error': 'Username already exists'}), 409
    
    # Créer l'utilisateur
    users[username] = {
        'password_hash': hash_password(password),
        'email': email,
        'created_at': datetime.now().isoformat(),
        'preferences': {
            'language': 'vf'
        }
    }
    
    save_users(users)
    
    return jsonify({
        'success': True,
        'message': f'User {username} created successfully',
        'user_id': username
    }), 201


@users_bp.route('/login', methods=['POST'])
def login():
    """
    Se connecter et obtenir un token de session.
    
    Body (JSON):
        {
            "username": "alice",
            "password": "motdepasse123"
        }
    
    Returns:
        JSON: Token de session
    """
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    username = data['username'].lower().strip()
    password = data['password']
    
    users = load_users()
    
    if username not in users:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Vérifier le mot de passe
    if users[username]['password_hash'] != hash_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Créer une session
    token = generate_token()
    sessions = load_sessions()
    
    sessions[token] = {
        'user_id': username,
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    save_sessions(sessions)
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'token': token,
        'user_id': username
    })


@users_bp.route('/logout', methods=['POST'])
def logout():
    """
    Se déconnecter (invalider le token).
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        JSON: Confirmation
    """
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header[7:]
    sessions = load_sessions()
    
    if token in sessions:
        del sessions[token]
        save_sessions(sessions)
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })


@users_bp.route('/verify', methods=['GET'])
def verify():
    """
    Vérifier si un token est valide.
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        JSON: Informations utilisateur si valide
    """
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header[7:]
    sessions = load_sessions()
    
    if token not in sessions:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    session = sessions[token]
    
    # Vérifier l'expiration
    expires_at = datetime.fromisoformat(session['expires_at'])
    if datetime.now() > expires_at:
        del sessions[token]
        save_sessions(sessions)
        return jsonify({'error': 'Token expired'}), 401
    
    return jsonify({
        'valid': True,
        'user_id': session['user_id'],
        'expires_at': session['expires_at']
    })


@users_bp.route('/profile', methods=['GET'])
def get_profile():
    """
    Obtenir le profil de l'utilisateur connecté.
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        JSON: Profil utilisateur
    """
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header[7:]
    sessions = load_sessions()
    
    if token not in sessions:
        return jsonify({'error': 'Invalid token'}), 401
    
    user_id = sessions[token]['user_id']
    users = load_users()
    
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user = users[user_id]
    
    return jsonify({
        'user_id': user_id,
        'email': user.get('email', ''),
        'created_at': user.get('created_at', ''),
        'preferences': user.get('preferences', {})
    })


@users_bp.route('/profile', methods=['PUT'])
def update_profile():
    """
    Mettre à jour le profil utilisateur.
    
    Headers:
        Authorization: Bearer <token>
    
    Body (JSON):
        {
            "email": "newemail@example.com",
            "preferences": {"language": "vo"}
        }
    
    Returns:
        JSON: Confirmation
    """
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header[7:]
    sessions = load_sessions()
    
    if token not in sessions:
        return jsonify({'error': 'Invalid token'}), 401
    
    user_id = sessions[token]['user_id']
    users = load_users()
    
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'email' in data:
        users[user_id]['email'] = data['email']
    
    if 'preferences' in data:
        if 'preferences' not in users[user_id]:
            users[user_id]['preferences'] = {}
        users[user_id]['preferences'].update(data['preferences'])
    
    save_users(users)
    
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully'
    })


@users_bp.route('/users', methods=['GET'])
def list_users():
    """
    Liste tous les utilisateurs (pour admin/debug).
    
    Returns:
        JSON: Liste des utilisateurs (sans mots de passe)
    """
    users = load_users()
    
    user_list = []
    for username, data in users.items():
        user_list.append({
            'user_id': username,
            'email': data.get('email', ''),
            'created_at': data.get('created_at', '')
        })
    
    return jsonify({
        'total': len(user_list),
        'users': user_list
    })

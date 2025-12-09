"""
API de notation avec MySQL
"""
from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db import execute_query

ratings_bp = Blueprint('ratings', __name__)

def init_ratings_data(titles):
    """Initialisation (pour compatibilité)."""
    pass

@ratings_bp.route('/rate', methods=['POST'])
def rate_series():
    """Noter une série."""
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'serie_id' not in data or 'rating' not in data:
        return jsonify({'error': 'Missing required fields: user_id, serie_id, rating'}), 400
    
    user_id_str = data['user_id']
    serie_title = data['serie_id']
    rating = data['rating']
    
    # Validation
    if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Récupérer ou créer l'utilisateur
    user = execute_query(
        "SELECT id FROM users WHERE username = %s",
        (user_id_str,),
        fetchone=True
    )
    
    if not user:
        # Créer un utilisateur temporaire
        user_id = execute_query(
            "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
            (user_id_str, 'a' * 64, f'{user_id_str}@temp.com'),
            commit=True
        )
    else:
        user_id = user['id']
    
    # Récupérer la série
    serie = execute_query(
        "SELECT id FROM series WHERE title = %s",
        (serie_title,),
        fetchone=True
    )
    
    if not serie:
        return jsonify({'error': 'Serie not found'}), 404
    
    serie_id = serie['id']
    
    # Ajouter/modifier la note
    execute_query(
        """INSERT INTO ratings (user_id, serie_id, rating) 
           VALUES (%s, %s, %s)
           ON DUPLICATE KEY UPDATE rating = %s, updated_at = NOW()""",
        (user_id, serie_id, rating, rating),
        commit=True
    )
    
    # Mettre à jour les statistiques de la série
    execute_query(
        """UPDATE series s
           SET average_rating = (SELECT AVG(rating) FROM ratings WHERE serie_id = s.id),
               num_ratings = (SELECT COUNT(*) FROM ratings WHERE serie_id = s.id),
               popularity_score = (SELECT AVG(rating) * LOG(1 + COUNT(*)) FROM ratings WHERE serie_id = s.id)
           WHERE s.id = %s""",
        (serie_id,),
        commit=True
    )
    
    return jsonify({
        'success': True,
        'message': f'Rating saved: {user_id_str} rated {serie_title} with {rating} stars'
    })

@ratings_bp.route('/user/<user_id>/ratings')
def get_user_ratings(user_id):
    """Récupérer toutes les notes d'un utilisateur."""
    # Récupérer l'utilisateur
    user = execute_query(
        "SELECT id FROM users WHERE username = %s",
        (user_id,),
        fetchone=True
    )
    
    if not user:
        return jsonify({'user_id': user_id, 'ratings': [], 'total': 0})
    
    # Récupérer les notations
    ratings = execute_query(
        """SELECT s.title as serie_id, r.rating, r.created_at
           FROM ratings r
           JOIN series s ON r.serie_id = s.id
           WHERE r.user_id = %s
           ORDER BY r.created_at DESC""",
        (user['id'],),
        fetchall=True
    )
    
    user_ratings = [{
        'serie_id': r['serie_id'],
        'rating': r['rating']
    } for r in ratings]
    
    return jsonify({
        'user_id': user_id,
        'ratings': user_ratings,
        'total': len(user_ratings)
    })

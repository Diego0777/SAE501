"""
API de gestion des notations utilisateur.
Permet de noter des séries et consulter les notes.
"""

from flask import Blueprint, request, jsonify
import os
import json

ratings_bp = Blueprint('ratings', __name__)

# Fichier des notations
ratings_file = './data/ratings.json'

# Variable pour stocker les titres valides (sera initialisée)
valid_titles = None


def init_ratings_data(titles_list):
    """Initialise les données de notation."""
    global valid_titles
    valid_titles = titles_list


@ratings_bp.route('/rate', methods=['POST'])
def rate_series():
    """
    Noter une série.
    
    Body (JSON):
        {
            "user_id": "alice",
            "serie_id": "lost_vf",
            "rating": 5
        }
    
    Returns:
        JSON: Confirmation
    """
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'serie_id' not in data or 'rating' not in data:
        return jsonify({'error': 'Missing required fields: user_id, serie_id, rating'}), 400
    
    user_id = data['user_id']
    serie_id = data['serie_id']
    rating = data['rating']
    
    # Validation
    if valid_titles and serie_id not in valid_titles:
        return jsonify({'error': 'Serie not found'}), 404
    
    if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Charger les notes existantes
    if os.path.exists(ratings_file):
        with open(ratings_file, 'r', encoding='utf-8') as f:
            ratings = json.load(f)
    else:
        ratings = {}
    
    # Ajouter/modifier la note
    if user_id not in ratings:
        ratings[user_id] = {}
    
    ratings[user_id][serie_id] = rating
    
    # Sauvegarder
    with open(ratings_file, 'w', encoding='utf-8') as f:
        json.dump(ratings, f, indent=2, ensure_ascii=False)
    
    return jsonify({
        'success': True,
        'message': f'Rating saved: {user_id} rated {serie_id} with {rating} stars'
    })


@ratings_bp.route('/user/<user_id>/ratings')
def get_user_ratings(user_id):
    """
    Récupérer toutes les notes d'un utilisateur.
    
    Returns:
        JSON: Notes de l'utilisateur
    """
    if not os.path.exists(ratings_file):
        return jsonify({'user_id': user_id, 'ratings': []})
    
    with open(ratings_file, 'r', encoding='utf-8') as f:
        ratings = json.load(f)
    
    if user_id not in ratings:
        return jsonify({'user_id': user_id, 'ratings': []})
    
    user_ratings = [
        {'serie_id': serie, 'rating': rating}
        for serie, rating in ratings[user_id].items()
    ]
    
    return jsonify({
        'user_id': user_id,
        'ratings': user_ratings,
        'total': len(user_ratings)
    })

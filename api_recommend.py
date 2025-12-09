"""
API de recommandation de séries.
Trois types de recommandations : popularité, utilisateur, hybride.
"""

from flask import Blueprint, request, jsonify
import os
import sys

# Importer les fonctions du module recommend
sys.path.insert(0, os.path.dirname(__file__))
from recommend import (
    popularity_based_recommend,
    user_based_recommend,
    hybrid_recommend
)

recommend_bp = Blueprint('recommend', __name__)

# Fichier des notations
ratings_file = './data/ratings.json'


@recommend_bp.route('/recommend/popular')
def recommend_popular():
    """
    Recommandations basées sur la popularité (séries les mieux notées).
    
    Query params:
        top (int): Nombre de résultats (défaut: 10)
        language (str): Filtrer par langue 'vf' ou 'vo' (optionnel)
    
    Returns:
        JSON: Liste de séries populaires avec statistiques
    """
    top = int(request.args.get('top', '10'))
    language = request.args.get('language', '').lower()
    
    if language and language not in ['vf', 'vo']:
        language = None
    
    try:
        recs = popularity_based_recommend(
            ratings_file=ratings_file,
            topn=top,
            language=language
        )
        
        results = [{
            'title': series,
            'popularity_score': float(pop_score),
            'average_rating': float(avg_rating),
            'num_ratings': int(num_ratings)
        } for series, pop_score, avg_rating, num_ratings in recs]
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommend_bp.route('/recommend/user')
def recommend_user():
    """
    Recommandations personnalisées basées sur les utilisateurs similaires.
    
    Query params:
        user_id (str): Identifiant de l'utilisateur
        top (int): Nombre de résultats (défaut: 10)
    
    Returns:
        JSON: Liste de séries recommandées
    """
    user_id = request.args.get('user_id', '')
    top = int(request.args.get('top', '10'))
    
    if not user_id:
        return jsonify({'error': 'Parameter "user_id" is required'}), 400
    
    try:
        recs = user_based_recommend(
            user_id=user_id,
            ratings_file=ratings_file,
            topn=top
        )
        
        results = [{
            'title': series,
            'score': float(score)
        } for series, score in recs]
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommend_bp.route('/recommend/hybrid')
def recommend_hybrid():
    """
    Recommandations hybrides (préférences utilisateur + popularité).
    
    Query params:
        user_id (str): Identifiant de l'utilisateur
        top (int): Nombre de résultats (défaut: 10)
    
    Returns:
        JSON: Liste de séries recommandées
    """
    user_id = request.args.get('user_id', '')
    top = int(request.args.get('top', '10'))
    
    if not user_id:
        return jsonify({'error': 'Parameter "user_id" is required'}), 400
    
    try:
        recs = hybrid_recommend(
            user_id=user_id,
            ratings_file=ratings_file,
            topn=top
        )
        
        results = [{
            'title': series,
            'score': float(score)
        } for series, score in recs]
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

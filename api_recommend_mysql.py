"""
API de recommandation avec MySQL
"""
from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db import execute_query

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/recommend/popular')
def recommend_popular():
    """Recommandations basées sur la popularité."""
    top = int(request.args.get('top', '10'))
    language = request.args.get('language', '').lower()
    
    if language and language not in ['vf', 'vo']:
        language = ''
    
    # Requête
    if language:
        series = execute_query(
            """SELECT title, popularity_score, average_rating, num_ratings
               FROM series
               WHERE language = %s AND num_ratings > 0
               ORDER BY popularity_score DESC
               LIMIT %s""",
            (language, top),
            fetchall=True
        )
    else:
        series = execute_query(
            """SELECT title, popularity_score, average_rating, num_ratings
               FROM series
               WHERE num_ratings > 0
               ORDER BY popularity_score DESC
               LIMIT %s""",
            (top,),
            fetchall=True
        )
    
    results = [{
        'title': s['title'],
        'popularity_score': float(s['popularity_score']),
        'average_rating': float(s['average_rating']),
        'num_ratings': s['num_ratings']
    } for s in series]
    
    return jsonify(results)

@recommend_bp.route('/recommend/user')
def recommend_user():
    """Recommandations personnalisées basées sur les utilisateurs similaires."""
    user_id_str = request.args.get('user_id', '')
    top = int(request.args.get('top', '10'))
    
    if not user_id_str:
        return jsonify({'error': 'Parameter "user_id" is required'}), 400
    
    # Récupérer l'utilisateur
    user = execute_query(
        "SELECT id FROM users WHERE username = %s",
        (user_id_str,),
        fetchone=True
    )
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_id = user['id']
    
    # Algorithme de filtrage collaboratif simplifié
    # Trouver les séries aimées par des utilisateurs similaires
    recommendations = execute_query(
        """SELECT 
               s.title,
               AVG(r2.rating) as predicted_score,
               COUNT(r2.id) as num_similar_users
           FROM ratings r1
           JOIN ratings r2 ON r1.serie_id = r2.serie_id
           JOIN series s ON r2.serie_id = s.id
           WHERE r1.user_id = %s 
             AND r2.user_id != %s
             AND r1.rating >= 4
             AND r2.rating >= 4
             AND s.id NOT IN (
                 SELECT serie_id FROM ratings WHERE user_id = %s
             )
           GROUP BY s.id, s.title
           HAVING num_similar_users >= 1
           ORDER BY predicted_score DESC, num_similar_users DESC
           LIMIT %s""",
        (user_id, user_id, user_id, top),
        fetchall=True
    )
    
    results = [{
        'title': r['title'],
        'score': float(r['predicted_score'])
    } for r in recommendations]
    
    return jsonify(results)

@recommend_bp.route('/recommend/hybrid')
def recommend_hybrid():
    """Recommandations hybrides (préférences utilisateur + popularité)."""
    user_id_str = request.args.get('user_id', '')
    top = int(request.args.get('top', '10'))
    
    if not user_id_str:
        return jsonify({'error': 'Parameter "user_id" is required'}), 400
    
    # Récupérer l'utilisateur
    user = execute_query(
        "SELECT id FROM users WHERE username = %s",
        (user_id_str,),
        fetchone=True
    )
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_id = user['id']
    
    # Combiner score collaboratif (70%) + popularité (30%)
    recommendations = execute_query(
        """SELECT 
               s.title,
               (COALESCE(collab.score, 0) * 0.7 + s.popularity_score * 0.3) as hybrid_score
           FROM series s
           LEFT JOIN (
               SELECT 
                   s2.id,
                   AVG(r2.rating) as score
               FROM ratings r1
               JOIN ratings r2 ON r1.serie_id = r2.serie_id
               JOIN series s2 ON r2.serie_id = s2.id
               WHERE r1.user_id = %s 
                 AND r2.user_id != %s
                 AND r1.rating >= 4
                 AND r2.rating >= 4
               GROUP BY s2.id
           ) collab ON s.id = collab.id
           WHERE s.id NOT IN (
               SELECT serie_id FROM ratings WHERE user_id = %s
           )
           ORDER BY hybrid_score DESC
           LIMIT %s""",
        (user_id, user_id, user_id, top),
        fetchall=True
    )
    
    results = [{
        'title': r['title'],
        'score': float(r['hybrid_score'])
    } for r in recommendations]
    
    return jsonify(results)

"""
API des séries avec MySQL
"""
from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db import execute_query

series_bp = Blueprint('series', __name__)

def init_series_data(model_dir):
    """Initialisation (pour compatibilité)."""
    pass

@series_bp.route('/series')
def get_series():
    """Liste toutes les séries disponibles."""
    language = request.args.get('language', '').lower()
    
    if language and language not in ['vf', 'vo']:
        language = ''
    
    # Requête avec ou sans filtre de langue
    if language:
        series = execute_query(
            """SELECT s.title, s.language, s.average_rating, s.num_ratings, s.popularity_score,
                      GROUP_CONCAT(k.keyword ORDER BY k.score DESC LIMIT 10) as keywords
               FROM series s
               LEFT JOIN keywords k ON s.id = k.serie_id
               WHERE s.language = %s
               GROUP BY s.id, s.title, s.language, s.average_rating, s.num_ratings, s.popularity_score
               ORDER BY s.title""",
            (language,),
            fetchall=True
        )
    else:
        series = execute_query(
            """SELECT s.title, s.language, s.average_rating, s.num_ratings, s.popularity_score,
                      GROUP_CONCAT(k.keyword ORDER BY k.score DESC LIMIT 10) as keywords
               FROM series s
               LEFT JOIN keywords k ON s.id = k.serie_id
               GROUP BY s.id, s.title, s.language, s.average_rating, s.num_ratings, s.popularity_score
               ORDER BY s.title""",
            fetchall=True
        )
    
    results = []
    for s in series:
        serie_data = {
            'title': s['title'],
            'average_rating': float(s['average_rating']) if s['average_rating'] else 0.0,
            'num_ratings': s['num_ratings'] or 0
        }
        if s['keywords']:
            serie_data['keywords'] = s['keywords'].split(',')
        results.append(serie_data)
    
    return jsonify(results)

@series_bp.route('/series/<serie_id>')
def get_serie_details(serie_id):
    """Détails d'une série spécifique."""
    # Récupérer la série
    serie = execute_query(
        "SELECT * FROM series WHERE title = %s",
        (serie_id,),
        fetchone=True
    )
    
    if not serie:
        return jsonify({'error': 'Serie not found'}), 404
    
    # Récupérer les mots-clés
    keywords = execute_query(
        """SELECT keyword, score 
           FROM keywords 
           WHERE serie_id = %s 
           ORDER BY score DESC 
           LIMIT 20""",
        (serie['id'],),
        fetchall=True
    )
    
    details = {
        'title': serie['title'],
        'language': serie['language'],
        'average_rating': float(serie['average_rating']),
        'num_ratings': serie['num_ratings'],
        'popularity_score': float(serie['popularity_score']),
        'keywords': [{'keyword': k['keyword'], 'score': float(k['score'])} for k in keywords]
    }
    
    return jsonify(details)

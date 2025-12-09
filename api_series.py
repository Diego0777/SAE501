"""
API de gestion des séries.
Permet de lister et consulter les détails des séries.
"""

from flask import Blueprint, request, jsonify
import os
import sys
import joblib

sys.path.insert(0, os.path.dirname(__file__))
from recommend import get_series_stats

series_bp = Blueprint('series', __name__)

# Variables globales
titles = None
keywords_dict = {}
ratings_file = './data/ratings.json'


def init_series_data(model_dir='./data/index'):
    """Initialise les données des séries."""
    global titles, keywords_dict
    
    meta_path = os.path.join(model_dir, 'meta.joblib')
    meta = joblib.load(meta_path)
    titles = meta['titles']
    
    # Charger les mots-clés
    kw_dir = os.path.join(os.path.dirname(model_dir), 'keywords')
    kw_meta_path = os.path.join(kw_dir, 'keywords_meta.joblib')
    
    if os.path.exists(kw_meta_path):
        kw_data = joblib.load(kw_meta_path)
        keywords_dict = kw_data.get('keywords', {})


@series_bp.route('/series')
def get_series():
    """
    Liste toutes les séries disponibles.
    
    Query params:
        language (str): Filtrer par langue 'vf' ou 'vo' (optionnel)
    
    Returns:
        JSON: Liste de toutes les séries
    """
    language = request.args.get('language', '').lower()
    
    if language in ['vf', 'vo']:
        filtered = [t for t in titles if t.lower().endswith(f'_{language}')]
    else:
        filtered = titles
    
    # Ajouter les statistiques si disponibles
    stats = get_series_stats(ratings_file) if os.path.exists(ratings_file) else {}
    
    results = []
    for serie in filtered:
        serie_data = {'title': serie}
        if serie in stats:
            serie_data['average_rating'] = float(stats[serie]['avg_rating'])
            serie_data['num_ratings'] = int(stats[serie]['num_ratings'])
        if serie in keywords_dict:
            serie_data['keywords'] = [kw for kw, _ in keywords_dict[serie][:10]]
        results.append(serie_data)
    
    return jsonify(results)


@series_bp.route('/series/<serie_id>')
def get_serie_details(serie_id):
    """
    Détails d'une série spécifique.
    
    Returns:
        JSON: Informations détaillées sur la série
    """
    if serie_id not in titles:
        return jsonify({'error': 'Serie not found'}), 404
    
    stats = get_series_stats(ratings_file) if os.path.exists(ratings_file) else {}
    
    details = {
        'title': serie_id,
        'language': 'vf' if serie_id.lower().endswith('_vf') else 'vo'
    }
    
    if serie_id in stats:
        details['average_rating'] = float(stats[serie_id]['avg_rating'])
        details['num_ratings'] = int(stats[serie_id]['num_ratings'])
        details['popularity_score'] = float(stats[serie_id]['popularity_score'])
    
    if serie_id in keywords_dict:
        details['keywords'] = [
            {'keyword': kw, 'score': float(score)} 
            for kw, score in keywords_dict[serie_id][:20]
        ]
    
    return jsonify(details)

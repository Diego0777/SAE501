"""
API de recherche par mots-clés.
Permet de rechercher des séries TV en utilisant TF-IDF et boost par mots-clés.
"""

from flask import Blueprint, request, jsonify
from sklearn.metrics.pairwise import cosine_similarity
import os
import joblib

search_bp = Blueprint('search', __name__)

# Variables globales pour le modèle (chargées à l'initialisation)
vect = None
X = None
titles = None
keywords_dict = {}


def init_search_engine(model_dir='./data/index'):
    """Initialise le moteur de recherche."""
    global vect, X, titles, keywords_dict
    
    meta_path = os.path.join(model_dir, 'meta.joblib')
    matrix_path = os.path.join(model_dir, 'tfidf_matrix.joblib')
    
    meta = joblib.load(meta_path)
    vect = meta['vectorizer']
    titles = meta['titles']
    X = joblib.load(matrix_path)
    
    # Charger les mots-clés si disponibles
    kw_dir = os.path.join(os.path.dirname(model_dir), 'keywords')
    kw_meta_path = os.path.join(kw_dir, 'keywords_meta.joblib')
    
    if os.path.exists(kw_meta_path):
        kw_data = joblib.load(kw_meta_path)
        keywords_dict = kw_data.get('keywords', {})


@search_bp.route('/search')
def search():
    """
    Recherche de séries par mots-clés.
    
    Query params:
        q (str): Mots-clés de recherche
        top (int): Nombre de résultats (défaut: 10)
        language (str): Filtrer par langue 'vf' ou 'vo' (optionnel)
    
    Returns:
        JSON: Liste de séries avec scores
    """
    q = request.args.get('q', '')
    top = int(request.args.get('top', '10'))
    language = request.args.get('language', '').lower()
    
    if not q:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    # Recherche TF-IDF standard
    qv = vect.transform([q])
    sims = cosine_similarity(qv, X).flatten()
    
    # Appliquer boost basé sur les mots-clés
    if keywords_dict:
        query_lower = q.lower()
        query_tokens = set(query_lower.split())
        
        for i, title in enumerate(titles):
            if title in keywords_dict:
                kw_list = keywords_dict[title]
                boost = 0.0
                
                for keyword, kw_score in kw_list:
                    keyword_lower = keyword.lower()
                    if keyword_lower in query_lower:
                        boost += kw_score * 0.5
                    for qt in query_tokens:
                        if len(qt) > 2 and qt in keyword_lower:
                            boost += kw_score * 0.2
                
                sims[i] = sims[i] + boost
    
    # Filtrer par langue si spécifié
    if language in ['vf', 'vo']:
        filtered_indices = [i for i, t in enumerate(titles) if t.lower().endswith(f'_{language}')]
        filtered_sims = [(i, sims[i]) for i in filtered_indices]
        ranked = sorted(filtered_sims, key=lambda x: x[1], reverse=True)[:top]
        results = [{'title': titles[i], 'score': float(score)} for i, score in ranked if score > 0]
    else:
        ranked = sims.argsort()[::-1][:top]
        results = [{'title': titles[i], 'score': float(sims[i])} for i in ranked if sims[i] > 0]
    
    return jsonify(results)

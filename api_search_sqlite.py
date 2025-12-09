"""
API SQLite pour la recherche de séries (utilise TF-IDF + mots-clés)
"""
from flask import Blueprint, request, jsonify
from sklearn.metrics.pairwise import cosine_similarity
import os
import joblib
from database.db_sqlite import get_connection

api_search_sqlite = Blueprint('api_search_sqlite', __name__)

# Variables globales pour TF-IDF
vect = None
X = None
titles = None

def init_search_engine(model_dir='./data/index'):
    """Initialise le moteur de recherche TF-IDF."""
    global vect, X, titles
    
    meta_path = os.path.join(model_dir, 'meta.joblib')
    matrix_path = os.path.join(model_dir, 'tfidf_matrix.joblib')
    
    if os.path.exists(meta_path) and os.path.exists(matrix_path):
        meta = joblib.load(meta_path)
        vect = meta['vectorizer']
        titles = meta['titles']
        X = joblib.load(matrix_path)

@api_search_sqlite.route('/api/search', methods=['GET'])
def search():
    """Recherche de séries par mots-clés."""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    language = request.args.get('language', '').lower()
    
    if not query:
        return jsonify({'error': 'Paramètre q requis'}), 400
    
    # Initialiser si nécessaire
    if vect is None:
        init_search_engine()
    
    # Recherche TF-IDF
    q_vec = vect.transform([query])
    similarities = cosine_similarity(q_vec, X)[0]
    
    # Trier par similarité
    top_indices = similarities.argsort()[::-1]
    
    # Récupérer les détails depuis SQLite
    results = []
    with get_connection() as conn:
        cursor = conn.cursor()
        
        for idx in top_indices:
            if len(results) >= limit:
                break
            
            title = titles[idx]
            score = float(similarities[idx])
            
            if score == 0:
                continue
            
            # Filtrer par langue si demandé
            if language and not title.lower().endswith(f'_{language}'):
                continue
            
            # Récupérer les infos de la série
            cursor.execute(
                """SELECT id, title, language, average_rating, num_ratings, poster_url
                   FROM series WHERE title = ?""",
                (title,)
            )
            serie = cursor.fetchone()
            
            if serie:
                results.append({
                    'id': serie[0],
                    'title': serie[1],
                    'language': serie[2],
                    'average_rating': serie[3] if serie[3] else 0,
                    'num_ratings': serie[4],
                    'poster_url': serie[5],
                    'score': round(score, 3)
                })
    
    return jsonify({
        'query': query,
        'num_results': len(results),
        'results': results
    })

# Initialiser au chargement du module
init_search_engine()

"""
API SQLite pour la recherche de séries (utilise TF-IDF + mots-clés)
"""
from flask import Blueprint, request, jsonify
from sklearn.metrics.pairwise import cosine_similarity
import os
import joblib
import unicodedata
from database.db_sqlite import get_connection

api_search_sqlite = Blueprint('api_search_sqlite', __name__)

# Variables globales pour TF-IDF
vect = None
X = None
titles = None

def remove_accents(text):
    """
    Convertit les caractères accentués en caractères non accentués.
    Exemple: é -> e, ê -> e, à -> a, ç -> c, etc.
    """
    nfd_form = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd_form if unicodedata.category(char) != 'Mn')

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
    
    # Enlever les accents de la requête pour matcher les mots indexés
    query_clean = remove_accents(query).lower()
    
    # Recherche TF-IDF
    q_vec = vect.transform([query_clean])
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
                """SELECT s.id, s.title, s.language, 
                          COALESCE(AVG(r.rating), 0) as average_rating,
                          COUNT(r.id) as num_ratings,
                          s.poster_url
                   FROM series s
                   LEFT JOIN ratings r ON s.id = r.serie_id
                   WHERE s.title = ?
                   GROUP BY s.id, s.title, s.language, s.poster_url""",
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

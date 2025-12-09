"""
API SQLite pour les recommandations (déjà créé précédemment avec poster_url)
Modifié pour ajouter poster_url partout
"""
from flask import Blueprint, request, jsonify
import math
from database.db_sqlite import get_connection

api_recommend_sqlite = Blueprint('api_recommend_sqlite', __name__)

@api_recommend_sqlite.route('/api/recommend/popularity', methods=['GET'])
def recommend_popularity():
    """Recommandations basées sur la popularité."""
    limit = request.args.get('limit', 10, type=int)
    language = request.args.get('language')
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT s.id, s.title, s.language, s.average_rating, s.num_ratings, s.poster_url,
                   CASE 
                       WHEN s.num_ratings > 0 THEN (s.average_rating * LOG(1 + s.num_ratings))
                       ELSE (
                           SELECT COUNT(*) * 0.01
                           FROM keywords k
                           WHERE k.serie_id = s.id
                       )
                   END as pop_score
            FROM series s
        """
        params = []
        
        if language:
            query += " WHERE s.language = ?"
            params.append(language.lower())
        
        query += " ORDER BY pop_score DESC, s.title ASC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        series = cursor.fetchall()
    
    return jsonify({
        'method': 'popularity',
        'recommendations': [{
            'id': s[0],
            'title': s[1],
            'language': s[2],
            'average_rating': round(s[3], 2) if s[3] else 0,
            'num_ratings': s[4],
            'poster_url': s[5],
            'score': round(s[6], 2)
        } for s in series]
    })

@api_recommend_sqlite.route('/api/recommend/collaborative/<int:user_id>', methods=['GET'])
def recommend_collaborative(user_id):
    """Recommandations par filtrage collaboratif."""
    limit = request.args.get('limit', 10, type=int)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Vérifier que l'utilisateur existe
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Notes de l'utilisateur
        cursor.execute(
            "SELECT serie_id, rating FROM ratings WHERE user_id = ?",
            (user_id,)
        )
        user_ratings = {row[0]: row[1] for row in cursor.fetchall()}
        
        if not user_ratings:
            return jsonify({
                'method': 'collaborative',
                'message': 'Aucune note trouvée pour cet utilisateur',
                'recommendations': []
            })
        
        # Trouver les utilisateurs similaires (ont noté les mêmes séries)
        cursor.execute(
            """SELECT DISTINCT r2.user_id
               FROM ratings r1
               JOIN ratings r2 ON r1.serie_id = r2.serie_id
               WHERE r1.user_id = ? AND r2.user_id != r1.user_id""",
            (user_id,)
        )
        similar_users = [row[0] for row in cursor.fetchall()]
        
        if not similar_users:
            return jsonify({
                'method': 'collaborative',
                'message': 'Aucun utilisateur similaire trouvé',
                'recommendations': []
            })
        
        # Séries non vues par l'utilisateur mais aimées par les utilisateurs similaires
        placeholders = ','.join('?' * len(similar_users))
        cursor.execute(
            f"""SELECT s.id, s.title, s.language, s.average_rating, s.num_ratings, s.poster_url,
                       AVG(r.rating) as pred_rating
                FROM series s
                JOIN ratings r ON s.id = r.serie_id
                WHERE r.user_id IN ({placeholders})
                  AND s.id NOT IN ({','.join('?' * len(user_ratings))})
                GROUP BY s.id
                ORDER BY pred_rating DESC
                LIMIT ?""",
            similar_users + list(user_ratings.keys()) + [limit]
        )
        recommendations = cursor.fetchall()
    
    return jsonify({
        'method': 'collaborative',
        'recommendations': [{
            'id': r[0],
            'title': r[1],
            'language': r[2],
            'average_rating': round(r[3], 2) if r[3] else 0,
            'num_ratings': r[4],
            'poster_url': r[5],
            'score': round(r[6], 2)
        } for r in recommendations]
    })

@api_recommend_sqlite.route('/api/recommend/hybrid/<int:user_id>', methods=['GET'])
def recommend_hybrid(user_id):
    """Recommandations hybrides (collaborative + popularité)."""
    limit = request.args.get('limit', 10, type=int)
    
    # Récupérer les recommandations collaboratives
    collab_response = recommend_collaborative(user_id)
    collab_data = collab_response.get_json()
    
    # Si pas de recommandations collaboratives, utiliser la popularité
    if not collab_data.get('recommendations'):
        pop_response = recommend_popularity()
        pop_data = pop_response.get_json()
        return jsonify({
            'method': 'hybrid',
            'recommendations': pop_data['recommendations'][:limit]
        })
    
    # Combiner collaborative et popularité
    collab_recs = {r['id']: r for r in collab_data['recommendations']}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT s.id, s.title, s.language, s.average_rating, s.num_ratings, s.poster_url,
                      (s.average_rating * LOG(1 + s.num_ratings)) as pop_score
               FROM series s
               WHERE s.num_ratings > 0
               ORDER BY pop_score DESC
               LIMIT ?""",
            (limit * 2,)
        )
        pop_series = cursor.fetchall()
    
    # Fusionner les scores
    hybrid_recs = {}
    
    for s in pop_series:
        serie_id = s[0]
        if serie_id in collab_recs:
            # Moyenne des scores collaborative et popularité
            collab_score = collab_recs[serie_id]['score']
            pop_score = s[6]
            hybrid_score = (collab_score + pop_score) / 2
        else:
            hybrid_score = s[6]
        
        hybrid_recs[serie_id] = {
            'id': s[0],
            'title': s[1],
            'language': s[2],
            'average_rating': round(s[3], 2) if s[3] else 0,
            'num_ratings': s[4],
            'poster_url': s[5],
            'score': round(hybrid_score, 2)
        }
    
    # Trier par score et limiter
    sorted_recs = sorted(hybrid_recs.values(), key=lambda x: x['score'], reverse=True)[:limit]
    
    return jsonify({
        'method': 'hybrid',
        'recommendations': sorted_recs
    })

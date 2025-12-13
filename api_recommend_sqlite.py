"""
API de recommandation de séries TV utilisant SQLite.

Ce module implémente plusieurs algorithmes de recommandation:
1. Recommandations par popularité (score basé sur note moyenne et nombre de votes)
2. Filtrage collaboratif (basé sur la similitude entre utilisateurs)
3. Recommandations hybrides (combinaison des deux méthodes)

Algorithmes:
    - Popularité: score = note_moyenne * log(1 + nb_votes)
    - Collaboratif: Trouve les utilisateurs similaires puis recommande leurs séries préférées
    - Hybride: Moyenne pondérée des scores de popularité et collaboratif

La langue préférée de l'utilisateur est prise en compte pour personnaliser
les recommandations (VF vs VO).
"""
from flask import Blueprint, request, jsonify
import math
from database.db_sqlite import get_connection

api_recommend_sqlite = Blueprint('api_recommend_sqlite', __name__)


# ============================================================================
# HELPERS DE CALCUL DE SCORES
# ============================================================================

def calculate_popularity_score(average_rating, num_ratings):
    """
    Calculer un score de popularité pour une série.
    
    Le score combine la note moyenne avec le nombre de votes en utilisant
    une fonction logarithmique pour éviter que les séries avec beaucoup de
    votes mais une note moyenne écrasent les séries bien notées mais moins votées.
    
    Formule: score = note_moyenne * log(1 + nb_votes)
    
    Args:
        average_rating (float): Note moyenne de la série (0-5)
        num_ratings (int): Nombre total de votes
        
    Returns:
        float: Score de popularité calculé
    """
    if num_ratings > 0:
        return average_rating * math.log(1 + num_ratings)
    return 0.0


# ============================================================================
# RECOMMANDATIONS PAR POPULARITÉ
# ============================================================================

@api_recommend_sqlite.route('/api/recommend/popularity', methods=['GET'])
def recommend_popularity():
    """
    Recommander des séries basées sur leur popularité.
    
    Le score de popularité combine la note moyenne et le nombre de votes
    pour équilibrer qualité et consensus. Les séries sans votes sont également
    incluses avec un score basé sur le nombre de mots-clés (indicateur de richesse).
    
    Query params:
        limit (int): Nombre maximum de recommandations (défaut: 10)
        language (str): Filtrer par langue ('vf', 'vo', ou vide pour toutes)
        
    Returns:
        JSON: {
            'method': 'popularity',
            'recommendations': [...]
        }
    """
    limit = request.args.get('limit', 10, type=int)
    language = request.args.get('language')
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Construire la requête SQL avec score de popularité
        query = """
            SELECT s.id, s.title, s.language, 
                   COALESCE(AVG(r.rating), 0) as average_rating,
                   COUNT(r.id) as num_ratings,
                   s.poster_url,
                   CASE 
                       WHEN COUNT(r.id) > 0 THEN (AVG(r.rating) * LOG(1 + COUNT(r.id)))
                       ELSE 0
                   END as pop_score
            FROM series s
            LEFT JOIN ratings r ON s.id = r.serie_id
        """
        params = []
        
        # Appliquer le filtre de langue et les critères minimum
        where_clauses = ["COUNT(r.id) >= 1", "AVG(r.rating) >= 4.0"]
        
        if language:
            where_clauses.append("s.language = ?")
            params.append(language.lower())
        
        query += " GROUP BY s.id, s.title, s.language, s.poster_url"
        query += " HAVING " + " AND ".join(where_clauses)
        query += " ORDER BY pop_score DESC, average_rating DESC LIMIT ?"
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


# ============================================================================
# FILTRAGE COLLABORATIF
# ============================================================================

def find_similar_users(conn, user_id, min_common_ratings=2):
    """
    Trouver les utilisateurs avec des goûts similaires à un utilisateur donné.
    
    La similitude est calculée en comptant:
    - Le nombre de séries notées en commun
    - Le nombre de notes similaires (différence ≤ 1 étoile)
    
    Args:
        conn: Connexion à la base de données
        user_id (int): ID de l'utilisateur de référence
        min_common_ratings (int): Nombre minimum de séries en commun requises
        
    Returns:
        list: Liste des IDs d'utilisateurs similaires, triés par similarité
    """
    cursor = conn.cursor()
    cursor.execute(
        """SELECT r2.user_id, COUNT(*) as common_ratings,
                  SUM(CASE WHEN ABS(r1.rating - r2.rating) <= 1 THEN 1 ELSE 0 END) as similar_ratings
           FROM ratings r1
           JOIN ratings r2 ON r1.serie_id = r2.serie_id
           WHERE r1.user_id = ? AND r2.user_id != r1.user_id
           GROUP BY r2.user_id
           HAVING common_ratings >= ?
           ORDER BY similar_ratings DESC, common_ratings DESC
           LIMIT 10""",
        (user_id, min_common_ratings)
    )
    similar_users_data = cursor.fetchall()
    return [row[0] for row in similar_users_data]


@api_recommend_sqlite.route('/api/recommend/collaborative/<int:user_id>', methods=['GET'])
def recommend_collaborative(user_id):
    """
    Recommander des séries par filtrage collaboratif.
    
    Algorithme:
    1. Récupérer les notes de l'utilisateur et sa langue préférée
    2. Trouver des utilisateurs similaires (ayant noté les mêmes séries de façon similaire)
    3. Identifier les séries bien notées (≥4/5) par ces utilisateurs similaires
    4. Filtrer pour ne garder que les séries dans la langue préférée
    5. Exclure les séries déjà notées par l'utilisateur
    6. Trier par note moyenne prédite
    
    Query params:
        limit (int): Nombre maximum de recommandations (défaut: 10)
        
    Returns:
        JSON: {
            'method': 'collaborative',
            'recommendations': [...]
        }
    """
    limit = request.args.get('limit', 10, type=int)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Vérifier que l'utilisateur existe et récupérer sa langue préférée
        cursor.execute("SELECT id, language_preference FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        if not user_row:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        user_lang = user_row[1] if user_row[1] else 'vf'
        
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
        
        # Trouver les utilisateurs similaires avec score de similarité
        cursor.execute(
            """SELECT r2.user_id, COUNT(*) as common_ratings,
                      SUM(CASE WHEN ABS(r1.rating - r2.rating) <= 1 THEN 1 ELSE 0 END) as similar_ratings
               FROM ratings r1
               JOIN ratings r2 ON r1.serie_id = r2.serie_id
               WHERE r1.user_id = ? AND r2.user_id != r1.user_id
               GROUP BY r2.user_id
               HAVING common_ratings >= 2
               ORDER BY similar_ratings DESC, common_ratings DESC
               LIMIT 10""",
            (user_id,)
        )
        similar_users_data = cursor.fetchall()
        
        if not similar_users_data:
            return jsonify({
                'method': 'collaborative',
                'message': 'Aucun utilisateur similaire trouvé',
                'recommendations': []
            })
        
        similar_users = [row[0] for row in similar_users_data]
        
        # Séries non vues, aimées par utilisateurs similaires, dans la langue préférée
        placeholders = ','.join('?' * len(similar_users))
        cursor.execute(
            f"""SELECT s.id, s.title, s.language, 
                       COALESCE(AVG(rall.rating), 0) as average_rating,
                       COUNT(DISTINCT rall.id) as num_ratings,
                       s.poster_url,
                       AVG(r.rating) as pred_rating
                FROM series s
                JOIN ratings r ON s.id = r.serie_id
                LEFT JOIN ratings rall ON s.id = rall.serie_id
                WHERE r.user_id IN ({placeholders})
                  AND r.rating >= 4
                  AND s.id NOT IN ({','.join('?' * len(user_ratings))})
                  AND s.language = ?
                GROUP BY s.id, s.title, s.language, s.poster_url
                HAVING AVG(r.rating) >= 4.0
                ORDER BY pred_rating DESC, num_ratings DESC
                LIMIT ?""",
            similar_users + list(user_ratings.keys()) + [user_lang, limit]
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
            """SELECT s.id, s.title, s.language, 
                      COALESCE(AVG(r.rating), 0) as average_rating,
                      COUNT(r.id) as num_ratings,
                      s.poster_url,
                      CASE 
                          WHEN COUNT(r.id) > 0 THEN (AVG(r.rating) * LOG(1 + COUNT(r.id)))
                          ELSE 0
                      END as pop_score
               FROM series s
               LEFT JOIN ratings r ON s.id = r.serie_id
               GROUP BY s.id, s.title, s.language, s.poster_url
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

"""
API SQLite pour la gestion des séries
"""
from flask import Blueprint, request, jsonify
from database.db_sqlite import get_connection

api_series_sqlite = Blueprint('api_series_sqlite', __name__)

@api_series_sqlite.route('/api/series', methods=['GET'])
def list_series():
    """Liste toutes les séries."""
    language = request.args.get('language', '').lower()
    limit = request.args.get('limit', type=int)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT s.id, s.title, s.language, 
                   COALESCE(AVG(r.rating), 0) as average_rating,
                   COUNT(r.id) as num_ratings,
                   s.poster_url
            FROM series s
            LEFT JOIN ratings r ON s.id = r.serie_id
        """
        params = []
        
        if language in ['vf', 'vo']:
            query += " WHERE s.language = ?"
            params.append(language)
        
        query += " GROUP BY s.id, s.title, s.language, s.poster_url ORDER BY s.title"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        series = cursor.fetchall()
    
    return jsonify([{
        'id': s[0],
        'title': s[1],
        'language': s[2],
        'average_rating': s[3] if s[3] else 0,
        'num_ratings': s[4],
        'poster_url': s[5]
    } for s in series])

@api_series_sqlite.route('/api/series/<title>', methods=['GET'])
def get_series_details(title):
    """Détails d'une série."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
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
        
        if not serie:
            return jsonify({'error': 'Série non trouvée'}), 404
        
        # Récupérer les mots-clés
        cursor.execute(
            """SELECT keyword, score
               FROM keywords
               WHERE serie_id = ?
               ORDER BY score DESC
               LIMIT 20""",
            (serie[0],)
        )
        keywords = cursor.fetchall()
    
    return jsonify({
        'id': serie[0],
        'title': serie[1],
        'language': serie[2],
        'average_rating': serie[3] if serie[3] else 0,
        'num_ratings': serie[4],
        'poster_url': serie[5],
        'keywords': [{
            'keyword': k[0],
            'score': k[1]
        } for k in keywords]
    })

@api_series_sqlite.route('/api/series/search', methods=['GET'])
def search_series_by_name():
    """Recherche de séries par nom."""
    query = request.args.get('query', '').strip()
    language = request.args.get('language', '').lower()
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Recherche LIKE case-insensitive
        search_pattern = f"%{query}%"
        
        sql_query = """
            SELECT s.id, s.title, s.language, s.average_rating, s.num_ratings, s.poster_url
            FROM series s
            WHERE s.title LIKE ?
        """
        params = [search_pattern]
        
        if language in ['vf', 'vo']:
            sql_query += " AND s.language = ?"
            params.append(language)
        
        sql_query += " ORDER BY s.title LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql_query, params)
        series = cursor.fetchall()
    
    return jsonify({
        'query': query,
        'total': len(series),
        'series': [{
            'id': s[0],
            'title': s[1],
            'language': s[2],
            'average_rating': s[3] if s[3] else 0,
            'num_ratings': s[4],
            'poster_url': s[5]
        } for s in series]
    })

@api_series_sqlite.route('/api/series/stats', methods=['GET'])
def get_stats():
    """Statistiques générales."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN language = 'vf' THEN 1 ELSE 0 END) as vf,
                SUM(CASE WHEN language = 'vo' THEN 1 ELSE 0 END) as vo
            FROM series
        """)
        series_stats = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*), AVG(rating) FROM ratings")
        ratings_stats = cursor.fetchone()
    
    return jsonify({
        'total_series': series_stats[0],
        'series_vf': series_stats[1],
        'series_vo': series_stats[2],
        'total_users': users_count,
        'total_ratings': ratings_stats[0],
        'average_rating': round(ratings_stats[1], 2) if ratings_stats[1] else 0
    })

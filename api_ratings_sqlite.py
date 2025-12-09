"""
API SQLite pour les notes des utilisateurs
"""
from flask import Blueprint, request, jsonify
from database.db_sqlite import get_connection

api_ratings_sqlite = Blueprint('api_ratings_sqlite', __name__)

@api_ratings_sqlite.route('/api/ratings', methods=['GET'])
def get_ratings():
    """Obtenir toutes les notes (optionnel: filtrer par utilisateur)."""
    user_id = request.args.get('user_id', type=int)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute(
                """SELECT r.id, r.user_id, r.serie_id, s.title, r.rating, r.created_at
                   FROM ratings r
                   JOIN series s ON r.serie_id = s.id
                   WHERE r.user_id = ?
                   ORDER BY r.created_at DESC""",
                (user_id,)
            )
        else:
            cursor.execute(
                """SELECT r.id, r.user_id, r.serie_id, s.title, r.rating, r.created_at
                   FROM ratings r
                   JOIN series s ON r.serie_id = s.id
                   ORDER BY r.created_at DESC"""
            )
        
        ratings = cursor.fetchall()
    
    return jsonify([{
        'id': r[0],
        'user_id': r[1],
        'serie_id': r[2],
        'serie_title': r[3],
        'rating': r[4],
        'created_at': r[5]
    } for r in ratings])

@api_ratings_sqlite.route('/api/ratings/<series_title>', methods=['GET'])
def get_series_ratings(series_title):
    """Obtenir toutes les notes pour une série."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Trouver l'ID de la série
        cursor.execute("SELECT id FROM series WHERE title = ?", (series_title,))
        serie = cursor.fetchone()
        
        if not serie:
            return jsonify({'error': 'Série non trouvée'}), 404
        
        serie_id = serie[0]
        
        cursor.execute(
            """SELECT r.id, r.user_id, u.username, r.rating, r.created_at
               FROM ratings r
               JOIN users u ON r.user_id = u.id
               WHERE r.serie_id = ?
               ORDER BY r.created_at DESC""",
            (serie_id,)
        )
        ratings = cursor.fetchall()
    
    return jsonify({
        'serie_title': series_title,
        'ratings': [{
            'id': r[0],
            'user_id': r[1],
            'username': r[2],
            'rating': r[3],
            'created_at': r[4]
        } for r in ratings]
    })

@api_ratings_sqlite.route('/api/ratings', methods=['POST'])
def add_rating():
    """Ajouter ou mettre à jour une note."""
    data = request.json
    user_id = data.get('user_id')
    series_title = data.get('series_title')
    rating = data.get('rating')
    
    if not all([user_id, series_title, rating]):
        return jsonify({'error': 'user_id, series_title et rating requis'}), 400
    
    if not (1 <= rating <= 5):
        return jsonify({'error': 'La note doit être entre 1 et 5'}), 400
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Trouver l'ID de la série
        cursor.execute("SELECT id FROM series WHERE title = ?", (series_title,))
        serie = cursor.fetchone()
        
        if not serie:
            return jsonify({'error': 'Série non trouvée'}), 404
        
        serie_id = serie[0]
        
        # Insérer ou mettre à jour la note
        cursor.execute(
            """INSERT INTO ratings (user_id, serie_id, rating, created_at)
               VALUES (?, ?, ?, datetime('now'))
               ON CONFLICT(user_id, serie_id) 
               DO UPDATE SET rating = ?, updated_at = datetime('now')""",
            (user_id, serie_id, rating, rating)
        )
        
        rating_id = cursor.lastrowid
        
        # Mettre à jour les statistiques de la série
        cursor.execute(
            """UPDATE series
               SET average_rating = (SELECT AVG(rating) FROM ratings WHERE serie_id = ?),
                   num_ratings = (SELECT COUNT(*) FROM ratings WHERE serie_id = ?)
               WHERE id = ?""",
            (serie_id, serie_id, serie_id)
        )
    
    return jsonify({
        'success': True,
        'rating_id': rating_id,
        'message': 'Note enregistrée avec succès'
    })

@api_ratings_sqlite.route('/api/ratings/<int:rating_id>', methods=['DELETE'])
def delete_rating(rating_id):
    """Supprimer une note."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Récupérer l'ID de la série avant suppression
        cursor.execute("SELECT serie_id FROM ratings WHERE id = ?", (rating_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'Note non trouvée'}), 404
        
        serie_id = result[0]
        
        # Supprimer la note
        cursor.execute("DELETE FROM ratings WHERE id = ?", (rating_id,))
        
        # Mettre à jour les statistiques
        cursor.execute(
            """UPDATE series
               SET average_rating = COALESCE((SELECT AVG(rating) FROM ratings WHERE serie_id = ?), 0),
                   num_ratings = (SELECT COUNT(*) FROM ratings WHERE serie_id = ?)
               WHERE id = ?""",
            (serie_id, serie_id, serie_id)
        )
    
    return jsonify({'success': True, 'message': 'Note supprimée'})

@api_ratings_sqlite.route('/api/ratings/user/<int:user_id>/series/<series_title>', methods=['GET'])
def get_user_series_rating(user_id, series_title):
    """Obtenir la note d'un utilisateur pour une série."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT r.rating, r.created_at
               FROM ratings r
               JOIN series s ON r.serie_id = s.id
               WHERE r.user_id = ? AND s.title = ?""",
            (user_id, series_title)
        )
        rating = cursor.fetchone()
        
        if not rating:
            return jsonify({'rating': None})
        
        return jsonify({
            'rating': rating[0],
            'created_at': rating[1]
        })

"""
Module de connexion à la base de données MySQL
"""
import mysql.connector
from mysql.connector import pooling
import os

# Configuration de la base de données
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'tvseries'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# Pool de connexions pour de meilleures performances
connection_pool = None

def init_pool():
    """Initialiser le pool de connexions."""
    global connection_pool
    if connection_pool is None:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="tvseries_pool",
            pool_size=5,
            **DB_CONFIG
        )

def get_connection():
    """Obtenir une connexion depuis le pool."""
    if connection_pool is None:
        init_pool()
    return connection_pool.get_connection()

def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Exécuter une requête SQL.
    
    Args:
        query: Requête SQL
        params: Paramètres de la requête
        fetchone: Retourner une seule ligne
        fetchall: Retourner toutes les lignes
        commit: Faire un commit (pour INSERT/UPDATE/DELETE)
    
    Returns:
        Résultat de la requête ou ID du dernier insert
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(query, params or ())
        
        if commit:
            conn.commit()
            return cursor.lastrowid
        
        if fetchone:
            return cursor.fetchone()
        
        if fetchall:
            return cursor.fetchall()
        
        return cursor.lastrowid
    
    finally:
        cursor.close()
        conn.close()

def test_connection():
    """Tester la connexion à la base de données."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        return True, f"MySQL {version[0]}"
    except Exception as e:
        return False, str(e)

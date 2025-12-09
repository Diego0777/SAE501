"""
Module de connexion à la base de données SQLite
"""
import sqlite3
import os
from contextlib import contextmanager

# Chemin de la base de données
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'tvseries.db')

def init_db():
    """Initialiser la base de données avec le schéma."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema_sqlite.sql')
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
    
    conn.executescript(schema)
    conn.commit()
    conn.close()
    
    return True

@contextmanager
def get_connection():
    """Obtenir une connexion à la base de données (context manager)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # Activer les clés étrangères
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_query(query, params=None, fetchone=False, fetchall=False):
    """
    Exécuter une requête SQL.
    
    Args:
        query: Requête SQL
        params: Paramètres de la requête (tuple ou dict)
        fetchone: Retourner une seule ligne
        fetchall: Retourner toutes les lignes
    
    Returns:
        Résultat de la requête ou ID du dernier insert
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetchone:
            row = cursor.fetchone()
            return dict(row) if row else None
        
        if fetchall:
            return [dict(row) for row in cursor.fetchall()]
        
        return cursor.lastrowid

def test_connection():
    """Tester la connexion à la base de données."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            return True, f"SQLite {version}"
    except Exception as e:
        return False, str(e)

def get_db_stats():
    """Obtenir des statistiques sur la base de données."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        stats = {}
        for table in ['users', 'series', 'keywords', 'ratings', 'sessions']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]
        
        return stats

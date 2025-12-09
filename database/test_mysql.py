"""
Test complet de la base de données MySQL
"""
import sys

print("=" * 70)
print("TEST DE LA BASE DE DONNÉES MYSQL")
print("=" * 70)

# Test 1 : Import du module
print("\n1️⃣ Test d'import du module database...")
try:
    from database.db import test_connection, execute_query, init_pool
    print("   ✅ Module database importé avec succès")
except Exception as e:
    print(f"   ❌ Erreur d'import: {e}")
    print("\n💡 Solution : pip install mysql-connector-python")
    sys.exit(1)

# Test 2 : Connexion à MySQL
print("\n2️⃣ Test de connexion à MySQL...")
success, message = test_connection()
if success:
    print(f"   ✅ Connexion réussie : {message}")
else:
    print(f"   ❌ Erreur de connexion : {message}")
    print("\n💡 Solutions possibles :")
    print("   - Vérifier que MySQL est installé et démarré")
    print("   - Exécuter : mysql -u root -p < database/schema.sql")
    print("   - Vérifier DB_PASSWORD dans database/db.py")
    sys.exit(1)

# Test 3 : Vérifier les tables
print("\n3️⃣ Vérification des tables...")
try:
    init_pool()
    tables = execute_query("SHOW TABLES", fetchall=True)
    table_names = [list(t.values())[0] for t in tables]
    
    required_tables = ['users', 'series', 'keywords', 'ratings', 'sessions']
    missing = [t for t in required_tables if t not in table_names]
    
    if missing:
        print(f"   ⚠️ Tables manquantes : {', '.join(missing)}")
        print("   💡 Exécuter : mysql -u root -p < database/schema.sql")
    else:
        print(f"   ✅ Toutes les tables présentes : {', '.join(table_names)}")
except Exception as e:
    print(f"   ❌ Erreur : {e}")
    sys.exit(1)

# Test 4 : Compter les données
print("\n4️⃣ Statistiques de la base...")
try:
    stats = {
        'users': execute_query("SELECT COUNT(*) as count FROM users", fetchone=True)['count'],
        'series': execute_query("SELECT COUNT(*) as count FROM series", fetchone=True)['count'],
        'keywords': execute_query("SELECT COUNT(*) as count FROM keywords", fetchone=True)['count'],
        'ratings': execute_query("SELECT COUNT(*) as count FROM ratings", fetchone=True)['count'],
    }
    
    print(f"   👥 Utilisateurs : {stats['users']}")
    print(f"   📺 Séries : {stats['series']}")
    print(f"   🏷️  Mots-clés : {stats['keywords']}")
    print(f"   ⭐ Notations : {stats['ratings']}")
    
    if stats['series'] == 0:
        print("\n   ⚠️ Aucune série dans la base !")
        print("   💡 Exécuter : python database/import_data.py")
    else:
        print(f"\n   ✅ Base de données opérationnelle")
        
except Exception as e:
    print(f"   ❌ Erreur : {e}")
    sys.exit(1)

# Test 5 : Test de recherche
print("\n5️⃣ Test de recherche (Lost)...")
try:
    result = execute_query(
        "SELECT title, average_rating, num_ratings FROM series WHERE title LIKE %s",
        ('lost%',),
        fetchall=True
    )
    
    if result:
        for s in result:
            print(f"   ✅ Trouvé : {s['title']} - Note: {s['average_rating']:.2f} ({s['num_ratings']} votes)")
    else:
        print("   ⚠️ Aucune série 'Lost' trouvée")
        
except Exception as e:
    print(f"   ❌ Erreur : {e}")

# Test 6 : Test des mots-clés
print("\n6️⃣ Test des mots-clés (Lost)...")
try:
    result = execute_query(
        """SELECT k.keyword, k.score 
           FROM keywords k
           JOIN series s ON k.serie_id = s.id
           WHERE s.title = 'lost_vf'
           ORDER BY k.score DESC
           LIMIT 5""",
        fetchall=True
    )
    
    if result:
        print("   ✅ Mots-clés trouvés :")
        for kw in result:
            print(f"      - {kw['keyword']} (score: {kw['score']:.4f})")
    else:
        print("   ⚠️ Aucun mot-clé trouvé pour Lost")
        
except Exception as e:
    print(f"   ❌ Erreur : {e}")

# Test 7 : Top séries
print("\n7️⃣ Top 5 des séries VF...")
try:
    result = execute_query(
        """SELECT title, average_rating, num_ratings, popularity_score
           FROM series
           WHERE language = 'vf' AND num_ratings > 0
           ORDER BY popularity_score DESC
           LIMIT 5""",
        fetchall=True
    )
    
    if result:
        print("   ✅ Séries les plus populaires :")
        for i, s in enumerate(result, 1):
            print(f"      {i}. {s['title']} - {s['average_rating']:.1f}⭐ ({s['num_ratings']} votes) - Pop: {s['popularity_score']:.2f}")
    else:
        print("   ⚠️ Aucune série notée")
        
except Exception as e:
    print(f"   ❌ Erreur : {e}")

# Résumé
print("\n" + "=" * 70)
if stats['series'] > 0 and stats['keywords'] > 0:
    print("✅ TOUS LES TESTS RÉUSSIS - La base MySQL est opérationnelle !")
    print("\n📝 Prochaine étape : python database/switch_to_mysql.py")
else:
    print("⚠️ La base existe mais est vide")
    print("\n📝 Prochaine étape : python database/import_data.py")
print("=" * 70)

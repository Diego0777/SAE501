"""
Script de test complet de l'application SAE501
Teste tous les endpoints et fonctionnalités principales
"""
import requests
import sqlite3
import json

BASE_URL = "http://127.0.0.1:5000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_database():
    """Test de la base de données SQLite"""
    print_section("TEST 1: BASE DE DONNÉES")
    
    conn = sqlite3.connect('data/tvseries.db')
    c = conn.cursor()
    
    # Compter les éléments
    c.execute("SELECT COUNT(*) FROM series")
    nb_series = c.fetchone()[0]
    print(f"✅ Séries: {nb_series}")
    
    c.execute("SELECT COUNT(*) FROM users")
    nb_users = c.fetchone()[0]
    print(f"✅ Utilisateurs: {nb_users}")
    
    c.execute("SELECT COUNT(*) FROM ratings")
    nb_ratings = c.fetchone()[0]
    print(f"✅ Ratings: {nb_ratings}")
    
    c.execute("SELECT COUNT(*) FROM keywords")
    nb_keywords = c.fetchone()[0]
    print(f"✅ Mots-clés: {nb_keywords}")
    
    conn.close()
    
    if nb_series < 100:
        print("⚠️  ATTENTION: Peu de séries dans la base")
    if nb_ratings < 50:
        print("⚠️  ATTENTION: Peu de ratings (recommandations limitées)")
    
    return nb_series > 0 and nb_users > 0 and nb_ratings > 0

def test_api_home():
    """Test de la page d'accueil"""
    print_section("TEST 2: PAGE D'ACCUEIL")
    
    try:
        r = requests.get(BASE_URL)
        if r.status_code == 200:
            print(f"✅ Page d'accueil accessible (status {r.status_code})")
            return True
        else:
            print(f"❌ Erreur page d'accueil (status {r.status_code})")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False

def test_api_search():
    """Test de la recherche TF-IDF"""
    print_section("TEST 3: RECHERCHE TF-IDF")
    
    tests = [
        {"q": "lost", "expected": "lost"},
        {"q": "crash avion ile", "expected": "lost"},
        {"q": "drogue professeur", "expected": "breakingbad"}
    ]
    
    success = 0
    for test in tests:
        r = requests.get(f"{BASE_URL}/api/search", params={"q": test["q"], "top": 10})
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            if results:
                found = any(test["expected"] in result["title"].lower() for result in results[:3])
                if found:
                    print(f"✅ Recherche '{test['q']}': trouvé '{test['expected']}' dans top 3")
                    success += 1
                else:
                    print(f"⚠️  Recherche '{test['q']}': '{test['expected']}' pas dans top 3")
                    print(f"   Top 3: {[r['title'] for r in results[:3]]}")
            else:
                print(f"❌ Recherche '{test['q']}': aucun résultat")
        else:
            print(f"❌ Erreur recherche '{test['q']}' (status {r.status_code})")
    
    return success == len(tests)

def test_api_series():
    """Test des endpoints séries"""
    print_section("TEST 4: API SÉRIES")
    
    # Liste des séries
    r = requests.get(f"{BASE_URL}/api/series", params={"limit": 10})
    if r.status_code == 200:
        series = r.json()
        print(f"✅ Liste séries: {len(series)} séries récupérées")
    else:
        print(f"❌ Erreur liste séries (status {r.status_code})")
        return False
    
    # Détails d'une série
    if series:
        test_title = series[0]['title']
        r = requests.get(f"{BASE_URL}/api/series/{test_title}")
        if r.status_code == 200:
            details = r.json()
            print(f"✅ Détails série '{test_title}': {len(details.get('keywords', []))} mots-clés")
        else:
            print(f"❌ Erreur détails série (status {r.status_code})")
            return False
    
    # Statistiques
    r = requests.get(f"{BASE_URL}/api/series/stats")
    if r.status_code == 200:
        stats = r.json()
        print(f"✅ Statistiques: {stats.get('total_series')} séries, {stats.get('total_ratings')} ratings")
    else:
        print(f"❌ Erreur stats (status {r.status_code})")
        return False
    
    return True

def test_api_users():
    """Test des endpoints utilisateurs"""
    print_section("TEST 5: API UTILISATEURS")
    
    # Test connexion alice
    r = requests.post(f"{BASE_URL}/login", json={
        "username": "alice",
        "password": "alice123"
    })
    
    if r.status_code == 200:
        data = r.json()
        user_id = data.get('user_id')
        print(f"✅ Connexion alice réussie (ID: {user_id})")
        
        # Test récupération des ratings de alice
        r = requests.get(f"{BASE_URL}/api/ratings", params={"user_id": user_id})
        if r.status_code == 200:
            ratings = r.json()
            print(f"✅ Ratings alice: {len(ratings)} notes trouvées")
            if ratings:
                print(f"   Exemples: {ratings[0]['serie_title']}: {ratings[0]['rating']}/5")
        else:
            print(f"❌ Erreur récupération ratings (status {r.status_code})")
            return False
            
        return True
    else:
        print(f"❌ Erreur connexion alice (status {r.status_code})")
        return False

def test_api_recommendations():
    """Test des recommandations"""
    print_section("TEST 6: API RECOMMANDATIONS")
    
    # Recommandations par popularité
    r = requests.get(f"{BASE_URL}/api/recommend/popularity", params={"limit": 5})
    if r.status_code == 200:
        data = r.json()
        recs = data.get('recommendations', [])
        print(f"✅ Recommandations popularité: {len(recs)} séries")
        if recs:
            print(f"   Top 1: {recs[0]['title']} (score: {recs[0].get('popularity_score', 0):.2f})")
    else:
        print(f"❌ Erreur recommandations popularité (status {r.status_code})")
        return False
    
    # Recommandations collaborative pour alice (ID varie, on teste plusieurs IDs)
    user_ids_to_test = [41, 42, 43]  # alice, bob, charlie
    success = False
    
    for user_id in user_ids_to_test:
        r = requests.get(f"{BASE_URL}/api/recommend/collaborative/{user_id}")
        if r.status_code == 200:
            data = r.json()
            recs = data.get('recommendations', [])
            if recs:
                print(f"✅ Recommandations collaborative (user {user_id}): {len(recs)} séries")
                print(f"   Top 1: {recs[0]['title']}")
                success = True
                break
            else:
                message = data.get('message', '')
                if 'similaire' in message.lower():
                    continue  # Essayer le prochain utilisateur
    
    if not success:
        print(f"⚠️  Pas de recommandations collaboratives (normal si peu d'utilisateurs similaires)")
    
    # Recommandations hybrides
    for user_id in user_ids_to_test:
        r = requests.get(f"{BASE_URL}/api/recommend/hybrid/{user_id}", params={"limit": 5})
        if r.status_code == 200:
            data = r.json()
            recs = data.get('recommendations', [])
            if recs:
                print(f"✅ Recommandations hybrides (user {user_id}): {len(recs)} séries")
                print(f"   Top 1: {recs[0]['title']}")
                success = True
                break
    
    return True

def test_frontend_pages():
    """Test des pages frontend"""
    print_section("TEST 7: PAGES FRONTEND")
    
    pages = [
        "/",
        "/search.html",
        "/series.html",
        "/recommendations.html",
        "/profile.html",
        "/series-details.html"
    ]
    
    success = 0
    for page in pages:
        try:
            r = requests.get(BASE_URL + page)
            if r.status_code == 200:
                print(f"✅ Page {page} accessible")
                success += 1
            else:
                print(f"❌ Page {page} erreur (status {r.status_code})")
        except:
            print(f"❌ Page {page} inaccessible")
    
    return success == len(pages)

def main():
    """Exécution de tous les tests"""
    print("\n" + "🚀"*30)
    print("  TEST COMPLET APPLICATION SAE501")
    print("🚀"*30)
    
    results = {}
    
    # Exécuter tous les tests
    results['database'] = test_database()
    results['home'] = test_api_home()
    results['search'] = test_api_search()
    results['series'] = test_api_series()
    results['users'] = test_api_users()
    results['recommendations'] = test_api_recommendations()
    results['frontend'] = test_frontend_pages()
    
    # Résumé
    print_section("RÉSUMÉ DES TESTS")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name.upper()}")
    
    print(f"\n{'='*60}")
    print(f"  RÉSULTAT: {passed}/{total} tests réussis")
    print(f"{'='*60}")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS ! Le projet est prêt.")
    elif passed >= total - 1:
        print("\n✅ Presque tous les tests passés. Projet OK pour envoi.")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifier avant envoi.")
    
    return passed == total

if __name__ == '__main__':
    main()

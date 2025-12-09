"""
Script de test complet pour valider l'intégration SQLite
"""
import requests
import json
from colorama import init, Fore, Style

# Initialiser colorama
init(autoreset=True)

BASE_URL = "http://127.0.0.1:5000"

def print_test(name, success, details=""):
    """Afficher le résultat d'un test."""
    status = f"{Fore.GREEN}✅ PASS" if success else f"{Fore.RED}❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"   {Fore.CYAN}{details}")
    print()

def test_api_documentation():
    """Test 1 : Documentation de l'API."""
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}Test 1 : Documentation de l'API")
    print(f"{Fore.YELLOW}{'='*60}\n")
    
    try:
        r = requests.get(f"{BASE_URL}/api")
        data = r.json()
        
        success = (
            r.status_code == 200 and
            'name' in data and
            'SQLite' in data.get('database', '')
        )
        
        print_test(
            "Documentation API",
            success,
            f"Version: {data.get('version', 'N/A')}, DB: {data.get('database', 'N/A')}"
        )
        return success
    except Exception as e:
        print_test("Documentation API", False, str(e))
        return False

def test_search_crash_avion():
    """Test 2 : Recherche critique SAE - 'crash avion ile'."""
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}Test 2 : Recherche SAE - 'crash avion ile'")
    print(f"{Fore.YELLOW}{'='*60}\n")
    
    try:
        r = requests.get(f"{BASE_URL}/api/search?q=crash+avion+ile&limit=3")
        data = r.json()
        
        if r.status_code == 200 and data.get('results'):
            top_result = data['results'][0]
            is_lost = 'lost' in top_result['title'].lower()
            
            print_test(
                "Test SAE : Lost en position #1",
                is_lost,
                f"Top 1: {top_result['title']} (score: {top_result['score']})"
            )
            
            # Afficher le top 3
            print(f"{Fore.CYAN}   Top 3 résultats:")
            for i, result in enumerate(data['results'][:3], 1):
                print(f"   {i}. {result['title']} - Score: {result['score']}")
            print()
            
            return is_lost
        else:
            print_test("Test SAE : Lost en position #1", False, "Aucun résultat")
            return False
    except Exception as e:
        print_test("Test SAE : Lost en position #1", False, str(e))
        return False

def test_series_stats():
    """Test 3 : Statistiques de la base de données."""
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}Test 3 : Statistiques de la base de données")
    print(f"{Fore.YELLOW}{'='*60}\n")
    
    try:
        r = requests.get(f"{BASE_URL}/api/series/stats")
        data = r.json()
        
        success = (
            r.status_code == 200 and
            data.get('total_series', 0) == 250 and
            data.get('total_users', 0) == 6
        )
        
        details = (
            f"Séries: {data.get('total_series')}, "
            f"Users: {data.get('total_users')}, "
            f"Notes: {data.get('total_ratings')}, "
            f"Moyenne: {data.get('average_rating')}/5"
        )
        
        print_test("Statistiques BD", success, details)
        return success
    except Exception as e:
        print_test("Statistiques BD", False, str(e))
        return False

def test_series_details():
    """Test 4 : Détails d'une série (Lost VF)."""
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}Test 4 : Détails de Lost VF")
    print(f"{Fore.YELLOW}{'='*60}\n")
    
    try:
        r = requests.get(f"{BASE_URL}/api/series/lost_vf")
        data = r.json()
        
        success = (
            r.status_code == 200 and
            data.get('title') == 'lost_vf' and
            data.get('num_keywords', 0) > 0
        )
        
        details = (
            f"Note: {data.get('average_rating')}/5, "
            f"Mots-clés: {data.get('num_keywords')}, "
            f"Notes: {data.get('num_ratings')}"
        )
        
        if success:
            top_keywords = [kw['keyword'] for kw in data.get('keywords', [])[:5]]
            details += f"\nTop keywords: {', '.join(top_keywords)}"
        
        print_test("Détails Lost VF", success, details)
        return success
    except Exception as e:
        print_test("Détails Lost VF", False, str(e))
        return False

def test_users_list():
    """Test 5 : Liste des utilisateurs."""
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}Test 5 : Liste des utilisateurs")
    print(f"{Fore.YELLOW}{'='*60}\n")
    
    try:
        r = requests.get(f"{BASE_URL}/api/users")
        data = r.json()
        
        success = (
            r.status_code == 200 and
            len(data) == 6 and
            any(u['username'] == 'alice' for u in data)
        )
        
        print_test("Liste utilisateurs", success, f"{len(data)} utilisateurs trouvés")
        
        if success:
            print(f"{Fore.CYAN}   Utilisateurs:")
            for user in data:
                print(f"   - {user['username']} ({user['language_preference']}) - {user['num_ratings']} notes")
            print()
        
        return success
    except Exception as e:
        print_test("Liste utilisateurs", False, str(e))
        return False

def test_recommendations_popularity():
    """Test 6 : Recommandations par popularité."""
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}Test 6 : Recommandations par popularité")
    print(f"{Fore.YELLOW}{'='*60}\n")
    
    try:
        r = requests.get(f"{BASE_URL}/api/recommend/popularity?limit=5")
        data = r.json()
        
        success = (
            r.status_code == 200 and
            'recommendations' in data and
            len(data['recommendations']) > 0
        )
        
        print_test("Recommandations popularité", success, f"{len(data.get('recommendations', []))} recommandations")
        
        if success:
            print(f"{Fore.CYAN}   Top 5 populaires:")
            for i, rec in enumerate(data['recommendations'][:5], 1):
                print(f"   {i}. {rec['title']} - Note: {rec['average_rating']} ({rec['num_ratings']} notes)")
            print()
        
        return success
    except Exception as e:
        print_test("Recommandations popularité", False, str(e))
        return False

def test_recommendations_collaborative():
    """Test 7 : Recommandations collaboratives pour Alice."""
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}Test 7 : Recommandations collaboratives (Alice)")
    print(f"{Fore.YELLOW}{'='*60}\n")
    
    try:
        r = requests.get(f"{BASE_URL}/api/recommend/collaborative/1")
        data = r.json()
        
        success = (
            r.status_code == 200 and
            'recommendations' in data
        )
        
        num_recs = len(data.get('recommendations', []))
        print_test("Recommandations collaboratives", success, f"{num_recs} recommandations")
        
        if success and num_recs > 0:
            print(f"{Fore.CYAN}   Top 3 pour Alice:")
            for i, rec in enumerate(data['recommendations'][:3], 1):
                print(f"   {i}. {rec['title']} - Score: {rec['score']}")
            print()
        
        return success
    except Exception as e:
        print_test("Recommandations collaboratives", False, str(e))
        return False

def test_keywords_search():
    """Test 8 : Recherche par mot-clé."""
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}Test 8 : Recherche par mot-clé 'ile'")
    print(f"{Fore.YELLOW}{'='*60}\n")
    
    try:
        r = requests.get(f"{BASE_URL}/api/search/keyword?keyword=ile&limit=5")
        data = r.json()
        
        success = (
            r.status_code == 200 and
            'results' in data and
            len(data['results']) > 0
        )
        
        print_test("Recherche par mot-clé", success, f"{len(data.get('results', []))} résultats")
        
        if success:
            print(f"{Fore.CYAN}   Séries avec 'ile':")
            for i, result in enumerate(data['results'][:5], 1):
                print(f"   {i}. {result['title']} - Mot-clé: {result['matched_keyword']}")
            print()
        
        return success
    except Exception as e:
        print_test("Recherche par mot-clé", False, str(e))
        return False

def test_add_rating():
    """Test 9 : Ajouter une note."""
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}Test 9 : Ajouter une note")
    print(f"{Fore.YELLOW}{'='*60}\n")
    
    try:
        # Ajouter une note pour alice sur lost_vf
        payload = {
            'user_id': 1,
            'series_title': 'lost_vf',
            'rating': 5
        }
        
        r = requests.post(f"{BASE_URL}/api/ratings", json=payload)
        data = r.json()
        
        success = (
            r.status_code == 200 and
            data.get('success', False)
        )
        
        print_test("Ajout de note", success, data.get('message', ''))
        return success
    except Exception as e:
        print_test("Ajout de note", False, str(e))
        return False

def test_series_list():
    """Test 10 : Liste des séries (avec filtre VF)."""
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}Test 10 : Liste des séries VF")
    print(f"{Fore.YELLOW}{'='*60}\n")
    
    try:
        r = requests.get(f"{BASE_URL}/api/series?language=vf&limit=5")
        data = r.json()
        
        success = (
            r.status_code == 200 and
            len(data) > 0 and
            all(s['language'] == 'vf' for s in data)
        )
        
        print_test("Liste séries VF", success, f"{len(data)} séries")
        
        if success:
            print(f"{Fore.CYAN}   Premières 5 séries VF:")
            for serie in data[:5]:
                print(f"   - {serie['title']} - Note: {serie['average_rating']}")
            print()
        
        return success
    except Exception as e:
        print_test("Liste séries VF", False, str(e))
        return False

def main():
    """Exécuter tous les tests."""
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}🧪 TESTS D'INTÉGRATION SQLITE - SAE501")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    print(f"{Fore.CYAN}URL de test : {BASE_URL}")
    print(f"{Fore.CYAN}Base de données : SQLite (data/tvseries.db)\n")
    
    tests = [
        test_api_documentation,
        test_search_crash_avion,
        test_series_stats,
        test_series_details,
        test_users_list,
        test_recommendations_popularity,
        test_recommendations_collaborative,
        test_keywords_search,
        test_add_rating,
        test_series_list
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"{Fore.RED}Erreur lors du test : {e}\n")
            results.append(False)
    
    # Résumé
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}📊 RÉSUMÉ DES TESTS")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"{Fore.GREEN}✅ Tests réussis : {passed}/{total} ({percentage:.1f}%)")
    print(f"{Fore.RED}❌ Tests échoués : {total - passed}/{total}")
    
    if passed == total:
        print(f"\n{Fore.GREEN}🎉 TOUS LES TESTS SONT PASSÉS !")
        print(f"{Fore.GREEN}✅ Intégration SQLite validée")
        print(f"{Fore.GREEN}✅ Exigence SAE remplie (Lost #1)")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Certains tests ont échoué")
    
    print(f"\n{Fore.CYAN}Base de données : data/tvseries.db")
    print(f"{Fore.CYAN}Documentation : DATABASE_SQLITE_README.md")
    print(f"{Fore.CYAN}Projet complet : PROJET_FINAL_README.md\n")

if __name__ == '__main__':
    main()

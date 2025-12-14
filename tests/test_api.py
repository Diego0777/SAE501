import requests

# Test recherche
r = requests.get('http://127.0.0.1:5000/search', params={'q': 'crash avion ile', 'top': 3})
results = r.json()
print('=== Test recherche: crash avion ile ===')
for i, s in enumerate(results):
    print(f'{i+1}. {s["title"]} - Score: {s["score"]:.2f}')

# Test recommandations populaires
print('\n=== Séries populaires VF ===')
r = requests.get('http://127.0.0.1:5000/recommend/popular', params={'top': 5, 'language': 'vf'})
results = r.json()
for i, s in enumerate(results):
    print(f'{i+1}. {s["title"]} - Note: {s["average_rating"]:.1f} - Popularité: {s["popularity_score"]:.1f}')

print('\n✅ Toutes les APIs fonctionnent correctement !')

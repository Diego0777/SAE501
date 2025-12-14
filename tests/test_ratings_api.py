import requests

# Alice a l'ID 31
r = requests.get('http://127.0.0.1:5000/api/ratings?user_id=31')
print(f'Status: {r.status_code}')
data = r.json()
print(f'Ratings count: {len(data)}')
print('\nAlice ratings:')
for item in data[:10]:
    print(f"  {item['serie_title']}: {item['rating']}/5")

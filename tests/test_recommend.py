import requests

# Test recommandations collaborative pour alice (ID 41)
r = requests.get('http://127.0.0.1:5000/api/recommend/collaborative/41')
print(f'Status: {r.status_code}')
data = r.json()
print(f'Method: {data.get("method")}')
print(f'Message: {data.get("message", "No message")}')
print(f'Recommendations count: {len(data.get("recommendations", []))}')

if data.get("recommendations"):
    print('\nFirst 5 recommendations:')
    for item in data['recommendations'][:5]:
        print(f"  {item['title']}: {item.get('predicted_rating', 0):.2f}/5")

import requests

pages = ['search.html', 'series.html', 'recommendations.html', 'profile.html', 'series-details.html']
print("Test pages frontend:")
for p in pages:
    r = requests.get(f"http://127.0.0.1:5000/{p}")
    print(f"  {p}: {r.status_code}")

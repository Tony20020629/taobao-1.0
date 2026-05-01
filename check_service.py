import urllib.request
import json

try:
    url = 'http://localhost:8000/api/goods'
    response = urllib.request.urlopen(url, timeout=5)
    data = json.loads(response.read().decode('utf-8'))
    
    print('Backend service is RUNNING!')
    print(f'Goods count: {len(data)}')
    for g in data:
        print(f'  - ID: {g["id"]}, Name: {g["name"]}, Price: {g["current_price"]}')
except Exception as e:
    print(f'Backend service is NOT running: {e}')

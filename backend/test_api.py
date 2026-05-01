# -*- coding: utf-8 -*-
import urllib.request
import json

url = 'http://localhost:8000/api/goods/9/collect-now'
print(f'Calling API: POST {url}')

req = urllib.request.Request(url, method='POST')
try:
    response = urllib.request.urlopen(req, timeout=120)
    data = json.loads(response.read().decode('utf-8'))
    print('\n' + '='*60)
    print('Result:')
    print('='*60)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print('='*60)
except Exception as e:
    print(f'\nError: {e}')
    # Try to read error response
    try:
        if hasattr(e, 'read'):
            body = e.read().decode('utf-8')
            print(f'Response: {body}')
    except:
        pass

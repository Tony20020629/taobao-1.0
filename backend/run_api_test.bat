@echo off
cd /d e:\NewProject\taobao\backend
echo Testing Price Collection API...
C:\Users\22343\.conda\envs\taobao\python.exe -c "import urllib.request, json; req = urllib.request.Request('http://localhost:8000/api/goods/9/collect-now', method='POST'); resp = urllib.request.urlopen(req, timeout=120); data = json.loads(resp.read()); print('Result:', json.dumps(data, indent=2, ensure_ascii=False))" > test_result.txt 2>&1
type test_result.txt
echo.
echo Done! Check test_result.txt for results.
pause

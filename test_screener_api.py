import httpx
import json

url = "http://127.0.0.1:8000/api/screener"
data = {"strategy": "value", "query": "市盈率小于 20 且 ROE 大于 15% 且 市值前 50"}

print(f"POST {url}")
print(f"Data: {json.dumps(data, ensure_ascii=False)}\n")

try:
    with httpx.Client(timeout=90.0) as client:
        resp = client.post(url, json=data)
        print(f"Status: {resp.status_code}")
        result = resp.json()
        print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"Error: {e}")

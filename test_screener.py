import httpx
import json

url = "http://127.0.0.1:8000/api/screener"
data = {"query": "股价>100"}

print(f"POST {url}")
print(f"Query: {data['query']}\n")

try:
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, json=data)
        print(f"Status: {resp.status_code}")
        result = resp.json()
        print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"Error: {e}")

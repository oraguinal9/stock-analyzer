import httpx
import json

url = "http://127.0.0.1:8000/api/stock/query"
data = {"query": "300750"}

print(f"Testing query for stock: 300750 (宁德时代)\n")

try:
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, json=data)
        print(f"Status: {resp.status_code}")
        result = resp.json()
        print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"Error: {e}")

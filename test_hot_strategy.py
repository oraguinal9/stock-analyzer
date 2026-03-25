import httpx
import json

url = "http://127.0.0.1:8000/api/screener"
data = {"strategy": "hot", "query": "涨幅大于 5% 且 换手率大于 3%"}

print(f"Testing Hot Strategy:\n")

try:
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, json=data)
        result = resp.json()
        print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"Error: {e}")

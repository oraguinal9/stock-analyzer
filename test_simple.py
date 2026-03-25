import httpx

url = "http://127.0.0.1:8000/api/stock/query"
data = {"query": "比亚迪 002594", "select_type": "A 股"}

print(f"POST {url}")
print(f"Data: {data}")

try:
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, json=data)
        print(f"\nStatus: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

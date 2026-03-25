import httpx

url = "http://127.0.0.1:8000/api/sectors/hot"

print(f"GET {url}\n")

try:
    with httpx.Client(timeout=60.0) as client:
        resp = client.get(url)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")

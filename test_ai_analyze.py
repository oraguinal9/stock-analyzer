import httpx
import json

# 1. 查询股票
url_query = "http://127.0.0.1:8000/api/stock/query"
data_query = {"query": "300750"}

print("=" * 60)
print("Step 1: Query stock 300750")
print("=" * 60)

try:
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url_query, json=data_query)
        result = resp.json()
        if result.get("success"):
            stock = result.get("data", {})
            print(f"[OK] Stock: {stock.get('name')} ({stock.get('code')})")
            print(f"  Price: {stock.get('price')}")
            print(f"  Change: {stock.get('change_pct')}%")
        else:
            print(f"[ERROR] {result.get('data')}")
except Exception as e:
    print(f"✗ Error: {e}")

# 2. AI 分析
print("\n" + "=" * 60)
print("Step 2: AI Analysis")
print("=" * 60)

url_analyze = "http://127.0.0.1:8000/api/stock/analyze"
data_analyze = {"query": "300750"}

try:
    with httpx.Client(timeout=120.0) as client:
        print("  Sending request...")
        resp = client.post(url_analyze, json=data_analyze)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get("success"):
                report = result.get("data", {}).get("report", {})
                print(f"[OK] Report generated")
                print(f"  Rating: {report.get('rating')}")
                print(f"  Score: {report.get('score')}/100")
                print(f"  Summary: {report.get('summary', '')[:100]}...")
            else:
                print(f"[ERROR] {result.get('message')}")
        else:
            print(f"[ERROR] HTTP {resp.status_code}")
            print(f"  Content: {resp.text[:200]}")
except Exception as e:
    print(f"[ERROR] {e}")

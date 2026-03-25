import httpx
import json

url = "http://127.0.0.1:8000/api/stock/query"
data = {"query": "002594"}

print(f"Testing API for 002594 (比亚迪):\n")

try:
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, json=data)
        result = resp.json()
        
        if result.get("success"):
            stock = result.get("data", {})
            print(f"Code: {stock.get('code')}")
            print(f"Name: {stock.get('name')}")
            print(f"Price: {stock.get('price')}")
            print(f"Change%: {stock.get('change_pct')}")
            print(f"PE: {stock.get('pe')}")
            print(f"PB: {stock.get('pb')}")
            print(f"Turnover: {stock.get('turnover')}")
            print(f"Volume Ratio: {stock.get('volume_ratio')}")
            print(f"Market Cap: {stock.get('market_cap', 0)/1e8:.2f}亿")
        else:
            print(f"Error: {result}")
            
except Exception as e:
    print(f"Error: {e}")

import httpx
import json

url = "http://127.0.0.1:8000/api/screener"
data = {"strategy": "value", "query": "市盈率小于 20 且 ROE 大于 15% 且 市值前 50"}

print(f"Testing Smart Screener - Value Strategy:\n")
print("=" * 60)

try:
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, json=data)
        result = resp.json()
        
        if result.get("success"):
            stocks = result.get("data", [])
            print(f"Found {len(stocks)} stocks\n")
            
            if stocks:
                print(f"{'Code':<8} {'Name':<15} {'Price':<10} {'PE':<8} {'PB':<8} {'ROE':<8} {'Turnover':<10}")
                print("-" * 80)
                for stock in stocks[:10]:
                    print(f"{stock.get('code', 'N/A'):<8} {stock.get('name', 'N/A'):<15} {stock.get('price', 0):<10.2f} {stock.get('pe', 0):<8.2f} {stock.get('pb', 0):<8.2f} {stock.get('roe', 0):<8.2f} {stock.get('turnover', 0):<10.2f}%")
        else:
            print(f"Error: {result}")
            
except Exception as e:
    print(f"Error: {e}")

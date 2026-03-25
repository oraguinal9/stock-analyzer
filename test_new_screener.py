import httpx
import json

url = "http://127.0.0.1:8000/api/screener"

strategies = [
    {"strategy": "value", "query": "市盈率小于 20 且 ROE 大于 15% 且 市值前 50"},
    {"strategy": "hot", "query": "涨幅大于 5% 且 换手率大于 3%"},
]

for s in strategies:
    print(f"\n{'='*60}")
    print(f"Testing Strategy: {s['strategy']}")
    print(f"Query: {s['query']}")
    print('='*60)
    
    try:
        with httpx.Client(timeout=90.0) as client:
            resp = client.post(url, json=s)
            print(f"Status: {resp.status_code}")
            result = resp.json()
            
            if result.get("success"):
                stocks = result.get("data", [])
                print(f"[OK] Found {len(stocks)} stocks")
                
                if stocks:
                    print(f"\nTop 5 stocks:")
                    for i, stock in enumerate(stocks[:5], 1):
                        print(f"{i}. {stock.get('code')} - {stock.get('name')} - PE:{stock.get('pe')} - ROE:{stock.get('roe')}%")
            else:
                print(f"[ERROR] {result.get('message')}")
                
    except Exception as e:
        print(f"[ERROR] {e}")

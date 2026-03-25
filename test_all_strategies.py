import httpx
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "http://127.0.0.1:8000/api/screener"

strategies = [
    ("value", "价值投资"),
    ("growth", "成长龙头"),
    ("hot", "今日强势"),
    ("dividend", "高股息防御"),
    ("tech", "科技成长"),
    ("breakout", "突破新高"),
    ("lowrisk", "低风险稳健"),
    ("north", "北向重仓"),
]

print("=" * 70)
print("  智能选股 - 全策略测试")
print("=" * 70)

for strategy_id, strategy_name in strategies:
    print(f"\n--- {strategy_name} ({strategy_id}) ---")
    
    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, json={"strategy": strategy_id, "query": ""})
            result = resp.json()
            
            stocks = result.get("data", [])
            print(f"  结果: {len(stocks)} 只股票")
            
            for s in stocks[:3]:
                print(f"  {s.get('code')} {s.get('name'):<8} 价格:{s.get('price'):>8.2f} PE:{s.get('pe'):>6.1f} PB:{s.get('pb'):>5.2f} 涨跌:{s.get('change_pct'):>+6.2f}%")
            
            if len(stocks) > 3:
                print(f"  ... 还有 {len(stocks)-3} 只")
                
    except Exception as e:
        print(f"  [ERROR] {e}")

print("\n" + "=" * 70)
print("  测试完成")
print("=" * 70)

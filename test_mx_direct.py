"""直接测试 MiaoXiangAPI 类"""
import sys
sys.path.insert(0, r"C:\Users\admin\.openclaw\workspace\stock-analyzer-web")

from app.services.mx_api import MiaoXiangAPI
from app.utils.config import config

print(f"EM_API_KEY from config: {config.em_api_key[:10]}...")

mx = MiaoXiangAPI()
print(f"MX_API instance created")
print(f"MX_API key: {mx.api_key[:10]}...")

print("\nQuerying stock: 比亚迪 002594")
quote = mx.query_stock("比亚迪 002594", "A 股")

if quote:
    print(f"\nSuccess!")
    print(f"Code: {quote.code}")
    print(f"Name: {quote.name}")
    print(f"Price: {quote.price}")
    print(f"Change: {quote.change_pct}%")
else:
    print("\nFailed to query stock")

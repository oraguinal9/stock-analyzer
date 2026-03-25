import sys
sys.path.insert(0, r"C:\Users\admin\.openclaw\workspace\stock-analyzer-web")

from app.routes.api import parse_sectors_csv

sectors = parse_sectors_csv(r"C:\Users\admin\.openclaw\workspace\stock-analyzer-web\data\cache\mx_stocks_screener_3c878a47.csv")

print(f"Found {len(sectors)} sectors\n")
for i, s in enumerate(sectors[:5], 1):
    print(f"{i}. {s['name']} ({s['code']}) - {s['change_pct']}%")

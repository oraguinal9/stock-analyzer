import os, sys, asyncio

sys.path.insert(0, r"C:\Users\admin\AppData\Roaming\npm\node_modules\openclaw\skills\mx_stocks_screener")

os.environ["EM_API_KEY"] = "em_yLbSsg0pQvuU84DfS80bk3feU14OgJuB"
os.environ["MX_STOCKS_SCREENER_OUTPUT_DIR"] = r"C:\Users\admin\.openclaw\workspace\stock-analyzer-web\data\cache"

from scripts.get_data import query_mx_stocks_screener
from pathlib import Path

async def main():
    tests = [
        "股价最高的股票",
        "高价股",
        "股价>100",
        "市盈率小于 20",
    ]
    
    for query in tests:
        print(f"\n{'='*50}")
        print(f"[TEST] Query: {query}")
        print('='*50)
        result = await query_mx_stocks_screener(
            query=query,
            selectType="A 股",
            output_dir=Path(r"C:\Users\admin\.openclaw\workspace\stock-analyzer-web\data\cache"),
        )
        print(f"Result: {result.get('row_count', 0)} rows")
        if result.get('csv_path'):
            print(f"CSV: {result['csv_path']}")

asyncio.run(main())

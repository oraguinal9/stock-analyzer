import os, sys, asyncio

sys.path.insert(0, r"C:\Users\admin\AppData\Roaming\npm\node_modules\openclaw\skills\mx_stocks_screener")

os.environ["EM_API_KEY"] = "em_yLbSsg0pQvuU84DfS80bk3feU14OgJuB"
os.environ["MX_STOCKS_SCREENER_OUTPUT_DIR"] = r"C:\Users\admin\.openclaw\workspace\stock-analyzer-web\data\cache"

from scripts.get_data import query_mx_stocks_screener
from pathlib import Path

async def main():
    print("[TEST] Query: 股价大于 100 元")
    result = await query_mx_stocks_screener(
        query="股价大于 100 元",
        selectType="A 股",
        output_dir=Path(r"C:\Users\admin\.openclaw\workspace\stock-analyzer-web\data\cache"),
    )
    print(f"\nResult: {result}")
    
    if "csv_path" in result:
        print(f"\nCSV Path: {result['csv_path']}")
        csv_path = Path(result['csv_path'])
        if csv_path.exists():
            print(f"\nCSV Content (first 5 lines):")
            with open(csv_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i < 5:
                        print(line.strip())
                    else:
                        break

asyncio.run(main())

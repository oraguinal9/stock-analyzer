import os, sys, asyncio

sys.path.insert(0, r"C:\Users\admin\AppData\Roaming\npm\node_modules\openclaw\skills\mx_stocks_screener")

os.environ["EM_API_KEY"] = "em_yLbSsg0pQvuU84DfS80bk3feU14OgJuB"
os.environ["MX_STOCKS_SCREENER_OUTPUT_DIR"] = r"C:\Users\admin\.openclaw\workspace\stock-analyzer-web\data\cache"

from scripts.get_data import query_mx_stocks_screener
from pathlib import Path

async def main():
    tests = [
        "股价大于 100 元的股票",
        "市盈率小于 20 的股票",
        "市值前 50 的股票",
        "北向资金增持的股票",
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
        print(f"Rows: {result.get('row_count', 0)}")
        if result.get('csv_path'):
            csv_name = result['csv_path'].split('\\')[-1]
            print(f"CSV: {csv_name}")
            # 显示 CSV 前几行
            try:
                with open(result['csv_path'], 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:3]
                    for line in lines:
                        print(line.strip()[:100])
            except:
                pass
        else:
            print(f"Error: {result.get('error', 'Unknown')}")

asyncio.run(main())

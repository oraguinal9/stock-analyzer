"""测试妙想 API"""
import os
import sys
import asyncio
import io

# 设置 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 设置环境变量
os.environ["EM_API_KEY"] = "em_yLbSsg0pQvuU84DfS80bk3feU14OgJuB"
os.environ["MX_STOCKS_SCREENER_OUTPUT_DIR"] = r"C:\Users\admin\.openclaw\workspace\stock-analyzer-web\data\cache"

# 添加妙想脚本路径
sys.path.insert(0, r"C:\Users\admin\AppData\Roaming\npm\node_modules\openclaw\skills\mx_stocks_screener")

from scripts.get_data import query_mx_stocks_screener
from pathlib import Path

async def main():
    print("[TEST] Query: BYD 002594")
    result = await query_mx_stocks_screener(
        query="比亚迪 002594",
        selectType="A 股",
        output_dir=Path(r"C:\Users\admin\.openclaw\workspace\stock-analyzer-web\data\cache"),
    )
    print(f"\n[RESULT] {result}")
    
    if "csv_path" in result:
        print(f"\n[CSV PATH] {result['csv_path']}")
        csv_path = Path(result['csv_path'])
        if csv_path.exists():
            print(f"\n[CSV CONTENT]:")
            with open(csv_path, 'r', encoding='utf-8') as f:
                print(f.read())

if __name__ == "__main__":
    asyncio.run(main())

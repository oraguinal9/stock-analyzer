
import os
import sys
import asyncio
sys.path.insert(0, r"C:\Users\admin\AppData\Roaming\npm\node_modules\openclaw\skills\mx_stocks_screener")

os.environ["EM_API_KEY"] = "em_yLbSsg0pQvuU84DfS80bk3feU14OgJuB"
os.environ["MX_STOCKS_SCREENER_OUTPUT_DIR"] = r"data\cache"

from scripts.get_data import query_mx_stocks_screener
from pathlib import Path

async def main():
    result = await query_mx_stocks_screener(
        query="300750 股票",
        selectType="A 股",
        output_dir=Path(r"data\cache"),
    )
    print(result.get("csv_path", ""))

asyncio.run(main())

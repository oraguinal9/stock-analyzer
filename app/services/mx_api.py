"""
东方财富妙想 API 服务
"""
import asyncio
import csv
import httpx
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.utils.config import config
from app.utils.logger import get_logger
from app.models.stock import StockQuote, StockData, FinancialData

logger = get_logger("mx_api")


class MiaoXiangAPI:
    """东方财富妙想 API 封装"""
    
    BASE_DIR = Path(__file__).parent.parent.parent
    # 使用相对路径，支持跨平台部署
    MX_DIR = BASE_DIR.parent.parent / "mx_stocks_screener"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.em_api_key
        self.output_dir = self.BASE_DIR / "data" / "cache"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.api_key:
            logger.warning("EM_API_KEY not configured")
    
    def query_stock_sync(self, query: str, select_type: str = "A 股") -> Optional[StockData]:
        """
        查询股票数据（同步方式）
        
        Args:
            query: 查询条件（股票代码或名称）
            select_type: 资产类型（A 股/港股/美股等）
        
        Returns:
            StockData 对象
        """
        if not self.api_key:
            logger.error("API Key not configured")
            return None
        
        try:
            script_path = self.MX_DIR / "scripts" / "get_data.py"
            
            if not script_path.exists():
                logger.error(f"Script not found: {script_path}")
                return None
            
            # 创建 Python 包装脚本来避免编码问题
            wrapper_script = self.output_dir / "query_wrapper.py"
            wrapper_content = f'''
import os
import sys
import asyncio
sys.path.insert(0, r"{self.MX_DIR}")

os.environ["EM_API_KEY"] = "{self.api_key}"
os.environ["MX_STOCKS_SCREENER_OUTPUT_DIR"] = r"{self.output_dir}"

from scripts.get_data import query_mx_stocks_screener
from pathlib import Path

async def main():
    result = await query_mx_stocks_screener(
        query="{query}",
        selectType="{select_type}",
        output_dir=Path(r"{self.output_dir}"),
    )
    print(result.get("csv_path", ""))

asyncio.run(main())
'''
            wrapper_script.write_text(wrapper_content, encoding='utf-8')
            
            cmd = [sys.executable, str(wrapper_script)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )
            
            csv_path = result.stdout.strip()
            
            # 清理路径（移除可能的额外输出）
            for line in csv_path.split('\n'):
                line = line.strip()
                if '.csv' in line and 'mx_stocks_screener' in line:
                    csv_path = line
                    break
            
            if csv_path and '.csv' in csv_path:
                p = Path(csv_path)
                if p.exists():
                    logger.info(f"CSV found: {p}")
                    return self._parse_csv(str(p))
                # 尝试相对路径
                p = self.output_dir / csv_path.split('/')[-1].split('\\')[-1]
                if p.exists():
                    logger.info(f"CSV found (relative): {p}")
                    return self._parse_csv(str(p))
            
            logger.error(f"No CSV found. Output: {result.stdout[:500]}")
            return None
            
        except subprocess.TimeoutExpired:
            logger.error("Query timeout")
            return None
        except Exception as e:
            logger.error(f"Query error: {e}")
            return None
    
    async def query_stock(self, query: str, select_type: str = "A 股") -> Optional[StockData]:
        """异步查询股票"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.query_stock_sync, query, select_type)
    
    def _parse_csv(self, csv_path: str) -> Optional[StockData]:
        """解析 CSV 文件为 StockData"""
        try:
            # 尝试多种编码
            for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
                try:
                    with open(csv_path, "r", encoding=encoding) as f:
                        content = f.read()
                        break
                except:
                    continue
            else:
                logger.error("Failed to read CSV with any encoding")
                return None
            
            if content.startswith('\ufeff'):
                content = content[1:]
            
            lines = content.strip().split('\n')
            if len(lines) < 2:
                return None
            
            headers = lines[0].split(',')
            values = lines[1].split(',')
            
            # 创建映射（处理乱码的列名）
            data = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    # 根据列位置映射
                    if i == 0: data['序号'] = values[i]
                    elif i == 1: data['代码'] = values[i]
                    elif i == 2: data['名称'] = values[i]
                    elif i == 3: data['市场代码简称'] = values[i]
                    elif i == 4: data['最新价 (元)'] = values[i]
                    elif i == 5: data['涨跌幅 (%)'] = values[i]
                    elif i == 6: data['总市值 (元)'] = values[i]
                    elif i == 7: data['涨跌额 (元)'] = values[i]
                    elif i == 8: data['最高价 (元)'] = values[i]
                    elif i == 9: data['最低价 (元)'] = values[i]
                    elif i == 10: data['换手率 (%)'] = values[i]
                    elif i == 11: data['量比'] = values[i]
                    elif i == 12: data['成交量 (股)'] = values[i]
                    elif i == 13: data['成交额 (元)'] = values[i]
                    elif i == 14: data['市盈率 (动)(倍)'] = values[i]
                    elif i == 15: data['市净率 (倍)'] = values[i]
                    elif i == 16: data['流通市值 (元)'] = values[i]
            
            stock_data = StockData()
            stock_data.quote = self._parse_quote(data)
            
            return stock_data
                
        except Exception as e:
            logger.error(f"Parse CSV error: {e}")
            return None
    
    def _parse_quote(self, data: Dict[str, str]) -> StockQuote:
        """解析行情数据"""
        def parse_num(val: str, default: float = 0.0) -> float:
            if not val:
                return default
            try:
                s = str(val).strip().replace(',', '')
                if '亿' in s:
                    return float(s.replace('亿', '')) * 1e8
                elif '万' in s:
                    return float(s.replace('万', '')) * 1e4
                return float(s)
            except:
                return default
        
        quote = StockQuote()
        quote.code = data.get('代码', '')
        quote.name = data.get('名称', '')
        quote.market = data.get('市场代码简称', '')
        quote.price = parse_num(data.get('最新价 (元)', '0'))
        quote.change_pct = parse_num(data.get('涨跌幅 (%)', '0'))
        quote.change_amount = parse_num(data.get('涨跌额 (元)', '0'))
        quote.high = parse_num(data.get('最高价 (元)', '0'))
        quote.low = parse_num(data.get('最低价 (元)', '0'))
        quote.turnover = parse_num(data.get('换手率 (%)', '0'))
        quote.volume_ratio = parse_num(data.get('量比', '0'))
        quote.pe = parse_num(data.get('市盈率 (动)(倍)', '0'))
        quote.pb = parse_num(data.get('市净率 (倍)', '0'))
        quote.market_cap = parse_num(data.get('总市值 (元)', '0'))
        quote.float_market_cap = parse_num(data.get('流通市值 (元)', '0'))
        
        volume_str = data.get('成交量 (股)', '0')
        amount_str = data.get('成交额 (元)', '0')
        quote.volume = int(parse_num(volume_str))
        quote.amount = parse_num(amount_str)
        
        return quote
    
    async def get_hot_sectors(self) -> List[Dict[str, Any]]:
        """获取热门板块"""
        try:
            result = self.query_stock_sync("今天涨幅最大板块", "板块")
            if result:
                return [{"name": result.quote.name, **result.quote.to_dict()}]
            return []
        except Exception as e:
            logger.error(f"Get hot sectors error: {e}")
            return []
    
    async def screen_stocks(self, query: str) -> List[StockQuote]:
        """智能选股"""
        try:
            result = self.query_stock_sync(query, "A 股")
            if result:
                return [result.quote]
            return []
        except Exception as e:
            logger.error(f"Screen stocks error: {e}")
            return []


# 全局 API 实例
mx_api = MiaoXiangAPI()

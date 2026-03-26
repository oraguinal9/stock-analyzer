"""
API 路由
"""
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.services.mx_api import MiaoXiangAPI, StockQuote
from app.services.ai_analyzer import AIAnalyzer
from app.services.stock_data import StockDataService, stock_data_service
from app.utils.config import config
from app.utils.logger import get_logger

logger = get_logger("api")

router = APIRouter()

# 初始化服务
mx_api = MiaoXiangAPI()
ai_analyzer = AIAnalyzer()
stock_service = StockDataService()


class StockQuery(BaseModel):
    """股票查询请求"""
    query: str
    select_type: Optional[str] = "A 股"


class SettingsUpdate(BaseModel):
    """设置更新请求"""
    em_api_key: Optional[str] = None
    qwen_api_key: Optional[str] = None


@router.post("/stock/query")
async def query_stock(data: StockQuery) -> Dict[str, Any]:
    """查询股票数据"""
    # 使用腾讯 HTTP API（不依赖本地脚本）
    quote = stock_service.get_stock_quote(data.query)
    
    if not quote or not quote.get('name'):
        raise HTTPException(status_code=404, detail="未找到股票")
    
    return {
        "success": True,
        "data": quote
    }


@router.post("/stock/analyze")
async def analyze_stock(data: StockQuery) -> Dict[str, Any]:
    """分析股票"""
    # 使用腾讯 HTTP API（不依赖本地脚本）
    quote = stock_service.get_stock_quote(data.query)
    
    if not quote or not quote.get('name'):
        raise HTTPException(status_code=404, detail="未找到股票")
    
    # 转换为 StockData 对象供 AI 分析器使用
    from app.models.stock import StockData
    stock_data = StockData(**quote)
    report = ai_analyzer.analyze_stock(stock_data)
    
    return {
        "success": True,
        "data": {
            "quote": quote,
            "report": report
        }
    }


@router.get("/reports")
async def get_reports() -> Dict[str, Any]:
    """获取所有报告"""
    import os
    from pathlib import Path
    
    reports_dir = Path(config.get("output.reports_dir", "./data/reports"))
    reports = []
    
    if reports_dir.exists():
        for f in sorted(reports_dir.glob("*.md"), reverse=True):
            try:
                content = f.read_text(encoding='utf-8')
                # 解析报告元数据
                lines = content.split('\n')
                report = {
                    "id": f.stem.split('_')[2] if len(f.stem.split('_')) > 2 else f.stem,
                    "filename": f.name,
                    "content": content
                }
                
                for line in lines[:10]:
                    if "**报告 ID**:" in line:
                        report["id"] = line.split(":")[1].strip()
                    elif "**生成时间**:" in line:
                        report["created_at"] = line.split(":")[1].strip()
                    elif "**评级**:" in line:
                        report["rating"] = line.split(":")[1].strip()
                    elif "**评分**:" in line:
                        report["score"] = int(line.split(":")[1].strip().replace('/100', ''))
                    elif "# " in line and "(" in line:
                        # 提取股票名称和代码
                        import re
                        match = re.search(r'# (.+?) \((\d+)\)', line)
                        if match:
                            report["stock_name"] = match.group(1)
                            report["stock_code"] = match.group(2)
                
                reports.append(report)
            except Exception as e:
                logger.error(f"Error reading report {f}: {e}")
    
    return {
        "success": True,
        "data": reports[:50]  # 限制返回 50 条
    }


@router.delete("/reports/{report_id}")
async def delete_report(report_id: str) -> Dict[str, Any]:
    """删除报告"""
    import os
    from pathlib import Path
    
    reports_dir = Path(config.get("output.reports_dir", "./data/reports"))
    
    # 查找匹配的报告文件
    for f in reports_dir.glob(f"*{report_id}*.md"):
        try:
            f.unlink()
            return {"success": True, "message": "报告已删除"}
        except Exception as e:
            logger.error(f"Error deleting report: {e}")
    
    raise HTTPException(status_code=404, detail="报告未找到")


@router.get("/stock/{code}")
async def get_stock(code: str) -> Dict[str, Any]:
    """获取股票数据（通过代码）"""
    quote = mx_api.query_stock(code, "A 股")
    
    if not quote or not quote.name:
        raise HTTPException(status_code=404, detail="未找到股票")
    
    return {
        "success": True,
        "data": quote.to_dict()
    }


@router.post("/stock/{code}/analyze")
async def analyze_stock_by_code(code: str) -> Dict[str, Any]:
    """分析股票（通过代码）"""
    quote = mx_api.query_stock(code, "A 股")
    
    if not quote or not quote.name:
        raise HTTPException(status_code=404, detail="未找到股票")
    
    report = ai_analyzer.analyze_stock(quote)
    
    return {
        "success": True,
        "data": {
            "quote": quote.to_dict(),
            "report": report
        }
    }


@router.get("/settings")
async def get_settings() -> Dict[str, Any]:
    """获取设置"""
    return {
        "success": True,
        "data": {
            "em_api_key": config.em_api_key[:8] + "..." if config.em_api_key else "",
            "qwen_api_key": config.qwen_api_key[:8] + "..." if config.qwen_api_key else "",
        }
    }


@router.post("/settings")
async def update_settings(data: SettingsUpdate) -> Dict[str, Any]:
    """更新设置"""
    if data.em_api_key:
        config.set("api_keys.em_api_key", data.em_api_key)
    
    if data.qwen_api_key:
        config.set("api_keys.qwen_api_key", data.qwen_api_key)
    
    # 重新初始化服务
    global mx_api, ai_analyzer
    mx_api = MiaoXiangAPI(data.em_api_key)
    ai_analyzer = AIAnalyzer(data.qwen_api_key)
    
    return {
        "success": True,
        "message": "设置已保存"
    }


@router.get("/sectors/hot")
async def get_hot_sectors() -> Dict[str, Any]:
    """获取热门板块（前 5 名）- 使用东方财富板块 API"""
    try:
        import httpx
        
        # 东方财富板块排行 API
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": "1",
            "pz": "10",
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": "m:90 t:2",  # 行业板块
            "fields": "f12,f14,f2,f3,f4,f6"
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://quote.eastmoney.com/',
        }
        
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            
            if data.get("data") and data["data"].get("diff"):
                sectors = []
                for item in data["data"]["diff"]:
                    sector = {
                        "code": item.get("f12", ""),
                        "name": item.get("f14", ""),
                        "price": item.get("f2", 0),
                        "change_pct": item.get("f3", 0),
                        "change_amount": item.get("f4", 0),
                        "amount": item.get("f6", 0),
                    }
                    sectors.append(sector)
                
                logger.info(f"Fetched {len(sectors)} hot sectors from EM")
                return {
                    "success": True,
                    "data": sectors[:5]
                }
        
        # 备用：使用腾讯 API
        return await _get_sectors_from_tencent()
        
    except Exception as e:
        logger.error(f"Get hot sectors error: {e}")
        # 备用方案
        return await _get_sectors_from_tencent()


async def _get_sectors_from_tencent() -> Dict[str, Any]:
    """从腾讯获取板块数据"""
    try:
        import httpx
        
        # 腾讯板块 API
        sector_codes = [
            "bk0815",  # 新能源
            "bk0655",  # 半导体
            "bk0733",  # 医药生物
            "bk0424",  # 银行
            "bk0735",  # 白酒
        ]
        
        sectors = []
        for code in sector_codes:
            url = f"http://qt.gtimg.cn/q=s_{code}"
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    content = resp.content.decode('gbk')
                    if '~' in content:
                        data_str = content.split('=')[1].strip('"').split('~')
                        if len(data_str) > 5:
                            sectors.append({
                                "code": code,
                                "name": data_str[1] if len(data_str) > 1 else "",
                                "price": float(data_str[3]) if len(data_str) > 3 and data_str[3] else 0,
                                "change_pct": float(data_str[5]) if len(data_str) > 5 and data_str[5] else 0,
                                "change_amount": 0,
                                "amount": 0,
                            })
        
        sectors.sort(key=lambda x: x.get("change_pct", 0), reverse=True)
        
        return {
            "success": True,
            "data": sectors[:5]
        }
        
    except Exception as e:
        logger.error(f"Get sectors from Tencent error: {e}")
        return {"success": True, "data": []}


async def refresh_sectors_data() -> Dict[str, Any]:
    """刷新板块数据"""
    try:
        from pathlib import Path
        import subprocess
        import sys
        
        MX_DIR_STR = os.environ.get("MX_STOCKS_SCREENER_DIR", config.get("mx_screener.dir", ""))
        if not MX_DIR_STR:
            logger.warning("MX_DIR not configured, skipping sector refresh")
            return {"success": False, "data": [], "message": "妙想脚本目录未配置"}
        MX_DIR = Path(MX_DIR_STR)
        output_dir = Path(config.get("output.cache_dir", "./data/cache"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        api_key = config.em_api_key
        
        wrapper_script = output_dir / "sector_wrapper.py"
        wrapper_content = f'''
import os, sys, asyncio
sys.path.insert(0, r"{MX_DIR}")
os.environ["EM_API_KEY"] = "{api_key}"
os.environ["MX_STOCKS_SCREENER_OUTPUT_DIR"] = r"{output_dir}"
from scripts.get_data import query_mx_stocks_screener
from pathlib import Path

async def main():
    result = await query_mx_stocks_screener(query="今日涨幅最大的行业板块", selectType="板块", output_dir=Path(r"{output_dir}"))
    print(result.get("csv_path", ""))

asyncio.run(main())
'''
        wrapper_script.write_text(wrapper_content, encoding='utf-8')
        
        result = subprocess.run(
            [sys.executable, str(wrapper_script)],
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='ignore'
        )
        
        csv_path = None
        if result.stdout:
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line and '.csv' in line:
                    csv_path = line
                    break
        
        if csv_path:
            sectors = parse_sectors_csv(csv_path)
            return {"success": True, "data": sectors[:5]}
        
        return {"success": True, "data": []}
    except Exception as e:
        logger.error(f"Refresh sectors error: {e}")
        return {"success": False, "data": [], "message": str(e)}


def parse_sectors_csv(csv_path: str) -> list:
    """解析板块 CSV 文件，返回所有板块数据"""
    try:
        from pathlib import Path
        p = Path(csv_path)
        if not p.exists():
            # 尝试从输出目录查找
            csv_files = list(Path(csv_path).parent.glob("mx_stocks_screener_*.csv"))
            if csv_files:
                p = max(csv_files, key=lambda x: x.stat().st_mtime)
        
        if not p.exists():
            return []
        
        for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
            try:
                with open(p, "r", encoding=encoding) as f:
                    content = f.read()
                    break
            except:
                continue
        else:
            return []
        
        if content.startswith('\ufeff'):
            content = content[1:]
        
        lines = content.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = lines[0].split(',')
        
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
        
        def get_value(header_keywords: list, values: list, default: str = "") -> str:
            for i, h in enumerate(headers):
                for kw in header_keywords:
                    if kw in h:
                        return values[i] if i < len(values) else default
            return default
        
        sectors = []
        for line in lines[1:]:  # 跳过表头
            values = line.split(',')
            if len(values) < 5:
                continue
            
            sector = {
                "code": get_value(["代码"], values, ""),
                "name": get_value(["名称"], values, ""),
                "market": get_value(["市场"], values, ""),
                "price": parse_num(get_value(["最新价"], values, "0")),
                "change_pct": parse_num(get_value(["涨跌幅"], values, "0")),
                "change_amount": parse_num(get_value(["涨跌额"], values, "0")),
                "high": parse_num(get_value(["最高价"], values, "0")),
                "low": parse_num(get_value(["最低价"], values, "0")),
                "amount": parse_num(get_value(["成交额"], values, "0")),
            }
            sectors.append(sector)
        
        return sectors
        
    except Exception as e:
        logger.error(f"Parse sectors CSV error: {e}")
        return []


@router.post("/screener")
async def screen_stocks(data: dict) -> Dict[str, Any]:
    """智能选股 - 使用多数据源"""
    try:
        strategy = data.get("strategy", "")
        query = data.get("query", "")
        
        logger.info(f"Screener request - Strategy: {strategy}, Query: {query}")
        
        if not strategy:
            return {
                "success": False,
                "data": [],
                "message": "请选择一个策略"
            }
        
        # 使用新的数据服务筛选股票
        stocks = stock_service.screen_stocks(strategy, query)
        
        if stocks:
            return {
                "success": True,
                "data": stocks,
                "message": f"找到 {len(stocks)} 只符合条件的股票"
            }
        else:
            return {
                "success": True,
                "data": [],
                "message": "暂无符合条件的股票"
            }
            
    except Exception as e:
        logger.error(f"Screener error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "data": [],
            "message": str(e)
        }


def parse_stocks_csv(csv_path: str) -> list:
    """解析股票 CSV 文件"""
    try:
        from pathlib import Path
        p = Path(csv_path)
        if not p.exists():
            csv_files = list(p.parent.glob("mx_stocks_screener_*.csv"))
            if csv_files:
                p = max(csv_files, key=lambda x: x.stat().st_mtime)
        
        if not p.exists():
            return []
        
        for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
            try:
                with open(p, "r", encoding=encoding) as f:
                    content = f.read()
                    break
            except:
                continue
        else:
            return []
        
        if content.startswith('\ufeff'):
            content = content[1:]
        
        lines = content.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = lines[0].split(',')
        
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
        
        def get_value(header_keywords: list, values: list, default: str = "") -> str:
            for i, h in enumerate(headers):
                for kw in header_keywords:
                    if kw in h:
                        return values[i] if i < len(values) else default
            return default
        
        stocks = []
        for line in lines[1:]:
            values = line.split(',')
            if len(values) < 5:
                continue
            
            stock = {
                "code": get_value(["代码"], values, ""),
                "name": get_value(["名称"], values, ""),
                "market": get_value(["市场"], values, ""),
                "price": parse_num(get_value(["最新价"], values, "0")),
                "change_pct": parse_num(get_value(["涨跌幅"], values, "0")),
                "change_amount": parse_num(get_value(["涨跌额"], values, "0")),
                "high": parse_num(get_value(["最高价"], values, "0")),
                "low": parse_num(get_value(["最低价"], values, "0")),
                "pe": parse_num(get_value(["市盈率"], values, "0")),
                "pb": parse_num(get_value(["市净率"], values, "0")),
                "market_cap": parse_num(get_value(["总市值"], values, "0")),
                "turnover": parse_num(get_value(["换手率"], values, "0")),
            }
            stocks.append(stock)
        
        return stocks
        
    except Exception as e:
        logger.error(f"Parse stocks CSV error: {e}")
        return []

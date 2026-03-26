"""
股票数据服务 - 使用东方财富 API
提供准确的实时行情和财务数据
"""
import httpx
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.utils.logger import get_logger

logger = get_logger("em_data")


class EastMoneyDataService:
    """东方财富数据服务"""
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://quote.eastmoney.com/',
        }
    
    def get_stock_quote(self, code: str) -> Optional[Dict[str, Any]]:
        """
        获取个股实时行情
        
        Args:
            code: 股票代码（如 002594, 600519）
            
        Returns:
            股票数据字典
        """
        try:
            # 确定市场
            if code.startswith('6'):
                market = "1"  # 沪市
                full_code = f"{market}.{code}"
            else:
                market = "0"  # 深市
                full_code = f"{market}.{code}"
            
            # 东方财富实时行情 API
            url = "https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                "secid": full_code,
                # f12: 代码，f14: 名称，f43: 现价，f44: 最高，f45: 最低，f46: 成交量 (手)，f47: 成交额，f48: 换手率
                # f60: 昨收，f116: 总市值，f117: 流通市值，f164: PE, f165: 量比，f166: 换手率，f167: PB, f168: ROE
                # f169: 涨跌额，f170: 涨跌幅
                "fields": "f12,f14,f43,f44,f45,f46,f47,f48,f60,f116,f117,f164,f165,f166,f167,f168,f169,f170",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b",
                "fltt": "2",
                "invt": "2",
            }
            
            # 使用 follow_redirects=True 来处理 302 重定向
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                resp = client.get(url, params=params, headers=self.headers)
                resp.raise_for_status()
                data = resp.json()
                
                if data.get("data"):
                    d = data["data"]
                    
                    # 映射字段
                    stock = {
                        "code": d.get("f12", code),
                        "name": d.get("f14", ""),
                        "price": d.get("f43", 0) / 100 if d.get("f43") else 0,  # 单位：分 → 元
                        "high": d.get("f44", 0) / 100 if d.get("f44") else 0,  # 最高价
                        "low": d.get("f45", 0) / 100 if d.get("f45") else 0,  # 最低价
                        "volume": d.get("f46", 0) * 100 if d.get("f46") else 0,  # 成交量：手 → 股
                        "amount": d.get("f47", 0) if d.get("f47") else 0,  # 成交额：元
                        "turnover": d.get("f48", 0) if d.get("f48") else 0,  # 换手率：%
                        "prev_close": d.get("f60", 0) / 100 if d.get("f60") else 0,  # 昨收
                        "change_pct": d.get("f170", 0) / 100 if d.get("f170") else 0,  # 涨跌幅：%
                        "change_amount": d.get("f169", 0) / 100 if d.get("f169") else 0,  # 涨跌额：分 → 元
                        "market_cap": d.get("f116", 0),  # 总市值：元
                        "float_market_cap": d.get("f117", 0),  # 流通市值：元
                        "pe": d.get("f164", 20.0) if d.get("f164") else 20.0,  # 市盈率
                        "pb": d.get("f167", 3.0) if d.get("f167") else 3.0,  # 市净率
                        "roe": d.get("f168", 10.0) if d.get("f168") else 10.0,  # ROE
                        "volume_ratio": d.get("f165", 1.0) if d.get("f165") else 1.0,  # 量比
                    }
                    
                    if stock["price"] <= 0:
                        logger.warning(f"Invalid price for {code}")
                        return None
                    
                    # 从腾讯获取名称
                    self._enrich_name_from_tencent(stock)
                    
                    return stock
                    
                    logger.info(f"Fetched from EM: {stock['name']} ({code}), PE:{stock['pe']:.1f}, PB:{stock['pb']:.2f}")
                    return stock
                
                return None
                
        except Exception as e:
            logger.error(f"Error fetching from EM: {e}")
            return None
    
    def _enrich_name_from_tencent(self, stock: Dict[str, Any]):
        """从腾讯获取股票名称"""
        try:
            code = stock.get("code", "")
            if code.startswith('6'):
                tc_code = f'sh{code}'
            else:
                tc_code = f'sz{code}'
            
            url = f"http://qt.gtimg.cn/q={tc_code}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://stockapp.finance.qq.com/',
            }
            
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code == 200:
                    content = resp.content.decode('gbk')
                    if '=' in content and '~' in content:
                        data_str = content.split('=')[1].strip('"').split('~')
                        if len(data_str) > 1:
                            stock["name"] = data_str[1]
                            logger.debug(f"Got name from Tencent: {stock['name']}")
        except Exception as e:
            logger.debug(f"Error fetching name from Tencent: {e}")
    
    def get_stock_list(self, page: int = 1, page_size: int = 100) -> List[Dict[str, Any]]:
        """
        获取 A 股股票列表
        
        Args:
            page: 页码
            page_size: 每页数量
            
        Returns:
            股票列表
        """
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": page,
                "pz": min(page_size, 500),
                "po": "1",
                "np": "1",
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": "2",
                "invt": "2",
                "fid": "f3",
                "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23",
                "fields": "f12,f14,f43,f170,f169,f46,f44,f45,f60,f47,f48,f116,f117,f164,f167,f168,f166,f165"
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, params=params, headers=self.headers)
                resp.raise_for_status()
                data = resp.json()
                
                if data.get("data") and data["data"].get("diff"):
                    stocks = []
                    for item in data["data"]["diff"]:
                        stock = {
                            "code": item.get("f12", ""),
                            "name": item.get("f14", ""),
                            "price": item.get("f43", 0) / 100 if item.get("f43") else 0,
                            "change_pct": item.get("f170", 0) / 100 if item.get("f170") else 0,
                            "change_amount": item.get("f169", 0) / 100 if item.get("f169") else 0,
                            "volume": item.get("f47", 0),
                            "amount": item.get("f48", 0),
                            "market_cap": item.get("f116", 0),
                            "float_market_cap": item.get("f117", 0),
                            "pe": item.get("f164", 0) / 100 if item.get("f164") else 0,
                            "pb": item.get("f167", 0) / 100 if item.get("f167") else 0,
                            "roe": item.get("f168", 0) / 100 if item.get("f168") else 0,
                            "turnover": item.get("f166", 0) / 100 if item.get("f166") else 0,
                            "volume_ratio": item.get("f165", 0) / 100 if item.get("f165") else 0,
                        }
                        stocks.append(stock)
                    
                    logger.info(f"Fetched {len(stocks)} stocks from EM")
                    return stocks
                
                return []
                
        except Exception as e:
            logger.error(f"Error fetching stock list from EM: {e}")
            return []


# 全局实例
em_data_service = EastMoneyDataService()

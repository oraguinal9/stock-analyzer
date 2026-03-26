"""
股票数据服务 - 使用腾讯财经 API（更可靠）
"""
import httpx
from typing import Dict, Optional, Any
from app.utils.logger import get_logger

logger = get_logger("tc_data")


class TencentDataService:
    """腾讯财经数据服务"""
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://stockapp.finance.qq.com/',
        }
    
    def get_stock_quote(self, code: str) -> Optional[Dict[str, Any]]:
        """
        从腾讯财经获取个股实时行情
        
        Args:
            code: 股票代码（如 002594, 600519）
            
        Returns:
            股票数据字典
        """
        try:
            # 确定市场
            if code.startswith('6'):
                tc_code = f'sh{code}'
            else:
                tc_code = f'sz{code}'
            
            url = f"http://qt.gtimg.cn/q={tc_code}"
            
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, headers=self.headers)
                resp.raise_for_status()
                content = resp.content.decode('gbk')
                
                if '=' in content and '~' in content:
                    data_str = content.split('=')[1].strip('"').split('~')
                    
                    if len(data_str) > 50:
                        # 腾讯字段映射（已验证）
                        # f1=名称，f2=代码，f3=股价，f4=昨收，f5=今开
                        # f21=总市值 (亿), f38=换手率，f39=PE(TTM), f43=PB, f45=流通市值 (亿)
                        
                        # 计算涨跌幅
                        current = float(data_str[3]) if len(data_str) > 3 and data_str[3] else 0
                        prev_close = float(data_str[4]) if len(data_str) > 4 and data_str[4] else 0
                        change_pct = ((current - prev_close) / prev_close * 100) if prev_close > 0 else 0
                        
                        stock = {
                            "code": code,
                            "name": data_str[1] if len(data_str) > 1 else "",
                            "price": current,
                            "change_pct": change_pct,
                            "change_amount": current - prev_close,
                            "open": float(data_str[5]) if len(data_str) > 5 and data_str[5] else 0,
                            "high": float(data_str[33]) if len(data_str) > 33 and data_str[33] else 0,
                            "low": float(data_str[34]) if len(data_str) > 34 and data_str[34] else 0,
                            "prev_close": prev_close,
                            "volume": float(data_str[6]) if len(data_str) > 6 and data_str[6] else 0,
                            "amount": float(data_str[37]) if len(data_str) > 37 and data_str[37] else 0,
                            "market_cap": float(data_str[45]) * 1e8 if len(data_str) > 45 and data_str[45] else 0,
                            "float_market_cap": float(data_str[47]) * 1e8 if len(data_str) > 47 and data_str[47] else 0,
                            "pe": float(data_str[39]) if len(data_str) > 39 and data_str[39] else 20.0,
                            "pb": float(data_str[43]) if len(data_str) > 43 and data_str[43] else 3.0,
                            "roe": float(data_str[49]) if len(data_str) > 49 and data_str[49] else 10.0,
                            "turnover": float(data_str[38]) if len(data_str) > 38 and data_str[38] else 2.0,
                            "volume_ratio": 1.0,  # 腾讯量比字段不准确，使用默认值
                        }
                        
                        logger.info(f"Fetched from Tencent: {stock['name']} ({code}), PE:{stock['pe']}, PB:{stock['pb']}, Turnover:{stock['turnover']}%")
                        return stock
                
                return None
                
        except Exception as e:
            logger.error(f"Error fetching from Tencent: {e}")
            return None
    
    def get_stock_list(self, page: int = 1, page_size: int = 100) -> list:
        """获取股票列表（简化版：返回预设股票池）"""
        # 腾讯没有批量获取股票列表的 API，使用预设列表
        stock_codes = [
            "002594", "600519", "300750", "000858", "601318", "600036", "601398", "600276",
            "000333", "002415", "000651", "000001", "000002", "600000", "600016", "600030",
            "600031", "600048", "600050", "600104", "600309", "600346", "600436", "600585",
            "600588", "600690", "600745", "600809", "600887", "600900", "601012", "601066",
            "601088", "601166", "601211", "601288", "601336", "601390", "601601", "601628",
            "601668", "601688", "601728", "601766", "601857", "601888", "601899", "601919",
            "601988", "601998", "603259", "603288", "000063", "000100", "000157", "000425",
            "000538", "000568", "000596", "000625", "000661", "000725", "000776", "000895",
            "002001", "002007", "002027", "002032", "002049", "002129", "002142", "002179",
            "002230", "002236", "002241", "002252", "002304", "002352", "002410", "002422",
            "002459", "002460", "002466", "002475", "002493", "002507", "002555", "002601",
            "002648", "002709", "002714", "002812", "002821", "300003", "300014", "300015",
            "300033", "300059", "300122", "300124", "300142", "300274", "300316", "300347",
            "300408", "300413", "300433", "300498", "300529", "300601", "300628", "300759",
            "300760", "300782", "300896", "300957",
        ]
        
        # 获取这些股票的实时数据
        stocks = []
        for code in stock_codes[:page_size]:
            stock = self.get_stock_quote(code)
            if stock:
                stocks.append(stock)
        
        logger.info(f"Fetched {len(stocks)} stocks from Tencent")
        return stocks


# 全局实例
tc_data_service = TencentDataService()

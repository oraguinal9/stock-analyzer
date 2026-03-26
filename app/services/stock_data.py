"""
股票数据服务 - 使用腾讯财经批量接口
"""
import httpx
from typing import Dict, List, Any
from app.utils.logger import get_logger

logger = get_logger("stock_data")

# 预设股票池（沪深 300 核心成分股，去重）
STOCK_POOL = list(dict.fromkeys([
    "600519", "601398", "600036", "601318", "000858", "002594", "300750", "601088",
    "600276", "000333", "601166", "600000", "600016", "600030", "601288", "601668",
    "601857", "601988", "601601", "601628", "601688", "601766", "601919", "601899",
    "601012", "601211", "601336", "601390", "601728", "601888", "601998", "600900",
    "600104", "600048", "600050", "600309", "600346", "600436", "600585", "600588",
    "600690", "600745", "600809", "600887", "603259", "603288",
    "000001", "000002", "000063", "000100", "000157", "000425", "000538",
    "000568", "000596", "000625", "000651", "000661", "000725", "000776",
    "000895", "002001", "002007", "002027", "002032", "002049", "002129", "002142",
    "002179", "002230", "002236", "002241", "002252", "002304", "002352", "002410",
    "002415", "002422", "002459", "002460", "002466", "002475", "002493", "002507",
    "002555", "002601", "002648", "002709", "002714", "002812", "002821",
    "300003", "300014", "300015", "300033", "300059", "300122", "300124", "300142",
    "300274", "300316", "300347", "300408", "300413", "300433", "300498", "300529",
    "300601", "300628", "300759", "300760", "300782", "300896", "300957",
]))


class StockDataService:
    """股票数据服务"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://stockapp.finance.qq.com/',
        }
    
    def get_stock_list_batch(self) -> List[Dict[str, Any]]:
        """批量获取股票数据（腾讯批量接口）"""
        try:
            # 转换为腾讯格式
            tc_codes = []
            for code in STOCK_POOL:
                if code.startswith('6'):
                    tc_codes.append(f'sh{code}')
                else:
                    tc_codes.append(f'sz{code}')
            
            # 分批请求（每批 30 只）
            all_stocks = []
            batch_size = 30
            
            for i in range(0, len(tc_codes), batch_size):
                batch = tc_codes[i:i + batch_size]
                url = f"http://qt.gtimg.cn/q={','.join(batch)}"
                
                with httpx.Client(timeout=15.0) as client:
                    resp = client.get(url, headers=self.headers)
                    if resp.status_code == 200:
                        content = resp.content.decode('gbk')
                        lines = content.strip().split('\n')
                        
                        for line in lines:
                            stock = self._parse_tencent_line(line)
                            if stock and stock.get('price', 0) > 0:
                                all_stocks.append(stock)
            
            logger.info(f"Batch fetched {len(all_stocks)} stocks")
            return all_stocks
            
        except Exception as e:
            logger.error(f"Error batch fetching stocks: {e}")
            return []
    
    def _parse_tencent_line(self, line: str) -> Dict[str, Any]:
        """解析腾讯数据行"""
        try:
            if '=' not in line or '~' not in line:
                return {}
            
            data_str = line.split('=')[1].strip('"').split('~')
            if len(data_str) < 50:
                return {}
            
            current = float(data_str[3]) if data_str[3] else 0
            prev_close = float(data_str[4]) if data_str[4] else 0
            change_pct = ((current - prev_close) / prev_close * 100) if prev_close > 0 else 0
            
            return {
                "code": data_str[2] if len(data_str) > 2 else "",
                "name": data_str[1] if len(data_str) > 1 else "",
                "price": current,
                "change_pct": round(change_pct, 2),
                "change_amount": round(current - prev_close, 2),
                "pe": float(data_str[39]) if len(data_str) > 39 and data_str[39] else 0,
                "pb": float(data_str[43]) if len(data_str) > 43 and data_str[43] else 0,
                "turnover": float(data_str[38]) if len(data_str) > 38 and data_str[38] else 0,
                "market_cap": float(data_str[45]) * 1e8 if len(data_str) > 45 and data_str[45] else 0,
            }
        except Exception as e:
            return {}
    
    def screen_stocks(self, strategy: str, query: str) -> List[Dict[str, Any]]:
        """筛选股票"""
        logger.info(f"Screening: strategy={strategy}")
        
        stocks = self.get_stock_list_batch()
        
        if not stocks:
            logger.warning("No stocks fetched")
            return []
        
        filtered = self._filter_stocks(stocks, strategy)
        logger.info(f"Filtered {len(filtered)} from {len(stocks)}")
        return filtered
    
    def _filter_stocks(self, stocks: List[Dict[str, Any]], strategy: str) -> List[Dict[str, Any]]:
        """筛选股票"""
        filtered = []
        
        for stock in stocks:
            try:
                price = stock.get('price', 0)
                pe = stock.get('pe', 0)
                pb = stock.get('pb', 0)
                change_pct = stock.get('change_pct', 0)
                turnover = stock.get('turnover', 0)
                market_cap = stock.get('market_cap', 0)
                
                if price <= 0:
                    continue
                
                match = False
                
                if strategy == 'value':
                    # 价值投资：PE 在 5-20 之间，PB<3
                    match = (5 < pe < 20) and (pb < 3)
                
                elif strategy == 'growth':
                    # 成长龙头：PE 在 15-40 之间，市值>500亿
                    match = (15 < pe < 40) and (market_cap > 500e8)
                
                elif strategy == 'hot':
                    # 今日强势：涨幅>2%
                    match = change_pct > 2
                
                elif strategy == 'dividend':
                    # 高股息防御：PE<15，PB<2
                    match = (0 < pe < 15) and (pb < 2)
                
                elif strategy == 'tech':
                    # 科技成长：PE 在 20-50，市值>200亿
                    match = (20 < pe < 50) and (market_cap > 200e8)
                
                elif strategy == 'breakout':
                    # 突破新高：涨幅>1%，换手>1%
                    match = (change_pct > 1) and (turnover > 1)
                
                elif strategy == 'lowrisk':
                    # 低风险稳健：PE<25，PB<3
                    match = (0 < pe < 25) and (0 < pb < 3)
                
                elif strategy == 'north':
                    # 北向重仓：大盘蓝筹，PE<30，市值>1000亿
                    match = (0 < pe < 30) and (market_cap > 1000e8)
                
                if match:
                    filtered.append(stock)
                    
            except Exception:
                continue
        
        # 排序
        sort_key = {
            'value': lambda x: x.get('pe', 999),
            'growth': lambda x: -x.get('market_cap', 0),
            'hot': lambda x: -x.get('change_pct', 0),
            'dividend': lambda x: x.get('pe', 999),
            'tech': lambda x: -x.get('market_cap', 0),
            'breakout': lambda x: -x.get('change_pct', 0),
            'lowrisk': lambda x: x.get('pe', 999),
            'north': lambda x: -x.get('market_cap', 0),
        }
        
        if strategy in sort_key:
            filtered.sort(key=sort_key[strategy])
        
        return filtered[:20]


# 全局实例
stock_data_service = StockDataService()

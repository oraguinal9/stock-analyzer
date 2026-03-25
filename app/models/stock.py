"""
股票数据模型
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class StockQuote:
    """股票行情数据"""
    code: str = ""
    name: str = ""
    market: str = ""  # SZ, SH, HK, US
    price: float = 0.0
    change_pct: float = 0.0
    change_amount: float = 0.0
    high: float = 0.0
    low: float = 0.0
    open: float = 0.0
    prev_close: float = 0.0
    volume: int = 0
    amount: float = 0.0
    turnover: float = 0.0  # 换手率
    volume_ratio: float = 0.0  # 量比
    pe: float = 0.0  # 市盈率
    pb: float = 0.0  # 市净率
    market_cap: float = 0.0  # 总市值
    float_market_cap: float = 0.0  # 流通市值
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "market": self.market,
            "price": self.price,
            "change_pct": self.change_pct,
            "change_amount": self.change_amount,
            "high": self.high,
            "low": self.low,
            "volume": self.volume,
            "amount": self.amount,
            "turnover": self.turnover,
            "volume_ratio": self.volume_ratio,
            "pe": self.pe,
            "pb": self.pb,
            "market_cap": self.market_cap,
            "float_market_cap": self.float_market_cap,
        }


@dataclass
class FinancialData:
    """财务数据"""
    code: str = ""
    report_date: str = ""
    revenue: float = 0.0  # 营业收入
    net_profit: float = 0.0  # 净利润
    roe: float = 0.0  # 净资产收益率
    gross_margin: float = 0.0  # 毛利率
    net_margin: float = 0.0  # 净利率
    eps: float = 0.0  # 每股收益
    bvps: float = 0.0  # 每股净资产
    operating_cash_flow: float = 0.0  # 经营现金流
    debt_ratio: float = 0.0  # 资产负债率


@dataclass
class StockData:
    """完整股票数据"""
    quote: StockQuote = field(default_factory=StockQuote)
    financial: List[FinancialData] = field(default_factory=list)
    news: List[Dict[str, Any]] = field(default_factory=list)
    fund_flow: List[Dict[str, Any]] = field(default_factory=list)
    technical: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "quote": self.quote.to_dict(),
            "financial": [f.__dict__ for f in self.financial],
            "news": self.news,
            "fund_flow": self.fund_flow,
            "technical": self.technical,
        }

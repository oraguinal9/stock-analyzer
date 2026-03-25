"""
分析报告模型
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum


class Rating(Enum):
    """评级枚举"""
    STRONG_BUY = "强烈看涨"
    BUY = "看涨"
    NEUTRAL = "中性"
    SELL = "看跌"
    STRONG_SELL = "强烈看跌"


@dataclass
class AnalysisReport:
    """股票分析报告"""
    id: str = ""
    stock_code: str = ""
    stock_name: str = ""
    report_type: str = "stock"  # stock / sector
    content: str = ""
    rating: str = ""
    score: int = 0
    summary: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "stock_code": self.stock_code,
            "stock_name": self.stock_name,
            "report_type": self.report_type,
            "content": self.content,
            "rating": self.rating,
            "score": self.score,
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisReport":
        return cls(
            id=data.get("id", ""),
            stock_code=data.get("stock_code", ""),
            stock_name=data.get("stock_name", ""),
            report_type=data.get("report_type", "stock"),
            content=data.get("content", ""),
            rating=data.get("rating", ""),
            score=data.get("score", 0),
            summary=data.get("summary", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
        )

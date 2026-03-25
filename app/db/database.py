"""
SQLite 数据库操作
"""
import aiosqlite
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.utils.config import config
from app.utils.logger import get_logger
from app.models.report import AnalysisReport

logger = get_logger("database")


class Database:
    """数据库管理类"""
    
    _instance: Optional["Database"] = None
    _db: Optional[aiosqlite.Connection] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """连接数据库"""
        if self._db is None:
            db_path = Path(config.get("database.path", "./data/stock_analyzer.db"))
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self._db = await aiosqlite.connect(str(db_path))
            self._db.row_factory = aiosqlite.Row
            await self._create_tables()
            logger.info(f"Database connected: {db_path}")
    
    async def close(self):
        """关闭数据库"""
        if self._db:
            await self._db.close()
            self._db = None
    
    async def _create_tables(self):
        """创建数据表"""
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                stock_code TEXT NOT NULL,
                stock_name TEXT,
                report_type TEXT DEFAULT 'stock',
                content TEXT,
                rating TEXT,
                score INTEGER,
                summary TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                stock_name TEXT,
                market TEXT,
                created_at TEXT,
                UNIQUE(stock_code)
            )
        """)
        
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                condition_type TEXT,
                condition_value REAL,
                triggered INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)
        
        await self._db.commit()
    
    # 报告相关操作
    async def save_report(self, report: AnalysisReport):
        """保存报告"""
        await self._db.execute("""
            INSERT OR REPLACE INTO reports 
            (id, stock_code, stock_name, report_type, content, rating, score, summary, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report.id,
            report.stock_code,
            report.stock_name,
            report.report_type,
            report.content,
            report.rating,
            report.score,
            report.summary,
            report.created_at.isoformat(),
            report.updated_at.isoformat(),
        ))
        await self._db.commit()
    
    async def get_report(self, report_id: str) -> Optional[AnalysisReport]:
        """获取报告"""
        async with self._db.execute(
            "SELECT * FROM reports WHERE id = ?", (report_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return AnalysisReport.from_dict(dict(row))
            return None
    
    async def get_reports_by_stock(self, stock_code: str, limit: int = 10) -> List[AnalysisReport]:
        """获取某股票的历史报告"""
        async with self._db.execute(
            "SELECT * FROM reports WHERE stock_code = ? ORDER BY created_at DESC LIMIT ?",
            (stock_code, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [AnalysisReport.from_dict(dict(row)) for row in rows]
    
    async def get_all_reports(self, limit: int = 50) -> List[AnalysisReport]:
        """获取所有报告"""
        async with self._db.execute(
            "SELECT * FROM reports ORDER BY created_at DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [AnalysisReport.from_dict(dict(row)) for row in rows]
    
    async def delete_report(self, report_id: str):
        """删除报告"""
        await self._db.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        await self._db.commit()
    
    # 自选股相关操作
    async def add_favorite(self, stock_code: str, stock_name: str, market: str = ""):
        """添加自选股"""
        await self._db.execute("""
            INSERT OR REPLACE INTO favorites (stock_code, stock_name, market, created_at)
            VALUES (?, ?, ?, ?)
        """, (stock_code, stock_name, market, datetime.now().isoformat()))
        await self._db.commit()
    
    async def remove_favorite(self, stock_code: str):
        """删除自选股"""
        await self._db.execute("DELETE FROM favorites WHERE stock_code = ?", (stock_code,))
        await self._db.commit()
    
    async def get_favorites(self) -> List[Dict[str, Any]]:
        """获取自选股列表"""
        async with self._db.execute(
            "SELECT * FROM favorites ORDER BY created_at DESC"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def is_favorite(self, stock_code: str) -> bool:
        """检查是否在自选"""
        async with self._db.execute(
            "SELECT 1 FROM favorites WHERE stock_code = ?", (stock_code,)
        ) as cursor:
            return await cursor.fetchone() is not None


# 全局数据库实例
db = Database()

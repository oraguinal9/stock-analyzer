"""
AI 股票分析服务
"""
import httpx
from typing import Dict, Optional, Any
from datetime import datetime
from pathlib import Path

from app.utils.config import config
from app.utils.logger import get_logger
from app.models.stock import StockData, StockQuote
from app.models.report import AnalysisReport

logger = get_logger("ai_analyzer")


class AIAnalyzer:
    """AI 分析器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.qwen_api_key
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.reports_dir = config.reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    async def analyze_stock(self, stock_data: StockData) -> AnalysisReport:
        """
        分析个股
        
        Args:
            stock_data: 股票数据
        
        Returns:
            分析报告
        """
        quote = stock_data.quote
        
        if not self.api_key:
            logger.info("QWEN_API_KEY not configured, using local analysis")
            return self._local_analysis(quote)
        
        try:
            prompt = self._build_stock_prompt(quote)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "qwen-plus",
                        "messages": [
                            {"role": "system", "content": "你是一位专业的股票分析师，擅长技术分析和基本面分析，能给出客观专业的投资建议。"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                )
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 创建报告
                report = self._parse_analysis_content(content, quote)
                self._save_report(report)
                
                return report
                
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return self._local_analysis(quote)
    
    def _build_stock_prompt(self, quote: StockQuote) -> str:
        """构建分析 Prompt"""
        return f"""你是一位专业的股票分析师，请对以下股票进行全面诊断分析：

## 股票基本信息
- 股票名称：{quote.name}
- 股票代码：{quote.code}
- 所属市场：{quote.market}
- 分析时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}

## 实时行情数据
- 最新价：{quote.price:.2f} 元
- 涨跌幅：{quote.change_pct:+.2f}%
- 涨跌额：{quote.change_amount:+.2f} 元
- 最高价：{quote.high:.2f} 元
- 最低价：{quote.low:.2f} 元
- 成交量：{quote.volume:,} 股
- 成交额：{quote.amount:,.0f} 元

## 估值指标
- 总市值：{quote.market_cap/1e8:.2f} 亿
- 流通市值：{quote.float_market_cap/1e8:.2f} 亿
- 市盈率 (动)：{quote.pe:.2f} 倍
- 市净率：{quote.pb:.2f} 倍

## 交易活跃度
- 换手率：{quote.turnover:.2f}%
- 量比：{quote.volume_ratio:.2f}

请从以下维度进行分析：

1. **今日表现分析**：涨跌幅、成交量、换手率等指标的含义
2. **估值分析**：市盈率、市净率处于什么水平（高/中/低）
3. **资金面分析**：量比、成交额反映的资金态度
4. **技术面推测**：基于今日数据的短期走势判断
5. **风险提示**：可能的风险因素
6. **操作建议**：短线/中线/长线投资者的策略建议

要求：
- 分析专业、客观
- 给出明确的判断（看涨/看跌/中性）
- 建议具体可操作
- 字数 800-1500 字
- 使用 Markdown 格式输出
"""
    
    def _parse_analysis_content(self, content: str, quote: StockQuote) -> AnalysisReport:
        """解析 AI 分析内容"""
        import uuid
        import re
        
        # 尝试提取评级
        rating = "中性"
        if "强烈看涨" in content or "强烈看好" in content:
            rating = "强烈看涨"
        elif "看涨" in content or "看好" in content or "买入" in content:
            rating = "看涨"
        elif "看跌" in content or "卖出" in content:
            rating = "看跌"
        elif "强烈看跌" in content:
            rating = "强烈看跌"
        
        # 尝试提取评分
        score = 50
        score_match = re.search(r'(\d{1,3})\s*分', content)
        if score_match:
            score = int(score_match.group(1))
        
        # 生成摘要（取前 200 字）
        summary = content[:200].replace('\n', ' ') + "..." if len(content) > 200 else content
        
        return AnalysisReport(
            id=str(uuid.uuid4())[:8],
            stock_code=quote.code,
            stock_name=quote.name,
            report_type="stock",
            content=content,
            rating=rating,
            score=score,
            summary=summary,
        )
    
    def _local_analysis(self, quote: StockQuote) -> AnalysisReport:
        """本地简易分析（无 API Key 时）"""
        import uuid
        
        # 简单规则分析
        change_pct = quote.change_pct
        turnover = quote.turnover
        volume_ratio = quote.volume_ratio
        pe = quote.pe
        
        # 判断评级
        if change_pct > 5:
            rating = "看涨"
            score = min(80 + change_pct * 2, 95)
        elif change_pct > 2:
            rating = "看涨"
            score = 65 + change_pct * 3
        elif change_pct > -2:
            rating = "中性"
            score = 50 + change_pct * 5
        elif change_pct > -5:
            rating = "看跌"
            score = 40 + change_pct * 3
        else:
            rating = "看跌"
            score = max(20 + change_pct * 2, 10)
        
        content = f"""# {quote.name} ({quote.code}) 分析报告

## 📊 今日表现
- **涨幅**：{change_pct:+.2f}%，表现{'强势' if change_pct > 3 else '温和' if change_pct > 0 else '弱势'}
- **换手率**：{turnover:.2f}%，{'活跃' if turnover > 5 else '正常' if turnover > 2 else '清淡'}
- **量比**：{volume_ratio:.2f}，{'放量' if volume_ratio > 2 else '正常' if volume_ratio > 0.8 else '缩量'}

## 💰 估值分析
- **市盈率**：{pe:.2f}倍，处于{'较高' if pe > 50 else '中等' if pe > 20 else '较低'}水平
- **市净率**：{quote.pb:.2f}倍

## 📈 技术判断
- 短期：{'看涨' if change_pct > 2 else '中性' if change_pct > -2 else '看跌'}
- 成交量：{'放大' if volume_ratio > 1.5 else '正常' if volume_ratio > 0.8 else '萎缩'}

## ⚠️ 风险提示
1. 行业竞争和市场波动风险
2. 宏观经济环境影响
3. 政策变化可能带来的影响

## 💡 操作建议
- **短线**：{'可关注' if change_pct > 0 else '观望'}，设置好止损位
- **中线**：根据基本面情况逢低布局
- **长线**：关注行业前景和公司竞争力

---
*免责声明：以上分析仅供参考，不构成投资建议。股市有风险，投资需谨慎。*
"""
        
        report = AnalysisReport(
            id=str(uuid.uuid4())[:8],
            stock_code=quote.code,
            stock_name=quote.name,
            report_type="stock",
            content=content,
            rating=rating,
            score=int(score),
            summary=f"{quote.name} 今日{change_pct:+.2f}%，评级：{rating}",
        )
        
        self._save_report(report)
        return report
    
    def _save_report(self, report: AnalysisReport):
        """保存报告到文件"""
        timestamp = report.created_at.strftime("%Y%m%d_%H%M%S")
        filename = f"report_{report.stock_code}_{report.id}_{timestamp}.md"
        filepath = self.reports_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {report.stock_name} ({report.stock_code}) 分析报告\n\n")
            f.write(f"**报告 ID**: {report.id}\n")
            f.write(f"**生成时间**: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**评级**: {report.rating}\n")
            f.write(f"**评分**: {report.score}/100\n\n")
            f.write("---\n\n")
            f.write(report.content)
        
        logger.info(f"Report saved: {filepath}")
    
    async def analyze_sector(self, sector_data: Dict[str, Any]) -> AnalysisReport:
        """分析板块"""
        # TODO: 实现板块分析
        pass


# 全局分析器实例
ai_analyzer = AIAnalyzer()

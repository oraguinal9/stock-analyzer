"""
主窗口
"""
import customtkinter as ctk
from typing import Optional, Dict, Any
import asyncio

from app.utils.config import config
from app.utils.logger import get_logger
from app.services.mx_api import MiaoXiangAPI
from app.services.ai_analyzer import AIAnalyzer
from app.db.database import Database

logger = get_logger("gui")


class MainWindow(ctk.CTk):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 窗口配置
        self.title("📈 股票分析助手")
        width = config.get("app.window_width", 1200)
        height = config.get("app.window_height", 800)
        self.geometry(f"{width}x{height}")
        
        # 主题设置
        theme = config.get("app.theme", "dark")
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")
        
        # 服务初始化
        self.mx_api = MiaoXiangAPI()
        self.ai_analyzer = AIAnalyzer()
        self.db = Database()
        
        # 当前页面
        self.current_page: Optional[ctk.CTkFrame] = None
        self.pages: Dict[str, ctk.CTkFrame] = {}
        
        # 创建布局
        self._create_sidebar()
        self._create_main_area()
        self._create_status_bar()
        
        # 默认显示首页
        self._show_page("home")
        
        # 窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        logger.info("Main window initialized")
    
    def _create_sidebar(self):
        """创建侧边栏"""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        # 标题
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="📈 股票分析助手",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=20)
        
        # 导航按钮
        buttons = [
            ("🏠 首页", "home"),
            ("📊 个股分析", "stock"),
            ("📁 板块监控", "sector"),
            ("🎯 智能选股", "screener"),
            ("⭐ 自选股", "favorites"),
            ("📄 历史报告", "reports"),
            ("⚙️ 设置", "settings"),
        ]
        
        self.nav_buttons = {}
        for text, page_id in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda p=page_id: self._show_page(p),
                anchor="w",
                padx=20,
                pady=10,
                height=40,
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_buttons[page_id] = btn
    
    def _create_main_area(self):
        """创建主内容区"""
        self.main_container = ctk.CTkFrame(self, corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True)
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_bar.pack(side="bottom", fill="x")
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="就绪",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10)
    
    def _show_page(self, page_id: str):
        """显示页面"""
        # 更新导航按钮状态
        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent", hover_color=("gray75", "gray25"))
        if page_id in self.nav_buttons:
            self.nav_buttons[page_id].configure(
                fg_color=("#3B8ED0", "#1F6AA5"),
                hover_color=("#36719F", "#144871")
            )
        
        # 清空主内容区
        if self.current_page:
            self.current_page.destroy()
        
        # 创建新页面
        self.current_page = ctk.CTkFrame(self.main_container)
        self.current_page.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 加载页面内容
        if page_id == "home":
            self._load_home_page()
        elif page_id == "stock":
            self._load_stock_page()
        elif page_id == "sector":
            self._load_sector_page()
        elif page_id == "screener":
            self._load_screener_page()
        elif page_id == "favorites":
            self._load_favorites_page()
        elif page_id == "reports":
            self._load_reports_page()
        elif page_id == "settings":
            self._load_settings_page()
        
        logger.info(f"Page loaded: {page_id}")
    
    def _load_home_page(self):
        """加载首页"""
        # 标题
        title = ctk.CTkLabel(
            self.current_page,
            text="📈 欢迎使用股票分析助手",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=40)
        
        # 副标题
        subtitle = ctk.CTkLabel(
            self.current_page,
            text="基于东方财富妙想 API + 千问 AI 的智能股票分析工具",
            font=ctk.CTkFont(size=16)
        )
        subtitle.pack(pady=10)
        
        # 搜索框区域
        search_frame = ctk.CTkFrame(self.current_page, fg_color="transparent")
        search_frame.pack(pady=40)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="输入股票代码或名称（如：002594 或 比亚迪）",
            width=500,
            height=50,
            font=ctk.CTkFont(size=16)
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="🔍 分析",
            command=self._search_stock,
            width=120,
            height=50,
            font=ctk.CTkFont(size=16)
        )
        search_btn.pack(side="left")
        
        # 功能卡片
        features_frame = ctk.CTkFrame(self.current_page, fg_color="transparent")
        features_frame.pack(pady=20, fill="both", expand=True)
        
        features = [
            ("📊", "个股分析", "实时行情 + AI 诊断"),
            ("📁", "板块监控", "热门板块排行"),
            ("🎯", "智能选股", "自然语言筛选"),
            ("⭐", "自选管理", "批量分析监控"),
        ]
        
        for i, (icon, title, desc) in enumerate(features):
            card = ctk.CTkFrame(features_frame, width=200, height=120)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            features_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(
                card,
                text=icon,
                font=ctk.CTkFont(size=32)
            ).pack(pady=10)
            
            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack()
            
            ctk.CTkLabel(
                card,
                text=desc,
                font=ctk.CTkFont(size=12),
                text_color="gray"
            ).pack()
        
        # 绑定回车键搜索
        self.search_entry.bind("<Return>", lambda e: self._search_stock())
    
    def _load_stock_page(self):
        """加载个股分析页"""
        # TODO: 实现个股分析页面
        label = ctk.CTkLabel(
            self.current_page,
            text="📊 个股分析页\n\n（开发中...）",
            font=ctk.CTkFont(size=24)
        )
        label.pack(pady=100)
    
    def _load_sector_page(self):
        """加载板块监控页"""
        label = ctk.CTkLabel(
            self.current_page,
            text="📁 板块监控页\n\n（开发中...）",
            font=ctk.CTkFont(size=24)
        )
        label.pack(pady=100)
    
    def _load_screener_page(self):
        """加载智能选股页"""
        label = ctk.CTkLabel(
            self.current_page,
            text="🎯 智能选股页\n\n（开发中...）",
            font=ctk.CTkFont(size=24)
        )
        label.pack(pady=100)
    
    def _load_favorites_page(self):
        """加载自选股页"""
        label = ctk.CTkLabel(
            self.current_page,
            text="⭐ 自选股页\n\n（开发中...）",
            font=ctk.CTkFont(size=24)
        )
        label.pack(pady=100)
    
    def _load_reports_page(self):
        """加载历史报告页"""
        label = ctk.CTkLabel(
            self.current_page,
            text="📄 历史报告页\n\n（开发中...）",
            font=ctk.CTkFont(size=24)
        )
        label.pack(pady=100)
    
    def _load_settings_page(self):
        """加载设置页"""
        title = ctk.CTkLabel(
            self.current_page,
            text="⚙️ 设置",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # API Key 配置
        config_frame = ctk.CTkFrame(self.current_page)
        config_frame.pack(pady=20, padx=20, fill="x")
        
        # 东方财富 API Key
        ctk.CTkLabel(
            config_frame,
            text="东方财富妙想 API Key:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.em_api_entry = ctk.CTkEntry(
            config_frame,
            width=500,
            height=40
        )
        self.em_api_entry.pack(padx=20, pady=5)
        self.em_api_entry.insert(0, config.em_api_key)
        
        # 千问 API Key
        ctk.CTkLabel(
            config_frame,
            text="千问 API Key:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.qwen_api_entry = ctk.CTkEntry(
            config_frame,
            width=500,
            height=40
        )
        self.qwen_api_entry.pack(padx=20, pady=5)
        self.qwen_api_entry.insert(0, config.qwen_api_key)
        
        # 保存按钮
        save_btn = ctk.CTkButton(
            config_frame,
            text="💾 保存配置",
            command=self._save_settings,
            width=200,
            height=40
        )
        save_btn.pack(pady=30)
        
        # 说明
        info_label = ctk.CTkLabel(
            config_frame,
            text="💡 获取 API Key:\n- 东方财富妙想：https://ai.eastmoney.com/mxClaw\n- 千问 API: https://dashscope.console.aliyun.com/",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            justify="left"
        )
        info_label.pack(padx=20, pady=20, anchor="w")
    
    def _search_stock(self):
        """搜索股票"""
        query = self.search_entry.get().strip()
        if not query:
            self._set_status("请输入股票代码或名称")
            return
        
        self._set_status(f"正在搜索：{query}...")
        
        # 异步执行搜索
        asyncio.create_task(self._do_search_stock(query))
    
    async def _do_search_stock(self, query: str):
        """执行股票搜索"""
        try:
            # 查询股票数据
            stock_data = await self.mx_api.query_stock(query)
            
            if stock_data and stock_data.quote.name:
                self._set_status(f"找到股票：{stock_data.quote.name}")
                
                # 进行 AI 分析
                self._set_status("正在进行 AI 分析...")
                report = await self.ai_analyzer.analyze_stock(stock_data)
                
                self._set_status(f"分析完成！评级：{report.rating}")
                
                # TODO: 显示分析结果页面
                self._show_analysis_result(stock_data, report)
            else:
                self._set_status("未找到股票")
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            self._set_status(f"搜索失败：{str(e)}")
    
    def _show_analysis_result(self, stock_data, report):
        """显示分析结果"""
        # 清空当前页面
        self.current_page.destroy()
        self.current_page = ctk.CTkFrame(self.main_container)
        self.current_page.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 股票信息卡片
        info_frame = ctk.CTkFrame(self.current_page)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"📊 {stock_data.quote.name} ({stock_data.quote.code})",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=10)
        
        # 行情数据
        quote_data = (
            f"💰 最新价：{stock_data.quote.price:.2f}元  |  "
            f"📈 涨跌幅：{stock_data.quote.change_pct:+.2f}%  |  "
            f"💎 总市值：{stock_data.quote.market_cap/1e8:.2f}亿  |  "
            f"📊 市盈率：{stock_data.quote.pe:.2f}倍"
        )
        ctk.CTkLabel(
            info_frame,
            text=quote_data,
            font=ctk.CTkFont(size=14)
        ).pack(pady=5)
        
        # 评级卡片
        rating_frame = ctk.CTkFrame(self.current_page)
        rating_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            rating_frame,
            text=f"🎯 AI 评级：{report.rating}  |  评分：{report.score}/100",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # 报告内容（滚动区域）
        scroll_frame = ctk.CTkScrollableFrame(self.current_page)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            scroll_frame,
            text=report.content,
            font=ctk.CTkFont(size=14),
            justify="left",
            wraplength=900
        ).pack(padx=20, pady=20, anchor="w")
        
        # 操作按钮
        btn_frame = ctk.CTkFrame(self.current_page, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="🔙 返回首页",
            command=lambda: self._show_page("home"),
            width=150
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="⭐ 加入自选",
            command=lambda: self._add_to_favorite(stock_data.quote),
            width=150
        ).pack(side="left", padx=10)
    
    def _add_to_favorite(self, quote):
        """添加到自选"""
        asyncio.create_task(self._do_add_favorite(quote))
    
    async def _do_add_favorite(self, quote):
        """执行添加到自选"""
        try:
            await self.db.connect()
            await self.db.add_favorite(quote.code, quote.name, quote.market)
            self._set_status(f"已加入自选：{quote.name}")
        except Exception as e:
            logger.error(f"Add favorite error: {e}")
            self._set_status(f"添加失败：{str(e)}")
    
    def _save_settings(self):
        """保存设置"""
        em_key = self.em_api_entry.get().strip()
        qwen_key = self.qwen_api_entry.get().strip()
        
        config.set("api_keys.em_api_key", em_key)
        config.set("api_keys.qwen_api_key", qwen_key)
        
        # 重新初始化服务
        self.mx_api = MiaoXiangAPI(em_key)
        self.ai_analyzer = AIAnalyzer(qwen_key)
        
        self._set_status("配置已保存")
    
    def _set_status(self, text: str):
        """设置状态栏文本"""
        self.status_label.configure(text=text)
    
    def _on_closing(self):
        """窗口关闭事件"""
        logger.info("Application closing")
        asyncio.create_task(self.db.close())
        self.destroy()

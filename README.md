# 📈 股票分析助手 - Web 版

基于 FastAPI + 前端页面的本地 Web 应用，提供智能股票分析功能。

## 功能特性

- 📊 **个股分析** - 实时行情 + AI 智能诊断报告
- 📁 **板块监控** - 热门板块排行（开发中）
- 🎯 **智能选股** - 自然语言筛选（开发中）
- ⭐ **自选股管理** - 添加/删除自选（开发中）
- 📄 **历史报告** - 查看分析报告（开发中）
- ⚙️ **设置页面** - API Key 配置

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

访问 http://127.0.0.1:8000/settings 配置：
- 东方财富妙想 API: https://ai.eastmoney.com/mxClaw
- 千问 API: https://dashscope.console.aliyun.com/

### 3. 启动服务

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. 访问应用

浏览器打开：http://127.0.0.1:8000

## 项目结构

```
stock-analyzer-web/
├── app/
│   ├── main.py           # FastAPI 应用入口
│   ├── routes/
│   │   ├── api.py        # API 路由
│   │   └── pages.py      # 页面路由
│   ├── services/
│   │   ├── mx_api.py     # 妙想 API
│   │   └── ai_analyzer.py# AI 分析
│   ├── static/           # 静态文件
│   ├── templates/        # HTML 模板
│   └── utils/
│       ├── config.py     # 配置管理
│       └── logger.py     # 日志
├── data/                 # 数据目录
├── config.json           # 配置文件
├── requirements.txt      # 依赖
└── run.bat               # 启动脚本
```

## API 接口

### 股票查询
```bash
POST /api/stock/query
{
  "query": "比亚迪 002594",
  "select_type": "A 股"
}
```

### 股票分析
```bash
POST /api/stock/analyze
{
  "query": "比亚迪 002594"
}
```

### 获取/更新设置
```bash
GET  /api/settings
POST /api/settings
{
  "em_api_key": "...",
  "qwen_api_key": "..."
}
```

## 技术栈

- **后端**: FastAPI + Uvicorn
- **前端**: HTML + TailwindCSS + Alpine.js
- **数据源**: 东方财富妙想 API
- **AI 分析**: 千问 API

## 开发计划

- [x] 项目框架
- [x] 首页（含搜索和分析）
- [x] 设置页面
- [ ] 个股分析页（独立）
- [ ] 板块监控页
- [ ] 智能选股页
- [ ] 自选股管理
- [ ] 历史报告查看
- [ ] K 线图展示
- [ ] 数据导出

## 免责声明

本工具提供的数据和分析仅供参考，不构成投资建议。股市有风险，投资需谨慎。

## License

MIT

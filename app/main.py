"""
📈 股票分析助手 - Web 版
FastAPI 后端服务
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.routes import api, pages
from app.utils.config import config
from app.utils.logger import get_logger

logger = get_logger("main")

# 创建 FastAPI 应用
app = FastAPI(
    title="股票分析助手",
    description="基于东方财富妙想 API + 千问 AI 的智能股票分析工具",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
static_path = Path(__file__).parent / "static"
static_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# 配置模板 - 使用简单方式
templates_path = Path(__file__).parent / "templates"
templates_path.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory=str(templates_path))

# 注册路由
app.include_router(pages.router)
app.include_router(api.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("股票分析助手 Web 版启动")
    logger.info(f"访问地址：http://{config.get('app.host', '127.0.0.1')}:{config.get('app.port', 8000)}")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("股票分析助手 Web 版关闭")


@app.get("/")
async def root(request: Request):
    """根路径重定向到首页"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/home")


def find_available_port(start_port=8000, max_attempts=10):
    """查找可用端口"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    
    raise RuntimeError(f"无法找到可用端口（{start_port}-{start_port + max_attempts - 1}）")


if __name__ == "__main__":
    import uvicorn
    
    host = config.get("app.host", "127.0.0.1")
    port = config.get("app.port", 8000)
    
    # 智能端口检测
    try:
        actual_port = find_available_port(port)
        if actual_port != port:
            print(f"⚠️  端口 {port} 被占用，使用端口 {actual_port}")
        port = actual_port
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    print("=" * 60)
    print("  📈 股票分析助手 - Web 版")
    print("=" * 60)
    print(f"  访问地址：http://{host}:{port}")
    print(f"  API 文档：http://{host}:{port}/docs")
    print("=" * 60)
    print()
    
    uvicorn.run("app.main:app", host=host, port=port, reload=config.get("app.debug", False))

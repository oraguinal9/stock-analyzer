"""
页面路由
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    """首页"""
    from pathlib import Path
    templates_path = Path(__file__).parent.parent / "templates" / "home.html"
    return templates_path.read_text(encoding='utf-8')


@router.get("/sector", response_class=HTMLResponse)
async def sector_page(request: Request):
    """板块监控页"""
    from pathlib import Path
    templates_path = Path(__file__).parent.parent / "templates" / "sector.html"
    return templates_path.read_text(encoding='utf-8')


@router.get("/screener", response_class=HTMLResponse)
async def screener_page(request: Request):
    """智能选股页"""
    from pathlib import Path
    templates_path = Path(__file__).parent.parent / "templates" / "screener.html"
    return templates_path.read_text(encoding='utf-8')


@router.get("/favorites", response_class=HTMLResponse)
async def favorites_page(request: Request):
    """自选股页"""
    from pathlib import Path
    templates_path = Path(__file__).parent.parent / "templates" / "favorites.html"
    return templates_path.read_text(encoding='utf-8')


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """设置页"""
    from pathlib import Path
    templates_path = Path(__file__).parent.parent / "templates" / "settings.html"
    return templates_path.read_text(encoding='utf-8')

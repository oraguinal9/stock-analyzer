"""
配置管理模块
"""
import json
from pathlib import Path
from typing import Any, Optional

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.json"

class Config:
    """配置管理类"""
    
    _instance: Optional["Config"] = None
    _data: dict = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        """加载配置文件"""
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = self._default_config()
            self.save()
    
    def _default_config(self) -> dict:
        """默认配置"""
        return {
            "api_keys": {
                "em_api_key": "",
                "qwen_api_key": ""
            },
            "app": {
                "theme": "dark",
                "language": "zh-CN",
                "cache_days": 7,
                "window_width": 1200,
                "window_height": 800
            },
            "output": {
                "reports_dir": "./data/reports",
                "charts_dir": "./data/charts",
                "cache_dir": "./data/cache"
            },
            "database": {
                "path": "./data/stock_analyzer.db"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split(".")
        data = self._data
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value
        self.save()
    
    def save(self):
        """保存配置"""
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
    
    @property
    def em_api_key(self) -> str:
        return self.get("api_keys.em_api_key", "")
    
    @property
    def qwen_api_key(self) -> str:
        return self.get("api_keys.qwen_api_key", "")
    
    @property
    def theme(self) -> str:
        return self.get("app.theme", "dark")
    
    @property
    def reports_dir(self) -> Path:
        return Path(self.get("output.reports_dir", "./data/reports"))
    
    @property
    def charts_dir(self) -> Path:
        return Path(self.get("output.charts_dir", "./data/charts"))


# 全局配置实例
config = Config()

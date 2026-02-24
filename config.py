"""
UniLife OS — 全局配置
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# 兼容 WSL2 和 Windows 的路径处理
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# DeepSeek API 配置（国内直连，无需代理）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"  # DeepSeek-V3

# 应用配置
APP_NAME = "UniLife OS"
APP_ICON = "🎓"

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
DEEPSEEK_MODEL = "deepseek-v4-flash"  # DeepSeek-V4-Flash（function calling 优化）

# 豆包（Volces Ark）视觉 API 配置
# 用途：vision 类工具（拍小票/拍课表/拍食物/拍行李）
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "")
DOUBAO_BASE_URL = os.getenv(
    "DOUBAO_BASE_URL",
    "https://ark.cn-beijing.volces.com/api/v3",
)
DOUBAO_VISION_MODEL = os.getenv(
    "DOUBAO_VISION_MODEL",
    "doubao-vision-pro-32k-241028",
)

# 应用配置
APP_NAME = "UniLife OS"
APP_ICON = "🎓"

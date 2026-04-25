"""
UniLife OS — Agent 工具体系 facade（R2 重构后）

原 1261 行实现已迁移到 agent/ 目录：
- agent/schemas.py     TOOL_SCHEMAS + TOOL_DISPLAY_NAMES
- agent/executor.py    execute_tool 入口 + 注册表
- agent/tools/*.py     按域（course/finance/health/todo/travel）拆分

本文件保留为 re-export facade，保持 app.py / modules.chat_engine 的导入路径不变。
如需回滚 R2：`mv modules/tools.py.bak modules/tools.py` + `rm -rf agent/`。
"""
from __future__ import annotations

from agent import TOOL_SCHEMAS, TOOL_DISPLAY_NAMES, execute_tool

__all__ = ["TOOL_SCHEMAS", "TOOL_DISPLAY_NAMES", "execute_tool"]

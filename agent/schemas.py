"""
UniLife OS — 工具 Schema 注册表

TOOL_SCHEMAS 以 OpenAI function calling 格式描述工具，供 chat_engine 传给 DeepSeek。
TOOL_DISPLAY_NAMES 为工具名 → 中文名映射，供 UI 展示。

两者初始为空；agent/__init__.py 在导入时调用各 tools 模块的 register() 完成填充。
"""
from __future__ import annotations

TOOL_SCHEMAS: list[dict] = []
TOOL_DISPLAY_NAMES: dict[str, str] = {}

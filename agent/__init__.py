"""
UniLife OS — Agent 层（R2 新增）

本层托管所有 function calling 工具：
- schemas.py：OpenAI 工具 schema 列表 + 中文展示名映射（顶层常量，初始为空，由 tools 模块填充）
- executor.py：execute_tool 执行入口 + 工具名到回调的注册表
- tools/{course,finance,health,todo,travel}.py：按域拆分的工具实现，每个模块提供 register(...) 填充注册表
- tools/_validators.py：公共参数校验

外部入口：`from agent import TOOL_SCHEMAS, TOOL_DISPLAY_NAMES, execute_tool`
（modules.tools 作为 facade re-export 同样的三个符号，保持 app.py 的现有 import 不变。）
"""
from __future__ import annotations

from agent.schemas import TOOL_SCHEMAS, TOOL_DISPLAY_NAMES
from agent.executor import execute_tool, _TOOL_REGISTRY
from agent.tools import course, finance, health, todo, travel, vision


def _register_all() -> None:
    """导入时触发：把各域工具模块的 schema/display_names/callable 写入注册表。"""
    for module in (course, finance, health, todo, travel, vision):
        module.register(TOOL_SCHEMAS, TOOL_DISPLAY_NAMES, _TOOL_REGISTRY)


_register_all()

__all__ = ["TOOL_SCHEMAS", "TOOL_DISPLAY_NAMES", "execute_tool"]

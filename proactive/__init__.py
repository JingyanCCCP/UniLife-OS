"""
UniLife OS — proactive 包入口

对外暴露：
- engine.scan_and_persist / scan_safely / list_unread
- events.ProactiveEvent / mark_read
- rules（规则模块本体，便于单测）

约定：外部模块只 `from proactive import engine, events, rules`，不要跨包访问 persistence。
"""
from proactive import engine, events, rules  # noqa: F401
from proactive.events import ProactiveEvent, mark_read  # noqa: F401

__all__ = ["engine", "events", "rules", "ProactiveEvent", "mark_read"]

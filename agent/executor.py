"""
UniLife OS — 工具执行入口

execute_tool(name, args) 是 chat_engine 收到 LLM function_call 后调用的唯一入口。
- 所有工具通过 agent.tools.{...}.register() 写入 _TOOL_REGISTRY。
- 未注册工具返回友好错误串，不抛异常。
- 工具内部抛异常时也包装为错误串返回（LLM 继续会话，而不是挂掉）。
- R3 起成功路径末尾调 proactive.engine.scan_safely，刷新主动关怀事件。
- R5 起保留最近 _MAX_RECENT 次调用快照到 module-level 列表，供侧边栏 dev 信息展示。
"""
from __future__ import annotations

from datetime import datetime
from typing import Callable

# 工具名 → 回调。回调签名：Callable[[dict], str]。
_TOOL_REGISTRY: dict[str, Callable[[dict], str]] = {}

# 最近 N 次工具调用（非持久化，跟随进程）。只做可观测性使用。
_MAX_RECENT = 5
_RECENT_TOOL_CALLS: list[dict] = []


def execute_tool(name: str, args: dict) -> str:
    """按名称执行工具。兜底未知工具和运行时异常。

    执行成功后触发一次主动关怀扫描（`proactive.engine.scan_safely()` 吞掉所有异常），
    让下一轮 LLM 调用能看到最新事件。R3 引入。

    所有调用（成功 / 失败）都会被追加到 _RECENT_TOOL_CALLS（最多 N 条，先进先出）。
    """
    fn = _TOOL_REGISTRY.get(name)
    if fn is None:
        result = f"未知工具: {name}"
        _record_call(name, args, result, ok=False)
        return result
    if not isinstance(args, dict):
        result = f"工具参数必须是 JSON 对象，收到: {type(args).__name__}"
        _record_call(name, args, result, ok=False)
        return result
    try:
        result = fn(args)
    except Exception as e:
        result = f"工具执行出错: {e}"
        _record_call(name, args, result, ok=False)
        return result
    _record_call(name, args, result, ok=True)
    _scan_proactive()
    return result


def recent_tool_calls() -> list[dict]:
    """最近的工具调用快照（从旧到新）。用于侧边栏「开发者信息」。"""
    return list(_RECENT_TOOL_CALLS)


def _record_call(name: str, args, result: str, ok: bool) -> None:
    _RECENT_TOOL_CALLS.append({
        "name": name,
        "args": args if isinstance(args, dict) else str(args),
        "result": result,
        "ok": ok,
        "at": datetime.now().isoformat(timespec="seconds"),
    })
    if len(_RECENT_TOOL_CALLS) > _MAX_RECENT:
        del _RECENT_TOOL_CALLS[: len(_RECENT_TOOL_CALLS) - _MAX_RECENT]


def _scan_proactive() -> None:
    """工具执行后的主动关怀扫描钩子。延迟导入 proactive 以避免循环/启动成本。"""
    try:
        from proactive import engine
        engine.scan_safely()
    except Exception:  # pragma: no cover — 扫描失败不影响用户主流程
        pass

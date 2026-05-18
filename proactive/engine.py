"""
UniLife OS — 主动关怀扫描引擎（R3 新增）

scan_and_persist() 是同步触发入口：
- App 打开时（R4 接入 ui/sidebar）
- 每次工具执行后（agent/executor.execute_tool 收尾调用，吞异常）
- 每轮 chat 前（context_builder 读最新未读事件并注入）

去重策略：同 dedupe_key 在 DEDUPE_WINDOW_HOURS 小时内只写入一次。
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta

from proactive import events as ev_module
from proactive.events import ProactiveEvent
from proactive.rules import ALL_RULES


DEDUPE_WINDOW_HOURS = 12


def _recently_emitted(dedupe_key: str, now: datetime) -> bool:
    """同 dedupe_key 在 DEDUPE_WINDOW_HOURS 内是否已记录。"""
    window = timedelta(hours=DEDUPE_WINDOW_HOURS)
    for event in ev_module.list_all():
        if event.dedupe_key != dedupe_key:
            continue
        if not event.created_at:
            continue
        try:
            emitted_at = datetime.fromisoformat(event.created_at)
        except ValueError:
            continue
        if now - emitted_at < window:
            return True
    return False


def scan_and_persist() -> list[ProactiveEvent]:
    """跑所有规则，对未在 12h 内发过的事件 upsert 并返回新事件列表。"""
    now = datetime.now()
    new_events: list[ProactiveEvent] = []
    for rule_fn in ALL_RULES:
        try:
            produced = rule_fn() or []
        except Exception as e:  # pragma: no cover — 规则 bug 不影响主流程
            print(f"[proactive] rule {rule_fn.__name__} failed: {e}", file=sys.stderr)
            continue
        for ev in produced:
            if not isinstance(ev, ProactiveEvent):
                continue
            recently = _recently_emitted(ev.dedupe_key, now)
            if recently:
                # 数据可能变了（如预算金额），更新事件内容但不计入新事件
                ev_module.upsert(ev)
                continue
            ev_module.upsert(ev)
            new_events.append(ev)
    return new_events


def list_unread(limit: int | None = None) -> list[ProactiveEvent]:
    """未读事件快照（倒序），供 UI / context_builder 使用。"""
    return ev_module.list_unread(limit=limit)


def scan_safely() -> None:
    """执行扫描，吞掉所有异常。供 agent/executor 收尾钩子使用。"""
    try:
        scan_and_persist()
    except Exception as e:  # pragma: no cover
        print(f"[proactive] scan_safely error: {e}", file=sys.stderr)

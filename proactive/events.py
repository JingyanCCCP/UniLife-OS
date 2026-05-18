"""
UniLife OS — 主动关怀事件结构（R3 新增）

ProactiveEvent 是一条「系统主动发现的状态风险」的标准表示，在 persistence 中以 dict
形式存储（proactive_events 字段）。events.py 同时暴露与 persistence 的薄封装，
供 rules / engine / UI 使用。

字段说明：
- event_type: 规则类型。示例：budget_risk / todo_due / exam_near / sleep_short /
              exercise_missing / travel_packing
- severity:   high / medium / low
- title:      UI 卡片标题（2~10 字）
- reason:     一句话解释触发原因（LLM / UI 都会看到，要自然口语）
- suggested_action: 建议动作（要具体可执行，不说空话）
- dedupe_key: 去重键。示例：budget_risk:2026-04 / exam_near:线性代数 / todo_due:8
              相同 dedupe_key 在 12h 内只触发一次。
- created_at: ISO 格式 UTC 时间（`datetime.now().isoformat()`）
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime

from modules.persistence import (
    list_proactive_events,
    upsert_proactive_event,
    mark_proactive_read,
    get_proactive_read_keys,
)


@dataclass
class ProactiveEvent:
    """一条主动关怀事件。"""
    event_type: str
    severity: str  # "high" / "medium" / "low"
    title: str
    reason: str
    suggested_action: str
    dedupe_key: str
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat(timespec="seconds")

    def to_dict(self) -> dict:
        return asdict(self)


def from_dict(data: dict) -> ProactiveEvent:
    """宽松构造：persistence 里残缺字段时，补默认值。"""
    return ProactiveEvent(
        event_type=data.get("event_type", ""),
        severity=data.get("severity", "low"),
        title=data.get("title", ""),
        reason=data.get("reason", ""),
        suggested_action=data.get("suggested_action", ""),
        dedupe_key=data.get("dedupe_key", ""),
        created_at=data.get("created_at", ""),
    )


# ---------- persistence 薄封装 ----------

def list_all() -> list[ProactiveEvent]:
    """所有事件（含已读，按 created_at 倒序）。"""
    return [from_dict(e) for e in list_proactive_events()]


def _is_still_active(event: ProactiveEvent) -> bool:
    """过滤状态已经恢复的旧提醒，避免继续进入 UI / LLM 上下文。"""
    try:
        if event.event_type == "exercise_missing":
            from modules.mock_data import get_health
            return get_health().get("exercise_target_miss_streak", 0) >= 3
        if event.event_type == "budget_risk":
            from modules.mock_data import get_finance
            return get_finance().get("budget_usage_pct", 0) > 80
    except Exception:
        return True
    return True


def list_unread(limit: int | None = None) -> list[ProactiveEvent]:
    """未读事件（倒序，最多 limit 条）。"""
    read = set(get_proactive_read_keys())
    events = [e for e in list_all() if e.dedupe_key not in read and _is_still_active(e)]
    if limit is not None:
        events = events[:limit]
    return events


def upsert(event: ProactiveEvent) -> None:
    """写入/更新事件。created_at 自动刷新为当前时间，用于 12h 去重判定。"""
    # 每次 upsert 覆盖 created_at，保证去重窗口以最近一次触发为起点
    event.created_at = datetime.now().isoformat(timespec="seconds")
    upsert_proactive_event(event.to_dict())


def mark_read(dedupe_key: str) -> None:
    """标记事件为已读。"""
    mark_proactive_read(dedupe_key)

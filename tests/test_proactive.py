"""
R5 · test_proactive — 6 条规则触发 + 12h 去重 + mark_read + get_alerts 字段兼容。
"""
from __future__ import annotations

from datetime import datetime, timedelta

from proactive import engine, events, rules
from proactive.events import ProactiveEvent


def test_all_six_rules_exist():
    names = ["budget_risk", "todo_due", "exam_near", "sleep_short",
             "exercise_missing", "travel_packing"]
    for n in names:
        fn = getattr(rules, f"check_{n}", None)
        assert callable(fn), f"缺少规则 check_{n}"


def test_rules_all_return_list(tmp_data_file):
    for fn in rules.ALL_RULES:
        out = fn()
        assert isinstance(out, list)
        for ev in out:
            assert isinstance(ev, ProactiveEvent)
            assert ev.dedupe_key
            assert ev.severity in ("high", "medium", "low")


def test_scan_dedupe_within_12h(tmp_data_file):
    first = engine.scan_and_persist()
    # 首次扫描应至少触发 1 条（预算告急在当前 seed 下必然触发）
    assert len(first) >= 1, "首次扫描应至少 1 条事件（预算 82.5% > 80%）"
    second = engine.scan_and_persist()
    assert second == [], f"12h 内同 dedupe_key 应去重：{second}"


def test_mark_read_removes_from_unread(tmp_data_file):
    engine.scan_and_persist()
    unread = engine.list_unread()
    assert len(unread) > 0
    key = unread[0].dedupe_key
    events.mark_read(key)
    remaining = [e.dedupe_key for e in engine.list_unread()]
    assert key not in remaining


def test_dedupe_expires_after_window(tmp_data_file):
    """模拟事件在 13h 前发生 → 再次扫描应重新触发（同 dedupe_key 也算新事件）。"""
    # 先扫一轮
    first = engine.scan_and_persist()
    assert first

    # 手动把所有事件的 created_at 推回 13h 前
    from modules.persistence import load_user_data, save_user_data
    data = load_user_data()
    old_time = (datetime.now() - timedelta(hours=13)).isoformat(timespec="seconds")
    for e in data["proactive_events"]:
        e["created_at"] = old_time
    save_user_data(data)

    # 再次扫描应能重新触发
    second = engine.scan_and_persist()
    assert len(second) >= 1, "13h 后同 dedupe_key 应可再次触发"


def test_get_alerts_field_compatibility(tmp_data_file):
    from modules.mock_data import get_alerts
    alerts = get_alerts()
    for a in alerts:
        # 原接口字段
        assert {"severity", "icon", "title", "message"} <= a.keys()
        # R3 新增字段
        assert "suggested_action" in a
        assert "dedupe_key" in a


def test_alerts_limit_at_5(tmp_data_file):
    from modules.mock_data import get_alerts
    alerts = get_alerts()
    assert len(alerts) <= 5, f"get_alerts 应限 5 条，实际 {len(alerts)}"


def test_rule_exception_does_not_break_others(tmp_data_file, monkeypatch):
    """单条规则抛错时其他规则仍应跑通。"""
    def broken_rule():
        raise RuntimeError("故意的")

    # 把第一条规则换成会爆的
    original = list(rules.ALL_RULES)
    monkeypatch.setattr(rules, "ALL_RULES", [broken_rule] + original[1:])

    # 不应抛异常
    out = engine.scan_and_persist()
    # 后续规则仍能触发事件
    assert isinstance(out, list)

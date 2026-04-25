"""
R5 · test_persistence — 增量覆盖 / 跨天 / 跨周重置逻辑。
"""
from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import patch

from modules import persistence


def test_default_data_initialized(tmp_data_file):
    data = persistence.load_user_data()
    for k in persistence._DEFAULT_DATA.keys():
        assert k in data, f"默认字段 {k} 缺失"


def test_add_expense_persists(tmp_data_file):
    persistence.add_expense("奶茶", 18, "餐饮")
    data = persistence.load_user_data()
    assert len(data["extra_transactions"]) == 1
    record = data["extra_transactions"][0]
    assert record["item"] == "奶茶"
    assert record["amount"] == 18
    assert record["category"] == "餐饮"
    assert record["icon"] == "🍜"


def test_todo_status_update(tmp_data_file):
    persistence.update_todo_status(3, True)
    overrides = persistence.get_todo_overrides()
    assert overrides["3"] is True
    persistence.update_todo_status(3, False)
    overrides = persistence.get_todo_overrides()
    assert overrides["3"] is False


def test_water_increment_persists_cup_count(tmp_data_file):
    persistence.increment_water()
    persistence.increment_water()
    persistence.increment_water()
    overrides = persistence.get_health_overrides()
    assert overrides["water_cups"] == 3


def test_water_resets_when_date_changes(tmp_data_file):
    """水杯数是「当天叠加」，跨天自动归零。"""
    persistence.increment_water()
    assert persistence.get_health_overrides()["water_cups"] == 1

    # 模拟昨天已写入的数据
    data = persistence.load_user_data()
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    data["health_overrides"]["override_date"] = yesterday
    persistence.save_user_data(data)

    # 今天第一次喝水，跨天自动重置
    persistence.increment_water()
    overrides = persistence.get_health_overrides()
    assert overrides["water_cups"] == 1
    assert overrides["override_date"] == datetime.now().strftime("%Y-%m-%d")


def test_exercise_weekly_resets_across_week(tmp_data_file):
    """本周运动计数跨周重置。"""
    # 本周第一次打卡
    persistence.log_exercise()
    weekly = persistence.get_exercise_weekly()
    assert weekly["count"] == 1
    this_week = weekly["week_start"]

    # 模拟上周的计数
    data = persistence.load_user_data()
    data["exercise_weekly"] = {"week_start": "2020-01-06", "count": 5}
    data["health_overrides"] = {}  # 清掉今日打卡标记以便再次打卡
    persistence.save_user_data(data)

    persistence.log_exercise()
    weekly = persistence.get_exercise_weekly()
    assert weekly["count"] == 1, "跨周应重置为 1"
    assert weekly["week_start"] == this_week


def test_exercise_same_day_no_double_count(tmp_data_file):
    first = persistence.log_exercise()
    second = persistence.log_exercise()
    assert first is True
    assert second is False
    weekly = persistence.get_exercise_weekly()
    assert weekly["count"] == 1


def test_add_todo_unique_ids(tmp_data_file):
    t1 = persistence.add_todo("任务1", "2099-01-01")
    t2 = persistence.add_todo("任务2", "2099-01-02")
    assert t1["id"] != t2["id"]
    assert t1["id"] > 7  # mock 保留 1-7


def test_proactive_events_upsert_and_read(tmp_data_file):
    event = {
        "event_type": "budget_risk",
        "severity": "high",
        "title": "test",
        "reason": "r",
        "suggested_action": "a",
        "dedupe_key": "budget_risk:2026-04",
        "created_at": "2026-04-25T00:00:00",
    }
    persistence.upsert_proactive_event(event)
    events = persistence.list_proactive_events()
    assert len(events) == 1

    # upsert 相同 dedupe_key 覆盖
    event["severity"] = "low"
    persistence.upsert_proactive_event(event)
    events = persistence.list_proactive_events()
    assert len(events) == 1
    assert events[0]["severity"] == "low"

    # mark_read
    persistence.mark_proactive_read("budget_risk:2026-04")
    read = persistence.get_proactive_read_keys()
    assert "budget_risk:2026-04" in read


def test_save_chat_history_drops_raw_image_preview_bytes(tmp_data_file):
    persistence.save_chat_history([
        {
            "role": "user",
            "content": "帮我记账",
            "_image_preview": b"\xff\xd8",
            "_image_preview_b64": "/9g=",
        }
    ])
    messages = persistence.load_chat_history()
    assert messages[0]["_image_preview_b64"] == "/9g="
    assert "_image_preview" not in messages[0]

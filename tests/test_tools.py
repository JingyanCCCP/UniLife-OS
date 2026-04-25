"""
R5 · test_tools — 工具参数边界 + 未知工具 + 查询类返回非空。
"""
from __future__ import annotations

from modules.tools import TOOL_SCHEMAS, TOOL_DISPLAY_NAMES, execute_tool


def test_tool_count_is_28(tmp_data_file):
    """工具总数 = 24 文本工具 + 4 视觉工具（R7-T3 新增）。"""
    assert len(TOOL_SCHEMAS) == 28
    assert len(TOOL_DISPLAY_NAMES) == 28


def test_unknown_tool_graceful(tmp_data_file):
    r = execute_tool("不存在的工具", {})
    assert "未知工具" in r


def test_invalid_args_type(tmp_data_file):
    r = execute_tool("query_schedule", "不是 dict")
    assert "JSON 对象" in r or "参数" in r


def test_record_expense_empty_item(tmp_data_file):
    r = execute_tool("record_expense", {"item": "", "amount": 10, "category": "其他"})
    assert "消费项目" in r


def test_record_expense_negative_amount(tmp_data_file):
    r = execute_tool("record_expense", {"item": "t", "amount": -5, "category": "其他"})
    assert "金额" in r


def test_record_expense_huge_amount(tmp_data_file):
    r = execute_tool("record_expense", {"item": "t", "amount": 1_000_000, "category": "其他"})
    assert "金额" in r


def test_record_steps_boundary(tmp_data_file):
    assert "步数" in execute_tool("record_steps", {"steps": -1})
    assert "步数" in execute_tool("record_steps", {"steps": 9_999_999})
    # 合法边界通过
    ok = execute_tool("record_steps", {"steps": 8000})
    assert "已记录" in ok


def test_record_sleep_boundary(tmp_data_file):
    assert "睡眠" in execute_tool("record_sleep", {"hours": -1})
    assert "睡眠" in execute_tool("record_sleep", {"hours": 25})
    assert "已记录" in execute_tool("record_sleep", {"hours": 7.5, "quality": "良好"})


def test_set_exercise_goal_boundary(tmp_data_file):
    assert "运动目标" in execute_tool("set_exercise_goal", {"goal": 2})
    assert "运动目标" in execute_tool("set_exercise_goal", {"goal": 10})
    assert "每周" in execute_tool("set_exercise_goal", {"goal": 5})


def test_toggle_todo_unknown(tmp_data_file):
    r = execute_tool("toggle_todo", {"task_id": 9999})
    assert "未找到" in r


def test_query_tools_return_non_empty(tmp_data_file):
    for name in ["query_schedule", "query_finance", "query_health",
                 "query_todos", "query_exams", "query_travel"]:
        out = execute_tool(name, {})
        assert isinstance(out, str) and len(out) > 0
        assert "未知工具" not in out
        assert "工具执行出错" not in out


def test_update_packing(tmp_data_file):
    r = execute_tool("update_packing", {"item": "充电宝", "checked": True})
    assert "充电宝" in r
    r2 = execute_tool("update_packing", {"item": "充电宝", "checked": False})
    assert "充电宝" in r2


def test_add_course_and_delete(tmp_data_file):
    add_r = execute_tool("add_course", {
        "weekday": "周六", "time": "10:00-12:00",
        "course": "测试选修", "location": "测试楼",
    })
    assert "测试选修" in add_r
    del_r = execute_tool("delete_course", {"course_name": "测试选修"})
    assert "已删除" in del_r


def test_update_travel_create_then_add_stop(tmp_data_file):
    create_r = execute_tool("update_travel", {
        "create": True, "trip_name": "测试", "date": "2099-01-01", "budget": 100,
    })
    assert "已创建" in create_r
    add_r = execute_tool("add_itinerary_stop", {
        "time": "09:00", "activity": "测试活动", "location": "测试地点",
    })
    assert "测试活动" in add_r

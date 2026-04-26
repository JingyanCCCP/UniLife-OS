"""
R7-T5 · test_vision — modules/vision.py + agent/tools/vision.py 单元测试。

mock 豆包 chat.completions.create，覆盖：
- recognize_* 正常路径 + JSON 解析失败 + 网络异常 + KEY 缺失 + markdown 剥离
- 链式工具 record_expense_from_image / import_courses_from_image 真实写库
- 链式工具 低置信度兜底 + 非法 base64 兜底
"""
from __future__ import annotations

import base64
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import modules.vision as vision_mod
from modules.vision import (
    recognize_receipt,
    recognize_food,
    recognize_schedule,
    recognize_packing,
)


def _fake_response(content: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


@pytest.fixture
def mock_vision(monkeypatch):
    """返回 setter；setter(content_or_exc) 配置豆包下次返回（字符串）或抛异常。"""
    fake_client = MagicMock()

    def _set(content_or_exc):
        if isinstance(content_or_exc, BaseException):
            fake_client.chat.completions.create.side_effect = content_or_exc
            fake_client.chat.completions.create.return_value = None
        else:
            fake_client.chat.completions.create.side_effect = None
            fake_client.chat.completions.create.return_value = _fake_response(
                content_or_exc
            )

    monkeypatch.setattr(vision_mod, "_get_client", lambda: fake_client)
    monkeypatch.setattr(vision_mod, "_client", None)
    return _set


# ---------- recognize_receipt ----------

def test_recognize_receipt_happy(mock_vision):
    mock_vision('{"amount": 18, "item": "奶茶", "category": "餐饮", "confidence": 0.92}')
    r = recognize_receipt(b"\xff\xd8\xff")
    assert r["error"] is None
    assert r["amount"] == 18
    assert r["item"] == "奶茶"
    assert r["category"] == "餐饮"


def test_recognize_receipt_json_parse_fail(mock_vision):
    mock_vision("这不是 JSON 而是普通文本")
    r = recognize_receipt(b"\xff\xd8\xff")
    assert r["error"] and "不是合法 JSON" in r["error"]
    assert r["amount"] == 0


def test_recognize_receipt_network_error(mock_vision):
    mock_vision(ConnectionError("network down"))
    r = recognize_receipt(b"\xff\xd8\xff")
    assert r["error"] and "ConnectionError" in r["error"]


def test_recognize_receipt_missing_key(monkeypatch):
    monkeypatch.setattr(vision_mod, "_get_client", lambda: None)
    monkeypatch.setattr(vision_mod, "_client", None)
    r = recognize_receipt(b"\xff\xd8\xff")
    assert r["error"] and "DOUBAO_API_KEY" in r["error"]


def test_recognize_receipt_invalid_category_fallback(mock_vision):
    mock_vision('{"amount": 50, "item": "水果", "category": "蔬菜水果", "confidence": 0.9}')
    r = recognize_receipt(b"\xff\xd8\xff")
    assert r["category"] == "其他"  # 非合法分类回退


def test_recognize_receipt_markdown_codeblock_stripped(mock_vision):
    mock_vision(
        '```json\n{"amount": 5, "item": "矿泉水", "category": "餐饮", "confidence": 0.8}\n```'
    )
    r = recognize_receipt(b"\xff\xd8\xff")
    assert r["error"] is None
    assert r["amount"] == 5


def test_recognize_receipt_empty_bytes():
    r = recognize_receipt(b"")
    assert r["error"] and "image_bytes 为空" in r["error"]


# ---------- recognize_food ----------

def test_recognize_food_happy(mock_vision):
    mock_vision('{"name": "麻辣烫", "calorie_estimate": 450, "confidence": 0.85}')
    r = recognize_food(b"\xff\xd8")
    assert r["error"] is None
    assert r["name"] == "麻辣烫"
    assert r["calorie_estimate"] == 450


# ---------- recognize_schedule ----------

def test_recognize_schedule_multiple_courses(mock_vision):
    mock_vision(
        '{"courses": ['
        '{"name": "高数", "day": "周一", "time": "08:00-09:40", "location": "A101"},'
        '{"name": "线代", "day": "周三", "time": "10:00-11:40", "location": "B202"},'
        '{"name": "物理", "day": "周五", "time": "14:00-15:40", "location": "C303"}'
        ']}'
    )
    r = recognize_schedule(b"\xff\xd8")
    assert r["error"] is None
    assert len(r["courses"]) == 3
    assert r["courses"][0]["name"] == "高数"


def test_recognize_schedule_courses_field_not_list(mock_vision):
    """课程字段类型异常时强制回退为空数组。"""
    mock_vision('{"courses": null}')
    r = recognize_schedule(b"\xff\xd8")
    assert isinstance(r["courses"], list)
    assert len(r["courses"]) == 0


# ---------- recognize_packing ----------

def test_recognize_packing_missing_and_extra(mock_vision):
    mock_vision(
        '{"found": ["充电器", "牙刷"], "missing": ["雨伞"], "extra": ["耳机"]}'
    )
    r = recognize_packing(b"\xff\xd8", ["充电器", "牙刷", "雨伞"])
    assert r["error"] is None
    assert r["found"] == ["充电器", "牙刷"]
    assert r["missing"] == ["雨伞"]
    assert r["extra"] == ["耳机"]


# ---------- 链式工具：record_expense_from_image ----------

def test_chained_record_expense_writes_persistence(mock_vision, tmp_data_file):
    """end-to-end: 模型 mock + 真实持久化写入。"""
    from agent.executor import execute_tool
    from modules.persistence import get_extra_transactions

    mock_vision('{"amount": 28, "item": "麻辣烫", "category": "餐饮", "confidence": 0.92}')

    image_b64 = base64.b64encode(b"\xff\xd8\xff fake jpeg").decode()
    r = execute_tool("record_expense_from_image", {"image_b64": image_b64})

    assert "已识别并记账" in r
    assert "麻辣烫" in r
    assert "28" in r

    txns = get_extra_transactions()
    assert len(txns) == 1
    assert txns[0]["item"] == "麻辣烫"
    assert txns[0]["amount"] == 28
    assert txns[0]["category"] == "餐饮"


def test_chained_record_expense_low_confidence_no_write(mock_vision, tmp_data_file):
    """置信度 < 0.5 拒绝并提示，不写库。"""
    from agent.executor import execute_tool
    from modules.persistence import get_extra_transactions

    mock_vision('{"amount": 100, "item": "x", "category": "其他", "confidence": 0.2}')
    image_b64 = base64.b64encode(b"\xff\xd8 fake").decode()

    r = execute_tool("record_expense_from_image", {"image_b64": image_b64})
    assert "置信度过低" in r
    assert len(get_extra_transactions()) == 0


def test_chained_import_courses_writes_extra_courses(mock_vision, tmp_data_file):
    """链式：模型 mock 多门课 → 真实写到 extra_courses。"""
    from agent.executor import execute_tool
    from modules.persistence import get_extra_courses

    mock_vision(
        '{"courses": ['
        '{"name": "虚构选修课", "day": "周日", "time": "20:00-21:30", "location": "测试楼A"},'
        '{"name": "另一门虚构课", "day": "周六", "time": "14:00-15:30", "location": "测试楼B"}'
        ']}'
    )

    image_b64 = base64.b64encode(b"\xff").decode()
    r = execute_tool("import_courses_from_image", {"image_b64": image_b64})

    assert "已导入" in r
    assert "虚构选修课" in r

    new_courses = get_extra_courses()
    names = {c["course"] for c in new_courses}
    assert "虚构选修课" in names
    assert "另一门虚构课" in names


def test_chained_invalid_b64_friendly_error(tmp_data_file):
    """非法 base64 字符串返回友好错误，不抛 traceback。"""
    from agent.executor import execute_tool
    r = execute_tool("record_expense_from_image", {"image_b64": "!!! not base64 !!!"})
    assert isinstance(r, str)
    assert "解码失败" in r or "image_b64" in r


def test_chained_empty_b64_friendly_error(tmp_data_file):
    """空 image_b64 字符串友好错误。"""
    from agent.executor import execute_tool
    for tool in (
        "record_expense_from_image",
        "import_courses_from_image",
        "log_food_calories",
        "check_packing_from_image",
    ):
        r = execute_tool(tool, {"image_b64": ""})
        assert isinstance(r, str)
        assert "image_b64" in r

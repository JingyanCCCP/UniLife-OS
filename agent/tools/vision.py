"""agent.tools.vision — 多模态视觉链式工具（4 个，R7-T3 新增）。

工具清单：
- record_expense_from_image: 拍小票 → 识别 → 自动记账
- import_courses_from_image: 拍课表 → 识别 → 批量导入课程（去重）
- log_food_calories: 拍食物 → 识别 + 估卡路里（只返回文本，暂不写库）
- check_packing_from_image: 拍行李 → 对照旅行清单返回 missing/found/extra

每个工具都接收 base64 编码的图片字符串（image_b64），下游链式调用：
  modules.vision.recognize_*  →  modules.persistence.*  →  返回自然语言摘要

错误兜底：image_b64 为空 / base64 解码失败 / 豆包返回 error / 置信度过低 → 全部返回友好文本。
"""
from __future__ import annotations

import base64

from modules.vision import (
    recognize_receipt,
    recognize_food,
    recognize_schedule,
    recognize_packing,
)
from modules.persistence import (
    add_expense,
    add_course as persist_add_course,
)
from modules.mock_data import get_schedule, get_travel_plan

from agent.tools._validators import validate_non_empty_str


# ---------------------------------------------------------------------------
# 共享 helper
# ---------------------------------------------------------------------------

_MIN_RECEIPT_CONFIDENCE = 0.5
_MIN_FOOD_CONFIDENCE = 0.4


def _decode_image(image_b64: str) -> bytes | str:
    """解码 base64 → bytes。失败返回错误字符串。"""
    if (err := validate_non_empty_str(image_b64, "image_b64")):
        return err
    try:
        # 去掉可能的 data URL 前缀
        if image_b64.startswith("data:"):
            comma = image_b64.find(",")
            if comma > 0:
                image_b64 = image_b64[comma + 1:]
        return base64.b64decode(image_b64, validate=False)
    except (ValueError, TypeError, base64.binascii.Error) as e:
        return f"image_b64 解码失败：{type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "record_expense_from_image",
            "description": (
                "用户上传小票/收据照片时调用。识别图中金额、商品和类别后自动记一笔消费。"
                "返回的文本会包含识别结果和记账结果。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "image_b64": {
                        "type": "string",
                        "description": "小票图片的 base64 编码（前端已上传后注入 user 消息）",
                    },
                    "note": {
                        "type": "string",
                        "description": "可选备注，会附加在 item 名后",
                    },
                },
                "required": ["image_b64"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "import_courses_from_image",
            "description": (
                "用户上传课表截图时调用。识别图中所有课程并自动导入课表，"
                "已存在的课程会跳过避免重复。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "image_b64": {
                        "type": "string",
                        "description": "课表截图的 base64 编码",
                    },
                },
                "required": ["image_b64"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_food_calories",
            "description": (
                "用户上传食物照片时调用。识别食物名并估算卡路里。"
                "本工具只返回识别结果，不写入持久化（当前 health 模型不存食物记录）。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "image_b64": {
                        "type": "string",
                        "description": "食物照片的 base64 编码",
                    },
                },
                "required": ["image_b64"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_packing_from_image",
            "description": (
                "用户上传行李照片时调用。对照当前旅行计划的必带清单，"
                "返回已带物品 / 还差物品 / 额外物品。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "image_b64": {
                        "type": "string",
                        "description": "行李照片的 base64 编码",
                    },
                },
                "required": ["image_b64"],
            },
        },
    },
]

DISPLAY_NAMES: dict[str, str] = {
    "record_expense_from_image": "拍小票记账",
    "import_courses_from_image": "拍课表导入",
    "log_food_calories": "拍食物估卡路里",
    "check_packing_from_image": "拍行李清单",
}


# ---------------------------------------------------------------------------
# Executors
# ---------------------------------------------------------------------------

def _exec_record_expense_from_image(args: dict) -> str:
    decoded = _decode_image(args.get("image_b64", ""))
    if isinstance(decoded, str):
        return decoded

    result = recognize_receipt(decoded)
    if result.get("error"):
        return f"识别小票失败：{result['error']}"

    amount = result.get("amount", 0)
    item = (result.get("item") or "").strip()
    category = result.get("category", "其他")
    confidence = result.get("confidence", 0.0)

    if amount <= 0 or not item or confidence < _MIN_RECEIPT_CONFIDENCE:
        return (
            f"识别置信度过低（{confidence:.2f}），无法确认是有效小票。"
            f"识别结果：amount={amount}, item={item or '空'}。"
            "请改用文字告诉我消费详情。"
        )

    note = (args.get("note") or "").strip()
    full_item = f"{item}（{note}）" if note else item
    record = add_expense(full_item, float(amount), category)
    return (
        f"已识别并记账：{full_item} ¥{amount:.1f}（{category}），"
        f"识别置信度 {confidence:.2f}，记录日期 {record['date']}。"
    )


def _exec_import_courses_from_image(args: dict) -> str:
    decoded = _decode_image(args.get("image_b64", ""))
    if isinstance(decoded, str):
        return decoded

    result = recognize_schedule(decoded)
    if result.get("error"):
        return f"识别课表失败：{result['error']}"

    courses = result.get("courses", [])
    if not courses:
        return "图中未识别到任何课程，请确认是否为课表截图。"

    existing = get_schedule()
    existing_keys = {(c["weekday"], c["time"], c["course"]) for c in existing}

    imported, skipped = [], []
    valid_weekdays = {"周一", "周二", "周三", "周四", "周五", "周六", "周日"}

    for c in courses:
        name = (c.get("name") or "").strip()
        weekday = (c.get("day") or c.get("weekday") or "").strip()
        time = (c.get("time") or "").strip()
        location = (c.get("location") or "").strip()

        if not (name and weekday and time):
            continue
        if weekday not in valid_weekdays:
            continue

        key = (weekday, time, name)
        if key in existing_keys:
            skipped.append(f"{weekday} {time} {name}")
            continue

        record = persist_add_course(weekday, time, name, location or "待补充")
        imported.append(f"{weekday} {time} {name}（ID={record['id']}）")
        existing_keys.add(key)

    lines = []
    if imported:
        lines.append(f"已导入 {len(imported)} 门课程：")
        for x in imported:
            lines.append(f"  - {x}")
    if skipped:
        lines.append(f"跳过 {len(skipped)} 门已存在的课程：")
        for x in skipped:
            lines.append(f"  - {x}")
    if not imported and not skipped:
        lines.append("识别到的课程数据不完整，未导入任何课程。")
    return "\n".join(lines)


def _exec_log_food_calories(args: dict) -> str:
    decoded = _decode_image(args.get("image_b64", ""))
    if isinstance(decoded, str):
        return decoded

    result = recognize_food(decoded)
    if result.get("error"):
        return f"识别食物失败：{result['error']}"

    name = (result.get("name") or "").strip()
    cal = result.get("calorie_estimate", 0)
    confidence = result.get("confidence", 0.0)

    if not name or confidence < _MIN_FOOD_CONFIDENCE:
        return f"识别置信度过低（{confidence:.2f}），无法确认是食物。"

    return (
        f"🍱 识别为：{name}\n"
        f"估算热量：约 {cal} 千卡\n"
        f"识别置信度：{confidence:.2f}\n"
        "（提示：当前版本仅展示估算结果，暂不写入健康日志。）"
    )


def _exec_check_packing_from_image(args: dict) -> str:
    decoded = _decode_image(args.get("image_b64", ""))
    if isinstance(decoded, str):
        return decoded

    travel = get_travel_plan()
    if not travel or travel.get("status") == "已删除":
        return "当前没有进行中的旅行计划，无法对照清单。请先创建旅行计划。"

    expected = list(travel.get("packing_list") or [])
    if not expected:
        return "当前旅行计划没有必带清单，无法对照。请先在旅行计划中添加清单项。"

    result = recognize_packing(decoded, expected)
    if result.get("error"):
        return f"识别行李失败：{result['error']}"

    found = result.get("found", [])
    missing = result.get("missing", [])
    extra = result.get("extra", [])

    lines = [f"🧳 行李清单核对（旅行：{travel.get('trip_name', '当前计划')}）："]
    lines.append(f"✅ 已带（{len(found)}/{len(expected)}）：" + ("、".join(found) if found else "（无）"))
    if missing:
        lines.append(f"⚠️ 还差：" + "、".join(missing))
    else:
        lines.append("🎉 必带清单已全部备齐！")
    if extra:
        lines.append(f"➕ 额外物品：" + "、".join(extra))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

def register(schemas: list, display_names: dict, registry: dict) -> None:
    schemas.extend(SCHEMAS)
    display_names.update(DISPLAY_NAMES)
    registry.update({
        "record_expense_from_image": _exec_record_expense_from_image,
        "import_courses_from_image": _exec_import_courses_from_image,
        "log_food_calories": _exec_log_food_calories,
        "check_packing_from_image": _exec_check_packing_from_image,
    })

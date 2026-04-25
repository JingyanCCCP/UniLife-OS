"""agent.tools.travel — 旅行相关工具（6 个）。

工具清单：query_travel / update_travel / add_itinerary_stop /
         delete_itinerary_stop / update_itinerary_stop / update_packing
"""
from __future__ import annotations

from modules.mock_data import get_travel_plan
from modules.persistence import (
    update_travel as persist_update_travel,
    add_itinerary_item as persist_add_itinerary,
    delete_itinerary_item as persist_delete_itinerary,
    update_itinerary_item as persist_update_itinerary,
    delete_travel_plan as persist_delete_travel,
    reset_travel_itinerary as persist_reset_itinerary,
    update_packing as persist_update_packing,
    get_deleted_itinerary_idxs, get_extra_itinerary,
    load_user_data, save_user_data,
)

from agent.tools._validators import validate_cost_non_negative


SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "query_travel",
            "description": "查询旅行计划，包括行程、预算和必带清单。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_travel",
            "description": "修改或创建旅行计划。修改时用于更新名称、日期、预算等；创建时设 create=true 会清空旧行程，之后用 add_itinerary_stop 添加新行程。用户说'改旅行日期'、'创建一个旅行计划'、'删除旅行计划'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "trip_name": {"type": "string", "description": "旅行名称"},
                    "date": {"type": "string", "description": "旅行日期，格式 YYYY-MM-DD"},
                    "budget": {"type": "number", "description": "旅行预算（元）"},
                    "status": {
                        "type": "string",
                        "description": "旅行状态",
                        "enum": ["计划中", "已确认", "进行中", "已完成", "已取消"],
                    },
                    "companions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "同行人列表",
                    },
                    "packing_list": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "必带清单物品列表",
                    },
                    "create": {
                        "type": "boolean",
                        "description": "设为 true 表示创建全新旅行计划（会清空旧行程），之后用 add_itinerary_stop 添加新行程站点",
                    },
                    "delete": {"type": "boolean", "description": "设为 true 删除整个旅行计划"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_itinerary_stop",
            "description": "给旅行计划新增一个行程站点。用户说'加一个景点'、'行程加个午餐'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "time": {"type": "string", "description": "时间，如 '14:00' 或 '14:00-16:00'"},
                    "activity": {"type": "string", "description": "活动内容，如 '参观博物馆'"},
                    "location": {"type": "string", "description": "地点"},
                    "cost": {"type": "number", "description": "预估花费（元），默认 0"},
                    "icon": {"type": "string", "description": "图标 emoji，默认 📍"},
                },
                "required": ["time", "activity", "location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_itinerary_stop",
            "description": "删除旅行计划中的一个行程站点。用户说'去掉骑行那一站'、'删掉第3个行程'时调用。支持按序号或活动名称匹配。",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer", "description": "站点序号（从 1 开始，用户视角）"},
                    "activity_name": {"type": "string", "description": "活动名称（模糊匹配）"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_itinerary_stop",
            "description": "修改旅行计划中一个行程站点的信息。用户说'午餐改到12:30'、'骑行费用改成40'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer", "description": "站点序号（从 1 开始，用户视角）"},
                    "activity_name": {"type": "string", "description": "活动名称（模糊匹配，当不知道序号时使用）"},
                    "time": {"type": "string", "description": "新的时间"},
                    "activity": {"type": "string", "description": "新的活动内容"},
                    "location": {"type": "string", "description": "新的地点"},
                    "cost": {"type": "number", "description": "新的预估花费（元）"},
                    "icon": {"type": "string", "description": "新的图标 emoji"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_packing",
            "description": "更新旅行必带清单的勾选状态。用户说'充电宝准备好了'、'帮我勾掉防晒霜'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string",
                        "description": "清单物品名称，如 '充电宝'、'防晒霜'、'学生证（门票优惠）'、'水杯'、'零食'",
                    },
                    "checked": {
                        "type": "boolean",
                        "description": "是否已准备好（true=已勾选，false=取消勾选）",
                    },
                },
                "required": ["item", "checked"],
            },
        },
    },
]

DISPLAY_NAMES: dict[str, str] = {
    "query_travel": "查询旅行计划",
    "update_travel": "修改旅行计划",
    "add_itinerary_stop": "新增行程站点",
    "delete_itinerary_stop": "删除行程站点",
    "update_itinerary_stop": "修改行程站点",
    "update_packing": "更新旅行清单",
}


# ---------------------------------------------------------------------------
# Helpers: itinerary 索引映射
# ---------------------------------------------------------------------------

_MOCK_ITINERARY_COUNT = 8  # 与 persistence.reset_travel_itinerary() 严格一致


def _find_itinerary_stop(travel: dict | None, index: int | None, activity_name: str | None):
    """在当前行程中定位站点。返回 (display_idx, stop_dict) 或 (None, error_str)。"""
    if travel is None:
        return None, "当前没有旅行计划。"
    itinerary = travel.get("itinerary", [])
    if not itinerary:
        return None, "当前行程为空。"

    if index is not None:
        idx = index - 1  # 用户视角 1-based
        if idx < 0 or idx >= len(itinerary):
            return None, f"序号 {index} 超出范围，当前行程共 {len(itinerary)} 站。"
        return idx, itinerary[idx]

    if activity_name:
        for i, stop in enumerate(itinerary):
            if stop["activity"] == activity_name:
                return i, stop
        matches = [(i, s) for i, s in enumerate(itinerary) if activity_name in s["activity"]]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            names = "、".join(f"[{i+1}]{s['activity']}" for i, s in matches)
            return None, f"匹配到多个站点：{names}，请指定序号。"
        return None, f"未找到包含「{activity_name}」的行程站点。"

    return None, "请提供站点序号或活动名称。"


def _resolve_real_index(display_idx: int) -> tuple[int, bool]:
    """把「显示行程」索引映射为「原始 mock 索引 或 extra 索引」。
    返回 (real_idx, is_extra)。
    """
    deleted_idxs = get_deleted_itinerary_idxs()
    surviving_mock = [i for i in range(_MOCK_ITINERARY_COUNT) if i not in deleted_idxs]
    if display_idx < len(surviving_mock):
        return surviving_mock[display_idx], False
    return display_idx - len(surviving_mock), True


def _delete_extra_itinerary(real_idx: int) -> None:
    data = load_user_data()
    extra = data.get("extra_itinerary", [])
    if 0 <= real_idx < len(extra):
        extra.pop(real_idx)
        save_user_data(data)


def _update_extra_itinerary(real_idx: int, fields: dict) -> None:
    data = load_user_data()
    extra = data.get("extra_itinerary", [])
    if 0 <= real_idx < len(extra):
        for k, v in fields.items():
            extra[real_idx][k] = v
        save_user_data(data)


# ---------------------------------------------------------------------------
# Executors
# ---------------------------------------------------------------------------

def _exec_query_travel(args: dict) -> str:
    travel = get_travel_plan()
    if travel is None:
        return "当前没有旅行计划。"
    lines = [
        f"旅行计划：{travel['trip_name']}",
        f"- 日期: {travel['date']}",
        f"- 预算: ¥{travel['budget']:.0f}",
        f"- 预估花费: ¥{travel['total_estimated_cost']:.0f}",
        f"- 同行: {'、'.join(travel['companions'])}",
        "",
        "行程安排：",
    ]
    for stop in travel["itinerary"]:
        cost = f"¥{stop['cost']:.0f}" if stop["cost"] > 0 else "免费"
        lines.append(f"- {stop['time']} {stop['activity']}（{stop['location']}，{cost}）")
    lines.append("")
    lines.append("必带清单：" + "、".join(travel["packing_list"]))
    return "\n".join(lines)


def _exec_update_travel(args: dict) -> str:
    if args.get("delete"):
        persist_delete_travel()
        return "已删除旅行计划。"

    is_create = args.get("create", False)
    fields = {}
    for key in ("trip_name", "date", "budget", "status", "companions", "packing_list"):
        if key in args and args[key] is not None:
            fields[key] = args[key]

    if not fields and not is_create:
        return "没有提供需要修改的字段。请指定要修改的内容（如名称、日期、预算等）。"

    if "budget" in fields:
        b = fields["budget"]
        if not isinstance(b, (int, float)) or b <= 0:
            return "旅行预算须大于 0。"

    persist_update_travel(deleted=False, **fields)

    if is_create:
        persist_reset_itinerary()

    field_names = {"trip_name": "名称", "date": "日期", "budget": "预算",
                   "status": "状态", "companions": "同行人", "packing_list": "必带清单"}
    if is_create:
        changes = "、".join(f"{field_names.get(k, k)}: {v}" for k, v in fields.items())
        return f"已创建新旅行计划：{changes}\n可以继续用 add_itinerary_stop 添加行程站点。"
    changes = "、".join(f"{field_names.get(k, k)}→{v}" for k, v in fields.items())
    return f"已修改旅行计划：{changes}"


def _exec_add_itinerary_stop(args: dict) -> str:
    if get_travel_plan() is None:
        return "当前没有旅行计划，请先用 update_travel(create=true) 创建一个旅行计划。"

    cost = args.get("cost", 0)
    if (err := validate_cost_non_negative(cost)):
        return err

    item = persist_add_itinerary(
        args["time"], args["activity"], args["location"],
        float(cost), args.get("icon", "📍"),
    )
    cost_str = f"¥{item['cost']:.0f}" if item["cost"] > 0 else "免费"
    return (
        f"已新增行程站点：\n"
        f"- 时间: {item['time']}\n"
        f"- 活动: {item['activity']}\n"
        f"- 地点: {item['location']}\n"
        f"- 花费: {cost_str}"
    )


def _exec_delete_itinerary_stop(args: dict) -> str:
    index = args.get("index")
    activity_name = args.get("activity_name")
    if not index and not activity_name:
        return "请提供站点序号或活动名称。"

    travel = get_travel_plan()
    display_idx, stop = _find_itinerary_stop(travel, index, activity_name)
    if display_idx is None:
        return stop  # error message

    real_idx, is_extra = _resolve_real_index(display_idx)
    activity = stop["activity"]

    if is_extra:
        _delete_extra_itinerary(real_idx)
    else:
        persist_delete_itinerary(real_idx)
    return f"已删除行程站点「{activity}」。"


def _exec_update_itinerary_stop(args: dict) -> str:
    index = args.get("index")
    activity_name = args.get("activity_name")
    if not index and not activity_name:
        return "请提供站点序号或活动名称来定位要修改的站点。"

    travel = get_travel_plan()
    display_idx, stop = _find_itinerary_stop(travel, index, activity_name)
    if display_idx is None:
        return stop

    fields = {}
    for key in ("time", "activity", "location", "cost", "icon"):
        if key in args and args[key] is not None:
            fields[key] = args[key]
    if not fields:
        return "没有提供需要修改的字段。请指定要修改的内容（如时间、活动、地点、花费等）。"

    if "cost" in fields and (err := validate_cost_non_negative(fields["cost"])):
        return err

    real_idx, is_extra = _resolve_real_index(display_idx)
    original_activity = stop["activity"]

    if is_extra:
        _update_extra_itinerary(real_idx, fields)
    else:
        persist_update_itinerary(real_idx, **fields)

    field_names = {"time": "时间", "activity": "活动", "location": "地点",
                   "cost": "花费", "icon": "图标"}
    changes = "、".join(f"{field_names.get(k, k)}→{v}" for k, v in fields.items())
    return f"已修改行程站点「{original_activity}」：{changes}"


def _exec_update_packing(args: dict) -> str:
    item = args["item"]
    checked = args["checked"]
    persist_update_packing(item, checked)
    if checked:
        return f"已勾选旅行清单物品「{item}」，准备好了！"
    return f"已取消勾选旅行清单物品「{item}」。"


def register(schemas: list, display_names: dict, registry: dict) -> None:
    schemas.extend(SCHEMAS)
    display_names.update(DISPLAY_NAMES)
    registry.update({
        "query_travel": _exec_query_travel,
        "update_travel": _exec_update_travel,
        "add_itinerary_stop": _exec_add_itinerary_stop,
        "delete_itinerary_stop": _exec_delete_itinerary_stop,
        "update_itinerary_stop": _exec_update_itinerary_stop,
        "update_packing": _exec_update_packing,
    })

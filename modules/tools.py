"""
UniLife OS — Agent 工具定义
提供 OpenAI function calling 格式的工具 Schema 和执行路由。
"""
import json
from modules.mock_data import (
    get_schedule, get_today_schedule, get_finance, get_health,
    get_todos, get_upcoming_exams, get_travel_plan,
)
from modules.persistence import add_expense, update_todo_status

# ========== 工具 Schema（OpenAI function calling 格式）==========

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "query_schedule",
            "description": "查询课表。可以指定星期几查询，也可以不指定查询整周课表。",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {
                        "type": "string",
                        "description": "星期几，如 '周一'、'周二'。不传则查询整周。",
                        "enum": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_finance",
            "description": "查询本月财务状况，包括预算、消费、各类别占比和最近消费记录。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "可选，筛选特定消费类别，如 '餐饮'、'交通'、'购物'、'学习用品'、'娱乐'、'其他'。",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_expense",
            "description": "记录一笔新的消费。用户告诉你花了什么、多少钱时调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string",
                        "description": "消费项目名称，如 '奶茶'、'教材'",
                    },
                    "amount": {
                        "type": "number",
                        "description": "消费金额（元）",
                    },
                    "category": {
                        "type": "string",
                        "description": "消费类别",
                        "enum": ["餐饮", "交通", "购物", "学习用品", "娱乐", "其他"],
                    },
                },
                "required": ["item", "amount", "category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_health",
            "description": "查询今日健康数据，包括步数、睡眠、喝水、运动、心情等。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_todos",
            "description": "查询待办事项列表。可以筛选全部、未完成或已完成。",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "筛选状态：all=全部，pending=未完成，done=已完成",
                        "enum": ["all", "pending", "done"],
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_todo",
            "description": "切换一个待办事项的完成状态（完成↔未完成）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "待办事项的 ID",
                    }
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_exams",
            "description": "查询近期考试安排和倒计时。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_travel",
            "description": "查询旅行计划，包括行程、预算和必带清单。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# 工具名到中文描述的映射（用于 UI 展示）
TOOL_DISPLAY_NAMES = {
    "query_schedule": "查询课表",
    "query_finance": "查询财务数据",
    "record_expense": "记录消费",
    "query_health": "查询健康数据",
    "query_todos": "查询待办事项",
    "toggle_todo": "更新待办状态",
    "query_exams": "查询考试安排",
    "query_travel": "查询旅行计划",
}


# ========== 工具执行路由 ==========

def execute_tool(name: str, args: dict) -> str:
    """
    执行指定工具，返回结果字符串。
    args 已经是 dict（由 JSON 解析后传入）。
    """
    try:
        if name == "query_schedule":
            return _exec_query_schedule(args)
        elif name == "query_finance":
            return _exec_query_finance(args)
        elif name == "record_expense":
            return _exec_record_expense(args)
        elif name == "query_health":
            return _exec_query_health(args)
        elif name == "query_todos":
            return _exec_query_todos(args)
        elif name == "toggle_todo":
            return _exec_toggle_todo(args)
        elif name == "query_exams":
            return _exec_query_exams(args)
        elif name == "query_travel":
            return _exec_query_travel(args)
        else:
            return f"未知工具: {name}"
    except Exception as e:
        return f"工具执行出错: {str(e)}"


# ========== 各工具的具体执行逻辑 ==========

def _exec_query_schedule(args: dict) -> str:
    day = args.get("day")
    if day:
        courses = [c for c in get_schedule() if c["weekday"] == day]
        if not courses:
            return f"{day}没有课，可以自由安排！"
        lines = [f"{day}的课程安排："]
        for c in courses:
            lines.append(f"- {c['time']} {c['course']}（{c['location']}，{c['teacher']}，{c['type']}）")
        return "\n".join(lines)
    else:
        # 默认返回今日课表
        today = get_today_schedule()
        if not today:
            from datetime import datetime
            wd_map = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
            wd = wd_map[datetime.now().weekday()]
            return f"今天（{wd}）没有课，可以自由安排！"
        lines = ["今日课程安排："]
        for c in today:
            lines.append(f"- {c['time']} {c['course']}（{c['location']}，{c['teacher']}）")
        return "\n".join(lines)


def _exec_query_finance(args: dict) -> str:
    finance = get_finance()
    category = args.get("category")

    if category:
        amount = finance["categories"].get(category, 0)
        txns = [t for t in finance["recent_transactions"] if t["category"] == category]
        lines = [f"【{category}】消费情况："]
        lines.append(f"本月 {category} 总计: ¥{amount:.0f}")
        if txns:
            lines.append("相关消费记录：")
            for t in txns[:8]:
                lines.append(f"- {t['date']} {t['item']} ¥{t['amount']:.1f}")
        return "\n".join(lines)

    lines = [
        "本月财务概况：",
        f"- 预算: ¥{finance['monthly_budget']:.0f}",
        f"- 已花费: ¥{finance['spent']:.0f}（{finance['budget_usage_pct']}%）",
        f"- 剩余: ¥{finance['remaining']:.0f}",
        f"- 日均消费: ¥{finance['daily_avg_spent']:.1f}",
        f"- 剩余天数: {finance['days_left_in_month']} 天",
        f"- 建议日限: ¥{finance['suggested_daily']:.1f}",
        "",
        "各类别消费：",
    ]
    for cat, amount in finance["categories"].items():
        lines.append(f"- {cat}: ¥{amount:.0f}")

    lines.append("")
    lines.append("最近消费记录：")
    for t in finance["recent_transactions"][:10]:
        lines.append(f"- {t['date']} {t['item']} ¥{t['amount']:.1f}（{t['category']}）")

    return "\n".join(lines)


def _exec_record_expense(args: dict) -> str:
    item = args["item"]
    amount = args["amount"]
    category = args["category"]
    record = add_expense(item, amount, category)
    return f"已记录消费：{item} ¥{amount:.1f}（{category}），记录日期 {record['date']}。"


def _exec_query_health(args: dict) -> str:
    health = get_health()
    from datetime import datetime
    days_since = (datetime.now() - datetime.strptime(health["last_exercise"], "%Y-%m-%d")).days
    lines = [
        "今日健康数据：",
        f"- 步数: {health['today_steps']:,}/{health['step_goal']:,}",
        f"- 睡眠: {health['sleep_hours']}h（{health['sleep_quality']}）",
        f"- 喝水: {health['water_cups']}/{health['water_goal']} 杯",
        f"- 本周运动: {health['exercise_this_week']}/{health['exercise_goal']} 次",
        f"- 距上次运动: {days_since} 天",
        f"- 心情: {health['mood']}",
        f"- 连续打卡: {health['checkin_streak']} 天",
        f"- BMI: {health['bmi']} | 体重: {health['weight']}kg",
    ]
    return "\n".join(lines)


def _exec_query_todos(args: dict) -> str:
    todos = get_todos()
    status = args.get("status", "all")

    if status == "pending":
        todos = [t for t in todos if not t["done"]]
        title = "未完成的待办事项："
    elif status == "done":
        todos = [t for t in todos if t["done"]]
        title = "已完成的待办事项："
    else:
        title = "全部待办事项："

    if not todos:
        return "没有符合条件的待办事项。"

    lines = [title]
    for t in todos:
        status_mark = "✅" if t["done"] else "⬜"
        lines.append(f"- {status_mark} [{t['id']}] {t['priority']} {t['task']}（截止 {t['deadline']}）")
    return "\n".join(lines)


def _exec_toggle_todo(args: dict) -> str:
    task_id = args["task_id"]
    todos = get_todos()
    target = None
    for t in todos:
        if t["id"] == task_id:
            target = t
            break
    if not target:
        return f"未找到 ID 为 {task_id} 的待办事项。"

    new_status = not target["done"]
    update_todo_status(task_id, new_status)
    status_text = "已完成" if new_status else "未完成"
    return f"待办「{target['task']}」已标记为{status_text}。"


def _exec_query_exams(args: dict) -> str:
    exams = get_upcoming_exams()
    if not exams:
        return "近期没有考试安排。"
    lines = ["近期考试安排："]
    for e in exams:
        urgency = "🔴 紧急！" if e["days_left"] <= 3 else ("🟡 注意" if e["days_left"] <= 7 else "🔵")
        lines.append(
            f"- {urgency} {e['course']}（{e['type']}）"
            f"：{e['date']}，还有 {e['days_left']} 天"
            f"，地点：{e['location']}"
        )
    return "\n".join(lines)


def _exec_query_travel(args: dict) -> str:
    travel = get_travel_plan()
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

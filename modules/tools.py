"""
UniLife OS — Agent 工具定义
提供 OpenAI function calling 格式的工具 Schema 和执行路由。
"""
from __future__ import annotations

import json
from datetime import datetime
from modules.mock_data import (
    get_schedule, get_today_schedule, get_finance, get_health,
    get_todos, get_upcoming_exams, get_travel_plan,
)
from modules.persistence import (
    add_expense, update_todo_status,
    add_todo, increment_water, log_exercise, log_mood, update_packing,
    log_steps, log_sleep,
    add_course as persist_add_course,
    delete_course as persist_delete_course,
    update_course as persist_update_course,
    set_budget as persist_set_budget,
    set_exercise_goal as persist_set_exercise_goal,
    update_travel as persist_update_travel,
    add_itinerary_item as persist_add_itinerary,
    delete_itinerary_item as persist_delete_itinerary,
    update_itinerary_item as persist_update_itinerary,
    delete_travel_plan as persist_delete_travel,
    reset_travel_itinerary as persist_reset_itinerary,
)

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
    {
        "type": "function",
        "function": {
            "name": "record_water",
            "description": "记录喝水，每次调用喝水杯数 +1。用户说'喝了一杯水'、'记一下喝水'时调用。",
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
            "name": "record_exercise",
            "description": "记录运动打卡。用户说'我运动了'、'刚跑完步'时调用。",
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
            "name": "record_mood",
            "description": "记录用户心情。用户表达情绪如'我今天很开心'、'有点烦'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "mood": {
                        "type": "string",
                        "description": "用户的心情描述，如 '😊 开心'、'😐 一般'、'😢 难过'",
                    }
                },
                "required": ["mood"],
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
    {
        "type": "function",
        "function": {
            "name": "add_todo",
            "description": "新增一个待办事项。用户说'帮我添加一个待办'、'记一下要做的事'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "待办事项内容",
                    },
                    "deadline": {
                        "type": "string",
                        "description": "截止日期，格式 YYYY-MM-DD",
                    },
                    "priority": {
                        "type": "string",
                        "description": "优先级",
                        "enum": ["🔴 紧急", "🟡 重要", "🟢 普通"],
                    },
                    "category": {
                        "type": "string",
                        "description": "分类",
                        "enum": ["学业", "生活", "社交"],
                    },
                },
                "required": ["task", "deadline"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_steps",
            "description": "记录今日步数。用户说'今天走了8000步'、'步数6000'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "integer",
                        "description": "今日步数",
                    }
                },
                "required": ["steps"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_sleep",
            "description": "记录昨晚睡眠情况。用户说'昨晚睡了7小时'、'睡眠8小时质量不错'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "number",
                        "description": "睡眠时长（小时），如 7.5",
                    },
                    "quality": {
                        "type": "string",
                        "description": "睡眠质量",
                        "enum": ["很好", "良好", "一般", "较差", "很差"],
                    },
                },
                "required": ["hours"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_course",
            "description": "添加一门新课程到课表。用户说'帮我加一门课'、'周三下午有个选修课'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "weekday": {
                        "type": "string",
                        "description": "星期几",
                        "enum": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                    },
                    "time": {
                        "type": "string",
                        "description": "上课时间，如 '14:00-15:35'",
                    },
                    "course": {
                        "type": "string",
                        "description": "课程名称",
                    },
                    "location": {
                        "type": "string",
                        "description": "上课地点",
                    },
                    "teacher": {
                        "type": "string",
                        "description": "任课教师（可选）",
                    },
                    "type": {
                        "type": "string",
                        "description": "课程类型，默认'选修'",
                        "enum": ["必修", "选修", "实验"],
                    },
                },
                "required": ["weekday", "time", "course", "location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_course",
            "description": "从课表删除一门课程。用户说'帮我删掉体育课'、'这门课不上了'时调用。支持按课程 ID 或名称删除。",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_id": {
                        "type": "integer",
                        "description": "课程 ID（可选，优先使用）",
                    },
                    "course_name": {
                        "type": "string",
                        "description": "课程名称（可选，当不知道 ID 时使用，模糊匹配）",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_course",
            "description": "修改课表中一门课程的信息。用户说'线性代数换教室了'、'高数改到周二'时调用。支持按课程 ID 或名称定位。",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_id": {
                        "type": "integer",
                        "description": "课程 ID（可选，优先使用）",
                    },
                    "course_name": {
                        "type": "string",
                        "description": "课程名称（可选，当不知道 ID 时使用）",
                    },
                    "course": {
                        "type": "string",
                        "description": "新的课程名称（重命名时使用）",
                    },
                    "weekday": {
                        "type": "string",
                        "description": "新的星期几",
                        "enum": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                    },
                    "time": {
                        "type": "string",
                        "description": "新的上课时间",
                    },
                    "location": {
                        "type": "string",
                        "description": "新的上课地点",
                    },
                    "teacher": {
                        "type": "string",
                        "description": "新的任课教师",
                    },
                    "type": {
                        "type": "string",
                        "description": "新的课程类型",
                        "enum": ["必修", "选修", "实验"],
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_budget",
            "description": "设置本月预算金额。用户说'把预算改成3000'、'这个月预算2500'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "预算金额（元）",
                    },
                },
                "required": ["amount"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_exercise_goal",
            "description": "设置每周运动打卡目标次数。用户说'运动目标改成5次'、'每周锻炼4次'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {
                        "type": "integer",
                        "description": "每周运动目标次数（3-7）",
                        "enum": [3, 4, 5, 6, 7],
                    },
                },
                "required": ["goal"],
            },
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
                    "trip_name": {
                        "type": "string",
                        "description": "旅行名称",
                    },
                    "date": {
                        "type": "string",
                        "description": "旅行日期，格式 YYYY-MM-DD",
                    },
                    "budget": {
                        "type": "number",
                        "description": "旅行预算（元）",
                    },
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
                    "delete": {
                        "type": "boolean",
                        "description": "设为 true 删除整个旅行计划",
                    },
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
                    "time": {
                        "type": "string",
                        "description": "时间，如 '14:00' 或 '14:00-16:00'",
                    },
                    "activity": {
                        "type": "string",
                        "description": "活动内容，如 '参观博物馆'",
                    },
                    "location": {
                        "type": "string",
                        "description": "地点",
                    },
                    "cost": {
                        "type": "number",
                        "description": "预估花费（元），默认 0",
                    },
                    "icon": {
                        "type": "string",
                        "description": "图标 emoji，默认 📍",
                    },
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
                    "index": {
                        "type": "integer",
                        "description": "站点序号（从 1 开始，用户视角）",
                    },
                    "activity_name": {
                        "type": "string",
                        "description": "活动名称（模糊匹配）",
                    },
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
                    "index": {
                        "type": "integer",
                        "description": "站点序号（从 1 开始，用户视角）",
                    },
                    "activity_name": {
                        "type": "string",
                        "description": "活动名称（模糊匹配，当不知道序号时使用）",
                    },
                    "time": {
                        "type": "string",
                        "description": "新的时间",
                    },
                    "activity": {
                        "type": "string",
                        "description": "新的活动内容",
                    },
                    "location": {
                        "type": "string",
                        "description": "新的地点",
                    },
                    "cost": {
                        "type": "number",
                        "description": "新的预估花费（元）",
                    },
                    "icon": {
                        "type": "string",
                        "description": "新的图标 emoji",
                    },
                },
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
    "record_water": "记录喝水",
    "record_exercise": "运动打卡",
    "record_mood": "记录心情",
    "update_packing": "更新旅行清单",
    "add_todo": "新增待办事项",
    "record_steps": "记录步数",
    "record_sleep": "记录睡眠",
    "add_course": "添加课程",
    "delete_course": "删除课程",
    "update_course": "修改课程",
    "set_budget": "设置预算",
    "set_exercise_goal": "设置运动目标",
    "update_travel": "修改旅行计划",
    "add_itinerary_stop": "新增行程站点",
    "delete_itinerary_stop": "删除行程站点",
    "update_itinerary_stop": "修改行程站点",
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
        elif name == "record_water":
            return _exec_record_water(args)
        elif name == "record_exercise":
            return _exec_record_exercise(args)
        elif name == "record_mood":
            return _exec_record_mood(args)
        elif name == "update_packing":
            return _exec_update_packing(args)
        elif name == "add_todo":
            return _exec_add_todo(args)
        elif name == "record_steps":
            return _exec_record_steps(args)
        elif name == "record_sleep":
            return _exec_record_sleep(args)
        elif name == "add_course":
            return _exec_add_course(args)
        elif name == "delete_course":
            return _exec_delete_course(args)
        elif name == "update_course":
            return _exec_update_course(args)
        elif name == "set_budget":
            return _exec_set_budget(args)
        elif name == "set_exercise_goal":
            return _exec_set_exercise_goal(args)
        elif name == "update_travel":
            return _exec_update_travel(args)
        elif name == "add_itinerary_stop":
            return _exec_add_itinerary_stop(args)
        elif name == "delete_itinerary_stop":
            return _exec_delete_itinerary_stop(args)
        elif name == "update_itinerary_stop":
            return _exec_update_itinerary_stop(args)
        else:
            return f"未知工具: {name}"
    except Exception as e:
        return f"工具执行出错: {str(e)}"


# ========== 各工具的具体执行逻辑 ==========

def _format_course_line(c: dict) -> str:
    """格式化单条课程信息，跳过空字段。"""
    parts = [c["location"]]
    if c.get("teacher"):
        parts.append(c["teacher"])
    parts.append(c["type"])
    return f"- {c['time']} {c['course']}（{'，'.join(parts)}）"


def _exec_query_schedule(args: dict) -> str:
    day = args.get("day")
    if day:
        courses = [c for c in get_schedule() if c["weekday"] == day]
        if not courses:
            return f"{day}没有课，可以自由安排！"
        lines = [f"{day}的课程安排："]
        for c in courses:
            lines.append(_format_course_line(c))
        return "\n".join(lines)
    else:
        # 不指定星期 → 返回整周课表
        schedule = get_schedule()
        if not schedule:
            return "课表为空，还没有任何课程。"
        weekday_order = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        grouped = {}
        for c in schedule:
            grouped.setdefault(c["weekday"], []).append(c)
        lines = ["本周课表："]
        for wd in weekday_order:
            if wd in grouped:
                lines.append(f"\n📅 {wd}：")
                for c in grouped[wd]:
                    lines.append(_format_course_line(c))
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
    if not item or not item.strip():
        return "消费项目不能为空。"
    if amount <= 0 or amount > 100000:
        return "金额须在 0～100,000 元之间。"
    record = add_expense(item.strip(), amount, category)
    return f"已记录消费：{item} ¥{amount:.1f}（{category}），记录日期 {record['date']}。"


def _exec_query_health(args: dict) -> str:
    health = get_health()
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
    task_id = int(args["task_id"])  # 兼容 LLM 传入 str 的情况
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
        if e["days_left"] == 0:
            urgency = "🔴 今天考试！"
            countdown = "就在今天"
        elif e["days_left"] <= 3:
            urgency = "🔴 紧急！"
            countdown = f"还有 {e['days_left']} 天"
        elif e["days_left"] <= 7:
            urgency = "🟡 注意"
            countdown = f"还有 {e['days_left']} 天"
        else:
            urgency = "🔵"
            countdown = f"还有 {e['days_left']} 天"
        lines.append(
            f"- {urgency} {e['course']}（{e['type']}）"
            f"：{e['date']}，{countdown}"
            f"，地点：{e['location']}"
        )
    return "\n".join(lines)


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


def _exec_record_water(args: dict) -> str:
    increment_water()
    health = get_health()
    return f"已记录喝水！今天累计喝了 {health['water_cups']} 杯水。"


def _exec_record_exercise(args: dict) -> str:
    is_new = log_exercise()
    if is_new:
        return "运动打卡成功！今天的运动已记录。"
    return "今天已经打过卡了，不用重复打卡哦~"


def _exec_record_mood(args: dict) -> str:
    mood = args["mood"]
    log_mood(mood)
    return f"已记录心情：{mood}"


def _exec_update_packing(args: dict) -> str:
    item = args["item"]
    checked = args["checked"]
    update_packing(item, checked)
    if checked:
        return f"已勾选旅行清单物品「{item}」，准备好了！"
    else:
        return f"已取消勾选旅行清单物品「{item}」。"


def _exec_add_todo(args: dict) -> str:
    task = args["task"]
    deadline = args["deadline"]
    priority = args.get("priority", "🟢 普通")
    category = args.get("category", "生活")
    todo = add_todo(task, deadline, priority, category)
    return (
        f"已新增待办事项：\n"
        f"- ID: {todo['id']}\n"
        f"- 任务: {todo['task']}\n"
        f"- 截止: {todo['deadline']}\n"
        f"- 优先级: {todo['priority']}\n"
        f"- 分类: {todo['category']}"
    )


def _exec_record_steps(args: dict) -> str:
    steps = args["steps"]
    if not isinstance(steps, (int, float)) or steps < 0 or steps > 200000:
        return "步数须在 0～200,000 之间。"
    steps = int(steps)
    log_steps(steps)
    return f"已记录今日步数：{steps:,} 步。"


def _exec_record_sleep(args: dict) -> str:
    hours = args["hours"]
    if not isinstance(hours, (int, float)) or hours < 0 or hours > 24:
        return "睡眠时长须在 0～24 小时之间。"
    quality = args.get("quality", "一般")
    log_sleep(hours, quality)
    return f"已记录睡眠：{hours} 小时，质量「{quality}」。"


def _find_course_by_name(name: str) -> dict | str | None:
    """
    在当前课表中按名称匹配课程。
    返回: dict（唯一匹配）/ str（多个匹配时返回错误提示）/ None（无匹配）
    """
    schedule = get_schedule()
    # 精确匹配
    for c in schedule:
        if c["course"] == name:
            return c
    # 模糊匹配（搜索词是课程名的子串）
    matches = [c for c in schedule if name in c["course"]]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        names = "、".join(f"[{c['id']}]{c['course']}" for c in matches)
        return f"匹配到多门课程：{names}，请指定课程 ID 或更精确的名称。"
    return None


def _exec_add_course(args: dict) -> str:
    weekday = args["weekday"]
    time = args["time"]
    course = args["course"]
    location = args["location"]
    teacher = args.get("teacher", "")
    course_type = args.get("type", "选修")
    record = persist_add_course(weekday, time, course, location, teacher, course_type)
    return (
        f"已添加课程：\n"
        f"- ID: {record['id']}\n"
        f"- {record['weekday']} {record['time']} {record['course']}\n"
        f"- 地点: {record['location']}\n"
        f"- 教师: {record['teacher'] or '未指定'}\n"
        f"- 类型: {record['type']}"
    )


def _exec_delete_course(args: dict) -> str:
    course_id = args.get("course_id")
    course_name = args.get("course_name")

    if not course_id and not course_name:
        return "请提供课程 ID 或课程名称。"

    # 按名称查找 → 得到 course_id
    if not course_id and course_name:
        found = _find_course_by_name(course_name)
        if isinstance(found, str):
            return found  # 多个匹配的提示
        if not found:
            return f"未找到名为「{course_name}」的课程。"
        course_id = found["id"]

    # 统一 int 转换 + 按 ID 验证存在 + 获取规范名称
    course_id = int(course_id)
    schedule = get_schedule()
    target = None
    for c in schedule:
        if c["id"] == course_id:
            target = c
            break
    if not target:
        return f"未找到 ID 为 {course_id} 的课程。"

    persist_delete_course(course_id)
    return f"已删除课程「{target['course']}」(ID={course_id})。"


def _exec_update_course(args: dict) -> str:
    course_id = args.get("course_id")
    course_name = args.get("course_name")

    if not course_id and not course_name:
        # Fallback: LLM 可能把 "course" 当作标识符而非修改字段
        if "course" in args:
            found = _find_course_by_name(args["course"])
            if isinstance(found, str):
                return found
            if found:
                course_id = found["id"]
            else:
                return f"未找到名为「{args['course']}」的课程。"
        else:
            return "请提供课程 ID 或课程名称来定位要修改的课程。"

    # 按名称查找 → 得到 course_id
    if not course_id and course_name:
        found = _find_course_by_name(course_name)
        if isinstance(found, str):
            return found  # 多个匹配的提示
        if not found:
            return f"未找到名为「{course_name}」的课程。"
        course_id = found["id"]

    # 统一 int 转换 + 按 ID 验证存在 + 获取规范名称
    course_id = int(course_id)
    schedule = get_schedule()
    target = None
    for c in schedule:
        if c["id"] == course_id:
            target = c
            break
    if not target:
        return f"未找到 ID 为 {course_id} 的课程。"
    verified_name = target["course"]

    # 收集要修改的字段（含 course 名称）
    fields = {}
    for key in ("weekday", "time", "course", "location", "teacher", "type"):
        if key in args and key not in ("course_id", "course_name") and args[key] is not None:
            fields[key] = args[key]

    if not fields:
        return "没有提供需要修改的字段。请指定要修改的内容（如时间、地点、教师等）。"

    persist_update_course(course_id, **fields)
    field_names = {"weekday": "星期", "time": "时间", "course": "课程名",
                   "location": "地点", "teacher": "教师", "type": "类型"}
    changes = "、".join(f"{field_names.get(k, k)}→{v}" for k, v in fields.items())
    return f"已修改课程「{verified_name}」：{changes}"


def _exec_set_budget(args: dict) -> str:
    amount = args["amount"]
    if not isinstance(amount, (int, float)) or amount <= 0 or amount > 100000:
        return "预算金额须在 0～100,000 元之间。"
    persist_set_budget(float(amount))
    return f"已将本月预算设置为 ¥{amount:.0f}。"


def _exec_set_exercise_goal(args: dict) -> str:
    goal = args["goal"]
    if goal not in (3, 4, 5, 6, 7):
        return "运动目标须在 3～7 次之间。"
    persist_set_exercise_goal(goal)
    return f"已将每周运动目标设置为 {goal} 次。"


def _exec_update_travel(args: dict) -> str:
    # 检查是否要删除
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

    # 清除 deleted 标记（允许重新创建已删除的计划）
    persist_update_travel(deleted=False, **fields)

    # 创建模式：清空旧行程数据，以便用 add_itinerary_stop 从头添加
    if is_create:
        persist_reset_itinerary()

    field_names = {"trip_name": "名称", "date": "日期", "budget": "预算",
                   "status": "状态", "companions": "同行人", "packing_list": "必带清单"}
    if is_create:
        changes = "、".join(f"{field_names.get(k, k)}: {v}" for k, v in fields.items())
        return f"已创建新旅行计划：{changes}\n可以继续用 add_itinerary_stop 添加行程站点。"
    else:
        changes = "、".join(f"{field_names.get(k, k)}→{v}" for k, v in fields.items())
        return f"已修改旅行计划：{changes}"


def _exec_add_itinerary_stop(args: dict) -> str:
    # 检查旅行计划是否存在
    travel = get_travel_plan()
    if travel is None:
        return "当前没有旅行计划，请先用 update_travel(create=true) 创建一个旅行计划。"

    time_str = args["time"]
    activity = args["activity"]
    location = args["location"]
    cost = args.get("cost", 0)
    icon = args.get("icon", "📍")
    if cost < 0:
        return "花费不能为负数。"
    item = persist_add_itinerary(time_str, activity, location, float(cost), icon)
    cost_str = f"¥{item['cost']:.0f}" if item["cost"] > 0 else "免费"
    return (
        f"已新增行程站点：\n"
        f"- 时间: {item['time']}\n"
        f"- 活动: {item['activity']}\n"
        f"- 地点: {item['location']}\n"
        f"- 花费: {cost_str}"
    )


def _find_itinerary_stop(travel: dict | None, index: int | None, activity_name: str | None):
    """
    在当前行程中定位站点。
    返回 (real_index, stop_dict) 或 (None, error_str)。
    real_index 是该站点在原始 mock 行程中的索引（用于持久化），对 extra 站点返回负数。
    """
    if travel is None:
        return None, "当前没有旅行计划。"

    itinerary = travel.get("itinerary", [])
    if not itinerary:
        return None, "当前行程为空。"

    if index is not None:
        # 用户视角从 1 开始
        idx = index - 1
        if idx < 0 or idx >= len(itinerary):
            return None, f"序号 {index} 超出范围，当前行程共 {len(itinerary)} 站。"
        return idx, itinerary[idx]

    if activity_name:
        # 精确匹配
        for i, stop in enumerate(itinerary):
            if stop["activity"] == activity_name:
                return i, stop
        # 模糊匹配
        matches = [(i, s) for i, s in enumerate(itinerary) if activity_name in s["activity"]]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            names = "、".join(f"[{i+1}]{s['activity']}" for i, s in matches)
            return None, f"匹配到多个站点：{names}，请指定序号。"
        return None, f"未找到包含「{activity_name}」的行程站点。"

    return None, "请提供站点序号或活动名称。"


def _resolve_itinerary_real_index(travel: dict, display_idx: int) -> tuple[int, bool]:
    """
    将显示行程中的索引转换为原始 mock 索引。
    返回 (real_idx, is_extra)。
    """
    from modules.persistence import get_deleted_itinerary_idxs, get_extra_itinerary
    deleted_idxs = get_deleted_itinerary_idxs()

    # 原始 mock 行程有 8 项，减去被删除的
    mock_count = 8  # mock 行程数
    surviving_mock = [(i, i) for i in range(mock_count) if i not in deleted_idxs]

    extra = get_extra_itinerary()
    total_mock_surviving = len(surviving_mock)

    if display_idx < total_mock_surviving:
        # 是 mock 站点
        return surviving_mock[display_idx][1], False
    else:
        # 是 extra 站点
        return display_idx - total_mock_surviving, True


def _exec_delete_itinerary_stop(args: dict) -> str:
    index = args.get("index")
    activity_name = args.get("activity_name")

    if not index and not activity_name:
        return "请提供站点序号或活动名称。"

    travel = get_travel_plan()
    display_idx, stop = _find_itinerary_stop(travel, index, activity_name)
    if display_idx is None:
        return stop  # error message

    real_idx, is_extra = _resolve_itinerary_real_index(travel, display_idx)
    activity = stop["activity"]

    if is_extra:
        # 直接从 extra_itinerary 中删除
        from modules.persistence import load_user_data, save_user_data
        data = load_user_data()
        extra = data.get("extra_itinerary", [])
        if 0 <= real_idx < len(extra):
            extra.pop(real_idx)
            save_user_data(data)
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
        return stop  # error message

    fields = {}
    for key in ("time", "activity", "location", "cost", "icon"):
        if key in args and args[key] is not None:
            fields[key] = args[key]

    if not fields:
        return "没有提供需要修改的字段。请指定要修改的内容（如时间、活动、地点、花费等）。"

    if "cost" in fields and (not isinstance(fields["cost"], (int, float)) or fields["cost"] < 0):
        return "花费不能为负数。"

    real_idx, is_extra = _resolve_itinerary_real_index(travel, display_idx)
    original_activity = stop["activity"]

    if is_extra:
        from modules.persistence import load_user_data, save_user_data
        data = load_user_data()
        extra = data.get("extra_itinerary", [])
        if 0 <= real_idx < len(extra):
            for k, v in fields.items():
                extra[real_idx][k] = v
            save_user_data(data)
    else:
        persist_update_itinerary(real_idx, **fields)

    field_names = {"time": "时间", "activity": "活动", "location": "地点",
                   "cost": "花费", "icon": "图标"}
    changes = "、".join(f"{field_names.get(k, k)}→{v}" for k, v in fields.items())
    return f"已修改行程站点「{original_activity}」：{changes}"

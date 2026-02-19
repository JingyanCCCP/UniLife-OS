"""
UniLife OS — Mock 数据中心
所有伪造数据集中管理，便于 Day 2 扩展和 Day 4 注入 Agent
"""
from datetime import datetime, timedelta

def get_schedule() -> list[dict]:
    """获取本周课表 Mock 数据"""
    return [
        {"weekday": "周一", "time": "08:30-10:05", "course": "高等数学 II",
         "location": "教学楼 A-301", "teacher": "王教授"},
        {"weekday": "周一", "time": "14:00-15:35", "course": "大学物理",
         "location": "实验楼 B-205", "teacher": "李教授"},
        {"weekday": "周二", "time": "10:15-11:50", "course": "Python 程序设计",
         "location": "计算机楼 C-102", "teacher": "张教授"},
        {"weekday": "周三", "time": "08:30-10:05", "course": "线性代数",
         "location": "教学楼 A-405", "teacher": "陈教授"},
        {"weekday": "周三", "time": "14:00-15:35", "course": "英语听说",
         "location": "外语楼 D-201", "teacher": "Emily"},
        {"weekday": "周四", "time": "10:15-11:50", "course": "数据结构",
         "location": "计算机楼 C-301", "teacher": "刘教授"},
        {"weekday": "周五", "time": "08:30-10:05", "course": "思想政治理论",
         "location": "教学楼 A-101", "teacher": "赵教授"},
    ]

def get_finance() -> dict:
    """获取本月财务 Mock 数据"""
    return {
        "monthly_budget": 2000.00,
        "spent": 1650.00,
        "remaining": 350.00,
        "budget_usage_pct": 82.5,
        "categories": {
            "餐饮": 820.00,
            "交通": 150.00,
            "购物": 380.00,
            "学习用品": 120.00,
            "娱乐": 100.00,
            "其他": 80.00,
        },
        "recent_transactions": [
            {"date": "2026-02-19", "item": "食堂午餐", "amount": 15.00,
             "category": "餐饮"},
            {"date": "2026-02-18", "item": "奶茶", "amount": 18.00,
             "category": "餐饮"},
            {"date": "2026-02-18", "item": "地铁充值", "amount": 50.00,
             "category": "交通"},
            {"date": "2026-02-17", "item": "教材《数据结构》", "amount": 45.00,
             "category": "学习用品"},
            {"date": "2026-02-16", "item": "电影票", "amount": 39.90,
             "category": "娱乐"},
        ],
    }

def get_health() -> dict:
    """获取健康状态 Mock 数据"""
    return {
        "today_steps": 4523,
        "step_goal": 8000,
        "sleep_hours": 6.5,
        "sleep_quality": "一般",
        "water_cups": 4,
        "water_goal": 8,
        "exercise_this_week": 1,
        "exercise_goal": 3,
        "last_exercise": "2026-02-15",
        "mood": "😐 一般",
        "checkin_streak": 5,
    }

def get_todos() -> list[dict]:
    """获取待办事项 Mock 数据"""
    return [
        {"task": "提交高数作业", "deadline": "2026-02-20",
         "priority": "🔴 紧急", "done": False},
        {"task": "复习线性代数期中", "deadline": "2026-02-26",
         "priority": "🟡 重要", "done": False},
        {"task": "Python 实验报告", "deadline": "2026-02-22",
         "priority": "🟡 重要", "done": False},
        {"task": "归还图书馆的书", "deadline": "2026-02-21",
         "priority": "🟢 普通", "done": False},
        {"task": "社团例会", "deadline": "2026-02-20",
         "priority": "🟢 普通", "done": True},
    ]

def get_upcoming_exams() -> list[dict]:
    """获取考试安排 Mock 数据"""
    return [
        {"course": "线性代数", "date": "2026-02-26",
         "days_left": 7, "location": "教学楼 A-101"},
        {"course": "高等数学 II", "date": "2026-03-05",
         "days_left": 14, "location": "教学楼 A-301"},
    ]

def build_context_summary() -> dict:
    """
    构建上下文摘要，用于注入 System Prompt。
    这是 Day 4 智能联动的核心桥梁。
    """
    finance = get_finance()
    health = get_health()
    todos = get_todos()
    exams = get_upcoming_exams()
    schedule = get_schedule()

    # 财务摘要
    finance_summary = (
        f"本月预算 {finance['monthly_budget']}元，"
        f"已花费 {finance['spent']}元（{finance['budget_usage_pct']}%），"
        f"剩余 {finance['remaining']}元。"
        f"{'⚠️ 预算已超过80%，需要注意节省！' if finance['budget_usage_pct'] > 80 else ''}"
    )

    # 健康摘要
    health_summary = (
        f"今日步数 {health['today_steps']}/{health['step_goal']}，"
        f"昨晚睡眠 {health['sleep_hours']}小时（{health['sleep_quality']}），"
        f"本周运动 {health['exercise_this_week']}/{health['exercise_goal']}次，"
        f"喝水 {health['water_cups']}/{health['water_goal']}杯。"
        f"打卡连续 {health['checkin_streak']}天。"
    )

    # 待办摘要
    pending = [t for t in todos if not t["done"]]
    urgent = [t for t in pending if "紧急" in t["priority"]]
    todo_summary = (
        f"待办 {len(pending)} 项"
        f"{'，其中 ' + str(len(urgent)) + ' 项紧急！' if urgent else '。'}"
    )
    for t in pending:
        todo_summary += f"\n  - {t['priority']} {t['task']}（截止 {t['deadline']}）"

    # 课程摘要
    weekday_map = {0: "周一", 1: "周二", 2: "周三",
                   3: "周四", 4: "周五", 5: "周六", 6: "周日"}
    today_weekday = weekday_map[datetime.now().weekday()]
    today_courses = [s for s in schedule if s["weekday"] == today_weekday]
    if today_courses:
        schedule_summary = f"今天（{today_weekday}）有 {len(today_courses)} 节课：\n"
        for c in today_courses:
            schedule_summary += (
                f"  - {c['time']} {c['course']}（{c['location']}）\n"
            )
    else:
        schedule_summary = f"今天（{today_weekday}）没有课，可以自由安排 🎉"

    # 考试提醒
    if exams:
        schedule_summary += "\n📝 近期考试：\n"
        for e in exams:
            schedule_summary += (
                f"  - {e['course']}：{e['date']}"
                f"（还有 {e['days_left']} 天）\n"
            )

    return {
        "schedule_summary": schedule_summary,
        "finance_summary": finance_summary,
        "health_summary": health_summary,
        "todo_summary": todo_summary,
    }

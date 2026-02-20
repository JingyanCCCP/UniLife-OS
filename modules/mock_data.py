"""
UniLife OS — Mock 数据中心 (Day 2 增强版)
所有伪造数据集中管理，Day 2 扩展：
- 消费记录扩展至 20+ 条，覆盖整月
- 健康数据日历化（最近 7 天历史）
- 新增旅行规划 Mock 数据
- 课表智能匹配当日
"""
from datetime import datetime, timedelta

def get_schedule() -> list[dict]:
    """获取本周课表 Mock 数据"""
    return [
        {"weekday": "周一", "time": "08:30-10:05", "course": "高等数学 II",
         "location": "教学楼 A-301", "teacher": "王教授", "type": "必修"},
        {"weekday": "周一", "time": "14:00-15:35", "course": "大学物理",
         "location": "实验楼 B-205", "teacher": "李教授", "type": "必修"},
        {"weekday": "周二", "time": "10:15-11:50", "course": "Python 程序设计",
         "location": "计算机楼 C-102", "teacher": "张教授", "type": "必修"},
        {"weekday": "周二", "time": "14:00-15:35", "course": "体育（羽毛球）",
         "location": "体育馆 B区", "teacher": "孙老师", "type": "必修"},
        {"weekday": "周三", "time": "08:30-10:05", "course": "线性代数",
         "location": "教学楼 A-405", "teacher": "陈教授", "type": "必修"},
        {"weekday": "周三", "time": "14:00-15:35", "course": "英语听说",
         "location": "外语楼 D-201", "teacher": "Emily", "type": "必修"},
        {"weekday": "周四", "time": "10:15-11:50", "course": "数据结构",
         "location": "计算机楼 C-301", "teacher": "刘教授", "type": "必修"},
        {"weekday": "周四", "time": "14:00-17:00", "course": "物理实验",
         "location": "实验楼 B-101", "teacher": "李教授", "type": "实验"},
        {"weekday": "周五", "time": "08:30-10:05", "course": "思想政治理论",
         "location": "教学楼 A-101", "teacher": "赵教授", "type": "必修"},
        {"weekday": "周五", "time": "14:00-15:35", "course": "创新创业基础",
         "location": "教学楼 A-501", "teacher": "周老师", "type": "选修"},
    ]

def get_today_schedule() -> list[dict]:
    """获取今日课程，自动匹配星期几"""
    weekday_map = {0: "周一", 1: "周二", 2: "周三",
                   3: "周四", 4: "周五", 5: "周六", 6: "周日"}
    today_weekday = weekday_map[datetime.now().weekday()]
    schedule = get_schedule()
    return [s for s in schedule if s["weekday"] == today_weekday]

def get_finance() -> dict:
    """获取本月财务 Mock 数据（Day 2 增强：20+ 条消费记录）"""
    return {
        "monthly_budget": 2000.00,
        "spent": 1650.00,
        "remaining": 350.00,
        "budget_usage_pct": 82.5,
        "daily_avg_spent": 82.5,
        "days_left_in_month": 8,
        "suggested_daily": 43.75,
        "categories": {
            "餐饮": 820.00,
            "交通": 150.00,
            "购物": 380.00,
            "学习用品": 120.00,
            "娱乐": 100.00,
            "其他": 80.00,
        },
        "recent_transactions": [
            {"date": "2026-02-20", "item": "食堂早餐", "amount": 7.00,
             "category": "餐饮", "icon": "🍜"},
            {"date": "2026-02-19", "item": "食堂午餐", "amount": 15.00,
             "category": "餐饮", "icon": "🍜"},
            {"date": "2026-02-19", "item": "超市零食", "amount": 23.50,
             "category": "购物", "icon": "🛒"},
            {"date": "2026-02-18", "item": "奶茶（一点点）", "amount": 18.00,
             "category": "餐饮", "icon": "🧋"},
            {"date": "2026-02-18", "item": "地铁充值", "amount": 50.00,
             "category": "交通", "icon": "🚇"},
            {"date": "2026-02-17", "item": "教材《数据结构》", "amount": 45.00,
             "category": "学习用品", "icon": "📚"},
            {"date": "2026-02-17", "item": "食堂晚餐", "amount": 18.00,
             "category": "餐饮", "icon": "🍜"},
            {"date": "2026-02-16", "item": "电影票《流浪地球3》", "amount": 39.90,
             "category": "娱乐", "icon": "🎬"},
            {"date": "2026-02-16", "item": "爆米花可乐", "amount": 28.00,
             "category": "餐饮", "icon": "🍿"},
            {"date": "2026-02-15", "item": "外卖（麻辣烫）", "amount": 25.00,
             "category": "餐饮", "icon": "🥡"},
            {"date": "2026-02-14", "item": "情人节礼物", "amount": 99.00,
             "category": "购物", "icon": "🎁"},
            {"date": "2026-02-13", "item": "打印资料", "amount": 8.50,
             "category": "学习用品", "icon": "🖨️"},
            {"date": "2026-02-12", "item": "食堂午餐", "amount": 14.00,
             "category": "餐饮", "icon": "🍜"},
            {"date": "2026-02-11", "item": "公交月卡", "amount": 50.00,
             "category": "交通", "icon": "🚌"},
            {"date": "2026-02-10", "item": "水果（苹果+香蕉）", "amount": 15.80,
             "category": "餐饮", "icon": "🍎"},
            {"date": "2026-02-09", "item": "理发", "amount": 35.00,
             "category": "其他", "icon": "💇"},
            {"date": "2026-02-08", "item": "网易云音乐会员", "amount": 15.00,
             "category": "娱乐", "icon": "🎵"},
            {"date": "2026-02-07", "item": "食堂晚餐", "amount": 16.00,
             "category": "餐饮", "icon": "🍜"},
            {"date": "2026-02-05", "item": "淘宝（数据线）", "amount": 19.90,
             "category": "购物", "icon": "🛒"},
            {"date": "2026-02-03", "item": "洗衣液+纸巾", "amount": 32.00,
             "category": "其他", "icon": "🧴"},
            {"date": "2026-02-01", "item": "开学聚餐AA", "amount": 68.00,
             "category": "餐饮", "icon": "🍻"},
        ],
    }

def get_health() -> dict:
    """获取健康状态 Mock 数据（Day 2 增强：7 天历史）"""
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
        "bmi": 21.3,
        "weight": 65.0,
        # 最近 7 天历史数据
        "history": [
            {"date": "2026-02-20", "steps": 4523, "sleep": 6.5,
             "water": 4, "exercise": False, "mood": "😐"},
            {"date": "2026-02-19", "steps": 6210, "sleep": 7.0,
             "water": 6, "exercise": False, "mood": "🙂"},
            {"date": "2026-02-18", "steps": 3800, "sleep": 5.5,
             "water": 3, "exercise": False, "mood": "😫"},
            {"date": "2026-02-17", "steps": 7500, "sleep": 7.5,
             "water": 7, "exercise": False, "mood": "😊"},
            {"date": "2026-02-16", "steps": 5100, "sleep": 6.0,
             "water": 5, "exercise": False, "mood": "😐"},
            {"date": "2026-02-15", "steps": 10200, "sleep": 7.0,
             "water": 8, "exercise": True, "mood": "😄"},
            {"date": "2026-02-14", "steps": 8900, "sleep": 8.0,
             "water": 6, "exercise": False, "mood": "😊"},
        ],
    }

def get_todos() -> list[dict]:
    """获取待办事项 Mock 数据"""
    return [
        {"id": 1, "task": "提交高数作业", "deadline": "2026-02-20",
         "priority": "🔴 紧急", "done": False, "category": "学业"},
        {"id": 2, "task": "复习线性代数期中", "deadline": "2026-02-26",
         "priority": "🟡 重要", "done": False, "category": "学业"},
        {"id": 3, "task": "Python 实验报告", "deadline": "2026-02-22",
         "priority": "🟡 重要", "done": False, "category": "学业"},
        {"id": 4, "task": "归还图书馆的书", "deadline": "2026-02-21",
         "priority": "🟢 普通", "done": False, "category": "生活"},
        {"id": 5, "task": "社团例会", "deadline": "2026-02-20",
         "priority": "🟢 普通", "done": True, "category": "社交"},
        {"id": 6, "task": "给妈妈打电话", "deadline": "2026-02-21",
         "priority": "🟢 普通", "done": False, "category": "生活"},
        {"id": 7, "task": "洗衣服", "deadline": "2026-02-20",
         "priority": "🟢 普通", "done": False, "category": "生活"},
    ]

def get_upcoming_exams() -> list[dict]:
    """获取考试安排 Mock 数据"""
    return [
        {"course": "线性代数", "date": "2026-02-26",
         "days_left": 6, "location": "教学楼 A-101", "type": "期中考试"},
        {"course": "高等数学 II", "date": "2026-03-05",
         "days_left": 13, "location": "教学楼 A-301", "type": "期中考试"},
        {"course": "大学物理", "date": "2026-03-12",
         "days_left": 20, "location": "实验楼 B-205", "type": "期中考试"},
    ]

def get_travel_plan() -> dict:
    """获取旅行规划 Mock 数据（Day 2 新增）"""
    return {
        "trip_name": "周末深圳一日游 🏖️",
        "date": "2026-03-01",
        "budget": 300.00,
        "status": "计划中",
        "companions": ["室友小李", "同学小王"],
        "itinerary": [
            {"time": "08:00", "activity": "学校出发（地铁）",
             "location": "大学城站", "cost": 8.00, "icon": "🚇"},
            {"time": "09:30", "activity": "到达世界之窗",
             "location": "世界之窗", "cost": 0, "icon": "🏰"},
            {"time": "09:30-12:00", "activity": "游玩世界之窗",
             "location": "世界之窗", "cost": 80.00, "icon": "🎢"},
            {"time": "12:00-13:00", "activity": "午餐（海岸城）",
             "location": "海岸城购物中心", "cost": 60.00, "icon": "🍱"},
            {"time": "13:30-16:00", "activity": "深圳湾公园骑行",
             "location": "深圳湾公园", "cost": 30.00, "icon": "🚴"},
            {"time": "16:30-18:00", "activity": "海岸城逛街",
             "location": "海岸城购物中心", "cost": 50.00, "icon": "🛍️"},
            {"time": "18:00-19:00", "activity": "晚餐",
             "location": "海岸城美食区", "cost": 55.00, "icon": "🍜"},
            {"time": "19:30", "activity": "返程（地铁）",
             "location": "后海站", "cost": 8.00, "icon": "🚇"},
        ],
        "total_estimated_cost": 291.00,
        "packing_list": ["充电宝", "防晒霜", "学生证（门票优惠）", "水杯", "零食"],
    }

def get_alerts() -> list[dict]:
    """
    智能提醒生成器（Day 2 新增）
    基于当前数据自动判断需要提醒的事项
    """
    alerts = []
    finance = get_finance()
    health = get_health()
    todos = get_todos()
    exams = get_upcoming_exams()

    # 预算告急提醒
    if finance["budget_usage_pct"] > 80:
        alerts.append({
            "type": "warning",
            "icon": "💰",
            "title": "预算告急",
            "message": (
                f"本月预算已用 {finance["budget_usage_pct"]}%，"
                f"剩余 ¥{finance["remaining"]:.0f}。"
                f"剩余 {finance["days_left_in_month"]} 天，"
                f"建议每天控制在 ¥{finance["suggested_daily"]:.0f} 以内。"
            ),
            "severity": "high",
        })

    # 考试临近提醒
    for exam in exams:
        if exam["days_left"] <= 7:
            alerts.append({
                "type": "exam",
                "icon": "📝",
                "title": f"{exam["course"]}考试倒计时",
                "message": (
                    f"{exam["course"]} {exam["type"]}还有 "
                    f"**{exam["days_left"]} 天**！"
                    f"地点：{exam["location"]}。建议制定复习计划。"
                ),
                "severity": "high" if exam["days_left"] <= 3 else "medium",
            })

    # 运动不足提醒
    days_since_exercise = (
        datetime.now() - datetime.strptime(health["last_exercise"], "%Y-%m-%d")
    ).days
    if days_since_exercise >= 3:
        alerts.append({
            "type": "health",
            "icon": "🏃",
            "title": "运动提醒",
            "message": (
                f"已经 **{days_since_exercise} 天**没有运动了，"
                f"本周运动 {health["exercise_this_week"]}/{health["exercise_goal"]} 次。"
                f"去操场跑两圈或打会儿球吧！"
            ),
            "severity": "medium",
        })

    # 睡眠不足提醒
    if health["sleep_hours"] < 7:
        alerts.append({
            "type": "health",
            "icon": "😴",
            "title": "睡眠不足",
            "message": (
                f"昨晚只睡了 **{health["sleep_hours"]} 小时**，"
                f"质量「{health["sleep_quality"]}」。"
                f"建议今晚 11 点前上床休息哦。"
            ),
            "severity": "low",
        })

    # 喝水不足提醒
    if health["water_cups"] < health["water_goal"] // 2:
        alerts.append({
            "type": "health",
            "icon": "💧",
            "title": "记得喝水",
            "message": (
                f"今天才喝了 **{health["water_cups"]}** 杯水，"
                f"目标 {health["water_goal"]} 杯。多喝水保持精力！"
            ),
            "severity": "low",
        })

    # 紧急待办提醒
    urgent_todos = [t for t in todos if not t["done"] and "紧急" in t["priority"]]
    if urgent_todos:
        tasks = "、".join([t["task"] for t in urgent_todos])
        alerts.append({
            "type": "todo",
            "icon": "🔥",
            "title": "紧急待办",
            "message": f"今天必须完成：**{tasks}**，别忘了！",
            "severity": "high",
        })

    return alerts

def build_context_summary() -> dict:
    """
    构建上下文摘要，用于注入 System Prompt。
    Day 2 增强版：更丰富的上下文信息。
    """
    finance = get_finance()
    health = get_health()
    todos = get_todos()
    exams = get_upcoming_exams()
    schedule = get_schedule()
    travel = get_travel_plan()
    alerts = get_alerts()

    # 财务摘要
    finance_summary = (
        f"本月预算 {finance['monthly_budget']}元，"
        f"已花费 {finance['spent']}元（{finance['budget_usage_pct']}%），"
        f"剩余 {finance['remaining']}元。"
        f"日均消费 {finance['daily_avg_spent']}元，"
        f"本月还剩 {finance['days_left_in_month']} 天，"
        f"建议每天控制在 {finance['suggested_daily']}元以内。"
        f"{'⚠️ 预算已超过80%，需要注意节省！' if finance['budget_usage_pct'] > 80 else ''}"
        f"\n消费前三：{'、'.join(list(finance['categories'].keys())[:3])}"
    )

    # 健康摘要
    days_since_exercise = (
        datetime.now() - datetime.strptime(health["last_exercise"], "%Y-%m-%d")
    ).days
    health_summary = (
        f"今日步数 {health['today_steps']}/{health['step_goal']}，"
        f"昨晚睡眠 {health['sleep_hours']}小时（{health['sleep_quality']}），"
        f"本周运动 {health['exercise_this_week']}/{health['exercise_goal']}次，"
        f"喝水 {health['water_cups']}/{health['water_goal']}杯。"
        f"打卡连续 {health['checkin_streak']}天。"
        f"已有 {days_since_exercise} 天未运动。"
        f"BMI: {health['bmi']}，体重 {health['weight']}kg。"
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
    today_courses = get_today_schedule()
    weekday_map = {0: "周一", 1: "周二", 2: "周三",
                   3: "周四", 4: "周五", 5: "周六", 6: "周日"}
    today_weekday = weekday_map[datetime.now().weekday()]

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

    # 旅行摘要
    travel_summary = (
        f"计划中的旅行：{travel['trip_name']}，"
        f"日期 {travel['date']}，"
        f"预算 ¥{travel['budget']}，"
        f"同行：{'、'.join(travel['companions'])}。"
    )

    # 智能提醒摘要
    if alerts:
        alert_summary = "当前提醒：\n"
        for a in alerts:
            alert_summary += f"  - {a['icon']} {a['title']}：{a['message']}\n"
    else:
        alert_summary = "当前没有需要特别关注的事项 ✅"

    return {
        "schedule_summary": schedule_summary,
        "finance_summary": finance_summary,
        "health_summary": health_summary,
        "todo_summary": todo_summary,
        "travel_summary": travel_summary,
        "alert_summary": alert_summary,
    }
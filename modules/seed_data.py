"""
UniLife OS — Seed 数据模板层（R1 新增）

职责：
- 纯模板 + 动态日期生成。所有 `build_*_seed()` 都以 `today` 为输入参数，默认取 datetime.now().date()。
- 不读、不写 persistence。
- 不做聚合（聚合逻辑留在 modules.mock_data）。

设计原则：
- 单一事实来源：所有硬编码模板只在这里出现一次。
- 确定性：传同一个 today 返回同一个结果，便于 pytest。
- 可回放：tools/reset_demo.py 通过清空 persistence 回到 seed 态，seed 自身再随当前时间渲染。
"""
from __future__ import annotations

from datetime import datetime, date, timedelta


# ---------------------------------------------------------------------------
# 课表（固定周循环模板）
# ---------------------------------------------------------------------------

_SCHEDULE_TEMPLATE: list[dict] = [
    {"id": 1, "weekday": "周一", "time": "08:30-10:05", "course": "高等数学 II",
     "location": "教学楼 A-301", "teacher": "王教授", "type": "必修"},
    {"id": 2, "weekday": "周一", "time": "14:00-15:35", "course": "大学物理",
     "location": "实验楼 B-205", "teacher": "李教授", "type": "必修"},
    {"id": 3, "weekday": "周二", "time": "10:15-11:50", "course": "Python 程序设计",
     "location": "计算机楼 C-102", "teacher": "张教授", "type": "必修"},
    {"id": 4, "weekday": "周二", "time": "14:00-15:35", "course": "体育(羽毛球)",
     "location": "体育馆 B区", "teacher": "孙老师", "type": "必修"},
    {"id": 5, "weekday": "周三", "time": "08:30-10:05", "course": "线性代数",
     "location": "教学楼 A-405", "teacher": "陈教授", "type": "必修"},
    {"id": 6, "weekday": "周三", "time": "14:00-15:35", "course": "英语听说",
     "location": "外语楼 D-201", "teacher": "Emily", "type": "必修"},
    {"id": 7, "weekday": "周四", "time": "10:15-11:50", "course": "数据结构",
     "location": "计算机楼 C-301", "teacher": "刘教授", "type": "必修"},
    {"id": 8, "weekday": "周四", "time": "14:00-17:00", "course": "物理实验",
     "location": "实验楼 B-101", "teacher": "李教授", "type": "实验"},
    {"id": 9, "weekday": "周五", "time": "08:30-10:05", "course": "思想政治理论",
     "location": "教学楼 A-101", "teacher": "赵教授", "type": "必修"},
    {"id": 10, "weekday": "周五", "time": "14:00-15:35", "course": "创新创业基础",
     "location": "教学楼 A-501", "teacher": "周老师", "type": "选修"},
]


def build_schedule_seed() -> list[dict]:
    """返回本周课表 seed 的深拷贝。"""
    return [dict(c) for c in _SCHEDULE_TEMPLATE]


# ---------------------------------------------------------------------------
# 财务
# ---------------------------------------------------------------------------

# base_spent / base_categories 为本月累计总额的 mock（代表演示用户「本月已经花过」的历史状态）。
# base_transactions 是展示给用户看的最近 21 条消费流水，日期相对 today 动态。
_FINANCE_BASE_SPENT: float = 1650.00

_FINANCE_CATEGORIES: dict[str, float] = {
    "餐饮": 820.00,
    "交通": 150.00,
    "购物": 380.00,
    "学习用品": 120.00,
    "娱乐": 100.00,
    "其他": 80.00,
}

# (item, amount, category, icon, days_ago) —— 共 21 条，days_ago 单调递增
_FINANCE_TXN_TEMPLATE: list[tuple[str, float, str, str, int]] = [
    ("食堂早餐",          7.00,  "餐饮",    "🍜", 0),
    ("食堂午餐",          15.00, "餐饮",    "🍜", 1),
    ("超市零食",          23.50, "购物",    "🛒", 1),
    ("奶茶(一点点)",      18.00, "餐饮",    "🧋", 2),
    ("地铁充值",          50.00, "交通",    "🚇", 2),
    ("教材《数据结构》",   45.00, "学习用品","📚", 3),
    ("食堂晚餐",          18.00, "餐饮",    "🍜", 3),
    ("电影票",            39.90, "娱乐",    "🎬", 4),
    ("爆米花可乐",        28.00, "餐饮",    "🍿", 4),
    ("外卖(麻辣烫)",      25.00, "餐饮",    "🥡", 5),
    ("情人节礼物",        99.00, "购物",    "🎁", 6),
    ("打印资料",          8.50,  "学习用品","🖨️", 7),
    ("食堂午餐",          14.00, "餐饮",    "🍜", 8),
    ("公交月卡",          50.00, "交通",    "🚌", 9),
    ("水果(苹果+香蕉)",   15.80, "餐饮",    "🍎", 10),
    ("理发",              35.00, "其他",    "💇", 11),
    ("网易云音乐会员",    15.00, "娱乐",    "🎵", 12),
    ("食堂晚餐",          16.00, "餐饮",    "🍜", 13),
    ("淘宝(数据线)",      19.90, "购物",    "🛒", 15),
    ("洗衣液+纸巾",       32.00, "其他",    "🧴", 17),
    ("开学聚餐AA",        68.00, "餐饮",    "🍻", 20),
]


def build_finance_seed(today: date | None = None) -> tuple[float, dict, list[dict]]:
    """返回 `(base_spent, base_categories_copy, base_transactions)`。

    - base_spent / base_categories 为月度总额（mock 本月历史已花）。
    - base_transactions 按 today 动态渲染日期。
    """
    today = today or datetime.now().date()
    categories = dict(_FINANCE_CATEGORIES)
    transactions = [
        {
            "date": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "item": item,
            "amount": amount,
            "category": category,
            "icon": icon,
        }
        for item, amount, category, icon, days_ago in _FINANCE_TXN_TEMPLATE
    ]
    return _FINANCE_BASE_SPENT, categories, transactions


# ---------------------------------------------------------------------------
# 待办
# ---------------------------------------------------------------------------

# (id, task, deadline_offset_days, priority, done, category)
# offset 为相对 today 的天数。完整范围 [-2, +6]，对应规划案 R1 要求。
_TODOS_TEMPLATE: list[tuple[int, str, int, str, bool, str]] = [
    (1, "提交高数作业",       0, "🔴 紧急", False, "学业"),
    (2, "复习线性代数期中",   6, "🟡 重要", False, "学业"),
    (3, "Python 实验报告",    2, "🟡 重要", False, "学业"),
    (4, "归还图书馆的书",     1, "🟢 普通", False, "生活"),
    (5, "社团例会",           0, "🟢 普通", True,  "社交"),
    (6, "给妈妈打电话",       1, "🟢 普通", False, "生活"),
    (7, "洗衣服",             0, "🟢 普通", False, "生活"),
]


def build_todos_seed(today: date | None = None) -> list[dict]:
    """返回 7 条 base todos，deadline 随 today 动态滚动。"""
    today = today or datetime.now().date()
    return [
        {
            "id": tid,
            "task": task,
            "deadline": (today + timedelta(days=offset)).strftime("%Y-%m-%d"),
            "priority": priority,
            "done": done,
            "category": category,
        }
        for tid, task, offset, priority, done, category in _TODOS_TEMPLATE
    ]


# ---------------------------------------------------------------------------
# 考试
# ---------------------------------------------------------------------------

# (course, days_ahead, location, type) —— 按规划案 R1 固定为 +1 / +8 / +15 天
_EXAMS_TEMPLATE: list[tuple[str, int, str, str]] = [
    ("线性代数",       1,  "教学楼 A-101", "期中考试"),
    ("高等数学 II",    8,  "教学楼 A-301", "期中考试"),
    ("大学物理",       15, "实验楼 B-205", "期中考试"),
]


def build_exams_seed(today: date | None = None) -> list[dict]:
    """返回 3 条考试 seed，date 随 today 动态滚动。不含 days_left 字段，由聚合层计算。"""
    today = today or datetime.now().date()
    return [
        {
            "course": course,
            "date": (today + timedelta(days=offset)).strftime("%Y-%m-%d"),
            "location": location,
            "type": exam_type,
        }
        for course, offset, location, exam_type in _EXAMS_TEMPLATE
    ]


# ---------------------------------------------------------------------------
# 旅行
# ---------------------------------------------------------------------------

_TRAVEL_BASE: dict = {
    "trip_name": "周末深圳一日游 🏖️",
    "budget": 300.00,
    "status": "计划中",
    "companions": ["室友小李", "同学小王"],
    "packing_list": ["充电宝", "防晒霜", "学生证(门票优惠)", "水杯", "零食"],
}

# 8 条 —— 与 persistence.reset_travel_itinerary() 里的 range(8) 严格对应，不要改长度。
_TRAVEL_ITINERARY_TEMPLATE: list[dict] = [
    {"time": "08:00",       "activity": "学校出发(地铁)",
     "location": "大学城站",   "cost": 8.00,  "icon": "🚇"},
    {"time": "09:30",       "activity": "到达世界之窗",
     "location": "世界之窗",   "cost": 0,     "icon": "🏰"},
    {"time": "09:30-12:00", "activity": "游玩世界之窗",
     "location": "世界之窗",   "cost": 80.00, "icon": "🎢"},
    {"time": "12:00-13:00", "activity": "午餐(海岸城)",
     "location": "海岸城购物中心", "cost": 60.00, "icon": "🍱"},
    {"time": "13:30-16:00", "activity": "深圳湾公园骑行",
     "location": "深圳湾公园", "cost": 30.00, "icon": "🚴"},
    {"time": "16:30-18:00", "activity": "海岸城逛街",
     "location": "海岸城购物中心", "cost": 50.00, "icon": "🛍️"},
    {"time": "18:00-19:00", "activity": "晚餐",
     "location": "海岸城美食区", "cost": 55.00, "icon": "🍜"},
    {"time": "19:30",       "activity": "返程(地铁)",
     "location": "后海站",     "cost": 8.00,  "icon": "🚇"},
]


def _next_saturday(today: date) -> date:
    """返回今天之后的下一个周六。如果今天就是周六，推到下周六。"""
    days_until_sat = (5 - today.weekday()) % 7 or 7
    return today + timedelta(days=days_until_sat)


def build_travel_seed(today: date | None = None) -> dict:
    """返回旅行计划 seed。date = 下一个周六。行程列表由 build_travel_itinerary_seed 提供。"""
    today = today or datetime.now().date()
    base = dict(_TRAVEL_BASE)
    base["companions"] = list(_TRAVEL_BASE["companions"])
    base["packing_list"] = list(_TRAVEL_BASE["packing_list"])
    base["date"] = _next_saturday(today).strftime("%Y-%m-%d")
    return base


def build_travel_itinerary_seed() -> list[dict]:
    """返回 8 条 base 行程站点的深拷贝。长度固定 8，不要改，与 persistence 配合。"""
    return [dict(s) for s in _TRAVEL_ITINERARY_TEMPLATE]


# ---------------------------------------------------------------------------
# 健康（今日基础值 + 过去 6 天历史）
# ---------------------------------------------------------------------------

_HEALTH_TODAY_BASE: dict = {
    "steps": 4523,
    "sleep_hours": 6.5,
    "sleep_quality": "一般",
    "mood": "😐 一般",
    "water_cups": 4,
    "last_exercise_days_ago": 5,   # 今日未打卡时，最近一次运动的 days_ago
}

# index 0 = 昨天；已是相对 today 的模板，无硬编码日期
_HEALTH_PAST_TEMPLATE: list[dict] = [
    {"steps": 6210,  "sleep": 7.0, "water": 6, "exercise": False, "mood": "🙂"},
    {"steps": 3800,  "sleep": 5.5, "water": 3, "exercise": False, "mood": "😫"},
    {"steps": 7500,  "sleep": 7.5, "water": 7, "exercise": False, "mood": "😊"},
    {"steps": 5100,  "sleep": 6.0, "water": 5, "exercise": False, "mood": "😐"},
    {"steps": 10200, "sleep": 7.0, "water": 8, "exercise": True,  "mood": "😄"},
    {"steps": 8900,  "sleep": 8.0, "water": 6, "exercise": False, "mood": "😊"},
]


def build_health_today_base() -> dict:
    """今日健康基础值（steps / sleep / mood / water / last_exercise_days_ago）。"""
    return dict(_HEALTH_TODAY_BASE)


def build_health_history_seed() -> list[dict]:
    """过去 6 天历史模板，不含 date 字段（由聚合层附加 today - timedelta(days=i+1)）。"""
    return [dict(d) for d in _HEALTH_PAST_TEMPLATE]

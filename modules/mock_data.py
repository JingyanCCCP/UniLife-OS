"""
UniLife OS — Mock 数据聚合层

职责（R1 重构后）：
- 聚合 seed_data 的静态模板 + persistence 的增量 overlay，输出 app.py / tools.py 使用的 `get_*()` 快照。
- 只做组装，不再承载模板常量。
- 暴露 build_context_summary 作为 re-export，app.py / prompts 导入路径不变。

与 R1 前的差异：
- 所有 base_* 模板已搬到 modules.seed_data，日期字段改为相对 datetime.now() 动态生成。
- build_context_summary 已搬到 modules.context_builder；本文件仅 re-export 保持向后兼容。
"""
from __future__ import annotations

from datetime import datetime, timedelta
from calendar import monthrange

from modules.persistence import (
    get_todo_overrides, get_extra_transactions, get_health_overrides, get_extra_todos,
    get_extra_courses, get_deleted_course_ids, get_course_updates,
    get_budget, get_travel_overrides, get_extra_itinerary,
    get_deleted_itinerary_idxs, get_itinerary_updates,
    get_exercise_weekly, get_exercise_goal, set_exercise_goal,  # noqa: F401 (set_exercise_goal 供 tools 使用)
)
from modules.seed_data import (
    build_schedule_seed,
    build_finance_seed,
    build_todos_seed,
    build_exams_seed,
    build_travel_seed,
    build_travel_itinerary_seed,
    build_health_today_base,
    build_health_history_seed,
)
from modules.context_builder import build_context_summary  # re-export


def get_schedule() -> list[dict]:
    """本周课表 = seed 模板 - 已删除 mock 课程 + 覆盖字段 + 用户新增课程。"""
    base = build_schedule_seed()

    deleted_ids = get_deleted_course_ids()
    schedule = [c for c in base if c["id"] not in deleted_ids]

    updates = get_course_updates()
    for c in schedule:
        cid_str = str(c["id"])
        if cid_str in updates:
            for k, v in updates[cid_str].items():
                c[k] = v

    schedule.extend(get_extra_courses())
    return schedule


def get_today_schedule() -> list[dict]:
    """今日课程。按当前星期几从整周课表里筛选。"""
    weekday_map = {0: "周一", 1: "周二", 2: "周三",
                   3: "周四", 4: "周五", 5: "周六", 6: "周日"}
    today_weekday = weekday_map[datetime.now().weekday()]
    return [s for s in get_schedule() if s["weekday"] == today_weekday]


def get_finance() -> dict:
    """本月财务概览 = seed 模板 + 用户新增消费。"""
    today = datetime.now()
    base_spent, base_categories, base_transactions = build_finance_seed(today.date())
    budget = get_budget() or 2000.00

    extra = get_extra_transactions()
    extra_total = sum(t["amount"] for t in extra)
    all_transactions = extra + base_transactions  # 新消费排在前面

    categories = dict(base_categories)
    for t in extra:
        cat = t.get("category", "其他")
        categories[cat] = categories.get(cat, 0) + t["amount"]

    spent = base_spent + extra_total
    remaining = max(budget - spent, 0)
    _, days_in_month = monthrange(today.year, today.month)
    days_passed = max(today.day, 1)
    days_left = max(days_in_month - today.day, 1)
    usage_pct = round(spent / budget * 100, 1)
    daily_avg = round(spent / days_passed, 1)
    suggested = round(remaining / days_left, 2) if remaining > 0 else 0

    return {
        "monthly_budget": budget,
        "spent": spent,
        "remaining": remaining,
        "budget_usage_pct": usage_pct,
        "daily_avg_spent": daily_avg,
        "days_left_in_month": days_left,
        "suggested_daily": suggested,
        "categories": categories,
        "recent_transactions": all_transactions,
    }


def get_health() -> dict:
    """今日健康状态 = seed base + persistence overrides。"""
    overrides = get_health_overrides()
    today = datetime.now()

    base = build_health_today_base()
    base_water = base["water_cups"]
    base_steps = base["steps"]
    base_sleep = base["sleep_hours"]
    base_sleep_quality = base["sleep_quality"]
    base_mood = base["mood"]
    base_last_exercise = (
        today - timedelta(days=base["last_exercise_days_ago"])
    ).strftime("%Y-%m-%d")

    is_today = overrides.get("override_date") == today.strftime("%Y-%m-%d")
    if is_today:
        steps = overrides.get("steps", base_steps)
        sleep_hours = overrides.get("sleep_hours", base_sleep)
        sleep_quality = overrides.get("sleep_quality", base_sleep_quality)
        water = base_water + overrides.get("water_cups", 0)
        exercise_today = overrides.get("exercise_today", False)
        mood = overrides.get("mood", base_mood)
    else:
        steps = base_steps
        sleep_hours = base_sleep
        sleep_quality = base_sleep_quality
        water = base_water
        exercise_today = False
        mood = base_mood
    last_exercise = today.strftime("%Y-%m-%d") if exercise_today else base_last_exercise

    # 过去 6 天历史（从最近到最远）
    past_base = build_health_history_seed()

    # 本周运动次数 = 过去 6 天中本周内的运动天数 + 持久化计数
    week_start_date = (today - timedelta(days=today.weekday())).date()
    base_exercise_week = 0
    for i, past in enumerate(past_base):
        day = (today - timedelta(days=i + 1)).date()
        if day >= week_start_date and past.get("exercise"):
            base_exercise_week += 1
    weekly_data = get_exercise_weekly()
    week_start_str = week_start_date.strftime("%Y-%m-%d")
    persisted_count = weekly_data.get("count", 0) if weekly_data.get("week_start") == week_start_str else 0
    exercise_week = base_exercise_week + persisted_count

    exercise_goal = get_exercise_goal() or 3

    # 生成最近 7 天历史：今天 + 过去 6 天
    mood_short = mood.split(" ")[0] if " " in mood else mood
    today_entry = {
        "date": today.strftime("%Y-%m-%d"),
        "steps": steps,
        "sleep": sleep_hours,
        "water": water,
        "exercise": exercise_today,
        "mood": mood_short,
    }
    history = [today_entry]
    for i, past in enumerate(past_base):
        day = today - timedelta(days=i + 1)
        entry = dict(past)
        entry["date"] = day.strftime("%Y-%m-%d")
        history.append(entry)

    step_goal = 8000
    exercise_target_miss_streak = 0
    for entry in history:
        if entry.get("steps", 0) >= step_goal:
            break
        exercise_target_miss_streak += 1

    return {
        "today_steps": steps,
        "step_goal": step_goal,
        "sleep_hours": sleep_hours,
        "sleep_quality": sleep_quality,
        "water_cups": water,
        "water_goal": 8,
        "exercise_this_week": exercise_week,
        "exercise_goal": exercise_goal,
        "last_exercise": last_exercise,
        "mood": mood,
        "checkin_streak": 6 if exercise_today else 5,
        "exercise_target_miss_streak": exercise_target_miss_streak,
        "bmi": 21.3,
        "weight": 65.0,
        "history": history,
    }


def get_todos() -> list[dict]:
    """待办列表 = seed 7 条 + 用户新增 - 7 天前过期项，合并完成状态覆盖。"""
    todos = build_todos_seed(datetime.now().date())

    overrides = get_todo_overrides()
    for t in todos:
        tid = str(t["id"])
        if tid in overrides:
            t["done"] = overrides[tid]

    extra = get_extra_todos()
    for t in extra:
        tid = str(t["id"])
        if tid in overrides:
            t["done"] = overrides[tid]
    todos.extend(extra)

    today = datetime.now().date()
    cutoff = today - timedelta(days=7)
    todos = [t for t in todos if datetime.strptime(t["deadline"], "%Y-%m-%d").date() >= cutoff]
    return todos


def get_upcoming_exams() -> list[dict]:
    """近期考试（动态倒计时，过滤已过期）。"""
    today = datetime.now().date()
    raw = build_exams_seed(today)
    exams = []
    for e in raw:
        exam_date = datetime.strptime(e["date"], "%Y-%m-%d").date()
        days_left = (exam_date - today).days
        if days_left >= 0:
            exams.append({**e, "days_left": days_left, "is_today": days_left == 0})
    return exams


def get_travel_plan() -> dict | None:
    """旅行计划 = seed + persistence overrides。返回 None 表示计划被删除。"""
    overrides = get_travel_overrides()
    if overrides.get("deleted"):
        return None

    today = datetime.now().date()
    base = build_travel_seed(today)
    base_itinerary = build_travel_itinerary_seed()

    for key in ("trip_name", "date", "budget", "status", "companions", "packing_list"):
        if key in overrides:
            base[key] = overrides[key]

    if isinstance(base["companions"], str):
        base["companions"] = [
            c.strip()
            for c in base["companions"].replace("，", "、").split("、")
            if c.strip()
        ]

    deleted_idxs = get_deleted_itinerary_idxs()
    updates = get_itinerary_updates()
    itinerary = []
    for i, stop in enumerate(base_itinerary):
        if i in deleted_idxs:
            continue
        idx_str = str(i)
        if idx_str in updates:
            stop = dict(stop)
            for k, v in updates[idx_str].items():
                stop[k] = v
        itinerary.append(stop)

    itinerary.extend(get_extra_itinerary())
    total_cost = sum(s.get("cost", 0) for s in itinerary)

    base["itinerary"] = itinerary
    base["total_estimated_cost"] = total_cost
    return base


def get_alerts() -> list[dict]:
    """
    主动关怀提醒（R3 起由 proactive 引擎产出）。

    本函数是薄兼容层：
    - 先触发一次扫描（`proactive.engine.scan_and_persist`）确保事件最新。
    - 再读取 `list_unread(limit=5)` 作为 UI / LLM context 的数据源。
    - 映射为历史 alert dict（含 severity/icon/title/message），保持 app.py `render_alerts()`
      原有调用路径不变。
    - 额外保留 `suggested_action` / `dedupe_key` 字段，R4 UI 可直接用。

    注意：message 含 HTML <strong>，渲染路径 unsafe_allow_html；context_builder 会在注入
    LLM 前剥离标签。
    """
    from proactive import engine  # 延迟导入避免循环依赖
    engine.scan_safely()
    events = engine.list_unread(limit=5)

    icon_by_type = {
        "budget_risk": "💰",
        "todo_due": "🔥",
        "exam_near": "📝",
        "sleep_short": "😴",
        "exercise_missing": "🏃",
        "travel_packing": "🧳",
    }

    alerts: list[dict] = []
    for ev in events:
        alerts.append({
            "type": ev.event_type,
            "icon": icon_by_type.get(ev.event_type, "🔔"),
            "title": ev.title,
            "message": ev.reason,
            "suggested_action": ev.suggested_action,
            "dedupe_key": ev.dedupe_key,
            "severity": ev.severity,
        })
    return alerts

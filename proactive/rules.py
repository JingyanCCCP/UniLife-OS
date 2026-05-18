"""
UniLife OS — 主动关怀规则库（R3 新增）

6 条规则，每条一个 check_* 函数，返回 list[ProactiveEvent]（空 list 表示无事件）。

- check_budget_risk:       预算使用超过 80%
- check_todo_due:          未完成待办 24h 内到期（每条一个事件）
- check_exam_near:         未来 7 天内考试（每场一个事件）
- check_sleep_short:       连续 3 天睡眠 < 7h
- check_exercise_missing:  连续 3 天未达到日运动目标
- check_travel_packing:    旅行 ≤ 3 天但必带清单未勾选

规则尽量独立、纯读：只查 mock_data / persistence，不写回。产出事件由 engine 负责去重和
写入。所有规则异常由 engine 吞掉，不会炸主流程。
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable

from proactive.events import ProactiveEvent


# ---------------------------------------------------------------------------
# 规则
# ---------------------------------------------------------------------------

def check_budget_risk() -> list[ProactiveEvent]:
    """预算使用率 > 80% → 高严重度事件。dedupe_key 按年月。"""
    from modules.mock_data import get_finance  # 延迟导入避免循环
    finance = get_finance()
    usage = finance.get("budget_usage_pct", 0)
    if usage <= 80:
        return []
    now = datetime.now()
    return [ProactiveEvent(
        event_type="budget_risk",
        severity="high",
        title="预算告急",
        reason=(
            f"本月预算已用 {usage}%，仅剩 ¥{finance.get('remaining', 0):.0f}。"
            f"按剩余 {finance.get('days_left_in_month', 0)} 天均摊，每天只能花 "
            f"¥{finance.get('suggested_daily', 0):.0f}。"
        ),
        suggested_action=(
            f"接下来几天优先控制餐饮/娱乐支出，每天控制在 "
            f"¥{finance.get('suggested_daily', 0):.0f} 以内。"
        ),
        dedupe_key=f"budget_risk:{now.strftime('%Y-%m')}",
    )]


def check_todo_due() -> list[ProactiveEvent]:
    """未完成待办中，deadline 在今天~明天之间的每条产生一个事件。"""
    from modules.mock_data import get_todos
    today = datetime.now().date()
    horizon = today + timedelta(days=1)  # 24h 窗口（今天 + 明天）
    events = []
    for t in get_todos():
        if t.get("done"):
            continue
        try:
            deadline = datetime.strptime(t["deadline"], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            continue
        if deadline < today or deadline > horizon:
            continue
        days_left = (deadline - today).days
        when = "今天" if days_left == 0 else "明天"
        events.append(ProactiveEvent(
            event_type="todo_due",
            severity="high" if "紧急" in t.get("priority", "") or days_left == 0 else "medium",
            title="待办到期",
            reason=f"{when}截止：{t.get('task', '(未命名)')}（{t.get('priority', '')}）。",
            suggested_action="打开待办 Tab 把它安排进今天的时间块，完成后记得勾选。",
            dedupe_key=f"todo_due:{t['id']}",
        ))
    return events


def check_exam_near() -> list[ProactiveEvent]:
    """未来 7 天内考试每场一个事件。"""
    from modules.mock_data import get_upcoming_exams
    events = []
    for exam in get_upcoming_exams():
        days_left = exam.get("days_left", -1)
        if not 0 <= days_left <= 7:
            continue
        events.append(ProactiveEvent(
            event_type="exam_near",
            severity="high" if days_left <= 3 else "medium",
            title=f"{exam['course']} 考试临近",
            reason=(
                f"{exam['course']}（{exam.get('type', '考试')}）还有 {days_left} 天，"
                f"地点 {exam.get('location', '未知')}。"
            ),
            suggested_action="列出复习大纲 + 每天安排一块 2h 的学习时间块。",
            dedupe_key=f"exam_near:{exam['course']}",
        ))
    return events


def check_sleep_short() -> list[ProactiveEvent]:
    """连续 3 天睡眠 < 7h（看 history 最近 3 天，不含今日）。"""
    from modules.mock_data import get_health
    history = get_health().get("history", [])
    # 过滤掉今日，取最近 3 天历史
    today_str = datetime.now().strftime("%Y-%m-%d")
    past = [h for h in history if h.get("date") != today_str][:3]
    if len(past) < 3:
        return []
    if not all(h.get("sleep", 0) < 7 for h in past):
        return []
    avg = sum(h.get("sleep", 0) for h in past) / 3
    return [ProactiveEvent(
        event_type="sleep_short",
        severity="medium",
        title="睡眠不足",
        reason=f"过去 3 天平均睡眠 {avg:.1f} 小时，低于 7 小时基线。",
        suggested_action="今晚 23:00 前放下手机；把明早课程前的早起时间往后推 15 分钟。",
        dedupe_key="sleep_short",
    )]


def check_exercise_missing() -> list[ProactiveEvent]:
    """连续 3 天未达到日运动目标（按每日步数目标判断，包含今日）。"""
    from modules.mock_data import get_health
    health = get_health()
    miss_streak = health.get("exercise_target_miss_streak", 0)
    if miss_streak < 3:
        return []
    remaining_steps = max(health["step_goal"] - health["today_steps"], 0)
    return [ProactiveEvent(
        event_type="exercise_missing",
        severity="medium",
        title="运动未达标",
        reason=f"你已经连续 {miss_streak} 天没有达到日运动目标，今天还差 {remaining_steps} 步。",
        suggested_action="今晚去操场走 20 分钟，或者饭后绕校园散一圈，把今天的步数先补到目标线附近。",
        dedupe_key="exercise_missing",
    )]


def check_travel_packing() -> list[ProactiveEvent]:
    """旅行 ≤ 3 天且必带清单未全部勾选。"""
    from modules.mock_data import get_travel_plan
    from modules.persistence import get_packing_checked
    travel = get_travel_plan()
    if not travel:
        return []
    try:
        trip_date = datetime.strptime(travel["date"], "%Y-%m-%d").date()
    except (KeyError, ValueError):
        return []
    days_left = (trip_date - datetime.now().date()).days
    if not 0 <= days_left <= 3:
        return []
    packing = travel.get("packing_list", [])
    checked = set(get_packing_checked())
    unchecked = [p for p in packing if p not in checked]
    if not unchecked:
        return []
    trip_name = travel.get("trip_name", "旅行")
    return [ProactiveEvent(
        event_type="travel_packing",
        severity="high" if days_left <= 1 else "medium",
        title="旅行清单未备齐",
        reason=(
            f"{trip_name} 还有 {days_left} 天出发，但「"
            f"{'、'.join(unchecked[:3])}{'…' if len(unchecked) > 3 else ''}"
            f"」还没勾选。"
        ),
        suggested_action="今晚花 10 分钟把清单物品一项项打钩，确认确实已装进包里。",
        dedupe_key=f"travel_packing:{trip_name}",
    )]


# ---------------------------------------------------------------------------
# 规则注册表
# ---------------------------------------------------------------------------

ALL_RULES: list[Callable[[], list[ProactiveEvent]]] = [
    check_budget_risk,
    check_todo_due,
    check_exam_near,
    check_sleep_short,
    check_exercise_missing,
    check_travel_packing,
]

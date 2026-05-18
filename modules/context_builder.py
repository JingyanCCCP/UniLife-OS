"""
UniLife OS — Context Builder（R1 新增）

职责：
- 构建注入 System Prompt 的上下文摘要（schedule / finance / health / todo / travel / alert）。
- 纯读函数，不写 persistence。
- 所有 `get_*` 查询通过 modules.mock_data 的聚合函数获取（函数内延迟导入以避免循环引用）。

迁移说明：本模块从 modules/mock_data.py 搬运过来。mock_data 继续 re-export
`build_context_summary` 供 app.py 使用，导入路径不变。
"""
from __future__ import annotations

import re
from datetime import datetime


def build_context_summary() -> dict:
    """
    构建对话上下文摘要，返回 6 个字符串字段，供 System Prompt 拼装：
      - schedule_summary：今日课程 + 近期考试
      - finance_summary：本月预算 / 已花 / 剩余 / 日均 / 建议日预算
      - health_summary：步数 / 睡眠 / 喝水 / 运动 / 打卡连续 / 体重
      - todo_summary：待办数量 + 紧急项清单
      - travel_summary：旅行计划概况
      - alert_summary：主动提醒（已剥离 HTML）
    """
    # 延迟导入：打破 mock_data <-> context_builder 的循环。
    from modules.mock_data import (
        get_schedule,  # noqa: F401  (保留给未来扩展，例如周视图摘要)
        get_today_schedule,
        get_finance,
        get_health,
        get_todos,
        get_upcoming_exams,
        get_travel_plan,
        get_alerts,
    )

    finance = get_finance()
    health = get_health()
    todos = get_todos()
    exams = get_upcoming_exams()
    travel = get_travel_plan()
    alerts = get_alerts()

    # ---- 财务摘要 ----
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

    # ---- 健康摘要 ----
    health_summary = (
        f"今日步数 {health['today_steps']}/{health['step_goal']}，"
        f"昨晚睡眠 {health['sleep_hours']}小时（{health['sleep_quality']}），"
        f"本周运动 {health['exercise_this_week']}/{health['exercise_goal']}次，"
        f"喝水 {health['water_cups']}/{health['water_goal']}杯。"
        f"健康记录连续 {health['checkin_streak']}天。"
        f"日运动目标已连续 {health['exercise_target_miss_streak']} 天未达标。"
        f"BMI: {health['bmi']}，体重 {health['weight']}kg。"
    )

    # ---- 待办摘要 ----
    pending = [t for t in todos if not t["done"]]
    urgent = [t for t in pending if "紧急" in t["priority"]]
    todo_summary = (
        f"待办 {len(pending)} 项"
        f"{'，其中 ' + str(len(urgent)) + ' 项紧急！' if urgent else '。'}"
    )
    for t in pending:
        todo_summary += f"\n  - {t['priority']} {t['task']}（截止 {t['deadline']}）"

    # ---- 课程 + 考试摘要 ----
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

    if exams:
        schedule_summary += "\n📝 近期考试：\n"
        for e in exams:
            countdown = "今天！" if e["days_left"] == 0 else f"还有 {e['days_left']} 天"
            schedule_summary += (
                f"  - {e['course']}：{e['date']}（{countdown}）\n"
            )

    # ---- 旅行摘要 ----
    if travel:
        travel_summary = (
            f"计划中的旅行：{travel['trip_name']}，"
            f"日期 {travel['date']}，"
            f"预算 ¥{travel['budget']}，"
            f"同行：{'、'.join(travel['companions'])}。"
        )
    else:
        travel_summary = "暂无旅行计划。"

    # ---- 主动提醒摘要（剥离 HTML 标签，防止 <strong> 漏到 LLM 上下文）----
    if alerts:
        alert_summary = (
            "以下是系统主动扫描出的当前状态风险（已按 12 小时窗口去重，最多 5 条）。"
            "如果与用户当前话题相关，请用自然口吻带到；不要硬推销。\n"
        )
        for a in alerts:
            clean_msg = re.sub(r"<[^>]+>", "", a["message"])
            severity = a.get("severity", "")
            line = f"  - {a['icon']} {a['title']}（{severity}）：{clean_msg}"
            suggestion = a.get("suggested_action", "")
            if suggestion:
                line += f" 建议动作：{suggestion}"
            alert_summary += line + "\n"
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

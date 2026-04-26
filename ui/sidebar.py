from __future__ import annotations

import html as html_mod
import os
from datetime import datetime

import streamlit as st

from config import APP_NAME, DEEPSEEK_API_KEY
from modules.mock_data import (
    get_finance,
    get_health,
    get_today_schedule,
    get_todos,
    get_upcoming_exams,
)
from modules.persistence import (
    add_expense,
    clear_chat_history,
    increment_water,
    log_exercise,
    log_mood,
    log_sleep,
    set_budget,
    set_exercise_goal,
    update_todo_status,
)
from ui.components import ICON_CAP, toast_and_rerun

_EXPENSE_CATEGORIES = ["餐饮", "交通", "购物", "学习用品", "娱乐", "其他"]
_MOOD_OPTIONS = ["😊 开心", "🙂 还行", "😐 一般", "😢 难过", "😫 疲惫"]
_WEEKDAY_MAP = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
_PRIORITY_GRAY = {"🔴": "🔘", "🟡": "🔘", "🟢": "🔘"}


def _api_status() -> None:
    if DEEPSEEK_API_KEY:
        st.success("AI 引擎已连接", icon="✅")
    else:
        st.error("请配置 DeepSeek API Key", icon="⚠️")
        st.info("在项目根目录创建 `.env` 文件，添加：\n`DEEPSEEK_API_KEY=你的密钥`")


def _today_schedule_block() -> None:
    today_courses = get_today_schedule()
    today_wd = _WEEKDAY_MAP[datetime.now().weekday()]
    st.markdown(f"### 今日课程（{today_wd}）")
    if today_courses:
        for course in today_courses:
            badge = "🧪" if course.get("type") == "实验" else "📖"
            st.markdown(
                f"{badge} **{course['course']}**  \n"
                f"⏰ {course['time']}  📍 {course['location']}"
            )
    else:
        st.info("🎉 今天没有课，自由安排！")


def _finance_block() -> None:
    finance = get_finance()
    st.markdown("### 财务快览")

    st.metric(
        label="本月剩余",
        value=f"¥{int(finance['remaining'])}",
        delta=f"-¥{int(finance['spent'])} 已花费",
        delta_color="inverse",
        border=True,
    )
    st.progress(min(finance["budget_usage_pct"] / 100, 1.0))
    st.markdown(
        f'<div class="sidebar-progress-note">预算使用 {finance["budget_usage_pct"]}%</div>',
        unsafe_allow_html=True,
    )
    if finance["budget_usage_pct"] > 80:
        st.warning(
            f"预算紧张！剩余 {finance['days_left_in_month']} 天，"
            f"建议每天 ≤ ¥{int(finance['suggested_daily'])}"
        )

    with st.expander("📋 最近消费流水"):
        for transaction in finance["recent_transactions"][:8]:
            icon = transaction.get("icon", "💳")
            safe_item = html_mod.escape(transaction["item"])
            safe_cat = html_mod.escape(transaction["category"])
            st.markdown(
                f"{icon} <strong>{safe_item}</strong> · ¥{transaction['amount']}  "
                f"<br><small>{transaction['date']} · {safe_cat}</small>",
                unsafe_allow_html=True,
            )

    with st.expander("✏️ 快速记一笔"):
        with st.form("quick_expense", clear_on_submit=True):
            form_cols = st.columns([2, 1])
            with form_cols[0]:
                item = st.text_input("花了什么", placeholder="奶茶")
            with form_cols[1]:
                amount = st.number_input("金额", min_value=0.0, step=0.5, format="%.1f")
            category = st.selectbox("分类", _EXPENSE_CATEGORIES)
            if st.form_submit_button("📝 记录"):
                if not item or amount <= 0:
                    st.warning("请填写消费项目并输入大于 0 的金额")
                else:
                    add_expense(item, amount, category)
                    toast_and_rerun(f"已记录：{item} ¥{amount}（{category}）", "💾")

    with st.expander("⚙️ 预算设置"):
        new_budget = st.number_input(
            "月预算 (元)",
            value=float(finance["monthly_budget"]),
            min_value=100.0,
            step=100.0,
            format="%.0f",
        )
        if st.button("保存预算"):
            set_budget(new_budget)
            toast_and_rerun(f"预算已更新为 ¥{int(new_budget)}", "💰")


def _health_block() -> None:
    health = get_health()
    st.markdown("### 今日健康")

    hcol1, hcol2 = st.columns(2)
    with hcol1:
        st.metric(
            "步数",
            f"{health['today_steps']:,}",
            delta=f"目标 {health['step_goal']:,}",
            border=True,
        )
    with hcol2:
        st.metric("睡眠", f"{health['sleep_hours']}h", delta=health["sleep_quality"], border=True)

    hcol3, hcol4 = st.columns(2)
    with hcol3:
        st.metric("喝水", f"{health['water_cups']}/{health['water_goal']}杯", border=True)
    with hcol4:
        st.metric("运动", f"{health['exercise_this_week']}/{health['exercise_goal']}次", border=True)

    st.caption(f"😊 心情: {health['mood']} | 🔥 连续打卡 {health['checkin_streak']} 天")

    st.markdown("**快速打卡：**")
    btn_cols = st.columns(3)
    with btn_cols[0]:
        if st.button("💧+1杯"):
            increment_water()
            total = get_health()["water_cups"]
            toast_and_rerun(f"喝水 +1，已喝 {total} 杯！", "💧")
    with btn_cols[1]:
        exercise_done = health.get("last_exercise") == datetime.now().strftime("%Y-%m-%d")
        btn_label = "✅ 已打卡" if exercise_done else "🏃运动"
        if st.button(btn_label, disabled=exercise_done):
            log_exercise()
            toast_and_rerun("运动打卡成功，已保存", "🎉")
    with btn_cols[2]:
        selected_mood = st.selectbox(
            "心情",
            _MOOD_OPTIONS,
            label_visibility="collapsed",
            key="mood_select",
        )
        if st.button("📝记心情"):
            log_mood(selected_mood)
            toast_and_rerun(f"{selected_mood} 心情记录成功！", "✨")

    with st.expander("😴 记录睡眠"):
        sleep_input_hours = st.number_input(
            "睡眠时长 (小时)",
            min_value=0.0,
            max_value=24.0,
            value=float(health["sleep_hours"]),
            step=0.5,
            format="%.1f",
            key="sidebar_sleep_hours",
        )
        sleep_input_quality = st.selectbox(
            "睡眠质量",
            ["很好", "良好", "一般", "较差", "很差"],
            index=1,
            key="sidebar_sleep_quality",
        )
        if st.button("💤 保存睡眠", key="sidebar_sleep_btn"):
            log_sleep(sleep_input_hours, sleep_input_quality)
            toast_and_rerun(f"已记录睡眠：{sleep_input_hours}h，质量「{sleep_input_quality}」", "💤")

    with st.expander("🎯 运动目标设置"):
        goal_options = [3, 4, 5, 6, 7]
        current_goal = health["exercise_goal"]
        default_idx = goal_options.index(current_goal) if current_goal in goal_options else 0
        new_goal = st.selectbox("每周运动次数", goal_options, index=default_idx)
        if st.button("保存运动目标"):
            set_exercise_goal(new_goal)
            toast_and_rerun(f"运动目标已更新为每周 {new_goal} 次", "🎯")


def _todo_block() -> None:
    todos = get_todos()
    pending = [todo for todo in todos if not todo["done"]]
    done_todos = [todo for todo in todos if todo["done"]]

    st.markdown(f"### 待办事项 ({len(pending)})")
    st.session_state.todo_done = {todo["id"]: todo["done"] for todo in todos}

    for todo in pending:
        label = f"{todo['priority']} {todo['task']}（{todo['deadline']}）"
        checked = st.checkbox(label, value=False, key=f"todo_{todo['id']}")
        if checked and not st.session_state.todo_done.get(todo["id"]):
            st.session_state.todo_done[todo["id"]] = True
            update_todo_status(todo["id"], True)
            toast_and_rerun(f"完成：{todo['task']}", "🎉")

    if not pending:
        st.info("🎉 所有待办已完成！")

    if done_todos:
        with st.expander(f"✅ 已完成 ({len(done_todos)})", expanded=False):
            for todo in done_todos:
                gray_label = todo["priority"]
                for color, gray in _PRIORITY_GRAY.items():
                    gray_label = gray_label.replace(color, gray)
                label = f"{gray_label} ~~{todo['task']}~~（{todo['deadline']}）"
                unchecked = st.checkbox(label, value=True, key=f"todo_{todo['id']}")
                if not unchecked and st.session_state.todo_done.get(todo["id"], True):
                    st.session_state.todo_done[todo["id"]] = False
                    update_todo_status(todo["id"], False)
                    toast_and_rerun(f"已恢复：{todo['task']}", "🔄")


def _exam_block() -> None:
    exams = get_upcoming_exams()
    if not exams:
        return
    st.markdown("### 考试倒计时")
    for exam in exams:
        countdown = "今天！" if exam["days_left"] == 0 else f"{exam['days_left']} 天后"
        msg = f"**{exam['course']}** · {countdown}\n📍 {exam['location']}"
        if exam["days_left"] == 0:
            st.error(f"🔴 {msg}")
        elif exam["days_left"] <= 3:
            st.error(f"🔴 {msg}！")
        elif exam["days_left"] <= 7:
            st.warning(f"🟡 {msg}")
        else:
            st.info(f"🔵 {msg}")


def _clear_chat_block() -> None:
    if st.button("🔄 清除对话", width="stretch"):
        st.session_state.messages = []
        clear_chat_history()
        toast_and_rerun("对话已清除", "🔄")


def _demo_reset_block() -> None:
    if os.getenv("APP_MODE", "").lower() != "demo":
        return
    st.caption("🧪 DEMO 模式工具")
    if st.button("🧹 一键重置 demo 数据", width="stretch"):
        from tools.reset_demo import reset

        reset()
        toast_and_rerun("demo 数据已重置到 seed 态", "🧹")


def _dev_info_block() -> None:
    if os.getenv("APP_MODE", "").lower() != "demo":
        return
    with st.expander("🧪 开发者信息（observability）", expanded=False):
        from agent.executor import recent_tool_calls
        from proactive import events as proactive_events

        st.caption("最近 5 次工具调用（按时间倒序）")
        calls = list(reversed(recent_tool_calls()))
        if calls:
            for call in calls:
                ok_tag = "✅" if call.get("ok") else "⚠️"
                summary = str(call.get("result", ""))[:80]
                st.code(
                    f"{ok_tag} [{call['at']}] {call['name']}({call['args']})\n  → {summary}",
                    language=None,
                )
        else:
            st.caption("(尚无调用)")

        st.caption("最近 3 条主动事件（含已读）")
        events = proactive_events.list_all()[:3]
        if events:
            for event in events:
                st.code(
                    f"[{event.severity}] {event.title} ({event.dedupe_key})\n  reason: {event.reason}",
                    language=None,
                )
        else:
            st.caption("(尚无事件)")


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand">'
            f'<span class="sidebar-brand-icon">{ICON_CAP}</span>'
            f'<div><div class="sidebar-brand-title">{APP_NAME}</div>'
            '<div class="sidebar-brand-subtitle">你的大学生活智能操作系统</div></div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.divider()
        _api_status()
        st.divider()
        _today_schedule_block()
        st.divider()
        _finance_block()
        st.divider()
        _health_block()
        st.divider()
        _todo_block()
        st.divider()
        _exam_block()
        st.divider()
        _clear_chat_block()
        _demo_reset_block()
        _dev_info_block()

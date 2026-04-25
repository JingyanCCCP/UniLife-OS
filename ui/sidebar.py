"""
UniLife OS — 侧边栏视图（R4 新增）

保持原 735 行 app.py 中 `render_sidebar()` 的完整交互逻辑不变，仅在末尾新增
R4-T3「一键重置 demo 数据」按钮（仅当环境变量 APP_MODE=demo 时显示）。
"""
from __future__ import annotations

import html as html_mod
import os
from datetime import datetime

import streamlit as st

from config import APP_NAME, APP_ICON, DEEPSEEK_API_KEY
from modules.mock_data import (
    get_today_schedule, get_finance, get_health, get_todos,
    get_upcoming_exams,
)
from modules.persistence import (
    update_todo_status, add_expense, increment_water,
    log_exercise, log_mood,
    clear_chat_history, set_budget, set_exercise_goal,
)

from ui.components import toast_and_rerun


# ---------------------------------------------------------------------------
# 各模块卡片（仅在 render_sidebar 内部的 with st.sidebar 上下文中调用）
# ---------------------------------------------------------------------------

def _api_status() -> None:
    if DEEPSEEK_API_KEY:
        st.success("🟢 AI 引擎已连接", icon="✅")
    else:
        st.error("🔴 请配置 DeepSeek API Key", icon="⚠️")
        st.info("在项目根目录创建 `.env` 文件，添加：\n`DEEPSEEK_API_KEY=你的密钥`")


def _today_schedule_block() -> None:
    today_courses = get_today_schedule()
    weekday_map = {0: "周一", 1: "周二", 2: "周三", 3: "周四",
                   4: "周五", 5: "周六", 6: "周日"}
    today_wd = weekday_map[datetime.now().weekday()]

    st.markdown(f"### 📅 今日课程（{today_wd}）")
    if today_courses:
        for c in today_courses:
            type_badge = "🧪" if c.get("type") == "实验" else "📖"
            st.markdown(
                f"{type_badge} **{c['course']}**  \n"
                f"⏰ {c['time']}  📍 {c['location']}"
            )
    else:
        st.info("🎉 今天没有课，自由安排！")


def _finance_block() -> None:
    finance = get_finance()
    st.markdown("### 💰 财务快览")

    st.metric(
        label="本月剩余",
        value=f"¥{int(finance['remaining'])}",
        delta=f"-¥{int(finance['spent'])} 已花费",
        delta_color="inverse",
    )
    st.progress(
        min(finance["budget_usage_pct"] / 100, 1.0),
        text=f"预算使用 {finance['budget_usage_pct']}%",
    )
    if finance["budget_usage_pct"] > 80:
        st.warning(
            f"⚠️ 预算紧张！剩余 {finance['days_left_in_month']} 天，"
            f"建议每天 ≤ ¥{int(finance['suggested_daily'])}"
        )

    with st.expander("📋 最近消费流水"):
        for t in finance["recent_transactions"][:8]:
            t_icon = t.get("icon", "💳")
            safe_item = html_mod.escape(t["item"])
            safe_cat = html_mod.escape(t["category"])
            st.markdown(
                f"{t_icon} <strong>{safe_item}</strong> — ¥{t['amount']}  "
                f"<br><small>{t['date']} · {safe_cat}</small>",
                unsafe_allow_html=True,
            )

    with st.expander("✏️ 快速记一笔"):
        with st.form("quick_expense", clear_on_submit=True):
            form_cols = st.columns([2, 1])
            with form_cols[0]:
                item = st.text_input("花了什么", placeholder="奶茶")
            with form_cols[1]:
                amount = st.number_input("金额", min_value=0.0, step=0.5, format="%.1f")
            category = st.selectbox(
                "分类",
                ["餐饮", "交通", "购物", "学习用品", "娱乐", "其他"],
            )
            submitted = st.form_submit_button("📝 记录")
            if submitted:
                if not item or amount <= 0:
                    st.warning("⚠️ 请填写消费项目并输入大于 0 的金额")
                else:
                    add_expense(item, amount, category)
                    toast_and_rerun(
                        f"✅ 已记录：{item} ¥{amount}（{category}）", "💾"
                    )

    with st.expander("⚙️ 预算设置"):
        new_budget = st.number_input(
            "月预算 (元)",
            value=float(finance["monthly_budget"]),
            min_value=100.0, step=100.0, format="%.0f",
        )
        if st.button("保存预算"):
            set_budget(new_budget)
            toast_and_rerun(f"预算已更新为 ¥{int(new_budget)}", "💰")


def _health_block() -> None:
    health = get_health()
    st.markdown("### 🏥 今日健康")

    hcol1, hcol2 = st.columns(2)
    with hcol1:
        st.metric("步数", f"{health['today_steps']:,}",
                  delta=f"目标 {health['step_goal']:,}")
    with hcol2:
        st.metric("睡眠", f"{health['sleep_hours']}h", delta=health["sleep_quality"])

    hcol3, hcol4 = st.columns(2)
    with hcol3:
        st.metric("喝水", f"{health['water_cups']}/{health['water_goal']}杯")
    with hcol4:
        st.metric("运动", f"{health['exercise_this_week']}/{health['exercise_goal']}次")

    st.caption(
        f"😊 心情: {health['mood']} | 🔥 连续打卡 {health['checkin_streak']} 天"
    )

    st.markdown("**快速打卡：**")
    btn_cols = st.columns(3)
    with btn_cols[0]:
        if st.button("💧+1杯"):
            increment_water()
            total = get_health()["water_cups"]
            toast_and_rerun(f"💧 喝水 +1，已喝 {total} 杯！", "💧")
    with btn_cols[1]:
        exercise_done = (
            health.get("last_exercise") == datetime.now().strftime("%Y-%m-%d")
        )
        btn_label = "✅ 已打卡" if exercise_done else "🏃运动"
        if st.button(btn_label, disabled=exercise_done):
            log_exercise()
            toast_and_rerun("🏃 运动打卡成功！已保存", "🎉")
    with btn_cols[2]:
        mood_options = ["😊 开心", "🙂 还行", "😐 一般", "😢 难过", "😫 疲惫"]
        selected_mood = st.selectbox(
            "心情", mood_options, label_visibility="collapsed", key="mood_select",
        )
        if st.button("📝记心情"):
            log_mood(selected_mood)
            toast_and_rerun(f"{selected_mood} 心情记录成功！", "✨")

    with st.expander("🎯 运动目标设置"):
        goal_options = [3, 4, 5, 6, 7]
        current_goal = health["exercise_goal"]
        default_idx = (
            goal_options.index(current_goal) if current_goal in goal_options else 0
        )
        new_goal = st.selectbox("每周运动次数", goal_options, index=default_idx)
        if st.button("保存运动目标"):
            set_exercise_goal(new_goal)
            toast_and_rerun(f"运动目标已更新为每周 {new_goal} 次", "🎯")


def _todo_block() -> None:
    todos = get_todos()
    pending = [t for t in todos if not t["done"]]
    done_todos = [t for t in todos if t["done"]]

    st.markdown(f"### 📝 待办事项 ({len(pending)})")

    # 每次渲染同步最新状态（Agent 新增/修改的待办也能反映）
    st.session_state.todo_done = {t["id"]: t["done"] for t in todos}

    for t in pending:
        label = f"{t['priority']} {t['task']}（{t['deadline']}）"
        checked = st.checkbox(label, value=False, key=f"todo_{t['id']}")
        if checked and not st.session_state.todo_done.get(t["id"]):
            st.session_state.todo_done[t["id"]] = True
            update_todo_status(t["id"], True)
            toast_and_rerun(f"✅ 完成：{t['task']}", "🎉")

    if not pending:
        st.info("🎉 所有待办已完成！")

    if done_todos:
        gray_priority = {"🔴": "🔘", "🟡": "🔘", "🟢": "🔘"}
        with st.expander(f"✅ 已完成 ({len(done_todos)})", expanded=False):
            for t in done_todos:
                gray_label = t["priority"]
                for color, gray in gray_priority.items():
                    gray_label = gray_label.replace(color, gray)
                label = f"{gray_label} ~~{t['task']}~~（{t['deadline']}）"
                unchecked = st.checkbox(label, value=True, key=f"todo_{t['id']}")
                if not unchecked and st.session_state.todo_done.get(t["id"], True):
                    st.session_state.todo_done[t["id"]] = False
                    update_todo_status(t["id"], False)
                    toast_and_rerun(f"↩️ 已恢复：{t['task']}", "🔄")


def _exam_block() -> None:
    exams = get_upcoming_exams()
    if not exams:
        return
    st.markdown("### 🎯 考试倒计时")
    for e in exams:
        countdown = "今天！" if e["days_left"] == 0 else f"{e['days_left']} 天后"
        msg = f"**{e['course']}** — {countdown}\n📍 {e['location']}"
        if e["days_left"] == 0:
            st.error(f"🔴 {msg}")
        elif e["days_left"] <= 3:
            st.error(f"🔴 {msg}！")
        elif e["days_left"] <= 7:
            st.warning(f"🟡 {msg}")
        else:
            st.info(f"🔵 {msg}")


def _clear_chat_block() -> None:
    if st.button("🔄 清除对话", use_container_width=True):
        st.session_state.messages = []
        clear_chat_history()
        toast_and_rerun("对话已清除", "🔄")


def _demo_reset_block() -> None:
    """R4-T3：仅当 APP_MODE=demo 时显示的演示重置按钮。"""
    if os.getenv("APP_MODE", "").lower() != "demo":
        return
    st.caption("🧪 DEMO 模式工具")
    if st.button("🧹 一键重置 demo 数据", use_container_width=True):
        from tools.reset_demo import reset  # 延迟导入，非演示模式不加载
        reset()
        toast_and_rerun("demo 数据已重置到 seed 态", "🧹")


def _dev_info_block() -> None:
    """R5-T3：开发者信息折叠区，仅 APP_MODE=demo 时显示。

    展示最近 5 次工具调用（来自 agent.executor）和最近 3 条主动事件（来自 proactive）。
    """
    if os.getenv("APP_MODE", "").lower() != "demo":
        return
    with st.expander("🧪 开发者信息（observability）", expanded=False):
        from agent.executor import recent_tool_calls
        from proactive import events as proactive_events

        st.caption("最近 5 次工具调用（按时间倒序）")
        calls = list(reversed(recent_tool_calls()))
        if calls:
            for c in calls:
                ok_tag = "✅" if c.get("ok") else "⚠️"
                summary = str(c.get("result", ""))[:80]
                st.code(
                    f"{ok_tag} [{c['at']}] {c['name']}({c['args']})\n  → {summary}",
                    language=None,
                )
        else:
            st.caption("(尚无调用)")

        st.caption("最近 3 条主动事件（含已读）")
        events = proactive_events.list_all()[:3]
        if events:
            for e in events:
                st.code(
                    f"[{e.severity}] {e.title} ({e.dedupe_key})\n  reason: {e.reason}",
                    language=None,
                )
        else:
            st.caption("(尚无事件)")


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(f"## {APP_ICON} {APP_NAME}")
        st.caption("你的大学生活智能操作系统")
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

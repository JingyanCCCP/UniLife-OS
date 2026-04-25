from __future__ import annotations

import html as html_mod

import streamlit as st

from config import DEEPSEEK_API_KEY
from modules.mock_data import (
    build_context_summary,
    get_alerts,
    get_finance,
    get_health,
    get_today_schedule,
    get_todos,
)


def toast_and_rerun(msg: str, icon: str = "✅") -> None:
    # st.toast 会被 st.rerun 清除，先暂存到 session_state。
    st.session_state._pending_toast = (msg, icon)
    st.rerun()


def apply_pending_toast() -> None:
    if "_pending_toast" in st.session_state:
        msg, icon = st.session_state._pending_toast
        st.toast(msg, icon=icon)
        del st.session_state._pending_toast


def alert_card_html(severity: str, icon: str, title: str, message: str) -> str:
    safe_icon = html_mod.escape(icon)
    safe_title = html_mod.escape(title)
    safe_message = html_mod.escape(message)
    return (
        f'<div class="alert-card-{severity}">'
        f'<span class="alert-card-icon">{safe_icon}</span>'
        f'<div><h4>{safe_title}</h4>'
        f'<p>{safe_message}</p></div>'
        f'</div>'
    )


def travel_item_html(icon: str, time_str: str, activity: str,
                     location: str, cost_str: str) -> str:
    safe_icon = html_mod.escape(icon)
    safe_time = html_mod.escape(time_str)
    safe_activity = html_mod.escape(activity)
    safe_location = html_mod.escape(location)
    safe_cost = html_mod.escape(cost_str)
    return (
        f'<div class="travel-item">'
        f'<div class="travel-time">{safe_icon} {safe_time}</div>'
        f'<div class="travel-main">{safe_activity}</div>'
        f'<div class="travel-meta">📍 {safe_location} · 💵 {safe_cost}</div>'
        f'</div>'
    )


def _metric_tile(label: str, value: str, note: str = "") -> str:
    safe_label = html_mod.escape(label)
    safe_value = html_mod.escape(value)
    safe_note = html_mod.escape(note)
    return (
        '<div class="hero-metric">'
        f'<span>{safe_label}</span>'
        f'<strong>{safe_value}</strong>'
        f'<small>{safe_note}</small>'
        '</div>'
    )


def render_header() -> None:
    finance = get_finance()
    health = get_health()
    pending_count = len([t for t in get_todos() if not t["done"]])
    course_count = len(get_today_schedule())
    ai_state = "AI 在线" if DEEPSEEK_API_KEY else "离线模式"
    budget_usage = f"{finance['budget_usage_pct']}%"
    exercise = f"{health['exercise_this_week']}/{health['exercise_goal']}"

    metrics = "".join(
        [
            _metric_tile("今日课程", f"{course_count} 节", "排程已同步"),
            _metric_tile("待办压力", f"{pending_count} 项", "优先级待处理"),
            _metric_tile("预算使用", budget_usage, "本月消费进度"),
            _metric_tile("运动周频", exercise, "本周目标"),
        ]
    )
    status_class = "is-online" if DEEPSEEK_API_KEY else "is-offline"
    st.markdown(
        '<section class="main-header">'
        '<div class="hero-copy">'
        '<div class="hero-kicker">Campus life operating system</div>'
        '<h1>UniLife OS</h1>'
        '<p>把课程、消费、健康、待办和出行放进一个清晰的学生生活控制台。需要操作时，直接和 AI 对话。</p>'
        f'<div class="hero-status {status_class}"><span></span>{ai_state}</div>'
        '</div>'
        f'<div class="hero-metrics">{metrics}</div>'
        '</section>',
        unsafe_allow_html=True,
    )


_MAX_VISIBLE_ALERTS = 3


def _alert_card_with_action(alert: dict, index: int) -> None:
    severity = alert.get("severity", "low")
    message = alert.get("message", "")
    suggestion = alert.get("suggested_action", "")
    html = alert_card_html(
        severity,
        alert.get("icon", "🔔"),
        alert.get("title", ""),
        message,
    )
    st.markdown(html, unsafe_allow_html=True)
    if suggestion:
        st.caption(f"建议：{suggestion}")
    key = alert.get("dedupe_key") or f"alert_{index}"
    if st.button("标为已读", key=f"ack_{key}_{index}", width="stretch"):
        from proactive import mark_read
        mark_read(key)
        toast_and_rerun("已标记为已读", "📭")


def render_alerts() -> None:
    alerts = get_alerts()
    if not alerts:
        return
    st.markdown(
        '<div class="section-heading">'
        '<span>Proactive care</span>'
        '<h2>主动关怀</h2>'
        '</div>',
        unsafe_allow_html=True,
    )
    top = alerts[:_MAX_VISIBLE_ALERTS]
    cols = st.columns(len(top))
    for i, alert in enumerate(top):
        with cols[i]:
            _alert_card_with_action(alert, i)
    if len(alerts) > _MAX_VISIBLE_ALERTS:
        rest = alerts[_MAX_VISIBLE_ALERTS:]
        with st.expander(f"查看其余 {len(rest)} 条"):
            for j, alert in enumerate(rest, start=_MAX_VISIBLE_ALERTS):
                _alert_card_with_action(alert, j)


def generate_welcome() -> str:
    context = build_context_summary()
    alerts = get_alerts()

    lines = [
        "欢迎回来，我是 **UniLife**，你的校园生活助手。\n",
        "今天的关键状态：\n",
    ]

    lines.append("📅 **课程** · " + context["schedule_summary"].split("\n")[0])
    lines.append("💰 **财务** · " + context["finance_summary"].split("\n")[0])
    lines.append("📝 **待办** · " + context["todo_summary"].split("\n")[0])
    health_parts = context["health_summary"].split("。")
    lines.append("🏥 **健康** · " + (health_parts[0] + "。" if health_parts[0] else ""))

    if alerts:
        lines.append(
            f"\n需要关注：当前有 {len(alerts)} 条提醒，"
            f"最重要的是 {alerts[0]['icon']} {alerts[0]['title']}。"
        )

    lines.append("\n你可以直接说：今天有什么课、帮我记一笔奶茶 18 元、分析这个月花销。")
    return "\n".join(lines)

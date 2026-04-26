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


ICON_SPARKLES = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" '
    'viewBox="0 0 24 24" aria-hidden="true">'
    '<g fill="none" stroke="currentColor" stroke-linecap="round" '
    'stroke-linejoin="round" stroke-width="2">'
    '<path fill="currentColor" d="M11.017 2.814a1 1 0 0 1 1.966 0'
    'l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 '
    '0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558'
    'a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594'
    'l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 '
    '1.594-1.594zM20 2v4m2-2h-4"/>'
    '<circle fill="currentColor" cx="4" cy="20" r="2"/></g></svg>'
)
ICON_BELL = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" '
    'viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="none" stroke="currentColor" stroke-linecap="round" '
    'stroke-linejoin="round" stroke-width="2" d="M10.268 21a2 2 0 0 0 '
    '3.464 0M22 8c0-2.3-.8-4.3-2-6M3.262 15.326A1 1 0 0 0 '
    '4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 '
    '8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326M4 2C2.8 '
    '3.7 2 5.7 2 8"/></svg>'
)
ICON_CHART = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" '
    'viewBox="0 0 24 24" aria-hidden="true">'
    '<g fill="none" stroke="currentColor" stroke-linecap="round" '
    'stroke-linejoin="round" stroke-width="2">'
    '<path fill="currentColor" d="M3 3v16a2 2 0 0 0 2 2h16"/>'
    '<path fill="currentColor" d="m19 9l-5 5l-4-4l-3 3"/></g></svg>'
)
ICON_CAP = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" '
    'viewBox="0 0 24 24" aria-hidden="true">'
    '<g fill="none" stroke="currentColor" stroke-linecap="round" '
    'stroke-linejoin="round" stroke-width="2">'
    '<path fill="currentColor" d="M21.42 10.922a1 1 0 0 0-.019-1.838'
    'L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 '
    '1.832l8.57 3.908a2 2 0 0 0 1.66 0zM22 10v6"/>'
    '<path fill="currentColor" d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>'
    '</g></svg>'
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


def section_heading_html(
    eyebrow: str,
    title: str,
    icon_svg: str = "",
    class_name: str = "",
) -> str:
    safe_eyebrow = html_mod.escape(eyebrow)
    safe_title = html_mod.escape(title)
    safe_class = html_mod.escape(class_name)
    icon = f'<span class="section-icon">{icon_svg}</span>' if icon_svg else ""
    return (
        f'<div class="section-heading {safe_class}">'
        '<div>'
        f'<span class="section-eyebrow">{icon}{safe_eyebrow}</span>'
        f'<div class="section-title">{safe_title}</div>'
        '</div>'
        '</div>'
    )


def render_section_heading(
    eyebrow: str,
    title: str,
    icon_svg: str = "",
    class_name: str = "",
) -> None:
    st.markdown(
        section_heading_html(eyebrow, title, icon_svg, class_name),
        unsafe_allow_html=True,
    )


def alert_card_html(severity: str, icon: str, title: str, message: str) -> str:
    safe_severity = html_mod.escape(severity if severity in {"high", "medium", "low"} else "low")
    safe_icon = html_mod.escape(icon or "🔔")
    safe_title = html_mod.escape(title)
    safe_message = html_mod.escape(message)
    severity_label = {"high": "紧急", "medium": "警告", "low": "提醒"}.get(
        safe_severity, "提醒"
    )
    return (
        f'<div class="alert-card alert-card-{safe_severity}">'
        '<div class="alert-card-head">'
        f'<span class="alert-severity-badge">{severity_label}</span>'
        '</div>'
        '<div class="alert-card-content">'
        f'<span class="alert-card-icon">{safe_icon}</span>'
        '<div class="alert-card-body">'
        f'<h4>{safe_title}</h4>'
        f'<p>{safe_message}</p>'
        '</div>'
        '</div>'
        '</div>'
    )


def travel_item_html(
    icon: str,
    time_str: str,
    activity: str,
    location: str,
    cost_str: str,
) -> str:
    safe_icon = html_mod.escape(icon)
    safe_time = html_mod.escape(time_str)
    safe_activity = html_mod.escape(activity)
    safe_location = html_mod.escape(location)
    safe_cost = html_mod.escape(cost_str)
    return (
        '<div class="travel-item">'
        f'<div class="travel-time">{safe_icon} {safe_time}</div>'
        f'<div class="travel-main">{safe_activity}</div>'
        f'<div class="travel-meta">📍 {safe_location} · 💵 {safe_cost}</div>'
        '</div>'
    )


def _hero_metrics() -> list[tuple[str, str, str]]:
    today_classes = len(get_today_schedule())
    pending_todos = sum(1 for t in get_todos() if not t["done"])
    finance = get_finance()
    health = get_health()
    return [
        ("今日课程", f"{today_classes} 节", "排程已同步"),
        ("待办压力", f"{pending_todos} 项", "优先级待处理"),
        ("预算使用", f"{int(finance['budget_usage_pct'])}%", f"剩 ¥{int(finance['remaining'])}"),
        ("今日喝水", f"{health['water_cups']}/{health['water_goal']}", f"目标 {health['water_goal']} 杯"),
    ]


def _hero_metric_tile(label: str, value: str, note: str) -> str:
    safe_label = html_mod.escape(label)
    safe_value = html_mod.escape(value)
    safe_note = html_mod.escape(note)
    return (
        '<div class="hero-metric">'
        f'<span class="hero-metric-label">{safe_label}</span>'
        f'<strong class="hero-metric-value">{safe_value}</strong>'
        f'<small class="hero-metric-note">{safe_note}</small>'
        '</div>'
    )


def render_header() -> None:
    metrics_html = "".join(
        _hero_metric_tile(label, value, note)
        for label, value, note in _hero_metrics()
    )
    ai_state = "AI 在线" if DEEPSEEK_API_KEY else "离线模式"
    status_class = "is-online" if DEEPSEEK_API_KEY else "is-offline"
    st.markdown(
        '<section class="main-header">'
        '<div class="hero-copy">'
        f'<span class="hero-eyebrow"><span class="hero-icon">{ICON_CAP}</span>'
        'Campus Life Operating System</span>'
        '<div class="hero-title">UniLife OS</div>'
        '<p class="hero-desc">把课程、消费、健康、待办和出行整理成一个清晰的学生生活操控台。需要操作时，直接和 AI 对话。</p>'
        f'<div class="hero-status {status_class}">'
        '<span class="hero-status-dot"></span>'
        f'{html_mod.escape(ai_state)}'
        '</div>'
        '</div>'
        f'<div class="hero-metrics">{metrics_html}</div>'
        '</section>',
        unsafe_allow_html=True,
    )


_MAX_VISIBLE_ALERTS = 3


def _event_to_alert(event) -> dict:
    icon_by_type = {
        "budget_risk": "💰",
        "todo_due": "🔥",
        "exam_near": "📝",
        "sleep_short": "😴",
        "exercise_missing": "🏃",
        "travel_packing": "🧳",
    }
    return {
        "type": event.event_type,
        "icon": icon_by_type.get(event.event_type, "🔔"),
        "title": event.title,
        "message": event.reason,
        "suggested_action": event.suggested_action,
        "dedupe_key": event.dedupe_key,
        "severity": event.severity,
    }


def _fallback_active_alerts(limit: int = 5) -> list[dict]:
    """首页视觉区兜底：未读为空时仍展示当前活跃事件，避免主动关怀整块消失。"""
    from proactive import engine, events

    engine.scan_safely()
    return [_event_to_alert(event) for event in events.list_all()[:limit]]


def _alert_card_with_action(alert: dict, index: int) -> None:
    severity = alert.get("severity", "low")
    message = alert.get("message", "")
    suggestion = alert.get("suggested_action", "")
    card = alert_card_html(severity, alert.get("icon", "🔔"), alert.get("title", ""), message)
    st.markdown(card, unsafe_allow_html=True)

    safe_suggestion = html_mod.escape(suggestion)
    if safe_suggestion:
        suggestion_html = f'<div class="alert-suggestion">👉 {safe_suggestion}</div>'
    else:
        suggestion_html = '<div class="alert-suggestion is-empty">&nbsp;</div>'
    st.markdown(suggestion_html, unsafe_allow_html=True)

    key = alert.get("dedupe_key") or f"alert_{index}"
    if st.button("标为已读", key=f"ack_{key}_{index}", width="stretch"):
        from proactive import mark_read

        mark_read(key)
        toast_and_rerun("已标记为已读", "📭")


def render_alerts() -> None:
    alerts = get_alerts()
    if not alerts:
        alerts = _fallback_active_alerts()
    if not alerts:
        return

    st.markdown(
        '<div class="proactive-heading">'
        '<div class="proactive-heading-left">'
        f'<span class="section-icon">{ICON_BELL}</span>'
        '<span>Proactive care</span>'
        '</div>'
        '<div class="proactive-heading-title">主动关怀</div>'
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
        "今天先看这几件事：\n",
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

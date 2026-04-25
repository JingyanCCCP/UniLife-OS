"""
UniLife OS — UI 公用组件（R4 新增）

职责：header / 主动关怀卡片 / 旅行条目 HTML / toast 延迟显示 / 欢迎消息。

主动关怀卡片（render_alerts）是 R3 引擎与 UI 的汇合点：
- 每次渲染先调用 `proactive.engine.scan_safely()` 刷新事件
- 读取 `list_unread(limit=5)`，顶部 3 条以卡片展示（每条含 reason + suggested_action + 已读按钮）
- 其余 2 条折叠
"""
from __future__ import annotations

import streamlit as st

from modules.mock_data import (
    get_alerts, build_context_summary,
)


# ---------------------------------------------------------------------------
# Toast 延迟显示
# ---------------------------------------------------------------------------

def toast_and_rerun(msg: str, icon: str = "✅") -> None:
    """暂存 toast 消息到 session_state，rerun 后在 main() 顶部显示。

    Streamlit 原生 st.toast 会被紧跟的 st.rerun 清除，所以统一用这个 helper。
    """
    st.session_state._pending_toast = (msg, icon)
    st.rerun()


def apply_pending_toast() -> None:
    """如果 session_state 里有暂存的 toast，显示后清空。main() 顶部调用。"""
    if "_pending_toast" in st.session_state:
        msg, icon = st.session_state._pending_toast
        st.toast(msg, icon=icon)
        del st.session_state._pending_toast


# ---------------------------------------------------------------------------
# 卡片 HTML 片段（保留 unsafe_allow_html 渲染路径）
# ---------------------------------------------------------------------------

def alert_card_html(severity: str, icon: str, title: str, message: str) -> str:
    """主动关怀卡片 HTML（使用 alert-card-{severity} 类）。"""
    return (
        f'<div class="alert-card-{severity}">'
        f'<h4>{icon} {title}</h4>'
        f'<p>{message}</p>'
        f'</div>'
    )


def travel_item_html(icon: str, time_str: str, activity: str,
                     location: str, cost_str: str) -> str:
    """旅行行程条目 HTML。"""
    return (
        f'<div class="travel-item">'
        f'<strong>{icon} {time_str}</strong> — {activity}<br>'
        f'<small>📍 {location} 💰 {cost_str}</small>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

def render_header() -> None:
    """主页面头部紫色 banner（Phase 6.3 紧凑布局）。"""
    st.markdown(
        '<div class="main-header">'
        '<h1>🎓 UniLife OS</h1>'
        '<p>Hi！我是你的大学生活智能助手，课程、消费、健康、出行——我都能帮你搞定 ✨</p>'
        '</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# 主动关怀事件卡片（R4 新：含已读按钮）
# ---------------------------------------------------------------------------

_MAX_VISIBLE_ALERTS = 3


def _alert_card_with_action(alert: dict, index: int) -> None:
    """单张卡片：HTML 区块 + 已读按钮。"""
    severity = alert.get("severity", "low")
    message = alert.get("message", "")
    suggestion = alert.get("suggested_action", "")
    html = alert_card_html(severity, alert.get("icon", "🔔"),
                           alert.get("title", ""), message)
    st.markdown(html, unsafe_allow_html=True)
    if suggestion:
        st.caption(f"👉 {suggestion}")
    key = alert.get("dedupe_key") or f"alert_{index}"
    if st.button("标为已读", key=f"ack_{key}_{index}",
                 use_container_width=True):
        from proactive import mark_read
        mark_read(key)
        toast_and_rerun("已标记为已读", "📭")


def render_alerts() -> None:
    """今日快报：主动关怀事件卡片（top 3 + 折叠其余）。"""
    alerts = get_alerts()
    if not alerts:
        return

    st.markdown("### 🔔 主动关怀事件（系统主动扫描）")
    top = alerts[:_MAX_VISIBLE_ALERTS]
    cols = st.columns(len(top))
    for i, alert in enumerate(top):
        with cols[i]:
            _alert_card_with_action(alert, i)

    if len(alerts) > _MAX_VISIBLE_ALERTS:
        rest = alerts[_MAX_VISIBLE_ALERTS:]
        with st.expander(f"📋 查看其余 {len(rest)} 条"):
            for j, alert in enumerate(rest, start=_MAX_VISIBLE_ALERTS):
                _alert_card_with_action(alert, j)


# ---------------------------------------------------------------------------
# 欢迎消息
# ---------------------------------------------------------------------------

def generate_welcome() -> str:
    """首次进入 AI 对话 Tab 的欢迎语。基于当前状态快照生成。"""
    context = build_context_summary()
    alerts = get_alerts()

    lines = [
        "Hey！欢迎回来 👋 我是 **UniLife**，你的校园生活小助手~\n",
        "这是你今天的快报：\n",
    ]

    schedule_first = context["schedule_summary"].split("\n")[0]
    finance_first = context["finance_summary"].split("\n")[0]
    todo_first = context["todo_summary"].split("\n")[0]
    health_parts = context["health_summary"].split("。")
    health_first = health_parts[0] + "。" if health_parts[0] else ""

    lines.append("📅 **课程** — " + schedule_first)
    lines.append("💰 **财务** — " + finance_first)
    lines.append("📝 **待办** — " + todo_first)
    lines.append("🏥 **健康** — " + health_first)

    if alerts:
        lines.append(
            f"\n⚡ **需要关注** — 有 {len(alerts)} 条提醒，"
            f"最重要的是：{alerts[0]['icon']} {alerts[0]['title']}"
        )

    lines.append("\n有什么我能帮你的？随时聊！💬")
    lines.append("\n💡 *试试问我：「我今天有什么课？」「帮我记一笔：奶茶 18 元」「分析一下这个月花销」*")
    return "\n".join(lines)

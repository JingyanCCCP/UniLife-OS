"""
UniLife OS — UI 公用组件（R4 起；V3.4 仿 jj66-ui-refactor 分支扩层）

职责：header / 主动关怀卡片 / 旅行条目 HTML / toast 延迟显示 / 欢迎消息。

V3.4 视觉调整：
- header 输出双卡 hero 结构（外卡 .main-header 包 .hero-copy + .hero-metrics），AI 状态走右下角胶囊
- hero metric tile 从 2 行 (value/label) 改 3 行 (label/value/note)，note 给"目标 X" / "已花费 ¥Y" 类轻量解释
- alert_card_html 复活 icon 参数，渲染左侧 2.1rem 圆形 badge（功能性 marker，不违反"标题去 emoji"红线）
- render_alerts 用 .section-heading（eyebrow + h2）替代单行 ### markdown
- travel_item_html 改 3 行 (time / activity / location · cost) 配合新拟态卡的 padding / clip-path 缺角

主动关怀卡片（render_alerts）是 R3 引擎与 UI 的汇合点：
- 每次渲染先调用 `proactive.engine.scan_safely()` 刷新事件
- 读取 `list_unread(limit=5)`，顶部 3 条以卡片展示（每条含 reason + suggested_action + 已读按钮）
- 其余 2 条折叠
"""
from __future__ import annotations

import html as html_mod

import streamlit as st

from config import DEEPSEEK_API_KEY
from modules.mock_data import (
    get_alerts, build_context_summary,
    get_today_schedule, get_todos, get_finance, get_health,
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
    """主动关怀卡片 HTML（V3.4：grid icon badge + h4 + p）。

    icon 走左侧圆形 badge（.alert-card-icon），是功能性 marker；
    h4 / p 仍然不带 emoji，保持"标题去 emoji"红线。
    """
    safe_icon = html_mod.escape(icon or "🔔")
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
    """旅行行程条目 HTML（V3.4：3 行结构 + clip-path 缺角靠 CSS）。"""
    safe_icon = html_mod.escape(icon)
    safe_time = html_mod.escape(time_str)
    safe_activity = html_mod.escape(activity)
    safe_location = html_mod.escape(location)
    safe_cost = html_mod.escape(cost_str)
    return (
        f'<div class="travel-item">'
        f'<strong>{safe_icon} {safe_time}</strong> — {safe_activity}<br>'
        f'<small>📍 {safe_location} 💰 {safe_cost}</small>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Header（V3.4：外卡 + 双内卡 + AI 状态胶囊 + 3-line metric tile）
# ---------------------------------------------------------------------------

def _hero_metrics() -> list[tuple[str, str, str]]:
    """首屏 4-up 数字面板。V3.4 改 3-tuple (label, value, note)，note 给数字旁的 caption。"""
    today_classes = len(get_today_schedule())
    pending_todos = sum(1 for t in get_todos() if not t["done"])
    finance = get_finance()
    health = get_health()
    return [
        ("今日课程", str(today_classes), "排程已同步"),
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
    """主页面头部（V3.4：外卡 .main-header 包 .hero-copy + .hero-metrics 双内卡）。"""
    metrics_html = "".join(
        _hero_metric_tile(label, value, note)
        for label, value, note in _hero_metrics()
    )
    ai_state = "AI 在线" if DEEPSEEK_API_KEY else "离线模式"
    status_class = "is-online" if DEEPSEEK_API_KEY else "is-offline"
    st.markdown(
        '<section class="main-header">'
        '<div class="hero-copy">'
        '<span class="hero-eyebrow">Campus Life Operating System</span>'
        '<h1>UniLife OS</h1>'
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


# ---------------------------------------------------------------------------
# 主动关怀事件卡片（R4 新；V3.4：section-heading 包裹）
# ---------------------------------------------------------------------------

_MAX_VISIBLE_ALERTS = 3


def _alert_card_with_action(alert: dict, index: int) -> None:
    """单张卡片：HTML 区块 + 已读按钮。"""
    severity = alert.get("severity", "low")
    message = alert.get("message", "")
    suggestion = alert.get("suggested_action", "")
    icon = alert.get("icon", "🔔")
    html = alert_card_html(severity, icon, alert.get("title", ""), message)
    st.markdown(html, unsafe_allow_html=True)
    if suggestion:
        st.caption(f"👉 {suggestion}")
    key = alert.get("dedupe_key") or f"alert_{index}"
    if st.button("标为已读", key=f"ack_{key}_{index}", width="stretch"):
        from proactive import mark_read
        mark_read(key)
        toast_and_rerun("已标记为已读", "📭")


def render_alerts() -> None:
    """今日快报：主动关怀事件卡片（top 3 + 折叠其余）。V3.4：用 section-heading 包标题。"""
    alerts = get_alerts()
    if not alerts:
        return

    st.markdown(
        '<div class="section-heading">'
        '<div>'
        '<span class="section-eyebrow">Proactive care</span>'
        '<h2>主动关怀</h2>'
        '</div>'
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

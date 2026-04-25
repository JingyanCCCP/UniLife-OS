"""
UniLife OS — 主入口

R4 重构后 app.py 职责仅剩四件事：
1. st.set_page_config
2. 注入全局 CSS（ui.styles.inject_css）+ PWA meta
3. 显示上一轮 rerun 暂存的 toast（ui.components.apply_pending_toast）
4. main() 路由到 sidebar / header / alerts / 两个 Tab

所有视图逻辑在 ui/ 目录。改 UI 时优先改子模块，避免动本文件让 rerun 循环再出现
（见 CLAUDE.md Phase 7 教训）。
"""
import streamlit as st

from config import APP_NAME, APP_ICON

from ui.styles import inject_css, inject_pwa_meta
from ui.components import apply_pending_toast, render_header, render_alerts
from ui.sidebar import render_sidebar
from ui.chat import render_chat_tab
from ui.dashboard import render_dashboard_tab


st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
inject_pwa_meta()


def main() -> None:
    apply_pending_toast()
    render_sidebar()
    render_header()
    render_alerts()

    tab_chat, tab_dashboard = st.tabs(["💬 AI 对话", "📊 数据看板"])
    with tab_chat:
        render_chat_tab()
    with tab_dashboard:
        render_dashboard_tab()


if __name__ == "__main__":
    main()

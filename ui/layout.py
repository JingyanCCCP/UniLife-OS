from __future__ import annotations

import streamlit as st

from ui.chat import render_chat_tab
from ui.components import apply_pending_toast, render_alerts, render_header
from ui.dashboard import render_dashboard_tab
from ui.sidebar import render_sidebar


def render_workspace_tabs() -> None:
    st.markdown(
        '<div class="workspace-tabs-shell">',
        unsafe_allow_html=True,
    )
    tab_chat, tab_dashboard = st.tabs(["AI 对话", "数据看板"])
    with tab_chat:
        render_chat_tab()
    with tab_dashboard:
        render_dashboard_tab()
    st.markdown("</div>", unsafe_allow_html=True)


def render_app_layout() -> None:
    apply_pending_toast()
    render_sidebar()
    render_header()
    render_alerts()
    render_workspace_tabs()

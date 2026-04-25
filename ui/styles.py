"""
UniLife OS — CSS 样式层（R4 新增）

把 app.py 顶部的 CSS 整块搬出来。调用方只需在 `st.set_page_config` 之后一次调用
`inject_css()`。所有 Light/Dark 双模式调优的历史都保留，不要随意精简。
"""
from __future__ import annotations

import streamlit as st


_CSS = """
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.7rem 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    .main-header h1 { margin: 0; font-size: 1.3rem; white-space: nowrap; }
    .main-header p  { margin: 0; opacity: 0.85; font-size: 0.85rem; }
    .alert-card-high {
        background: linear-gradient(135deg, rgba(220,53,69,0.85) 0%, rgba(176,42,55,0.92) 100%);
        padding: 1rem 1.2rem; border-radius: 10px; color: white; margin-bottom: 0.5rem;
    }
    .alert-card-medium {
        background: linear-gradient(135deg, rgba(200,133,51,0.85) 0%, rgba(160,82,45,0.92) 100%);
        padding: 1rem 1.2rem; border-radius: 10px; color: white; margin-bottom: 0.5rem;
    }
    .alert-card-low {
        background: linear-gradient(135deg, rgba(39,174,96,0.85) 0%, rgba(30,132,73,0.92) 100%);
        padding: 1rem 1.2rem; border-radius: 10px; color: white; margin-bottom: 0.5rem;
    }
    .alert-card-high h4, .alert-card-medium h4, .alert-card-low h4 {
        margin: 0 0 0.3rem 0; font-size: 1rem;
    }
    .alert-card-high p, .alert-card-medium p, .alert-card-low p {
        margin: 0; font-size: 0.85rem; opacity: 0.95;
    }
    .travel-item {
        border-left: 3px solid #667eea;
        padding: 0.5rem 0 0.5rem 1rem;
        margin-bottom: 0.3rem;
    }
    /* 侧边栏：淡紫渐变叠在主题原生底色上 */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(180deg,
            rgba(129,140,248,0.26) 0%,
            rgba(139,92,246,0.18) 50%,
            rgba(196,181,253,0.12) 100%);
    }
    /* 指标卡片 */
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background: rgba(255,255,255,0.30);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        border: 1.5px solid rgba(139,92,246,0.28);
        border-radius: 10px;
        padding: 0.5rem 0.75rem;
        box-shadow: 0 2px 12px rgba(139,92,246,0.14);
    }
    /* 折叠面板 */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: rgba(255,255,255,0.20);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        border: 1.5px solid rgba(139,92,246,0.22);
        border-radius: 10px;
    }
    /* 侧边栏按钮：紫调统一风格 */
    [data-testid="stSidebar"] .stButton > button {
        border: 1.5px solid rgba(139,92,246,0.25);
        border-radius: 10px;
        background: rgba(139,92,246,0.08);
        transition: all 0.15s ease;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(139,92,246,0.18);
        border-color: rgba(139,92,246,0.40);
        box-shadow: 0 2px 8px rgba(139,92,246,0.15);
    }
    /* Tab 导航：胶囊式按钮 */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: none !important;
    }
    [data-testid="stTabs"] button[data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.55rem 1.8rem;
        font-weight: 600;
        border: 1px solid rgba(102,126,234,0.25);
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(102,126,234,0.30);
    }
    .stChatMessage { border-radius: 12px !important; }
    /* 聊天滚动容器：去除默认边框，自适应高度 */
    [data-testid="stTabs"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stChatMessage"]) {
        border: none !important;
        height: calc(100vh - 280px) !important;
        min-height: 350px;
    }
    [data-testid="stTabs"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stChatMessage"]) > div {
        height: 100% !important;
    }
</style>
"""


_PWA_META = """
<link rel="manifest" href="app/static/manifest.json">
<meta name="theme-color" content="#667eea">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="apple-touch-icon" href="app/static/icon.svg">
<script>
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('app/static/sw.js', {scope: '/'})
        .then(function(reg) { console.log('SW registered:', reg.scope); })
        .catch(function(err) { console.log('SW scope limited to static path:', err); });
}
</script>
"""


def inject_css() -> None:
    """注入主题 CSS。调用时机：st.set_page_config 之后、任何其它渲染之前。"""
    st.markdown(_CSS, unsafe_allow_html=True)


def inject_pwa_meta() -> None:
    """注入 PWA manifest / Service Worker 注册脚本。与 inject_css 同阶段调用。"""
    st.markdown(_PWA_META, unsafe_allow_html=True)

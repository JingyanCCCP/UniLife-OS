"""
UniLife OS — CSS 样式层（R4 新增；R8-T2 接入设计系统令牌）

调用方只需在 `st.set_page_config` 之后一次调用 `inject_css()`。
设计系统令牌见 docs/设计系统.md。

R8 阶段视觉重构按卡片分批推进：
- R8-T2 ✅ Header + 全局背景（本文件已切换到 :root 令牌）
- R8-T3 ⏸ Alert / Metric / Expander
- R8-T4 ⏸ Tab / 按钮
- R8-T5 ⏸ 侧边栏
"""
from __future__ import annotations

import streamlit as st


_CSS = """
<style>
    /* ============================================================
     * 设计系统令牌（R8-T1 定稿，详见 docs/设计系统.md）
     * ============================================================ */
    :root {
        /* 中性 */
        --color-bg-primary:  #F5F2EC;
        --color-bg-surface:  #FFFFFF;
        --color-bg-emphasis: #1A1A1A;
        --color-bg-muted:    #ECE9E2;
        --color-text-primary: #1A1A1A;
        --color-text-muted:   #6B6B6B;
        --color-text-inverse: #F5F2EC;

        /* 品牌 */
        --color-brand:      #8B2727;
        --color-brand-soft: #C24747;

        /* 语义 */
        --color-severity-high:   #D62828;
        --color-severity-medium: #F77F00;
        --color-severity-low:    #2A9D8F;

        /* 数据可视化 */
        --color-data-1: #1D3557;
        --color-data-2: #8B2727;
        --color-data-3: #C68B4A;

        /* 边框 */
        --color-border-hairline: rgba(26, 26, 26, 0.10);
        --color-border-strong:   rgba(26, 26, 26, 0.85);

        /* 字号 */
        --fs-display:  2.0rem;
        --fs-h2:       1.4rem;
        --fs-h3:       1.05rem;
        --fs-body:     0.95rem;
        --fs-caption:  0.8rem;

        /* 间距（8px 网格） */
        --space-1: 4px;
        --space-2: 8px;
        --space-3: 16px;
        --space-4: 24px;
        --space-5: 32px;
        --space-6: 48px;

        /* 圆角 */
        --radius-sm: 2px;
        --radius-md: 4px;
        --radius-lg: 8px;
    }

    /* ============================================================
     * 全局背景：米色 off-white
     * ============================================================ */
    .stApp,
    [data-testid="stAppViewContainer"] {
        background-color: var(--color-bg-primary) !important;
    }

    /* 主内容区文字默认色 */
    .stApp,
    [data-testid="stAppViewContainer"] {
        color: var(--color-text-primary);
    }

    /* ============================================================
     * Header（R8-T2）
     * ============================================================ */
    .main-header {
        background: var(--color-bg-emphasis);
        color: var(--color-text-inverse);
        padding: var(--space-3) var(--space-4) var(--space-3) calc(var(--space-4) + 4px);
        border-radius: 0;
        border-left: 4px solid var(--color-brand);
        margin-bottom: var(--space-4);
        display: flex;
        align-items: center;
        gap: var(--space-3);
    }
    .main-header h1 {
        margin: 0;
        font-size: var(--fs-display);
        font-weight: 700;
        letter-spacing: 0.02em;
        color: var(--color-text-inverse);
        white-space: nowrap;
    }
    .main-header p {
        margin: 0;
        opacity: 0.72;
        font-size: var(--fs-body);
        color: var(--color-text-inverse);
    }

    /* ============================================================
     * 以下规则将在 R8-T3 / T4 / T5 阶段逐步重构。
     * 暂保留旧紫色样式以避免视觉断层；T3 起按卡片替换。
     * ============================================================ */

    /* ============================================================
     * Alert 卡片（R8-T3）：白底 + 4px severity 左色条
     * ============================================================ */
    .alert-card-high,
    .alert-card-medium,
    .alert-card-low {
        background: var(--color-bg-surface);
        padding: var(--space-3) var(--space-3) var(--space-3) calc(var(--space-3) + 4px);
        border-radius: var(--radius-sm);
        margin-bottom: var(--space-2);
        color: var(--color-text-primary);
    }
    .alert-card-high {
        border-left: 4px solid var(--color-severity-high);
    }
    .alert-card-medium {
        border-left: 4px solid var(--color-severity-medium);
    }
    .alert-card-low {
        border-left: 4px solid var(--color-severity-low);
    }
    .alert-card-high h4,
    .alert-card-medium h4,
    .alert-card-low h4 {
        margin: 0 0 var(--space-1) 0;
        font-size: var(--fs-h3);
        font-weight: 600;
    }
    .alert-card-high h4   { color: var(--color-severity-high); }
    .alert-card-medium h4 { color: var(--color-severity-medium); }
    .alert-card-low h4    { color: var(--color-severity-low); }
    .alert-card-high p,
    .alert-card-medium p,
    .alert-card-low p {
        margin: 0;
        font-size: var(--fs-body);
        color: var(--color-text-primary);
        opacity: 0.92;
    }

    /* 旅行行程条目 */
    .travel-item {
        border-left: 3px solid var(--color-brand);
        padding: var(--space-2) 0 var(--space-2) var(--space-3);
        margin-bottom: var(--space-1);
    }

    /* ============================================================
     * 侧边栏（R8-T5）：米色背景 + 文字层级 + hairline 分隔
     * ============================================================ */
    [data-testid="stSidebar"] {
        background-image: none;
        background-color: var(--color-bg-primary);
    }
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        background-color: transparent;
    }

    /* 侧边栏顶部 brand 区 */
    [data-testid="stSidebar"] h2 {
        font-size: var(--fs-h2);
        font-weight: 700;
        letter-spacing: 0.02em;
        color: var(--color-text-primary);
        margin-bottom: var(--space-1);
    }

    /* 模块标题（"今日课程""财务快览"等 ### 标题） */
    [data-testid="stSidebar"] h3 {
        font-size: var(--fs-h3);
        font-weight: 600;
        letter-spacing: 0.05em;
        color: var(--color-text-primary);
        margin-top: var(--space-3);
        margin-bottom: var(--space-2);
    }

    /* caption 与小字 */
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] small {
        font-size: var(--fs-caption);
        color: var(--color-text-muted);
    }

    /* 分隔线：默认 hairline */
    [data-testid="stSidebar"] hr {
        border: none;
        border-top: 1px solid var(--color-border-hairline);
        margin: var(--space-3) 0;
    }

    /* 进度条颜色对齐品牌 */
    [data-testid="stSidebar"] [data-testid="stProgress"] > div > div > div > div {
        background-color: var(--color-brand) !important;
    }
    /* ============================================================
     * Metric 指标卡（R8-T3）：白底 + hairline border + 大号数字
     * ============================================================ */
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background: var(--color-bg-surface);
        backdrop-filter: none;
        -webkit-backdrop-filter: none;
        border: 1px solid var(--color-border-hairline);
        border-radius: var(--radius-sm);
        padding: var(--space-3);
        box-shadow: none;
    }
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        font-size: var(--fs-caption);
        font-weight: 500;
        color: var(--color-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        font-size: var(--fs-h2);
        font-weight: 700;
        color: var(--color-text-primary);
        line-height: 1.2;
    }
    [data-testid="stSidebar"] [data-testid="stMetricDelta"] {
        font-size: var(--fs-caption);
        color: var(--color-text-muted);
    }

    /* ============================================================
     * Expander 折叠面板（R8-T3）：米色 + hairline，去毛玻璃
     * ============================================================ */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: var(--color-bg-surface);
        backdrop-filter: none;
        -webkit-backdrop-filter: none;
        border: 1px solid var(--color-border-hairline);
        border-radius: var(--radius-sm);
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        font-size: var(--fs-body);
        font-weight: 500;
        color: var(--color-text-primary);
    }

    /* 主区域 expander（图片上传等）同样规则 */
    [data-testid="stMain"] [data-testid="stExpander"] {
        background: var(--color-bg-surface);
        border: 1px solid var(--color-border-hairline);
        border-radius: var(--radius-sm);
    }
    /* ============================================================
     * 侧边栏按钮（R8-T4）：次按钮样式（透明 + hairline）
     * ============================================================ */
    [data-testid="stSidebar"] .stButton > button {
        border: 1px solid var(--color-border-hairline);
        border-radius: var(--radius-md);
        background: transparent;
        color: var(--color-text-primary);
        font-weight: 500;
        transition: all 0.15s ease;
        padding: var(--space-2) var(--space-3);
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--color-bg-muted);
        border-color: var(--color-border-strong);
        box-shadow: none;
    }

    /* form 内部主按钮（"📝 记录"等表单提交按钮）—— 主按钮样式 */
    [data-testid="stSidebar"] [data-testid="stForm"] .stButton > button,
    [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] > button {
        background: var(--color-bg-emphasis);
        color: var(--color-text-inverse);
        border: 1px solid var(--color-bg-emphasis);
        border-radius: var(--radius-md);
        font-weight: 600;
    }
    [data-testid="stSidebar"] [data-testid="stForm"] .stButton > button:hover,
    [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] > button:hover {
        background: var(--color-brand);
        border-color: var(--color-brand);
        color: var(--color-text-inverse);
        box-shadow: 0 2px 8px rgba(139, 39, 39, 0.15);
    }

    /* ============================================================
     * Tab 导航（R8-T4）：底部 3px 品牌色条 + 字重区分
     * ============================================================ */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: var(--space-4);
        border-bottom: 1px solid var(--color-border-hairline) !important;
    }
    [data-testid="stTabs"] button[data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        border-radius: 0 !important;
        padding: var(--space-2) var(--space-3) calc(var(--space-2) + 1px) var(--space-3);
        font-size: var(--fs-body);
        font-weight: 500;
        color: var(--color-text-muted) !important;
        box-shadow: none !important;
        margin-bottom: -1px;  /* 让底部线和 tab-list border-bottom 对齐 */
        transition: color 0.15s ease, border-color 0.15s ease;
    }
    [data-testid="stTabs"] button[data-baseweb="tab"]:hover {
        color: var(--color-text-primary) !important;
        background: transparent !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        background: transparent !important;
        color: var(--color-text-primary) !important;
        font-weight: 700 !important;
        border-bottom: 3px solid var(--color-brand) !important;
        box-shadow: none !important;
    }

    /* ============================================================
     * 输入框 focus（R8-T4）：品牌色 outline
     * ============================================================ */
    .stTextInput > div > div:focus-within,
    .stNumberInput > div > div:focus-within,
    .stTextArea > div > div:focus-within {
        border-color: var(--color-border-focus, var(--color-brand)) !important;
        box-shadow: 0 0 0 1px var(--color-brand) !important;
    }

    /* Chat input 也用品牌色 focus */
    [data-testid="stChatInput"] textarea:focus {
        border-color: var(--color-brand) !important;
        box-shadow: 0 0 0 1px var(--color-brand) !important;
    }

    /* ============================================================
     * Chat message（保留较温和的圆角）
     * ============================================================ */
    .stChatMessage {
        border-radius: var(--radius-lg) !important;
    }
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
<meta name="theme-color" content="#1A1A1A">
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

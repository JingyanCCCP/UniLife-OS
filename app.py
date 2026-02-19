"""
UniLife OS — 主入口
你的大学生活智能操作系统 🎓
"""
import streamlit as st
from modules.chat_engine import chat_stream
from modules.mock_data import (
    get_finance, get_health, get_todos,
    get_upcoming_exams, get_schedule, build_context_summary,
)
from prompts.system_prompt import build_system_prompt
from config import APP_NAME, APP_ICON, DEEPSEEK_API_KEY

# ========== 页面配置 ==========
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========== 自定义样式 ==========
st.markdown("""
<style>
    /* 主标题样式 */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }
    .main-header h1 { margin: 0; font-size: 1.8rem; }
    .main-header p  { margin: 0.3rem 0 0; opacity: 0.9; font-size: 0.95rem; }

    /* 状态卡片 */
    .status-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.6rem;
    }

    /* 侧边栏美化 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    /* 聊天消息气泡 */
    .stChatMessage { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ========== 侧边栏：状态监控面板 ==========
def render_sidebar():
    """渲染侧边栏状态监控"""
    with st.sidebar:
        st.markdown(f"## {APP_ICON} {APP_NAME}")
        st.caption("你的大学生活智能操作系统")
        st.divider()

        # API 连接状态
        if DEEPSEEK_API_KEY:
            st.success("🟢 AI 引擎已连接", icon="✅")
        else:
            st.error("🔴 请配置 DeepSeek API Key", icon="⚠️")

        st.divider()

        # 财务快览
        finance = get_finance()
        st.markdown("### 💰 财务快览")
        st.metric(
            label="本月剩余",
            value=f"¥{finance['remaining']:.0f}",
            delta=f"-¥{finance['spent']:.0f} 已花费",
            delta_color="inverse",
        )
        st.progress(
            finance["budget_usage_pct"] / 100,
            text=f"预算使用 {finance['budget_usage_pct']}%",
        )

        if finance["budget_usage_pct"] > 80:
            st.warning("⚠️ 预算已超过 80%，注意节省！")

        st.divider()

        # 健康快览
        health = get_health()
        st.markdown("### 🏥 今日健康")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("步数", f"{health['today_steps']:,}",
                       delta=f"目标 {health['step_goal']:,}"
            )
        with col2:
            st.metric("睡眠", f"{health['sleep_hours']}h",
                       delta=health["sleep_quality"])

        col3, col4 = st.columns(2)
        with col3:
            st.metric("喝水", f"{health['water_cups']}/{health['water_goal']}杯")
        with col4:
            st.metric("运动",
                       f"{health['exercise_this_week']}/{health['exercise_goal']}次")

        st.divider()

        # 待办速览
        todos = get_todos()
        pending = [t for t in todos if not t["done"]]
        st.markdown(f"### 📝 待办事项 ({len(pending)})")
        for t in pending:
            st.markdown(f"{t['priority']} **{t['task']}**  \n📅 {t['deadline']}" )

        st.divider()

        # 考试倒计时
        exams = get_upcoming_exams()
        if exams:
            st.markdown("### 🎯 考试倒计时")
            for e in exams:
                if e["days_left"] <= 7:
                    st.error(f"🔴 **{e['course']}** — {e['days_left']} 天后！")
                else:
                    st.info(f"🔵 **{e['course']}** — {e['days_left']} 天后")


# ========== 主页面头部 ==========
def render_header():
    """渲染主页面头部"""
    st.markdown("""
    <div class="main-header">
        <h1>🎓 UniLife OS</h1>
        <p>Hi！我是你的大学生活智能助手，课程、消费、健康、出行——我都能帮你搞定 ✨</p>
    </div>
    """, unsafe_allow_html=True)


# ========== Tab 1: AI 对话 ==========
def render_chat_tab():
    """渲染 AI 对话界面"""

    # 初始化聊天记录
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 显示历史消息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🎓" if msg["role"] == "assistant" else "🧑‍🎓"):
            st.markdown(msg["content"])

    # 欢迎语（首次进入时显示）
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🎓"):
            welcome = _generate_welcome()
            st.markdown(welcome)
            st.session_state.messages.append(
                {"role": "assistant", "content": welcome}
            )

    # 用户输入
    if prompt := st.chat_input("和我聊聊吧，比如「这个月钱还够花吗？」"):
        # 显示用户消息
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 构建完整对话（含 System Prompt）
        context = build_context_summary()
        system_prompt = build_system_prompt(context)
        full_messages = [{"role": "system", "content": system_prompt}]
        full_messages.extend(st.session_state.messages)

        # 流式输出 AI 回复
        with st.chat_message("assistant", avatar="🎓"):
            response = st.write_stream(chat_stream(full_messages))

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )


def _generate_welcome() -> str:
    """生成个性化欢迎语"""
    context = build_context_summary()
    lines = ["Hey！欢迎回来 👋 我是 **UniLife**，你的校园生活小助手~\n"]
    lines.append("这是你今天的快报：\n")

    # 课程提醒
    lines.append(f"📅 **课程** — {context['schedule_summary'].split(chr(10))[0]}")
    # 财务状况
    lines.append(f"💰 **财务** — {context['finance_summary']}")
    # 待办
    lines.append(f"📝 **待办** — {context['todo_summary'].split(chr(10))[0]}")
    # 健康
    lines.append(f"🏥 **健康** — {context['health_summary']}")

    lines.append("\n有什么我能帮你的？随时聊！💬")
    return "\n".join(lines)


# ========== Tab 2: 数据看板（Day 2-3 扩展） ==========
def render_dashboard_tab():
    """渲染数据看板 — 占位框架"""

    st.markdown("### 📊 个人数据看板")
    st.info("🚧 看板模块将在 Day 2-3 开发完成，届时将包含：\n"
            "- 💰 消费分析饼图\n"
            "- 📅 周课表视图\n"
            "- 🏥 健康趋势图\n"
            "- ✈️ 旅行规划面板")

    # 预留区域：Day 2 填充
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 💰 消费构成")
        st.caption("（Day 3 实现 Plotly 饼图）")
        # 先用 metric 卡片占位
        finance = get_finance()
        for cat, amount in finance["categories"].items():
            st.metric(cat, f"¥{amount:.0f}")

    with col2:
        st.markdown("#### 📅 本周课表")
        st.caption("（Day 3 实现表格视图）")
        import pandas as pd
        df = pd.DataFrame(get_schedule())
        st.dataframe(df, use_container_width=True, hide_index=True)


# ========== 主流程 ==========
def main():
    render_sidebar()
    render_header()

    # 主功能 Tabs
    tab_chat, tab_dashboard = st.tabs(["💬 AI 对话", "📊 数据看板"])

    with tab_chat:
        render_chat_tab()

    with tab_dashboard:
        render_dashboard_tab()


if __name__ == "__main__":
    main()

"""
UniLife OS — 主入口 (Phase 2: Agent + 持久化 + UI 优化)
新增：AI Agent 工具调用、数据持久化、清除对话、API 缺失提示、工具调用可视化
"""
import html as html_mod
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from modules.chat_engine import chat_agent, trim_messages
from modules.mock_data import (
    get_finance, get_health, get_todos,
    get_upcoming_exams, get_schedule, get_today_schedule,
    get_travel_plan, get_alerts, build_context_summary,
)
from modules.tools import TOOL_SCHEMAS, TOOL_DISPLAY_NAMES, execute_tool
from modules.persistence import (
    update_todo_status, add_expense, increment_water,
    log_exercise, log_mood, update_packing,
    save_chat_history, load_chat_history, clear_chat_history,
    get_packing_checked, set_budget,
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
""", unsafe_allow_html=True)

# ========== PWA 支持 ==========
st.markdown("""
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
""", unsafe_allow_html=True)


def _toast_and_rerun(msg: str, icon: str = "✅"):
    """暂存 toast 消息到 session_state，rerun 后在 main() 顶部显示。"""
    st.session_state._pending_toast = (msg, icon)
    st.rerun()


def _alert_card_html(severity, icon, title, message):
    return (
        f'<div class="alert-card-{severity}">'
        f'<h4>{icon} {title}</h4>'
        f'<p>{message}</p>'
        f'</div>'
    )


def _travel_item_html(icon, time_str, activity, location, cost_str):
    return (
        f'<div class="travel-item">'
        f'<strong>{icon} {time_str}</strong> — {activity}<br>'
        f'<small>📍 {location} 💰 {cost_str}</small>'
        f'</div>'
    )


# ========== 侧边栏 ==========
def render_sidebar():
    with st.sidebar:
        st.markdown("## " + APP_ICON + " " + APP_NAME)
        st.caption("你的大学生活智能操作系统")
        st.divider()

        if DEEPSEEK_API_KEY:
            st.success("🟢 AI 引擎已连接", icon="✅")
        else:
            st.error("🔴 请配置 DeepSeek API Key", icon="⚠️")
            st.info("在项目根目录创建 `.env` 文件，添加：\n`DEEPSEEK_API_KEY=你的密钥`")

        st.divider()

        # 今日课程
        today_courses = get_today_schedule()
        weekday_map = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
        today_wd = weekday_map[datetime.now().weekday()]

        st.markdown("### 📅 今日课程（" + today_wd + "）")
        if today_courses:
            for c in today_courses:
                type_badge = "🧪" if c.get("type") == "实验" else "📖"
                line = type_badge + " **" + c["course"] + "**  \n⏰ " + c["time"] + "  📍 " + c["location"]
                st.markdown(line)
        else:
            st.info("🎉 今天没有课，自由安排！")

        st.divider()

        # 财务快览
        finance = get_finance()
        st.markdown("### 💰 财务快览")
        remaining_str = "¥" + str(int(finance["remaining"]))
        spent_str = "-¥" + str(int(finance["spent"])) + " 已花费"
        st.metric(label="本月剩余", value=remaining_str, delta=spent_str, delta_color="inverse")
        st.progress(
            min(finance["budget_usage_pct"] / 100, 1.0),
            text="预算使用 " + str(finance["budget_usage_pct"]) + "%",
        )

        if finance["budget_usage_pct"] > 80:
            warn_msg = (
                "⚠️ 预算紧张！剩余 " + str(finance["days_left_in_month"])
                + " 天，建议每天 ≤ ¥" + str(int(finance["suggested_daily"]))
            )
            st.warning(warn_msg)

        with st.expander("📋 最近消费流水"):
            for t in finance["recent_transactions"][:8]:
                t_icon = t.get("icon", "💳")
                safe_item = html_mod.escape(t["item"])
                safe_cat = html_mod.escape(t["category"])
                line = (
                    t_icon + " <strong>" + safe_item + "</strong> — ¥" + str(t["amount"])
                    + "  <br><small>" + t["date"] + " · " + safe_cat + "</small>"
                )
                st.markdown(line, unsafe_allow_html=True)

        with st.expander("✏️ 快速记一笔"):
            with st.form("quick_expense", clear_on_submit=True):
                form_cols = st.columns([2, 1])
                with form_cols[0]:
                    item = st.text_input("花了什么", placeholder="奶茶")
                with form_cols[1]:
                    amount = st.number_input("金额", min_value=0.0, step=0.5, format="%.1f")
                category = st.selectbox("分类", ["餐饮", "交通", "购物", "学习用品", "娱乐", "其他"])
                submitted = st.form_submit_button("📝 记录")
                if submitted:
                    if not item or amount <= 0:
                        st.warning("⚠️ 请填写消费项目并输入大于 0 的金额")
                    else:
                        add_expense(item, amount, category)
                        _toast_and_rerun("✅ 已记录：" + item + " ¥" + str(amount) + "（" + category + "）", "💾")

        with st.expander("⚙️ 预算设置"):
            new_budget = st.number_input(
                "月预算 (元)", value=float(finance["monthly_budget"]),
                min_value=100.0, step=100.0, format="%.0f",
            )
            if st.button("保存预算"):
                set_budget(new_budget)
                _toast_and_rerun("预算已更新为 ¥" + str(int(new_budget)), "💰")

        st.divider()

        # 健康打卡
        health = get_health()
        st.markdown("### 🏥 今日健康")

        hcol1, hcol2 = st.columns(2)
        with hcol1:
            st.metric("步数", "{:,}".format(health["today_steps"]),
                      delta="目标 " + "{:,}".format(health["step_goal"]))
        with hcol2:
            st.metric("睡眠", str(health["sleep_hours"]) + "h", delta=health["sleep_quality"])

        hcol3, hcol4 = st.columns(2)
        with hcol3:
            st.metric("喝水", str(health["water_cups"]) + "/" + str(health["water_goal"]) + "杯")
        with hcol4:
            st.metric("运动", str(health["exercise_this_week"]) + "/" + str(health["exercise_goal"]) + "次")

        st.caption(
            "😊 心情: " + health["mood"] + " | 🔥 连续打卡 " + str(health["checkin_streak"]) + " 天"
        )

        st.markdown("**快速打卡：**")
        btn_cols = st.columns(3)
        with btn_cols[0]:
            if st.button("💧+1杯"):
                increment_water()
                total = get_health()["water_cups"]
                st.toast("💧 喝水 +1，已喝 " + str(total) + " 杯！", icon="💧")
        with btn_cols[1]:
            exercise_done = health.get("last_exercise") == datetime.now().strftime("%Y-%m-%d")
            btn_label = "✅ 已打卡" if exercise_done else "🏃运动"
            if st.button(btn_label, disabled=exercise_done):
                log_exercise()
                _toast_and_rerun("🏃 运动打卡成功！已保存", "🎉")
        with btn_cols[2]:
            mood_options = ["😊 开心", "🙂 还行", "😐 一般", "😢 难过", "😫 疲惫"]
            selected_mood = st.selectbox("心情", mood_options, label_visibility="collapsed", key="mood_select")
            if st.button("📝记心情"):
                log_mood(selected_mood)
                _toast_and_rerun(selected_mood + " 心情记录成功！", "✨")

        st.divider()

        # 待办事项（可勾选）
        todos = get_todos()
        pending = [t for t in todos if not t["done"]]
        done_todos = [t for t in todos if t["done"]]

        st.markdown("### 📝 待办事项 (" + str(len(pending)) + ")")

        # 每次渲染同步最新待办状态（兼容 Agent 新增/修改的待办）
        st.session_state.todo_done = {t["id"]: t["done"] for t in todos}

        # 只显示未完成的待办
        for t in pending:
            label = t["priority"] + " " + t["task"] + "（" + t["deadline"] + "）"
            checked = st.checkbox(
                label,
                value=False,
                key="todo_" + str(t["id"]),
            )
            if checked and not st.session_state.todo_done.get(t["id"]):
                st.session_state.todo_done[t["id"]] = True
                update_todo_status(t["id"], True)
                _toast_and_rerun("✅ 完成：" + t["task"], "🎉")

        if not pending:
            st.info("🎉 所有待办已完成！")

        # 已完成待办折叠区，图标置灰
        if done_todos:
            _gray_priority = {"🔴": "🔘", "🟡": "🔘", "🟢": "🔘"}
            with st.expander("✅ 已完成 (" + str(len(done_todos)) + ")", expanded=False):
                for t in done_todos:
                    gray_label = t["priority"]
                    for color, gray in _gray_priority.items():
                        gray_label = gray_label.replace(color, gray)
                    label = gray_label + " ~~" + t["task"] + "~~（" + t["deadline"] + "）"
                    unchecked = st.checkbox(
                        label,
                        value=True,
                        key="todo_" + str(t["id"]),
                    )
                    if not unchecked and st.session_state.todo_done.get(t["id"], True):
                        st.session_state.todo_done[t["id"]] = False
                        update_todo_status(t["id"], False)
                        _toast_and_rerun("↩️ 已恢复：" + t["task"], "🔄")

        st.divider()

        # 考试倒计时
        exams = get_upcoming_exams()
        if exams:
            st.markdown("### 🎯 考试倒计时")
            for e in exams:
                countdown = "今天！" if e["days_left"] == 0 else str(e["days_left"]) + " 天后"
                msg = "**" + e["course"] + "** — " + countdown + "\n📍 " + e["location"]
                if e["days_left"] == 0:
                    st.error("🔴 " + msg)
                elif e["days_left"] <= 3:
                    st.error("🔴 " + msg + "！")
                elif e["days_left"] <= 7:
                    st.warning("🟡 " + msg)
                else:
                    st.info("🔵 " + msg)

        st.divider()

        # 清除对话按钮
        if st.button("🔄 清除对话", use_container_width=True):
            st.session_state.messages = []
            clear_chat_history()
            _toast_and_rerun("对话已清除", "🔄")


# ========== 主页面头部 ==========
def render_header():
    st.markdown(
        '<div class="main-header">'
        '<h1>🎓 UniLife OS</h1>'
        '<p>Hi！我是你的大学生活智能助手，课程、消费、健康、出行——我都能帮你搞定 ✨</p>'
        '</div>',
        unsafe_allow_html=True,
    )


# ========== 智能提醒卡片 ==========
def render_alerts():
    alerts = get_alerts()
    if not alerts:
        return

    st.markdown("### 🔔 智能提醒")
    cols = st.columns(min(len(alerts), 3))
    for i, alert in enumerate(alerts[:3]):
        with cols[i % 3]:
            severity = alert.get("severity", "low")
            html = _alert_card_html(severity, alert["icon"], alert["title"], alert["message"])
            st.markdown(html, unsafe_allow_html=True)

    if len(alerts) > 3:
        with st.expander("📋 查看全部 " + str(len(alerts)) + " 条提醒"):
            for alert in alerts[3:]:
                severity = alert.get("severity", "low")
                html = _alert_card_html(severity, alert["icon"], alert["title"], alert["message"])
                st.markdown(html, unsafe_allow_html=True)


# ========== AI 对话（Agent 模式）==========
def render_chat_tab():
    # 启动时从持久化层加载聊天历史
    if "messages" not in st.session_state:
        saved = load_chat_history()
        st.session_state.messages = saved if saved else []

    # 可滚动消息区域（CSS 会覆盖高度为 calc(100vh - 280px)）
    chat_container = st.container(height=500)

    with chat_container:
        for msg in st.session_state.messages:
            avatar = "🎓" if msg["role"] == "assistant" else "🧑‍🎓"
            with st.chat_message(msg["role"], avatar=avatar):
                # 展示工具调用记录（如果有）
                tool_log = msg.get("tool_log")
                if tool_log:
                    for tc in tool_log:
                        display_name = TOOL_DISPLAY_NAMES.get(tc["name"], tc["name"])
                        with st.expander("🔧 " + display_name, expanded=False):
                            st.code(tc["result"], language=None)
                st.markdown(msg["content"])

        if not st.session_state.messages:
            with st.chat_message("assistant", avatar="🎓"):
                welcome = _generate_welcome()
                st.markdown(welcome)
                st.session_state.messages.append({"role": "assistant", "content": welcome})

    # 输入框在容器外部 → 始终可见
    if not DEEPSEEK_API_KEY:
        st.warning("💡 在项目根目录的 `.env` 文件中配置 `DEEPSEEK_API_KEY` 后重启应用即可使用 AI 对话功能。")
        st.chat_input("请先配置 DeepSeek API Key...", disabled=True)
        return

    if prompt := st.chat_input("和我聊聊吧，比如「我今天有什么课？」「帮我记一笔：奶茶 18 元」"):
        with chat_container:
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        context = build_context_summary()
        system_prompt = build_system_prompt(context)
        full_messages = [{"role": "system", "content": system_prompt}]
        # 只传纯文本消息给 API（过滤 tool_log 等额外字段）
        for m in st.session_state.messages:
            full_messages.append({"role": m["role"], "content": m["content"]})
        # 裁剪上下文，防止超出模型窗口
        full_messages = trim_messages(full_messages)

        with chat_container:
            with st.chat_message("assistant", avatar="🎓"):
                with st.status("🤔 思考中...", expanded=True) as status:
                    response_text, tool_log = chat_agent(
                        full_messages, TOOL_SCHEMAS, execute_tool
                    )

                    # 展示工具调用过程
                    if tool_log:
                        for tc in tool_log:
                            display_name = TOOL_DISPLAY_NAMES.get(tc["name"], tc["name"])
                            status.update(label="🔧 调用工具: " + display_name)
                            with st.expander("🔧 " + display_name, expanded=False):
                                st.code(tc["result"], language=None)
                        status.update(label="✅ 完成", state="complete", expanded=False)
                    else:
                        status.update(label="✅ 完成", state="complete", expanded=False)

                st.markdown(response_text)

        # 保存消息（附带工具调用记录）
        msg_record = {"role": "assistant", "content": response_text}
        if tool_log:
            msg_record["tool_log"] = tool_log
        st.session_state.messages.append(msg_record)
        save_chat_history(st.session_state.messages)


def _generate_welcome():
    context = build_context_summary()
    alerts = get_alerts()

    lines = []
    lines.append("Hey！欢迎回来 👋 我是 **UniLife**，你的校园生活小助手~\n")
    lines.append("这是你今天的快报：\n")

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
            "\n⚡ **需要关注** — 有 " + str(len(alerts))
            + " 条提醒，最重要的是：" + alerts[0]["icon"] + " " + alerts[0]["title"]
        )

    lines.append("\n有什么我能帮你的？随时聊！💬")
    lines.append("\n💡 *试试问我：「我今天有什么课？」「帮我记一笔：奶茶 18 元」「分析一下这个月花销」*")
    return "\n".join(lines)


# ========== Tab 2: 数据看板 ==========
def render_dashboard_tab():
    st.markdown("### 📊 个人数据看板")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💰 消费构成")
        finance = get_finance()
        cat_data = pd.DataFrame(
            list(finance["categories"].items()),
            columns=["类别", "金额"],
        )
        fig = px.pie(
            cat_data,
            values="金额",
            names="类别",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4,
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>金额: ¥%{value:.0f}<br>占比: %{percent}<extra></extra>",
        )
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=20, b=20, l=20, r=20),
            height=350,
            dragmode=False,
        )
        st.plotly_chart(fig, use_container_width=True,
            config={"displayModeBar": False, "scrollZoom": False})

        st.markdown("**📈 消费指标**")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("日均消费", "¥" + str(int(finance["daily_avg_spent"])))
        with m2:
            st.metric("剩余天数", str(finance["days_left_in_month"]) + "天")
        with m3:
            st.metric("建议日限", "¥" + str(int(finance["suggested_daily"])))

    with col2:
        st.markdown("#### 📅 本周课表")
        df = pd.DataFrame(get_schedule())
        st.dataframe(
            df[["weekday", "time", "course", "location", "type"]].rename(
                columns={
                    "weekday": "星期",
                    "time": "时间",
                    "course": "课程",
                    "location": "地点",
                    "type": "类型",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### 🏥 7 天健康趋势")
        health = get_health()
        history = health.get("history", [])
        if history:
            df_health = pd.DataFrame(history)
            df_health["date"] = pd.to_datetime(df_health["date"])
            df_health = df_health.sort_values("date")

            st.markdown("**👣 每日步数**")
            fig_steps = px.line(
                df_health,
                x="date",
                y="steps",
                markers=True,
                labels={"date": "日期", "steps": "步数"},
            )
            fig_steps.add_hline(
                y=health["step_goal"],
                line_dash="dash",
                line_color="red",
                annotation_text="目标 " + "{:,}".format(health["step_goal"]),
            )
            fig_steps.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                height=250,
                showlegend=False,
                dragmode=False,
            )
            st.plotly_chart(fig_steps, use_container_width=True,
                config={"displayModeBar": False, "scrollZoom": False})

            st.markdown("**😴 每日睡眠**")
            fig_sleep = px.bar(
                df_health,
                x="date",
                y="sleep",
                labels={"date": "日期", "sleep": "睡眠(小时)"},
                color="sleep",
                color_continuous_scale=["#ff6b6b", "#ffa502", "#7bed9f"],
            )
            fig_sleep.add_hline(
                y=7,
                line_dash="dash",
                line_color="green",
                annotation_text="建议 7h",
            )
            fig_sleep.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                height=250,
                showlegend=False,
                coloraxis_showscale=False,
                dragmode=False,
            )
            st.plotly_chart(fig_sleep, use_container_width=True,
                config={"displayModeBar": False, "scrollZoom": False})
        else:
            st.info("暂无历史健康数据")

    with col4:
        st.markdown("#### 🗺️ 旅行计划")
        travel = get_travel_plan()

        if travel is None:
            st.info("暂无旅行计划，可以通过 AI 对话创建新的旅行计划。")
        else:
            companions = travel.get("companions", [])
            if isinstance(companions, str):
                companions_str = companions
            else:
                companions_str = "、".join(companions) if companions else "独自出行"
            st.markdown(
                "**" + travel["trip_name"] + "**  \n"
                "📆 " + travel["date"] + " | 👥 " + companions_str
            )

            t_m1, t_m2 = st.columns(2)
            with t_m1:
                st.metric("预算", "¥" + str(int(travel["budget"])))
            with t_m2:
                st.metric(
                    "预估花费",
                    "¥" + str(int(travel["total_estimated_cost"])),
                    delta="剩余 ¥" + str(int(travel["budget"] - travel["total_estimated_cost"])),
                )

            st.markdown("**📍 行程时间线**")
            if travel["itinerary"]:
                for stop in travel["itinerary"]:
                    cost_str = "¥" + str(int(stop["cost"])) if stop["cost"] > 0 else "免费"
                    html = _travel_item_html(
                        stop.get("icon", "📍"), stop["time"], stop["activity"],
                        stop["location"], cost_str,
                    )
                    st.markdown(html, unsafe_allow_html=True)
            else:
                st.caption("暂无行程，可通过 AI 对话添加行程站点")

            packing_list = travel.get("packing_list", [])
            if packing_list:
                st.markdown("**🎒 必带清单**")
                packing_checked = get_packing_checked()
                for item in packing_list:
                    pack_key = "pack_" + item
                    is_checked = item in packing_checked
                    checked = st.checkbox(item, value=is_checked, key=pack_key)
                    # 只在用户主动交互（值变化）时持久化
                    if checked and not is_checked:
                        update_packing(item, True)
                        _toast_and_rerun("🎒 已保存", "💾")
                    elif not checked and is_checked:
                        update_packing(item, False)
                        _toast_and_rerun("🎒 已取消", "💾")


# ========== 主入口 ==========
def main():
    # 显示上次 rerun 前暂存的 toast 消息
    if "_pending_toast" in st.session_state:
        msg, icon = st.session_state._pending_toast
        st.toast(msg, icon=icon)
        del st.session_state._pending_toast

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

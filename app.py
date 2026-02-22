"""
UniLife OS — 主入口 (Phase 2: Agent + 持久化 + UI 优化)
新增：AI Agent 工具调用、数据持久化、清除对话、API 缺失提示、工具调用可视化
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from modules.chat_engine import chat_stream, chat_agent
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
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }
    .main-header h1 { margin: 0; font-size: 1.8rem; }
    .main-header p  { margin: 0.3rem 0 0; opacity: 0.9; font-size: 0.95rem; }
    .alert-card-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem 1.2rem; border-radius: 10px; color: white; margin-bottom: 0.5rem;
    }
    .alert-card-medium {
        background: linear-gradient(135deg, #ffa502 0%, #ff6348 100%);
        padding: 1rem 1.2rem; border-radius: 10px; color: white; margin-bottom: 0.5rem;
    }
    .alert-card-low {
        background: linear-gradient(135deg, #7bed9f 0%, #2ed573 100%);
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
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    .stChatMessage { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)


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
                line = (
                    t_icon + " **" + t["item"] + "** — ¥" + str(t["amount"])
                    + "  \n<small>" + t["date"] + " · " + t["category"] + "</small>"
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
                if submitted and item and amount > 0:
                    add_expense(item, amount, category)
                    st.success("✅ 已记录：" + item + " ¥" + str(amount) + "（" + category + "）")
                    st.toast("✅ 已保存", icon="💾")

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
                cups = increment_water()
                st.toast("💧 喝水 +1，已喝 " + str(cups) + " 杯！", icon="💧")
        with btn_cols[1]:
            if st.button("🏃运动"):
                log_exercise()
                st.toast("🏃 运动打卡成功！已保存", icon="🎉")
        with btn_cols[2]:
            if st.button("😊心情"):
                log_mood("😊 开心")
                st.toast("😊 心情记录成功！已保存", icon="✨")

        st.divider()

        # 待办事项（可勾选）
        todos = get_todos()
        pending = [t for t in todos if not t["done"]]

        st.markdown("### 📝 待办事项 (" + str(len(pending)) + ")")

        if "todo_done" not in st.session_state:
            st.session_state.todo_done = {t["id"]: t["done"] for t in todos}

        for t in todos:
            label = t["priority"] + " " + t["task"] + "（" + t["deadline"] + "）"
            checked = st.checkbox(
                label,
                value=st.session_state.todo_done.get(t["id"], t["done"]),
                key="todo_" + str(t["id"]),
            )
            if checked != st.session_state.todo_done.get(t["id"]):
                st.session_state.todo_done[t["id"]] = checked
                update_todo_status(t["id"], checked)
                if checked:
                    st.toast("✅ 完成：" + t["task"], icon="🎉")

        st.divider()

        # 考试倒计时
        exams = get_upcoming_exams()
        if exams:
            st.markdown("### 🎯 考试倒计时")
            for e in exams:
                msg = "**" + e["course"] + "** — " + str(e["days_left"]) + " 天后\n📍 " + e["location"]
                if e["days_left"] <= 3:
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
            st.toast("对话已清除", icon="🔄")
            st.rerun()


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


# ========== Tab 1: AI 对话（Agent 模式）==========
def render_chat_tab():
    render_alerts()
    st.divider()

    # 启动时从持久化层加载聊天历史
    if "messages" not in st.session_state:
        saved = load_chat_history()
        st.session_state.messages = saved if saved else []

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
            save_chat_history(st.session_state.messages)

    # API 缺失时禁用输入
    if not DEEPSEEK_API_KEY:
        st.chat_input("请先配置 DeepSeek API Key...", disabled=True)
        st.warning("💡 在项目根目录的 `.env` 文件中配置 `DEEPSEEK_API_KEY` 后重启应用即可使用 AI 对话功能。")
        return

    if prompt := st.chat_input("和我聊聊吧，比如「我今天有什么课？」「帮我记一笔：奶茶 18 元」"):
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        context = build_context_summary()
        system_prompt = build_system_prompt(context)
        full_messages = [{"role": "system", "content": system_prompt}]
        # 只传纯文本消息给 API（过滤 tool_log 等额外字段）
        for m in st.session_state.messages:
            full_messages.append({"role": m["role"], "content": m["content"]})

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
    render_alerts()
    st.divider()

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
        )
        st.plotly_chart(fig, use_container_width=True)

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
            height=350,
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
            )
            st.plotly_chart(fig_steps, use_container_width=True)

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
            )
            st.plotly_chart(fig_sleep, use_container_width=True)
        else:
            st.info("暂无历史健康数据")

    with col4:
        st.markdown("#### 🗺️ 旅行计划")
        travel = get_travel_plan()

        st.markdown(
            "**" + travel["trip_name"] + "**  \n"
            "📆 " + travel["date"] + " | 👥 " + "、".join(travel["companions"])
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
        for stop in travel["itinerary"]:
            cost_str = "¥" + str(int(stop["cost"])) if stop["cost"] > 0 else "免费"
            html = _travel_item_html(
                stop["icon"], stop["time"], stop["activity"],
                stop["location"], cost_str,
            )
            st.markdown(html, unsafe_allow_html=True)

        st.markdown("**🎒 必带清单**")
        from modules.persistence import get_packing_checked
        packing_checked = get_packing_checked()
        for item in travel["packing_list"]:
            checked = st.checkbox(
                item,
                value=(item in packing_checked),
                key="pack_" + item,
            )
            # 检测变化并持久化
            was_checked = item in packing_checked
            if checked != was_checked:
                update_packing(item, checked)
                st.toast("🎒 已保存", icon="💾")


# ========== 主入口 ==========
def main():
    render_sidebar()
    render_header()

    tab_chat, tab_dashboard = st.tabs(["💬 AI 对话", "📊 数据看板"])

    with tab_chat:
        render_chat_tab()

    with tab_dashboard:
        render_dashboard_tab()


if __name__ == "__main__":
    main()

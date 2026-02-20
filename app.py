"""
UniLife OS — 主入口 (Day 2 增强版)
新增：智能提醒卡片、待办勾选、健康打卡、快速记账、旅行面板、今日课程高亮
"""
import streamlit as st
import pandas as pd
from modules.chat_engine import chat_stream
from modules.mock_data import (
    get_finance, get_health, get_todos,
    get_upcoming_exams, get_schedule, get_today_schedule,
    get_travel_plan, get_alerts, build_context_summary,
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

    /* 提醒卡片样式 */
    .alert-card-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem 1.2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 0.5rem;
    }
    .alert-card-medium {
        background: linear-gradient(135deg, #ffa502 0%, #ff6348 100%);
        padding: 1rem 1.2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 0.5rem;
    }
    .alert-card-low {
        background: linear-gradient(135deg, #7bed9f 0%, #2ed573 100%);
        padding: 1rem 1.2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 0.5rem;
    }
    .alert-card-high h4, .alert-card-medium h4, .alert-card-low h4 {
        margin: 0 0 0.3rem 0;
        font-size: 1rem;
    }
    .alert-card-high p, .alert-card-medium p, .alert-card-low p {
        margin: 0;
        font-size: 0.85rem;
        opacity: 0.95;
    }

    /* 旅行时间线 */
    .travel-item {
        border-left: 3px solid #667eea;
        padding: 0.5rem 0 0.5rem 1rem;
        margin-bottom: 0.3rem;
    }

    /* 侧边栏美化 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    /* 聊天消息气泡 */
    .stChatMessage { border-radius: 12px !important; }

    /* 消费流水表格 */
    .transaction-row {
        padding: 0.3rem 0;
        border-bottom: 1px solid #333;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== 侧边栏：状态监控面板 (Day 2 增强) ==========
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

        # ========== 📅 今日课程 ==========
        today_courses = get_today_schedule()
        weekday_map = {0: "周一", 1: "周二", 2: "周三",
                       3: "周四", 4: "周五", 5: "周六", 6: "周日"}
        from datetime import datetime
        today_wd = weekday_map[datetime.now().weekday()]

        st.markdown(f"### 📅 今日课程（{today_wd}）")
        if today_courses:
            for c in today_courses:
                type_badge = "🧪" if c.get("type") == "实验" else "📖"
                st.markdown(
                    f"{type_badge} **{c['course']}**  
                    f"⏰ {c['time']}  📍 {c['location']}"
                )
        else:
            st.info("🎉 今天没有课，自由安排！")

        st.divider()

        # ========== 💰 财务快览 + 记账 ==========
        finance = get_finance()
        st.markdown("### 💰 财务快览")
        st.metric(
            label="本月剩余",
            value=f"¥{finance['remaining']:.0f}",
            delta=f"-¥{finance['spent']:.0f} 已花费",
            delta_color="inverse",
        )
        st.progress(
            min(finance["budget_usage_pct"] / 100, 1.0),
            text=f"预算使用 {finance['budget_usage_pct']}%",
        )

        if finance["budget_usage_pct"] > 80:
            st.warning(
                f"⚠️ 预算紧张！剩余 {finance['days_left_in_month']} 天，"
                f"建议每天 ≤ ¥{finance['suggested_daily']:.0f}"
            )

        # 展开查看最近消费
        with st.expander("📋 最近消费流水"):
            for t in finance["recent_transactions"][:8]:
                st.markdown(
                    f"{t.get('icon', '💳')} **{t['item']}** — ¥{t['amount']:.1f}  
                    f"<small>{t['date']} · {t['category']}</small>",
                    unsafe_allow_html=True,
                )

        # 快速记一笔
        with st.expander("✏️ 快速记一笔"):
            with st.form("quick_expense", clear_on_submit=True):
                cols = st.columns([2, 1])
                with cols[0]:
                    item = st.text_input("花了什么", placeholder="奶茶")
                with cols[1]:
                    amount = st.number_input("金额", min_value=0.0,
                                             step=0.5, format="%.1f")
                category = st.selectbox(
                    "分类",
                    ["餐饮", "交通", "购物", "学习用品", "娱乐", "其他"]
                )
                submitted = st.form_submit_button("📝 记录")
                if submitted and item and amount > 0:
                    st.success(f"✅ 已记录：{item} ¥{amount:.1f}（{category}）")
                    st.caption("⚠️ 当前为 Demo 模式，数据未持久化")

        st.divider()

        # ========== 🏥 健康打卡 ==========
        health = get_health()
        st.markdown("### 🏥 今日健康")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("步数", f"{health['today_steps']:,}",
                       delta=f"目标 {health['step_goal']:,}")
        with col2:
            st.metric("睡眠", f"{health['sleep_hours']}h",
                       delta=health["sleep_quality"])

        col3, col4 = st.columns(2)
        with col3:
            st.metric("喝水",
                       f"{health['water_cups']}/{health['water_goal']}杯")
        with col4:
            st.metric("运动",
                       f"{health['exercise_this_week']}/{health['exercise_goal']}次")

        st.caption(f"😊 心情: {health['mood']} | 🔥 连续打卡 {health['checkin_streak']} 天")

        # 健康打卡按钮
        st.markdown("**快速打卡：**")
        btn_cols = st.columns(3)
        with btn_cols[0]:
            if st.button("💧+1杯"):
                st.toast("💧 喝水 +1，继续保持！", icon="💧")
        with btn_cols[1]:
            if st.button("🏃运动"):
                st.toast("🏃 运动打卡成功！太棒了！", icon="🎉")
        with btn_cols[2]:
            if st.button("😊心情"):
                st.toast("😊 心情记录成功！", icon="✨")

        st.divider()

        # ========== 📝 待办事项（可勾选） ==========
        todos = get_todos()
        pending = [t for t in todos if not t["done"]]

        st.markdown(f"### 📝 待办事项 ({len(pending)})")

        # 初始化 session state
        if "todo_done" not in st.session_state:
            st.session_state.todo_done = {t["id"]: t["done"] for t in todos}

        for t in todos:
            checked = st.checkbox(
                f"{t['priority']} {t['task']}（{t['deadline']}）",
                value=st.session_state.todo_done.get(t["id"], t["done"]),
                key=f"todo_{t['id']}",
            )
            if checked != st.session_state.todo_done.get(t["id"]):
                st.session_state.todo_done[t["id"]] = checked
                if checked:
                    st.toast(f"✅ 完成：{t['task']}", icon="🎉")

        st.divider()

        # ========== 🎯 考试倒计时 ==========
        exams = get_upcoming_exams()
        if exams:
            st.markdown("### 🎯 考试倒计时")
            for e in exams:
                if e["days_left"] <= 3:
                    st.error(
                        f"🔴 **{e['course']}** — {e['days_left']} 天后！\n"
                        f"📍 {e['location']}"
                    )
                elif e["days_left"] <= 7:
                    st.warning(
                        f"🟡 **{e['course']}** — {e['days_left']} 天后\n"
                        f"📍 {e['location']}"
                    )
                else:
                    st.info(
                        f"🔵 **{e['course']}** — {e['days_left']} 天后\n"
                        f"📍 {e['location']}"
                    )


# ========== 主页面头部 ==========
def render_header():
    """渲染主页面头部"""
    st.markdown("""
    <div class="main-header">
        <h1>🎓 UniLife OS</h1>
        <p>Hi！我是你的大学生活智能助手，课程、消费、健康、出行——我都能帮你搞定 ✨</p>
    </div>
    """, unsafe_allow_html=True)


# ========== 智能提醒卡片 (Day 2 新增) ==========
def render_alerts():
    """渲染顶部智能提醒卡片"""
    alerts = get_alerts()
    if not alerts:
        return

    st.markdown("### 🔔 智能提醒")
    cols = st.columns(min(len(alerts), 3))
    for i, alert in enumerate(alerts[:3]):
        with cols[i % 3]:
            severity = alert.get("severity", "low")
            st.markdown(
                f'<div class="alert-card-{severity}">
                f'<h4>{alert["icon"]} {alert["title"]}</h4>'
                f'<p>{alert["message"]}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # 如果提醒超过 3 个，用 expander 展开
    if len(alerts) > 3:
        with st.expander(f"📋 查看全部 {len(alerts)} 条提醒"):
            for alert in alerts[3:]:
                severity = alert.get("severity", "low")
                st.markdown(
                    f'<div class="alert-card-{severity}">
                    f'<h4>{alert["icon"]} {alert["title"]}</h4>'
                    f'<p>{alert["message"]}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# ========== Tab 1: AI 对话 ==========
def render_chat_tab():
    """渲染 AI 对话界面"""

    # 显示智能提醒
    render_alerts()
    st.divider()

    # 初始化聊天记录
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 显示历史消息
    for msg in st.session_state.messages:
        avatar = "🎓" if msg["role"] == "assistant" else "🧑‍🎓"
        with st.chat_message(msg["role"], avatar=avatar):
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
    alerts = get_alerts()

    lines = ["Hey！欢迎回来 👋 我是 **UniLife**，你的校园生活小助手~\n"]
    lines.append("这是你今天的快报：\n")

    # 课程提醒
    lines.append(f"📅 **课程** — {context['schedule_summary'].split(chr(10))[0]}")
    # 财务状况
    lines.append(f"💰 **财务** — {context['finance_summary'].split(chr(10))[0]}")
    # 待办
    lines.append(f"📝 **待办** — {context['todo_summary'].split(chr(10))[0]}")
    # 健康
    lines.append(f"🏥 **健康** — {context['health_summary'].split('。')[0]}。\n")

    # 智能提醒摘要
    if alerts:
        lines.append(f"\n⚡ **需要关注** — 有 {len(alerts)} 条提醒，"
                      f"最重要的是：{alerts[0]['icon']} {alerts[0]['title']}")

    lines.append("\n有什么我能帮你的？随时聊！💬")
    return "\n".join(lines)


# ========== Tab 2: 数据看板 (Day 2 增强) ==========
def render_dashboard_tab():
    """渲染数据看板"""

    # 智能提醒
    render_alerts()
    st.divider()

    st.markdown("### 📊 个人数据看板")

    # ===== 第一行：财务 + 课表 =====
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💰 消费构成")
        finance = get_finance()
        # 用 Streamlit 原生柱状图
        cat_data = pd.DataFrame(
            list(finance["categories"].items()),
            columns=["类别", "金额"]
        )
        st.bar_chart(cat_data.set_index("类别"), height=300)

        # 消费趋势指标
        st.markdown("**📈 消费指标**")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("日均消费", f"¥{finance['daily_avg_spent']:.0f}")
        with m2:
            st.metric("剩余天数", f"{finance['days_left_in_month']}天")
        with m3:
            st.metric("建议日限", f"¥{finance['suggested_daily']:.0f}")

    with col2:
        st.markdown("#### 📅 本周课表")
        df = pd.DataFrame(get_schedule())
        # 高亮今天的课
        st.dataframe(
            df[["weekday", "time", "course", "location", "type"]].rename(
                columns={
                    "weekday": "星期", "time": "时间",
                    "course": "课程", "location": "地点", "type": "类型"
                }
            ),
            use_container_width=True,
            hide_index=True,
            height=350,
        )

    st.divider()

    # ===== 第二行：健康 + 待办 =====
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### 🏥 7 天健康趋势")
        health = get_health()
        history = health.get("history", [])
        if history:
            df_health = pd.DataFrame(history)
            df_health["date"] = pd.to_datetime(df_health["date"])
            df_health = df_health.sort_values("date")

            # 步数趋势
            st.markdown("**👣 每日步数**")
            st.line_chart(
                df_health.set_index("date")["steps"],
                height=200,
            )

            # 睡眠趋势
            st.markdown("**😴 每日睡眠 (小时)**")
            st.bar_chart(
                df_health.set_index("date")["sleep"],
                height=200,
            )

        # 今日健康指标
        st.markdown("**📋 今日指标**")
        h1, h2, h3, h4 = st.columns(4)
        with h1:
            st.metric("步数", f"{health['today_steps']:,}",
                       delta=f"{health['today_steps']-health['step_goal']:+,}")
        with h2:
            st.metric("睡眠", f"{health['sleep_hours']}h")
        with h3:
            st.metric("喝水", f"{health['water_cups']}杯")
        with h4:
            st.metric("BMI", f"{health['bmi']}")

    with col4:
        st.markdown("#### 📝 待办清单")
        todos = get_todos()
        pending = [t for t in todos if not t["done"]]
        done_list = [t for t in todos if t["done"]]

        # 待办进度
        total = len(todos)
        completed = len(done_list)
        st.progress(completed / total if total > 0 else 0,
                     text=f"完成进度 {completed}/{total}")

        # 按优先级分组显示
        for t in sorted(pending, key=lambda x: x["priority"]):
            st.markdown(
                f"{'🔴' if '紧急' in t['priority'] else '🟡' if '重要' in t['priority'] else '🟢'} "
                f"**{t['task']}**  
                f"📅 {t['deadline']} · 📂 {t.get('category', '其他')}"
            )

        if done_list:
            with st.expander(f"✅ 已完成 ({len(done_list)})"):
                for t in done_list:
                    st.markdown(f"~~{t['task']}~~")

        st.divider()

        # 考试倒计时面板
        st.markdown("#### 🎯 考试倒计时")
        exams = get_upcoming_exams()
        for e in exams:
            progress = max(0, 1 - e["days_left"] / 30)
            if e["days_left"] <= 7:
                st.error(f"🔴 **{e['course']}** — **{e['days_left']}** 天后 | {e['type']}")
            else:
                st.info(f"🔵 **{e['course']}** — **{e['days_left']}** 天后 | {e['type']}")
            st.progress(min(progress, 1.0))

    st.divider()

    # ===== 第三行：旅行规划 (Day 2 新增) =====
    st.markdown("#### ✈️ 旅行规划")
    travel = get_travel_plan()

    t1, t2 = st.columns([2, 1])
    with t1:
        st.markdown(f"### {travel['trip_name']}")
        st.markdown(
            f"📅 **日期**：{travel['date']}  |  "
            f"💰 **预算**：¥{travel['budget']:.0f}  |  "
            f"👥 **同行**：{'、'.join(travel['companions'])}  |  "
            f"📊 **状态**：{travel['status']}"
        )

        st.markdown("**📍 行程时间线**")
        for item in travel["itinerary"]:
            cost_str = f"¥{item['cost']:.0f}" if item["cost"] > 0 else "免费"
            st.markdown(
                f'<div class="travel-item">
                f"<strong>{item['icon']} {item['time']}</strong> — "
                f"{item['activity']}  \n"
                f"<small>📍 {item['location']} · 💰 {cost_str}</small>"
                f'</div>',
                unsafe_allow_html=True,
            )

    with t2:
        st.markdown("**💰 费用预估**")
        st.metric("总预估", f"¥{travel['total_estimated_cost']:.0f}",
                   delta=f"预算内 ¥{travel['budget'] - travel['total_estimated_cost']:.0f}")

        st.markdown("**🎒 携带清单**")
        for item in travel["packing_list"]:
            st.checkbox(item, key=f"pack_{item}")


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
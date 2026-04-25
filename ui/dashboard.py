"""
UniLife OS — 数据看板 Tab（R4 新增）

布局不变：
- 上半：左侧消费饼图 + 消费指标；右侧本周课表
- 下半：左侧 7 天健康趋势（步数折线 + 睡眠柱状）；右侧旅行计划时间线 + 必带清单
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.mock_data import (
    get_finance, get_health, get_schedule, get_travel_plan,
)
from modules.persistence import get_packing_checked, update_packing

from ui.components import travel_item_html, toast_and_rerun


def _finance_section(col) -> None:
    with col:
        st.markdown("#### 💰 消费构成")
        finance = get_finance()
        cat_data = pd.DataFrame(
            list(finance["categories"].items()), columns=["类别", "金额"],
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
            st.metric("日均消费", f"¥{int(finance['daily_avg_spent'])}")
        with m2:
            st.metric("剩余天数", f"{finance['days_left_in_month']}天")
        with m3:
            st.metric("建议日限", f"¥{int(finance['suggested_daily'])}")


def _schedule_section(col) -> None:
    with col:
        st.markdown("#### 📅 本周课表")
        df = pd.DataFrame(get_schedule())
        st.dataframe(
            df[["weekday", "time", "course", "location", "type"]].rename(
                columns={
                    "weekday": "星期", "time": "时间", "course": "课程",
                    "location": "地点", "type": "类型",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )


def _health_trend_section(col) -> None:
    with col:
        st.markdown("#### 🏥 7 天健康趋势")
        health = get_health()
        history = health.get("history", [])
        if not history:
            st.info("暂无历史健康数据")
            return

        df_health = pd.DataFrame(history)
        df_health["date"] = pd.to_datetime(df_health["date"])
        df_health = df_health.sort_values("date")

        st.markdown("**👣 每日步数**")
        fig_steps = px.line(
            df_health, x="date", y="steps", markers=True,
            labels={"date": "日期", "steps": "步数"},
        )
        fig_steps.add_hline(
            y=health["step_goal"], line_dash="dash", line_color="red",
            annotation_text=f"目标 {health['step_goal']:,}",
        )
        fig_steps.update_layout(
            margin=dict(t=20, b=20, l=20, r=20), height=250,
            showlegend=False, dragmode=False,
        )
        st.plotly_chart(fig_steps, use_container_width=True,
                        config={"displayModeBar": False, "scrollZoom": False})

        st.markdown("**😴 每日睡眠**")
        fig_sleep = px.bar(
            df_health, x="date", y="sleep",
            labels={"date": "日期", "sleep": "睡眠(小时)"},
            color="sleep",
            color_continuous_scale=["#ff6b6b", "#ffa502", "#7bed9f"],
        )
        fig_sleep.add_hline(
            y=7, line_dash="dash", line_color="green", annotation_text="建议 7h",
        )
        fig_sleep.update_layout(
            margin=dict(t=20, b=20, l=20, r=20), height=250,
            showlegend=False, coloraxis_showscale=False, dragmode=False,
        )
        st.plotly_chart(fig_sleep, use_container_width=True,
                        config={"displayModeBar": False, "scrollZoom": False})


def _travel_section(col) -> None:
    with col:
        st.markdown("#### 🗺️ 旅行计划")
        travel = get_travel_plan()
        if travel is None:
            st.info("暂无旅行计划，可以通过 AI 对话创建新的旅行计划。")
            return

        companions = travel.get("companions", [])
        if isinstance(companions, str):
            companions_str = companions
        else:
            companions_str = "、".join(companions) if companions else "独自出行"
        st.markdown(
            f"**{travel['trip_name']}**  \n"
            f"📆 {travel['date']} | 👥 {companions_str}"
        )

        t_m1, t_m2 = st.columns(2)
        with t_m1:
            st.metric("预算", f"¥{int(travel['budget'])}")
        with t_m2:
            st.metric(
                "预估花费",
                f"¥{int(travel['total_estimated_cost'])}",
                delta=f"剩余 ¥{int(travel['budget'] - travel['total_estimated_cost'])}",
            )

        st.markdown("**📍 行程时间线**")
        if travel["itinerary"]:
            for stop in travel["itinerary"]:
                cost_str = f"¥{int(stop['cost'])}" if stop["cost"] > 0 else "免费"
                html = travel_item_html(
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
                pack_key = f"pack_{item}"
                is_checked = item in packing_checked
                checked = st.checkbox(item, value=is_checked, key=pack_key)
                if checked and not is_checked:
                    update_packing(item, True)
                    toast_and_rerun("🎒 已保存", "💾")
                elif not checked and is_checked:
                    update_packing(item, False)
                    toast_and_rerun("🎒 已取消", "💾")


def render_dashboard_tab() -> None:
    st.markdown("### 📊 个人数据看板")

    col1, col2 = st.columns(2)
    _finance_section(col1)
    _schedule_section(col2)

    st.divider()

    col3, col4 = st.columns(2)
    _health_trend_section(col3)
    _travel_section(col4)

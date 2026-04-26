from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.mock_data import get_finance, get_health, get_schedule, get_travel_plan
from modules.persistence import get_packing_checked, update_packing
from ui.components import ICON_CHART, render_section_heading, toast_and_rerun, travel_item_html
from ui.theme import (
    BAR_PALETTE,
    DASHBOARD_PALETTE,
    MORANDI_BLUE,
    MORANDI_COPPER,
    MORANDI_VIOLET,
    MUTED,
    PLOTLY_CONFIG,
    apply_chart_theme,
)


def _finance_section(col) -> None:
    with col:
        st.markdown("#### 消费构成")
        finance = get_finance()

        cat_data = pd.DataFrame(
            list(finance["categories"].items()),
            columns=["类别", "金额"],
        )
        fig = px.pie(
            cat_data,
            values="金额",
            names="类别",
            color_discrete_sequence=DASHBOARD_PALETTE,
            hole=0.48,
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="rgba(255,250,242,0.95)", width=2)),
            hovertemplate="<b>%{label}</b><br>金额: ¥%{value:.0f}<br>占比: %{percent}<extra></extra>",
        )
        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.18,
                xanchor="center",
                x=0.5,
                font=dict(color=MUTED),
            ),
        )
        st.plotly_chart(apply_chart_theme(fig, 330), width="stretch", config=PLOTLY_CONFIG)

        st.markdown("**消费指标**")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("日均消费", f"¥{int(finance['daily_avg_spent'])}", border=True)
        with m2:
            st.metric("剩余天数", f"{finance['days_left_in_month']}天", border=True)
        with m3:
            st.metric("建议日限", f"¥{int(finance['suggested_daily'])}", border=True)


def _schedule_section(col) -> None:
    with col:
        st.markdown("#### 本周课表")
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
            width="stretch",
            hide_index=True,
        )


def _health_trend_section(col) -> None:
    with col:
        st.markdown("#### 7 天健康趋势")
        health = get_health()
        history = health.get("history", [])
        if not history:
            st.info("暂无历史健康数据")
            return

        df_health = pd.DataFrame(history)
        df_health["date"] = pd.to_datetime(df_health["date"])
        df_health = df_health.sort_values("date")

        st.markdown("**每日步数**")
        fig_steps = px.line(
            df_health,
            x="date",
            y="steps",
            markers=True,
            labels={"date": "日期", "steps": "步数"},
        )
        fig_steps.update_traces(
            line_color=MORANDI_BLUE,
            marker_color=MORANDI_BLUE,
            line_width=3,
        )
        fig_steps.add_hline(
            y=health["step_goal"],
            line_dash="dot",
            line_color=MORANDI_COPPER,
            annotation_text=f"目标 {health['step_goal']:,}",
        )
        fig_steps.update_layout(showlegend=False)
        st.plotly_chart(apply_chart_theme(fig_steps, 250), width="stretch", config=PLOTLY_CONFIG)

        st.markdown("**每日睡眠**")
        fig_sleep = px.bar(
            df_health,
            x="date",
            y="sleep",
            labels={"date": "日期", "sleep": "睡眠(小时)"},
            color="sleep",
            color_continuous_scale=BAR_PALETTE,
        )
        fig_sleep.add_hline(
            y=7,
            line_dash="dot",
            line_color=MORANDI_VIOLET,
            annotation_text="建议 7h",
        )
        fig_sleep.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(apply_chart_theme(fig_sleep, 250), width="stretch", config=PLOTLY_CONFIG)


def _travel_section(col) -> None:
    with col:
        st.markdown("#### 旅行计划")
        travel = get_travel_plan()
        if travel is None:
            st.info("暂无旅行计划，可以通过 AI 对话创建新的旅行计划。")
            return

        companions = travel.get("companions", [])
        companions_str = (
            companions
            if isinstance(companions, str)
            else "、".join(companions) if companions else "独自出行"
        )
        st.markdown(
            f"**{travel['trip_name']}**  \n"
            f"📆 {travel['date']} · 👥 {companions_str}"
        )

        t_m1, t_m2 = st.columns(2)
        with t_m1:
            st.metric("预算", f"¥{int(travel['budget'])}", border=True)
        with t_m2:
            st.metric(
                "预估花费",
                f"¥{int(travel['total_estimated_cost'])}",
                delta=f"剩余 ¥{int(travel['budget'] - travel['total_estimated_cost'])}",
                border=True,
            )

        st.markdown("**行程时间线**")
        if travel["itinerary"]:
            for stop in travel["itinerary"]:
                cost_str = f"¥{int(stop['cost'])}" if stop["cost"] > 0 else "免费"
                st.markdown(
                    travel_item_html(
                        stop.get("icon", "📍"),
                        stop["time"],
                        stop["activity"],
                        stop["location"],
                        cost_str,
                    ),
                    unsafe_allow_html=True,
                )
        else:
            st.caption("暂无行程，可通过 AI 对话添加行程站点")

        packing_list = travel.get("packing_list", [])
        if packing_list:
            st.markdown("**必带清单**")
            packing_checked = get_packing_checked()
            for item in packing_list:
                pack_key = f"pack_{item}"
                is_checked = item in packing_checked
                checked = st.checkbox(item, value=is_checked, key=pack_key)
                if checked and not is_checked:
                    update_packing(item, True)
                    toast_and_rerun("已保存", "💾")
                elif not checked and is_checked:
                    update_packing(item, False)
                    toast_and_rerun("已取消", "💾")


def render_dashboard_tab() -> None:
    render_section_heading("Personal data board", "个人数据看板", ICON_CHART, "dashboard-heading")
    top_left, top_right = st.columns([1.18, 0.82], gap="large")
    _finance_section(top_left)
    _schedule_section(top_right)

    st.divider()

    bottom_left, bottom_right = st.columns([1.08, 0.92], gap="large")
    _health_trend_section(bottom_left)
    _travel_section(bottom_right)

from __future__ import annotations

PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": False}
CHART_MARGIN = dict(t=18, b=18, l=18, r=18)

TEXT = "#251E19"
MUTED = "#62584F"
GRID = "rgba(37,30,25,0.13)"

MORANDI_COPPER = "#9A735F"
MORANDI_BLUE = "#7D897C"
MORANDI_CLAY = "#B27C70"
MORANDI_VIOLET = "#827983"
MORANDI_TEAL = "#77838A"
MORANDI_SAND = "#B4A07B"

DASHBOARD_PALETTE = [
    MORANDI_COPPER,
    MORANDI_SAND,
    MORANDI_TEAL,
    MORANDI_BLUE,
    MORANDI_VIOLET,
    MORANDI_CLAY,
]

BAR_PALETTE = [
    MORANDI_COPPER,
    MORANDI_SAND,
    MORANDI_TEAL,
    MORANDI_BLUE,
    MORANDI_VIOLET,
]


def apply_chart_theme(fig, height: int):
    fig.update_layout(
        height=height,
        margin=CHART_MARGIN,
        dragmode=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, family="PingFang SC, Microsoft YaHei UI, sans-serif"),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, color=MUTED)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, color=MUTED)
    return fig

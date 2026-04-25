from __future__ import annotations

PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": False}
CHART_MARGIN = dict(t=18, b=18, l=18, r=18)

TEXT = "#332A1F"
MUTED = "#887A6B"
GRID = "rgba(139,90,43,0.13)"

MORANDI_COPPER = "#8B5A2B"
MORANDI_BLUE = "#887A6B"
MORANDI_CLAY = "#C4554B"
MORANDI_VIOLET = "#BBB0A3"
MORANDI_TEAL = "#5B8C5A"
MORANDI_SAND = "#C49A4B"

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
        font=dict(color=TEXT, family="Geist Sans, SF Pro Display, sans-serif"),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, color=MUTED)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, color=MUTED)
    return fig

from __future__ import annotations

PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": False}
CHART_MARGIN = dict(t=18, b=18, l=18, r=18)

TEXT = "#211B17"
MUTED = "#62564E"
GRID = "rgba(33,27,23,0.13)"

MORANDI_COPPER = "#8E6A5A"
MORANDI_BLUE = "#6F7D73"
MORANDI_CLAY = "#A47D6B"
MORANDI_VIOLET = "#827983"
MORANDI_TEAL = "#73847E"
MORANDI_SAND = "#B09A76"

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

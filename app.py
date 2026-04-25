import streamlit as st

from config import APP_NAME, APP_ICON
from ui.styles import inject_css, inject_pwa_meta
from ui.layout import render_app_layout


st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
inject_pwa_meta()


def main() -> None:
    render_app_layout()


if __name__ == "__main__":
    main()

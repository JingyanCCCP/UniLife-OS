from __future__ import annotations

import streamlit as st

from config import DEEPSEEK_API_KEY
from modules.chat_engine import chat_agent, trim_messages
from modules.mock_data import build_context_summary
from modules.persistence import save_chat_history, load_chat_history
from modules.tools import TOOL_SCHEMAS, TOOL_DISPLAY_NAMES, execute_tool
from prompts.system_prompt import build_system_prompt
from ui.components import generate_welcome

_AVATAR_USER = "🧑‍🎓"
_AVATAR_ASSISTANT = "🎓"


def _render_message_history(chat_container) -> None:
    with chat_container:
        for msg in st.session_state.messages:
            avatar = _AVATAR_ASSISTANT if msg["role"] == "assistant" else _AVATAR_USER
            with st.chat_message(msg["role"], avatar=avatar):
                tool_log = msg.get("tool_log")
                if tool_log:
                    for tc in tool_log:
                        display_name = TOOL_DISPLAY_NAMES.get(tc["name"], tc["name"])
                        with st.expander(f"工具调用 · {display_name}", expanded=False):
                            st.code(tc["result"], language=None)
                st.markdown(msg["content"])

        if not st.session_state.messages:
            with st.chat_message("assistant", avatar=_AVATAR_ASSISTANT):
                welcome = generate_welcome()
                st.markdown(welcome)
                st.session_state.messages.append(
                    {"role": "assistant", "content": welcome}
                )


def _handle_user_prompt(prompt: str, chat_container) -> None:
    with chat_container:
        with st.chat_message("user", avatar=_AVATAR_USER):
            st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    context = build_context_summary()
    system_prompt = build_system_prompt(context)
    full_messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages:
        full_messages.append({"role": m["role"], "content": m["content"]})
    full_messages = trim_messages(full_messages)

    with chat_container:
        with st.chat_message("assistant", avatar=_AVATAR_ASSISTANT):
            with st.status("正在思考...", expanded=True) as status:
                response_text, tool_log = chat_agent(
                    full_messages, TOOL_SCHEMAS, execute_tool
                )
                if tool_log:
                    for tc in tool_log:
                        display_name = TOOL_DISPLAY_NAMES.get(tc["name"], tc["name"])
                        status.update(label=f"调用工具：{display_name}")
                        with st.expander(f"工具调用 · {display_name}", expanded=False):
                            st.code(tc["result"], language=None)
                status.update(label="完成", state="complete", expanded=False)
            st.markdown(response_text)

    msg_record = {"role": "assistant", "content": response_text}
    if tool_log:
        msg_record["tool_log"] = tool_log
    st.session_state.messages.append(msg_record)
    save_chat_history(st.session_state.messages)


def render_chat_tab() -> None:
    if "messages" not in st.session_state:
        saved = load_chat_history()
        st.session_state.messages = saved if saved else []

    st.markdown(
        '<div class="section-heading chat-heading">'
        '<span>Agent workspace</span>'
        '<h2>AI 对话</h2>'
        '</div>',
        unsafe_allow_html=True,
    )
    chat_container = st.container(height=500)
    _render_message_history(chat_container)

    if not DEEPSEEK_API_KEY:
        st.warning(
            "在项目根目录的 `.env` 文件中配置 `DEEPSEEK_API_KEY` 后重启应用即可使用 AI 对话功能。"
        )
        st.chat_input("请先配置 DeepSeek API Key...", disabled=True)
        return

    prompt = st.chat_input(
        "直接说出你要做的事，例如：今天有什么课、帮我记一笔奶茶 18 元、分析这个月花销"
    )
    if prompt:
        _handle_user_prompt(prompt, chat_container)

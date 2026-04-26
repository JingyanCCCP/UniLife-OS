from __future__ import annotations

import base64
import io

import streamlit as st

from config import DEEPSEEK_API_KEY
from modules.chat_engine import chat_agent, trim_messages
from modules.mock_data import build_context_summary
from modules.persistence import load_chat_history, save_chat_history
from modules.tools import TOOL_DISPLAY_NAMES, TOOL_SCHEMAS, execute_tool
from prompts.system_prompt import build_system_prompt
from ui.components import ICON_SPARKLES, generate_welcome, render_section_heading

_AVATAR_USER = "🧑‍🎓"
_AVATAR_ASSISTANT = "🎓"

_VISION_TOOL_NAMES = {
    "record_expense_from_image",
    "import_courses_from_image",
    "log_food_calories",
    "check_packing_from_image",
}

_IMAGE_HINT = (
    "\n\n[系统消息：用户已上传图片。请根据用户文字判断：拍小票→record_expense_from_image，"
    "拍课表→import_courses_from_image，拍食物→log_food_calories，拍行李→check_packing_from_image。"
    "image_b64 参数留空字符串即可，系统会自动注入。]"
)


def _ensure_pending_image(uploaded_file) -> None:
    file_bytes = uploaded_file.getvalue()
    file_hash = hash(file_bytes)
    if st.session_state.get("_uploaded_image_hash") == file_hash:
        return

    try:
        from PIL import Image

        img = Image.open(io.BytesIO(file_bytes))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        img.thumbnail((1024, 1024))

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80, optimize=True)
        compressed = buf.getvalue()

        st.session_state.pending_image_b64 = base64.b64encode(compressed).decode("ascii")
        st.session_state.pending_image_preview = compressed
        st.session_state._uploaded_image_hash = file_hash
    except Exception as exc:
        st.error(f"图片处理失败：{type(exc).__name__}: {exc}")


def _clear_pending_image() -> None:
    for key in (
        "pending_image_b64",
        "pending_image_preview",
        "_uploaded_image_hash",
        "chat_image",
    ):
        st.session_state.pop(key, None)


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

                preview_b64 = msg.get("_image_preview_b64")
                if preview_b64:
                    st.image(base64.b64decode(preview_b64), width=200)
                elif msg.get("_image_preview"):
                    st.image(msg["_image_preview"], width=200)

                st.markdown(msg["content"])

        if not st.session_state.messages:
            with st.chat_message("assistant", avatar=_AVATAR_ASSISTANT):
                welcome = generate_welcome()
                st.markdown(welcome)
                st.session_state.messages.append(
                    {"role": "assistant", "content": welcome}
                )


def _handle_user_prompt(prompt: str, chat_container) -> None:
    pending_b64 = st.session_state.get("pending_image_b64")
    pending_preview = st.session_state.get("pending_image_preview")

    with chat_container:
        with st.chat_message("user", avatar=_AVATAR_USER):
            if pending_preview:
                st.image(pending_preview, width=200)
            st.markdown(prompt)

    user_record = {"role": "user", "content": prompt}
    if pending_b64:
        user_record["_image_preview_b64"] = pending_b64
    st.session_state.messages.append(user_record)

    context = build_context_summary()
    system_prompt = build_system_prompt(context)
    full_messages = [{"role": "system", "content": system_prompt}]
    last_idx = len(st.session_state.messages) - 1
    for i, msg in enumerate(st.session_state.messages):
        content = msg["content"]
        if i == last_idx and msg["role"] == "user" and pending_b64:
            content += _IMAGE_HINT
        full_messages.append({"role": msg["role"], "content": content})
    full_messages = trim_messages(full_messages)

    def _exec_with_image(name: str, args: dict) -> str:
        if pending_b64 and name in _VISION_TOOL_NAMES and not args.get("image_b64"):
            args = {**args, "image_b64": pending_b64}
        return execute_tool(name, args)

    with chat_container:
        with st.chat_message("assistant", avatar=_AVATAR_ASSISTANT):
            with st.status("正在思考...", expanded=True) as status:
                response_text, tool_log = chat_agent(
                    full_messages, TOOL_SCHEMAS, _exec_with_image
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

    if pending_b64:
        _clear_pending_image()


def _render_image_upload() -> None:
    has_pending = bool(st.session_state.get("pending_image_b64"))
    label = "📷 已就绪：1 张图片（点击展开预览或更换）" if has_pending else "📷 上传图片（小票/课表/食物/行李）"

    with st.expander(label, expanded=has_pending):
        uploaded = st.file_uploader(
            "选择图片或从相册选取（支持 jpg/jpeg/png）",
            type=["jpg", "jpeg", "png"],
            key="chat_image",
            label_visibility="collapsed",
        )
        if uploaded is not None:
            _ensure_pending_image(uploaded)

        preview = st.session_state.get("pending_image_preview")
        if preview:
            cols = st.columns([3, 1])
            with cols[0]:
                st.image(preview, width=200, caption="已就绪，发送文字时会一起处理")
            with cols[1]:
                if st.button("清除", key="clear_pending_btn", width="stretch"):
                    _clear_pending_image()
                    st.rerun()


def render_chat_tab() -> None:
    if "messages" not in st.session_state:
        saved = load_chat_history()
        st.session_state.messages = saved if saved else []

    render_section_heading("Agent workspace", "AI 对话", ICON_SPARKLES, "chat-heading")
    chat_container = st.container(height=500)
    _render_message_history(chat_container)

    if not DEEPSEEK_API_KEY:
        st.warning(
            "在项目根目录的 `.env` 文件中配置 `DEEPSEEK_API_KEY` 后重启应用即可使用 AI 对话功能。"
        )
        st.chat_input("请先配置 DeepSeek API Key...", disabled=True)
        return

    _render_image_upload()
    pending = st.session_state.get("pending_image_b64")
    placeholder = (
        "图片已就绪，告诉我你想做什么（例如「帮我记账」「导入这周课表」）"
        if pending
        else "直接说出你要做的事，例如：今天有什么课、帮我记一笔奶茶 18 元、分析这个月花销"
    )

    prompt = st.chat_input(placeholder)
    if prompt:
        _handle_user_prompt(prompt, chat_container)

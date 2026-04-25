"""
UniLife OS — AI 对话 Tab（R4 新增，R7-T4 加多模态上传）

行为与 R1 前一致：
- session_state.messages 在首次渲染时从持久化历史加载。
- st.container(height=500) 是聊天滚动区；CSS 会重写其高度为 calc(100vh - 280px)。
- 不要把 st.chat_input 移到根作用域（Phase 7 曾尝试导致 rerun 循环，见 CLAUDE.md）。

R7-T4 新增：
- chat_input 上方新增「📷 上传图片」expander，含 file_uploader。
- 上传后用 Pillow 压缩到 ≤ 1024px JPEG q=80，base64 后存 session_state.pending_image_b64。
- 提交时：在 user message 末尾追加系统标记，提醒模型走 vision 工具；
  通过 _exec_with_image 包装层把 b64 注入到 vision 工具的 args 里（DeepSeek 不需要看到 b64）。
- 提交完成后清空 pending image。
"""
from __future__ import annotations

import base64
import io
import streamlit as st

from config import DEEPSEEK_API_KEY
from modules.chat_engine import chat_agent, trim_messages
from modules.mock_data import build_context_summary
from modules.persistence import save_chat_history, load_chat_history
from modules.tools import TOOL_SCHEMAS, TOOL_DISPLAY_NAMES, execute_tool
from prompts.system_prompt import build_system_prompt

from ui.components import generate_welcome


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


# ---------------------------------------------------------------------------
# 图片处理 helper
# ---------------------------------------------------------------------------

def _ensure_pending_image(uploaded_file) -> None:
    """把上传文件压缩 + 编码为 base64 存 session_state。同一张图不重复处理。"""
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
        b64 = base64.b64encode(compressed).decode("ascii")

        st.session_state.pending_image_b64 = b64
        st.session_state.pending_image_preview = compressed
        st.session_state._uploaded_image_hash = file_hash
    except Exception as e:
        st.error(f"图片处理失败：{type(e).__name__}: {e}")


def _clear_pending_image() -> None:
    for k in ("pending_image_b64", "pending_image_preview",
              "_uploaded_image_hash", "chat_image"):
        st.session_state.pop(k, None)


# ---------------------------------------------------------------------------
# 渲染 / 提交
# ---------------------------------------------------------------------------

def _render_message_history(chat_container) -> None:
    with chat_container:
        for msg in st.session_state.messages:
            avatar = "🎓" if msg["role"] == "assistant" else "🧑‍🎓"
            with st.chat_message(msg["role"], avatar=avatar):
                tool_log = msg.get("tool_log")
                if tool_log:
                    for tc in tool_log:
                        display_name = TOOL_DISPLAY_NAMES.get(tc["name"], tc["name"])
                        with st.expander(f"🔧 {display_name}", expanded=False):
                            st.code(tc["result"], language=None)
                # 历史用户消息中如果有图片缩略图，显示
                if msg.get("_image_preview"):
                    st.image(msg["_image_preview"], width=200)
                st.markdown(msg["content"])

        if not st.session_state.messages:
            with st.chat_message("assistant", avatar="🎓"):
                welcome = generate_welcome()
                st.markdown(welcome)
                st.session_state.messages.append(
                    {"role": "assistant", "content": welcome}
                )


def _handle_user_prompt(prompt: str, chat_container) -> None:
    pending_b64 = st.session_state.get("pending_image_b64")
    pending_preview = st.session_state.get("pending_image_preview")

    with chat_container:
        with st.chat_message("user", avatar="🧑‍🎓"):
            if pending_preview:
                st.image(pending_preview, width=200)
            st.markdown(prompt)

    user_record = {"role": "user", "content": prompt}
    if pending_preview:
        user_record["_image_preview"] = pending_preview
    st.session_state.messages.append(user_record)

    context = build_context_summary()
    system_prompt = build_system_prompt(context)

    full_messages = [{"role": "system", "content": system_prompt}]
    last_idx = len(st.session_state.messages) - 1
    for i, m in enumerate(st.session_state.messages):
        content = m["content"]
        # 仅在最后一条 user message 上拼接图片标记
        if i == last_idx and m["role"] == "user" and pending_b64:
            content = content + _IMAGE_HINT
        full_messages.append({"role": m["role"], "content": content})
    full_messages = trim_messages(full_messages)

    def _exec_with_image(name: str, args: dict) -> str:
        """工具执行包装层：vision 工具自动注入 pending_image_b64。"""
        if pending_b64 and name in _VISION_TOOL_NAMES and not args.get("image_b64"):
            args = {**args, "image_b64": pending_b64}
        return execute_tool(name, args)

    with chat_container:
        with st.chat_message("assistant", avatar="🎓"):
            with st.status("🤔 思考中...", expanded=True) as status:
                response_text, tool_log = chat_agent(
                    full_messages, TOOL_SCHEMAS, _exec_with_image
                )
                if tool_log:
                    for tc in tool_log:
                        display_name = TOOL_DISPLAY_NAMES.get(tc["name"], tc["name"])
                        status.update(label=f"🔧 调用工具: {display_name}")
                        with st.expander(f"🔧 {display_name}", expanded=False):
                            st.code(tc["result"], language=None)
                status.update(label="✅ 完成", state="complete", expanded=False)
            st.markdown(response_text)

    msg_record = {"role": "assistant", "content": response_text}
    if tool_log:
        msg_record["tool_log"] = tool_log
    st.session_state.messages.append(msg_record)
    save_chat_history(st.session_state.messages)

    # 提交完成，清空 pending image（下一次上传重新填充）
    if pending_b64:
        _clear_pending_image()


# ---------------------------------------------------------------------------
# 图片上传 UI（chat_input 上方）
# ---------------------------------------------------------------------------

def _render_image_upload() -> None:
    """chat_input 上方的图片上传区，默认折叠；上传后展示缩略图。"""
    has_pending = bool(st.session_state.get("pending_image_b64"))
    label = "📷 已就绪：1 张图片（点击展开预览或更换）" if has_pending else "📷 上传图片（拍小票/课表/食物/行李）"

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
                st.image(preview, width=200,
                         caption="✨ 已就绪，发送下方文字时会一起送 AI 处理")
            with cols[1]:
                if st.button("🗑️ 清除", key="clear_pending_btn",
                             use_container_width=True):
                    _clear_pending_image()
                    st.rerun()


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def render_chat_tab() -> None:
    if "messages" not in st.session_state:
        saved = load_chat_history()
        st.session_state.messages = saved if saved else []

    chat_container = st.container(height=500)
    _render_message_history(chat_container)

    if not DEEPSEEK_API_KEY:
        st.warning(
            "💡 在项目根目录的 `.env` 文件中配置 `DEEPSEEK_API_KEY` 后重启应用即可使用 AI 对话功能。"
        )
        st.chat_input("请先配置 DeepSeek API Key...", disabled=True)
        return

    _render_image_upload()

    pending = st.session_state.get("pending_image_b64")
    placeholder = (
        "图片已就绪，告诉我你想做什么（例如「帮我记账」「导入这周课表」）"
        if pending
        else "和我聊聊吧，比如「我今天有什么课？」「帮我记一笔：奶茶 18 元」"
    )

    prompt = st.chat_input(placeholder)
    if prompt:
        _handle_user_prompt(prompt, chat_container)

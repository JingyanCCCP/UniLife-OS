"""
UniLife OS — DeepSeek 对话引擎（Agent 增强版）
支持 function calling 的 Agent 循环。
"""
from __future__ import annotations

import json
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

MAX_TOOL_ROUNDS = 5  # 防止无限循环
MAX_CONTEXT_MESSAGES = 20  # 非 system 消息上限，防止超出上下文窗口

# 模块级单例客户端，避免每次调用都创建新连接
_client: OpenAI | None = None


def trim_messages(messages: list[dict], max_messages: int = MAX_CONTEXT_MESSAGES) -> list[dict]:
    """
    裁剪消息列表：保留所有 system 消息 + 最近 max_messages 条非 system 消息。
    用于防止对话历史超出模型上下文窗口。
    """
    system_msgs = [m for m in messages if m.get("role") == "system"]
    non_system_msgs = [m for m in messages if m.get("role") != "system"]
    if len(non_system_msgs) > max_messages:
        non_system_msgs = non_system_msgs[-max_messages:]
    return system_msgs + non_system_msgs


def get_client() -> OpenAI:
    """获取 DeepSeek API 客户端（单例复用连接池）"""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
        )
    return _client


def _call_with_tools(messages: list[dict], tools: list[dict]) -> object:
    """单次非流式 API 调用（带 tools 参数）。"""
    client = get_client()
    return client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        tools=tools,
        temperature=0.7,
        max_tokens=1024,
    )


def chat_agent(messages: list[dict], tools: list[dict], execute_tool_fn) -> tuple[str, list[dict]]:
    """
    Agent 循环：自动调用工具并将结果反馈给模型，直到得到最终文本回复。

    参数:
        messages: 完整消息列表（含 system prompt）
        tools: 工具 schema 列表
        execute_tool_fn: 工具执行函数 (name, args) -> str

    返回:
        (final_text, tool_call_log)
        - final_text: 最终回复文本
        - tool_call_log: 工具调用记录列表 [{"name": ..., "args": ..., "result": ...}, ...]
    """
    working_messages = list(trim_messages(messages))
    tool_call_log = []

    for _round in range(MAX_TOOL_ROUNDS):
        try:
            response = _call_with_tools(working_messages, tools)
        except Exception as e:
            return f"⚠️ 连接出了点问题：{str(e)}\n请检查 API Key 是否正确配置。", tool_call_log

        choice = response.choices[0]
        assistant_msg = choice.message

        # 没有工具调用 → 返回最终文本
        if not assistant_msg.tool_calls:
            text = assistant_msg.content or ""
            # 检测输出截断
            if choice.finish_reason == "length":
                text += "\n\n⚠️ *回复过长被截断，可以让我继续说~*"
            return text, tool_call_log

        # 有工具调用 → 执行并继续
        # 将 assistant 消息（含 tool_calls）加入对话
        working_messages.append({
            "role": "assistant",
            "content": assistant_msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in assistant_msg.tool_calls
            ],
        })

        # 逐个执行工具
        for tc in assistant_msg.tool_calls:
            func_name = tc.function.name
            try:
                func_args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                func_args = {}

            result = execute_tool_fn(func_name, func_args)

            tool_call_log.append({
                "name": func_name,
                "args": func_args,
                "result": result,
            })

            # 将工具结果作为 role="tool" 消息加入
            working_messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    # 超过最大轮次，做最后一次无工具调用获取总结
    try:
        final_response = get_client().chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=working_messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return final_response.choices[0].message.content or "", tool_call_log
    except Exception as e:
        return f"⚠️ 连接出了点问题：{str(e)}", tool_call_log

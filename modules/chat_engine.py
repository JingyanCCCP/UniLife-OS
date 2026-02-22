"""
UniLife OS — DeepSeek 对话引擎（Agent 增强版）
支持 function calling 的 Agent 循环，同时保留原有流式对话。
"""
import json
from openai import OpenAI
import streamlit as st
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

MAX_TOOL_ROUNDS = 5  # 防止无限循环


def get_client() -> OpenAI:
    """获取 DeepSeek API 客户端（兼容 OpenAI SDK）"""
    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
    )


def chat_stream(messages: list[dict]):
    """
    流式调用 DeepSeek-V3，返回生成器用于 Streamlit 流式输出。
    保留作为无工具的 fallback。
    """
    client = get_client()

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.8,
            max_tokens=1024,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    except Exception as e:
        yield f"⚠️ 连接出了点问题：{str(e)}\n请检查 API Key 是否正确配置。"


def chat_once(messages: list[dict]) -> str:
    """
    非流式调用，用于后台分析（如主动提醒生成）。
    """
    client = get_client()

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=512,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ 分析服务暂时不可用：{str(e)}"


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
    working_messages = list(messages)
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
            return assistant_msg.content or "", tool_call_log

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

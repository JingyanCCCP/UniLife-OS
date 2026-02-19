"""
UniLife OS — DeepSeek 对话引擎
"""
from openai import OpenAI
import streamlit as st
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

def get_client() -> OpenAI:
    """获取 DeepSeek API 客户端（兼容 OpenAI SDK）"""
    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
    )

def chat_stream(messages: list[dict]):
    """
    流式调用 DeepSeek-V3，返回生成器用于 Streamlit 流式输出。
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

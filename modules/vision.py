"""
UniLife OS — 豆包视觉客户端（R7-T2 新增）

封装 Volces Ark 视觉模型调用，提供 4 个识别函数：
- recognize_receipt: 小票 → {amount, item, category, confidence}
- recognize_food: 食物 → {name, calorie_estimate, confidence}
- recognize_schedule: 课表 → {courses: [{name, day, time, location}]}
- recognize_packing: 行李清单对照 → {found, missing, extra}

错误处理三类全部返回 dict 含 error 字段（不抛 traceback）：
- 未配置 DOUBAO_API_KEY → error 描述配置缺失
- 网络异常 / API 失败 → error 描述类型 + 消息
- 模型返回非合法 JSON → error 描述并附原文前 200 字

下游 Agent 工具（agent/tools/vision.py，R7-T3）通过这一层完成
"image → 结构化数据 → 链式调用 persistence" 的链路。
"""
from __future__ import annotations

import base64
import json
import re
from typing import Optional

from openai import OpenAI

from config import DOUBAO_API_KEY, DOUBAO_BASE_URL, DOUBAO_VISION_MODEL


_client: Optional[OpenAI] = None

_VALID_EXPENSE_CATEGORIES = {"餐饮", "交通", "购物", "学习用品", "娱乐", "其他"}


# ---------------------------------------------------------------------------
# 客户端单例
# ---------------------------------------------------------------------------

def _get_client() -> Optional[OpenAI]:
    """单例豆包 OpenAI 兼容客户端。未配置 KEY 时返回 None。"""
    global _client
    if not DOUBAO_API_KEY:
        return None
    if _client is None:
        _client = OpenAI(api_key=DOUBAO_API_KEY, base_url=DOUBAO_BASE_URL)
    return _client


# ---------------------------------------------------------------------------
# 内部 helper
# ---------------------------------------------------------------------------

def _bytes_to_data_url(image_bytes: bytes) -> str:
    """raw bytes → base64 data URL（默认 image/jpeg；豆包不强校验扩展名）。"""
    b64 = base64.b64encode(image_bytes).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def _strip_markdown_codeblock(text: str) -> str:
    """模型偶尔会返回 ```json\\n{...}\\n``` 包装，剥掉以便 json.loads。"""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def _vision_call(image_bytes: bytes, prompt: str) -> str:
    """统一豆包调用入口。返回模型的纯文本回复。

    抛 RuntimeError 表示配置缺失；其它异常由调用方兜底。
    本函数只做 IO + base64，不做 JSON 解析。
    """
    client = _get_client()
    if client is None:
        raise RuntimeError("未配置 DOUBAO_API_KEY，请在 .env 中设置后重启应用")

    data_url = _bytes_to_data_url(image_bytes)
    response = client.chat.completions.create(
        model=DOUBAO_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        temperature=0.1,
        max_tokens=1024,
    )
    return response.choices[0].message.content or ""


def _safe_json_call(image_bytes: bytes, prompt: str, fallback: dict) -> dict:
    """共享错误兜底：空图片 / KEY 缺失 / 网络异常 / JSON 解析失败 全返回 dict。

    成功路径：fallback ← 模型 JSON 字段，error 设为 None。
    失败路径：保留 fallback 默认值，error 描述失败原因。
    """
    if not image_bytes:
        return {**fallback, "error": "image_bytes 为空，请提供有效图片"}

    try:
        raw = _vision_call(image_bytes, prompt)
    except RuntimeError as e:
        return {**fallback, "error": str(e)}
    except Exception as e:
        return {**fallback, "error": f"豆包 API 调用失败：{type(e).__name__}: {e}"}

    cleaned = _strip_markdown_codeblock(raw)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        snippet = cleaned[:200]
        return {**fallback, "error": f"豆包返回不是合法 JSON：{snippet}"}

    if not isinstance(parsed, dict):
        return {
            **fallback,
            "error": f"豆包返回不是 JSON 对象：{type(parsed).__name__}",
        }

    return {**fallback, **parsed, "error": None}


# ---------------------------------------------------------------------------
# 4 个识别函数
# ---------------------------------------------------------------------------

def recognize_receipt(image_bytes: bytes) -> dict:
    """识别小票 → {amount, item, category, confidence, error}。"""
    prompt = (
        "你是校园记账助手。识别这张小票/账单图片。"
        "返回 JSON（不要 markdown 代码块），字段：\n"
        "- amount: 数字，消费总金额（人民币元）\n"
        "- item: 字符串，最显眼的商品名或店家名（≤ 20 字）\n"
        "- category: 必须是这 6 类之一：餐饮/交通/购物/学习用品/娱乐/其他\n"
        "- confidence: 0-1 的浮点数，识别置信度\n"
        "如果图中根本不是小票或无法识别，amount 返回 0、confidence 返回 < 0.3。"
    )
    fallback = {"amount": 0, "item": "", "category": "其他", "confidence": 0.0}
    result = _safe_json_call(image_bytes, prompt, fallback)
    if result.get("category") not in _VALID_EXPENSE_CATEGORIES:
        result["category"] = "其他"
    return result


def recognize_food(image_bytes: bytes) -> dict:
    """识别食物 → {name, calorie_estimate, confidence, error}。"""
    prompt = (
        "识别这张图片里的食物。返回 JSON（不要 markdown 代码块），字段：\n"
        "- name: 字符串，食物名（≤ 20 字）\n"
        "- calorie_estimate: 整数，估算卡路里（千卡）\n"
        "- confidence: 0-1 的浮点数\n"
        "如果不是食物或无法识别，name 返回空字符串、confidence 返回 < 0.3。"
    )
    fallback = {"name": "", "calorie_estimate": 0, "confidence": 0.0}
    return _safe_json_call(image_bytes, prompt, fallback)


def recognize_schedule(image_bytes: bytes) -> dict:
    """识别课表 → {courses: [{name, day, time, location}], error}。"""
    prompt = (
        "识别这张课表图片，提取所有课程信息。"
        "返回 JSON（不要 markdown 代码块），字段：\n"
        "- courses: 数组，每个元素含 name(课程名) / day(周一-周日) / "
        "time(如 08:00-09:40) / location(教室)\n"
        "如果图片不是课表或无法识别，courses 返回空数组 []。"
    )
    fallback = {"courses": []}
    result = _safe_json_call(image_bytes, prompt, fallback)
    if not isinstance(result.get("courses"), list):
        result["courses"] = []
    return result


def recognize_packing(image_bytes: bytes, expected_items: list[str]) -> dict:
    """对照行李清单 → {found, missing, extra, error}。"""
    if expected_items:
        expected_str = "、".join(expected_items)
        clause = f"预期清单：{expected_str}"
    else:
        clause = "用户未提供预期清单，仅识别图中物品并填到 found 里。"

    prompt = (
        f"识别图中的行李物品。{clause}\n"
        "返回 JSON（不要 markdown 代码块），字段：\n"
        "- found: 数组，预期清单中能在图中识别到的物品名\n"
        "- missing: 数组，预期清单中没在图中看到的物品名\n"
        "- extra: 数组，图中识别到但不在预期清单里的物品名\n"
        "如果无法识别图片，三个数组都返回空 []。"
    )
    fallback = {
        "found": [],
        "missing": list(expected_items or []),
        "extra": [],
    }
    result = _safe_json_call(image_bytes, prompt, fallback)
    for k in ("found", "missing", "extra"):
        if not isinstance(result.get(k), list):
            result[k] = []
    return result

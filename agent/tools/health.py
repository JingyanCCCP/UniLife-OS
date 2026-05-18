"""agent.tools.health — 健康相关工具（7 个）。

工具清单：query_health / record_water / record_exercise / record_mood /
         record_steps / record_sleep / set_exercise_goal
"""
from __future__ import annotations

from datetime import datetime

from modules.mock_data import get_health
from modules.persistence import (
    increment_water, log_exercise, log_mood, log_steps, log_sleep,
    set_exercise_goal as persist_set_exercise_goal,
)

from agent.tools._validators import (
    validate_steps, validate_sleep_hours, validate_exercise_goal,
)


SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "query_health",
            "description": "查询今日健康数据，包括步数、睡眠、喝水、运动、心情等。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_water",
            "description": "记录喝水，每次调用喝水杯数 +1。用户说'喝了一杯水'、'记一下喝水'时调用。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_exercise",
            "description": "记录运动打卡。用户说'我运动了'、'刚跑完步'时调用。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_mood",
            "description": "记录用户心情。用户表达情绪如'我今天很开心'、'有点烦'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "mood": {
                        "type": "string",
                        "description": "用户的心情描述，如 '😊 开心'、'😐 一般'、'😢 难过'",
                    }
                },
                "required": ["mood"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_steps",
            "description": "记录今日步数。用户说'今天走了8000步'、'步数6000'时调用。",
            "parameters": {
                "type": "object",
                "properties": {"steps": {"type": "integer", "description": "今日步数"}},
                "required": ["steps"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_sleep",
            "description": "记录昨晚睡眠情况。用户说'昨晚睡了7小时'、'睡眠8小时质量不错'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "hours": {"type": "number", "description": "睡眠时长（小时），如 7.5"},
                    "quality": {
                        "type": "string",
                        "description": "睡眠质量",
                        "enum": ["很好", "良好", "一般", "较差", "很差"],
                    },
                },
                "required": ["hours"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_exercise_goal",
            "description": "设置每周运动打卡目标次数。用户说'运动目标改成5次'、'每周锻炼4次'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {
                        "type": "integer",
                        "description": "每周运动目标次数（3-7）",
                        "enum": [3, 4, 5, 6, 7],
                    }
                },
                "required": ["goal"],
            },
        },
    },
]

DISPLAY_NAMES: dict[str, str] = {
    "query_health": "查询健康数据",
    "record_water": "记录喝水",
    "record_exercise": "运动打卡",
    "record_mood": "记录心情",
    "record_steps": "记录步数",
    "record_sleep": "记录睡眠",
    "set_exercise_goal": "设置运动目标",
}


def _exec_query_health(args: dict) -> str:
    health = get_health()
    days_since = (datetime.now() - datetime.strptime(health["last_exercise"], "%Y-%m-%d")).days
    lines = [
        "今日健康数据：",
        f"- 步数: {health['today_steps']:,}/{health['step_goal']:,}",
        f"- 日运动目标连续未达标: {health['exercise_target_miss_streak']} 天",
        f"- 睡眠: {health['sleep_hours']}h（{health['sleep_quality']}）",
        f"- 喝水: {health['water_cups']}/{health['water_goal']} 杯",
        f"- 本周运动: {health['exercise_this_week']}/{health['exercise_goal']} 次",
        f"- 距上次运动: {days_since} 天",
        f"- 心情: {health['mood']}",
        f"- 健康记录连续: {health['checkin_streak']} 天",
        f"- BMI: {health['bmi']} | 体重: {health['weight']}kg",
    ]
    return "\n".join(lines)


def _exec_record_water(args: dict) -> str:
    increment_water()
    health = get_health()
    return f"已记录喝水！今天累计喝了 {health['water_cups']} 杯水。"


def _exec_record_exercise(args: dict) -> str:
    is_new = log_exercise()
    if is_new:
        return "运动打卡成功！今天的运动已记录。"
    return "今天已经打过卡了，不用重复打卡哦~"


def _exec_record_mood(args: dict) -> str:
    mood = args["mood"]
    log_mood(mood)
    return f"已记录心情：{mood}"


def _exec_record_steps(args: dict) -> str:
    steps = args["steps"]
    if (err := validate_steps(steps)):
        return err
    steps = int(steps)
    log_steps(steps)
    return f"已记录今日步数：{steps:,} 步。"


def _exec_record_sleep(args: dict) -> str:
    hours = args["hours"]
    if (err := validate_sleep_hours(hours)):
        return err
    quality = args.get("quality", "一般")
    log_sleep(hours, quality)
    return f"已记录睡眠：{hours} 小时，质量「{quality}」。"


def _exec_set_exercise_goal(args: dict) -> str:
    goal = args["goal"]
    if (err := validate_exercise_goal(goal)):
        return err
    persist_set_exercise_goal(goal)
    return f"已将每周运动目标设置为 {goal} 次。"


def register(schemas: list, display_names: dict, registry: dict) -> None:
    schemas.extend(SCHEMAS)
    display_names.update(DISPLAY_NAMES)
    registry.update({
        "query_health": _exec_query_health,
        "record_water": _exec_record_water,
        "record_exercise": _exec_record_exercise,
        "record_mood": _exec_record_mood,
        "record_steps": _exec_record_steps,
        "record_sleep": _exec_record_sleep,
        "set_exercise_goal": _exec_set_exercise_goal,
    })

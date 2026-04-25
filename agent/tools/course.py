"""agent.tools.course — 课表相关工具（4 个）。

工具清单：query_schedule / add_course / delete_course / update_course
"""
from __future__ import annotations

from modules.mock_data import get_schedule
from modules.persistence import (
    add_course as persist_add_course,
    delete_course as persist_delete_course,
    update_course as persist_update_course,
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "query_schedule",
            "description": "查询课表。可以指定星期几查询，也可以不指定查询整周课表。",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {
                        "type": "string",
                        "description": "星期几，如 '周一'、'周二'。不传则查询整周。",
                        "enum": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_course",
            "description": "添加一门新课程到课表。用户说'帮我加一门课'、'周三下午有个选修课'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "weekday": {
                        "type": "string",
                        "description": "星期几",
                        "enum": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                    },
                    "time": {"type": "string", "description": "上课时间，如 '14:00-15:35'"},
                    "course": {"type": "string", "description": "课程名称"},
                    "location": {"type": "string", "description": "上课地点"},
                    "teacher": {"type": "string", "description": "任课教师（可选）"},
                    "type": {
                        "type": "string",
                        "description": "课程类型，默认'选修'",
                        "enum": ["必修", "选修", "实验"],
                    },
                },
                "required": ["weekday", "time", "course", "location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_course",
            "description": "从课表删除一门课程。用户说'帮我删掉体育课'、'这门课不上了'时调用。支持按课程 ID 或名称删除。",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_id": {"type": "integer", "description": "课程 ID（可选，优先使用）"},
                    "course_name": {
                        "type": "string",
                        "description": "课程名称（可选，当不知道 ID 时使用，模糊匹配）",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_course",
            "description": "修改课表中一门课程的信息。用户说'线性代数换教室了'、'高数改到周二'时调用。支持按课程 ID 或名称定位。",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_id": {"type": "integer", "description": "课程 ID（可选，优先使用）"},
                    "course_name": {"type": "string", "description": "课程名称（可选，当不知道 ID 时使用）"},
                    "course": {"type": "string", "description": "新的课程名称（重命名时使用）"},
                    "weekday": {
                        "type": "string",
                        "description": "新的星期几",
                        "enum": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                    },
                    "time": {"type": "string", "description": "新的上课时间"},
                    "location": {"type": "string", "description": "新的上课地点"},
                    "teacher": {"type": "string", "description": "新的任课教师"},
                    "type": {
                        "type": "string",
                        "description": "新的课程类型",
                        "enum": ["必修", "选修", "实验"],
                    },
                },
                "required": [],
            },
        },
    },
]

DISPLAY_NAMES: dict[str, str] = {
    "query_schedule": "查询课表",
    "add_course": "添加课程",
    "delete_course": "删除课程",
    "update_course": "修改课程",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_course_line(c: dict) -> str:
    """格式化单条课程信息，跳过空字段。"""
    parts = [c["location"]]
    if c.get("teacher"):
        parts.append(c["teacher"])
    parts.append(c["type"])
    return f"- {c['time']} {c['course']}（{'，'.join(parts)}）"


def _find_course_by_name(name: str) -> dict | str | None:
    """在当前课表中按名称匹配课程。
    返回: dict（唯一匹配）/ str（多个匹配时的错误提示）/ None（无匹配）。
    """
    schedule = get_schedule()
    for c in schedule:
        if c["course"] == name:
            return c
    matches = [c for c in schedule if name in c["course"]]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        names = "、".join(f"[{c['id']}]{c['course']}" for c in matches)
        return f"匹配到多门课程：{names}，请指定课程 ID 或更精确的名称。"
    return None


# ---------------------------------------------------------------------------
# Executors
# ---------------------------------------------------------------------------

def _exec_query_schedule(args: dict) -> str:
    day = args.get("day")
    if day:
        courses = [c for c in get_schedule() if c["weekday"] == day]
        if not courses:
            return f"{day}没有课，可以自由安排！"
        lines = [f"{day}的课程安排："]
        for c in courses:
            lines.append(_format_course_line(c))
        return "\n".join(lines)

    schedule = get_schedule()
    if not schedule:
        return "课表为空，还没有任何课程。"
    weekday_order = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    grouped: dict[str, list[dict]] = {}
    for c in schedule:
        grouped.setdefault(c["weekday"], []).append(c)
    lines = ["本周课表："]
    for wd in weekday_order:
        if wd in grouped:
            lines.append(f"\n📅 {wd}：")
            for c in grouped[wd]:
                lines.append(_format_course_line(c))
    return "\n".join(lines)


def _exec_add_course(args: dict) -> str:
    record = persist_add_course(
        args["weekday"], args["time"], args["course"], args["location"],
        args.get("teacher", ""), args.get("type", "选修"),
    )
    return (
        f"已添加课程：\n"
        f"- ID: {record['id']}\n"
        f"- {record['weekday']} {record['time']} {record['course']}\n"
        f"- 地点: {record['location']}\n"
        f"- 教师: {record['teacher'] or '未指定'}\n"
        f"- 类型: {record['type']}"
    )


def _exec_delete_course(args: dict) -> str:
    course_id = args.get("course_id")
    course_name = args.get("course_name")

    if not course_id and not course_name:
        return "请提供课程 ID 或课程名称。"

    if not course_id and course_name:
        found = _find_course_by_name(course_name)
        if isinstance(found, str):
            return found
        if not found:
            return f"未找到名为「{course_name}」的课程。"
        course_id = found["id"]

    course_id = int(course_id)
    schedule = get_schedule()
    target = next((c for c in schedule if c["id"] == course_id), None)
    if not target:
        return f"未找到 ID 为 {course_id} 的课程。"

    persist_delete_course(course_id)
    return f"已删除课程「{target['course']}」(ID={course_id})。"


def _exec_update_course(args: dict) -> str:
    course_id = args.get("course_id")
    course_name = args.get("course_name")

    if not course_id and not course_name:
        # Fallback：LLM 可能把 "course" 当作标识符而非修改字段
        if "course" in args:
            found = _find_course_by_name(args["course"])
            if isinstance(found, str):
                return found
            if found:
                course_id = found["id"]
            else:
                return f"未找到名为「{args['course']}」的课程。"
        else:
            return "请提供课程 ID 或课程名称来定位要修改的课程。"

    if not course_id and course_name:
        found = _find_course_by_name(course_name)
        if isinstance(found, str):
            return found
        if not found:
            return f"未找到名为「{course_name}」的课程。"
        course_id = found["id"]

    course_id = int(course_id)
    schedule = get_schedule()
    target = next((c for c in schedule if c["id"] == course_id), None)
    if not target:
        return f"未找到 ID 为 {course_id} 的课程。"
    verified_name = target["course"]

    fields = {}
    for key in ("weekday", "time", "course", "location", "teacher", "type"):
        if key in args and key not in ("course_id", "course_name") and args[key] is not None:
            fields[key] = args[key]

    if not fields:
        return "没有提供需要修改的字段。请指定要修改的内容（如时间、地点、教师等）。"

    persist_update_course(course_id, **fields)
    field_names = {"weekday": "星期", "time": "时间", "course": "课程名",
                   "location": "地点", "teacher": "教师", "type": "类型"}
    changes = "、".join(f"{field_names.get(k, k)}→{v}" for k, v in fields.items())
    return f"已修改课程「{verified_name}」：{changes}"


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

def register(schemas: list, display_names: dict, registry: dict) -> None:
    schemas.extend(SCHEMAS)
    display_names.update(DISPLAY_NAMES)
    registry.update({
        "query_schedule": _exec_query_schedule,
        "add_course": _exec_add_course,
        "delete_course": _exec_delete_course,
        "update_course": _exec_update_course,
    })

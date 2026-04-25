"""agent.tools.todo — 待办 + 考试（学业视域，共 4 个）。

工具清单：query_todos / toggle_todo / add_todo / query_exams
（query_exams 归类学业，与 todo 共享学业叙事，规划案第 R2 卡已批注。）
"""
from __future__ import annotations

from modules.mock_data import get_todos, get_upcoming_exams
from modules.persistence import update_todo_status, add_todo as persist_add_todo


SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "query_todos",
            "description": "查询待办事项列表。可以筛选全部、未完成或已完成。",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "筛选状态：all=全部，pending=未完成，done=已完成",
                        "enum": ["all", "pending", "done"],
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_todo",
            "description": "切换一个待办事项的完成状态（完成↔未完成）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "待办事项的 ID"}
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_todo",
            "description": "新增一个待办事项。用户说'帮我添加一个待办'、'记一下要做的事'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "待办事项内容"},
                    "deadline": {"type": "string", "description": "截止日期，格式 YYYY-MM-DD"},
                    "priority": {
                        "type": "string",
                        "description": "优先级",
                        "enum": ["🔴 紧急", "🟡 重要", "🟢 普通"],
                    },
                    "category": {
                        "type": "string",
                        "description": "分类",
                        "enum": ["学业", "生活", "社交"],
                    },
                },
                "required": ["task", "deadline"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_exams",
            "description": "查询近期考试安排和倒计时。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

DISPLAY_NAMES: dict[str, str] = {
    "query_todos": "查询待办事项",
    "toggle_todo": "更新待办状态",
    "add_todo": "新增待办事项",
    "query_exams": "查询考试安排",
}


def _exec_query_todos(args: dict) -> str:
    todos = get_todos()
    status = args.get("status", "all")

    if status == "pending":
        todos = [t for t in todos if not t["done"]]
        title = "未完成的待办事项："
    elif status == "done":
        todos = [t for t in todos if t["done"]]
        title = "已完成的待办事项："
    else:
        title = "全部待办事项："

    if not todos:
        return "没有符合条件的待办事项。"

    lines = [title]
    for t in todos:
        status_mark = "✅" if t["done"] else "⬜"
        lines.append(f"- {status_mark} [{t['id']}] {t['priority']} {t['task']}（截止 {t['deadline']}）")
    return "\n".join(lines)


def _exec_toggle_todo(args: dict) -> str:
    task_id = int(args["task_id"])  # LLM 可能传 str
    todos = get_todos()
    target = next((t for t in todos if t["id"] == task_id), None)
    if not target:
        return f"未找到 ID 为 {task_id} 的待办事项。"
    new_status = not target["done"]
    update_todo_status(task_id, new_status)
    status_text = "已完成" if new_status else "未完成"
    return f"待办「{target['task']}」已标记为{status_text}。"


def _exec_add_todo(args: dict) -> str:
    task = args["task"]
    deadline = args["deadline"]
    priority = args.get("priority", "🟢 普通")
    category = args.get("category", "生活")
    todo = persist_add_todo(task, deadline, priority, category)
    return (
        f"已新增待办事项：\n"
        f"- ID: {todo['id']}\n"
        f"- 任务: {todo['task']}\n"
        f"- 截止: {todo['deadline']}\n"
        f"- 优先级: {todo['priority']}\n"
        f"- 分类: {todo['category']}"
    )


def _exec_query_exams(args: dict) -> str:
    exams = get_upcoming_exams()
    if not exams:
        return "近期没有考试安排。"
    lines = ["近期考试安排："]
    for e in exams:
        if e["days_left"] == 0:
            urgency = "🔴 今天考试！"
            countdown = "就在今天"
        elif e["days_left"] <= 3:
            urgency = "🔴 紧急！"
            countdown = f"还有 {e['days_left']} 天"
        elif e["days_left"] <= 7:
            urgency = "🟡 注意"
            countdown = f"还有 {e['days_left']} 天"
        else:
            urgency = "🔵"
            countdown = f"还有 {e['days_left']} 天"
        lines.append(
            f"- {urgency} {e['course']}（{e['type']}）"
            f"：{e['date']}，{countdown}"
            f"，地点：{e['location']}"
        )
    return "\n".join(lines)


def register(schemas: list, display_names: dict, registry: dict) -> None:
    schemas.extend(SCHEMAS)
    display_names.update(DISPLAY_NAMES)
    registry.update({
        "query_todos": _exec_query_todos,
        "toggle_todo": _exec_toggle_todo,
        "add_todo": _exec_add_todo,
        "query_exams": _exec_query_exams,
    })

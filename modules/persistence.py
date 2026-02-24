"""
UniLife OS — JSON 数据持久化层
设计原则：mock_data 提供基础数据，persistence 只保存用户的增量修改。
存储文件：data/user_data.json
"""
from __future__ import annotations

import json
import tempfile
import os
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_FILE = DATA_DIR / "user_data.json"

_DEFAULT_DATA = {
    "todos": {},            # {todo_id: bool} — 完成状态覆盖
    "extra_transactions": [],  # 用户新增的消费记录
    "health_overrides": {},    # {"water_cups": n, "exercise_today": bool, "mood": "..."}
    "chat_messages": [],       # 对话历史
    "packing_checked": [],     # 旅行必带清单已勾选项
    "extra_todos": [],         # 用户通过 Agent 新增的待办事项
    "extra_courses": [],       # 用户新增的课程
    "deleted_course_ids": [],  # 被删除的 mock 课程 ID
    "course_updates": {},      # {course_id: {field: new_value}} 课程修改记录
    "monthly_budget": None,    # 月预算（None 表示未设置，用 mock 默认值 2000）
    "travel_overrides": {},       # {field: new_value} 旅行计划顶层字段覆盖
    "extra_itinerary": [],        # 用户新增的行程站点
    "deleted_itinerary_idxs": [], # 被删除的 mock 行程站点索引
    "itinerary_updates": {},      # {idx_str: {field: value}} 行程站点修改
}


def load_user_data() -> dict:
    """从 JSON 加载用户数据，不存在则用默认结构初始化。"""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 确保所有 key 都存在（兼容旧版本文件）
            for key, default in _DEFAULT_DATA.items():
                data.setdefault(key, default if not isinstance(default, (list, dict)) else type(default)(default))
            return data
        except (json.JSONDecodeError, IOError):
            return _init_default_data()
    return _init_default_data()


def save_user_data(data: dict):
    """保存用户数据到 JSON 文件（原子写入：先写临时文件再重命名，防止写入中断导致数据损坏）。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, DATA_FILE)
        except BaseException:
            # 写入失败时清理临时文件
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
    except OSError as e:
        # 写入权限或磁盘空间不足时，打印警告但不崩溃
        import sys
        print(f"[persistence] 写入失败: {e}", file=sys.stderr)


def _init_default_data() -> dict:
    """用默认结构初始化并保存。"""
    data = {k: (type(v)(v) if isinstance(v, (list, dict)) else v) for k, v in _DEFAULT_DATA.items()}
    save_user_data(data)
    return data


# ========== 便捷操作函数 ==========

def _ensure_today_overrides(data: dict) -> dict:
    """确保 health_overrides 是当天的数据，跨天自动重置所有健康打卡。"""
    overrides = data.setdefault("health_overrides", {})
    today = datetime.now().strftime("%Y-%m-%d")
    if overrides.get("override_date") != today:
        data["health_overrides"] = {"override_date": today}
    return data["health_overrides"]


def update_todo_status(todo_id: int, done: bool):
    """更新待办完成状态。"""
    data = load_user_data()
    data["todos"][str(todo_id)] = done
    save_user_data(data)


def add_expense(item: str, amount: float, category: str):
    """新增一笔消费记录。"""
    data = load_user_data()
    record = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "item": item,
        "amount": amount,
        "category": category,
        "icon": _category_icon(category),
    }
    data["extra_transactions"].insert(0, record)
    save_user_data(data)
    return record


def increment_water():
    """喝水 +1（跨天自动归零）。"""
    data = load_user_data()
    overrides = _ensure_today_overrides(data)
    overrides["water_cups"] = overrides.get("water_cups", 0) + 1
    save_user_data(data)
    return overrides["water_cups"]


def log_steps(steps: int):
    """记录今日步数（跨天自动归零）。"""
    data = load_user_data()
    overrides = _ensure_today_overrides(data)
    overrides["steps"] = steps
    save_user_data(data)
    return steps


def log_sleep(hours: float, quality: str = "一般"):
    """记录昨晚睡眠（跨天自动归零）。"""
    data = load_user_data()
    overrides = _ensure_today_overrides(data)
    overrides["sleep_hours"] = hours
    overrides["sleep_quality"] = quality
    save_user_data(data)


def log_exercise():
    """运动打卡（跨天自动归零）。"""
    data = load_user_data()
    overrides = _ensure_today_overrides(data)
    overrides["exercise_today"] = True
    save_user_data(data)


def log_mood(mood: str):
    """心情记录（跨天自动归零）。"""
    data = load_user_data()
    overrides = _ensure_today_overrides(data)
    overrides["mood"] = mood
    save_user_data(data)


def update_packing(item: str, checked: bool):
    """更新旅行必带清单勾选状态。"""
    data = load_user_data()
    packing = data.setdefault("packing_checked", [])
    if checked and item not in packing:
        packing.append(item)
    elif not checked and item in packing:
        packing.remove(item)
    save_user_data(data)


MAX_PERSISTED_MESSAGES = 50  # 持久化对话历史上限


def save_chat_history(messages: list[dict]):
    """保存对话历史（限制最大条数，防止 JSON 文件膨胀）。"""
    data = load_user_data()
    data["chat_messages"] = messages[-MAX_PERSISTED_MESSAGES:]
    save_user_data(data)


def load_chat_history() -> list[dict]:
    """加载对话历史。"""
    data = load_user_data()
    return data.get("chat_messages", [])


def clear_chat_history():
    """清空对话历史。"""
    data = load_user_data()
    data["chat_messages"] = []
    save_user_data(data)


def get_todo_overrides() -> dict:
    """获取待办状态覆盖字典 {todo_id_str: bool}。"""
    data = load_user_data()
    return data.get("todos", {})


def get_extra_transactions() -> list[dict]:
    """获取用户新增的消费记录。"""
    data = load_user_data()
    return data.get("extra_transactions", [])


def get_health_overrides() -> dict:
    """获取健康数据覆盖。"""
    data = load_user_data()
    return data.get("health_overrides", {})


def get_packing_checked() -> list[str]:
    """获取旅行清单已勾选项。"""
    data = load_user_data()
    return data.get("packing_checked", [])


def add_todo(task: str, deadline: str, priority: str = "🟢 普通", category: str = "生活") -> dict:
    """新增一个待办事项，自动分配递增 ID。"""
    data = load_user_data()
    extra = data.setdefault("extra_todos", [])
    # ID 从 max(7, 已有 extra ID) + 1 开始，避免与 mock 数据冲突
    existing_ids = [t["id"] for t in extra] if extra else [7]
    new_id = max(max(existing_ids), 7) + 1
    todo = {
        "id": new_id,
        "task": task,
        "deadline": deadline,
        "priority": priority,
        "done": False,
        "category": category,
    }
    extra.append(todo)
    save_user_data(data)
    return todo


def get_extra_todos() -> list[dict]:
    """获取用户通过 Agent 新增的待办事项（自动清理截止日期超过 7 天的过期项）。"""
    data = load_user_data()
    extra = data.get("extra_todos", [])
    if not extra:
        return extra
    from datetime import timedelta
    today = datetime.now().date()
    cutoff = today - timedelta(days=7)
    filtered = [t for t in extra if datetime.strptime(t["deadline"], "%Y-%m-%d").date() >= cutoff]
    if len(filtered) < len(extra):
        data["extra_todos"] = filtered
        save_user_data(data)
    return filtered


# ========== 课表相关操作 ==========

def add_course(weekday: str, time: str, course: str, location: str,
               teacher: str = "", course_type: str = "选修") -> dict:
    """新增一门课程，自动分配递增 ID（从 101 开始，避免与 mock 1~10 冲突）。"""
    data = load_user_data()
    extra = data.setdefault("extra_courses", [])
    existing_ids = [c["id"] for c in extra] if extra else [100]
    new_id = max(max(existing_ids), 100) + 1
    record = {
        "id": new_id,
        "weekday": weekday,
        "time": time,
        "course": course,
        "location": location,
        "teacher": teacher,
        "type": course_type,
    }
    extra.append(record)
    save_user_data(data)
    return record


def delete_course(course_id: int) -> bool:
    """删除课程。如果是用户新增课程则直接移除，如果是 mock 课程则标记删除。"""
    data = load_user_data()
    # 先检查是否在 extra_courses 中
    extra = data.setdefault("extra_courses", [])
    for i, c in enumerate(extra):
        if c["id"] == course_id:
            extra.pop(i)
            save_user_data(data)
            return True
    # 否则标记删除 mock 课程
    deleted = data.setdefault("deleted_course_ids", [])
    if course_id not in deleted:
        deleted.append(course_id)
        save_user_data(data)
    return True


def update_course(course_id: int, **fields) -> dict:
    """修改课程字段。对 extra_courses 直接修改，对 mock 课程记录 overlay。"""
    data = load_user_data()
    # 先检查是否在 extra_courses 中
    extra = data.setdefault("extra_courses", [])
    for c in extra:
        if c["id"] == course_id:
            for k, v in fields.items():
                c[k] = v
            save_user_data(data)
            return c
    # 否则记录为 mock 课程的修改 overlay
    updates = data.setdefault("course_updates", {})
    cid_str = str(course_id)
    updates.setdefault(cid_str, {}).update(fields)
    save_user_data(data)
    return updates[cid_str]


def get_extra_courses() -> list[dict]:
    """获取用户新增的课程列表。"""
    data = load_user_data()
    return data.get("extra_courses", [])


def get_deleted_course_ids() -> list[int]:
    """获取已删除的 mock 课程 ID 列表。"""
    data = load_user_data()
    return data.get("deleted_course_ids", [])


def get_course_updates() -> dict:
    """获取课程修改记录 {course_id_str: {field: value}}。"""
    data = load_user_data()
    return data.get("course_updates", {})


# ========== 预算相关操作 ==========

def set_budget(amount: float):
    """设置月预算金额。"""
    data = load_user_data()
    data["monthly_budget"] = amount
    save_user_data(data)


def get_budget() -> float | None:
    """获取月预算金额，None 表示未设置。"""
    data = load_user_data()
    return data.get("monthly_budget")


# ========== 旅行计划相关操作 ==========

def update_travel(**fields):
    """修改旅行计划顶层字段（trip_name/date/budget/status/companions）。"""
    data = load_user_data()
    overrides = data.setdefault("travel_overrides", {})
    overrides.update(fields)
    save_user_data(data)


def get_travel_overrides() -> dict:
    """获取旅行计划顶层字段覆盖。"""
    data = load_user_data()
    return data.get("travel_overrides", {})


def add_itinerary_item(time: str, activity: str, location: str,
                       cost: float = 0, icon: str = "📍") -> dict:
    """新增一个行程站点。"""
    data = load_user_data()
    extra = data.setdefault("extra_itinerary", [])
    item = {
        "time": time,
        "activity": activity,
        "location": location,
        "cost": cost,
        "icon": icon,
    }
    extra.append(item)
    save_user_data(data)
    return item


def delete_itinerary_item(index: int):
    """删除一个行程站点（索引从 0 开始，指 mock 行程列表的索引）。"""
    data = load_user_data()
    deleted = data.setdefault("deleted_itinerary_idxs", [])
    if index not in deleted:
        deleted.append(index)
    save_user_data(data)


def update_itinerary_item(index: int, **fields):
    """修改一个行程站点的字段。"""
    data = load_user_data()
    updates = data.setdefault("itinerary_updates", {})
    idx_str = str(index)
    updates.setdefault(idx_str, {}).update(fields)
    save_user_data(data)


def get_extra_itinerary() -> list[dict]:
    """获取用户新增的行程站点列表。"""
    data = load_user_data()
    return data.get("extra_itinerary", [])


def get_deleted_itinerary_idxs() -> list[int]:
    """获取已删除的行程站点索引列表。"""
    data = load_user_data()
    return data.get("deleted_itinerary_idxs", [])


def get_itinerary_updates() -> dict:
    """获取行程站点修改记录 {idx_str: {field: value}}。"""
    data = load_user_data()
    return data.get("itinerary_updates", {})


def delete_travel_plan():
    """标记整个旅行计划为已删除。"""
    data = load_user_data()
    overrides = data.setdefault("travel_overrides", {})
    overrides["deleted"] = True
    save_user_data(data)


def reset_travel_itinerary():
    """重置行程数据（清空所有行程修改，用于创建全新旅行计划）。"""
    data = load_user_data()
    data["extra_itinerary"] = []
    data["deleted_itinerary_idxs"] = list(range(8))  # 删除全部 mock 行程
    data["itinerary_updates"] = {}
    save_user_data(data)


def _category_icon(category: str) -> str:
    """根据消费类别返回对应图标。"""
    icons = {
        "餐饮": "🍜",
        "交通": "🚇",
        "购物": "🛒",
        "学习用品": "📚",
        "娱乐": "🎬",
        "其他": "💳",
    }
    return icons.get(category, "💳")

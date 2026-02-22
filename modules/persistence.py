"""
UniLife OS — JSON 数据持久化层
设计原则：mock_data 提供基础数据，persistence 只保存用户的增量修改。
存储文件：data/user_data.json
"""
import json
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
    """保存用户数据到 JSON 文件。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _init_default_data() -> dict:
    """用默认结构初始化并保存。"""
    data = {k: (type(v)(v) if isinstance(v, (list, dict)) else v) for k, v in _DEFAULT_DATA.items()}
    save_user_data(data)
    return data


# ========== 便捷操作函数 ==========

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
    """喝水 +1。"""
    data = load_user_data()
    overrides = data.setdefault("health_overrides", {})
    overrides["water_cups"] = overrides.get("water_cups", 0) + 1
    save_user_data(data)
    return overrides["water_cups"]


def log_exercise():
    """运动打卡。"""
    data = load_user_data()
    overrides = data.setdefault("health_overrides", {})
    overrides["exercise_today"] = True
    save_user_data(data)


def log_mood(mood: str):
    """心情记录。"""
    data = load_user_data()
    overrides = data.setdefault("health_overrides", {})
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


def save_chat_history(messages: list[dict]):
    """保存对话历史。"""
    data = load_user_data()
    data["chat_messages"] = messages
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

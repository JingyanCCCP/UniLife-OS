"""
UniLife OS — 工具参数公共校验（R2 新增）

所有校验返回 str | None：返回 str 代表校验失败（该串可直接作为工具错误回复），返回 None 代表通过。

这样设计的好处：
- 调用方不需要写 try/except，用 `if (err := validate_xxx(v)): return err` 即可。
- 单元测试容易，纯函数无副作用。
"""
from __future__ import annotations


def validate_amount(amount) -> str | None:
    """消费/预算金额：0 < amount ≤ 100,000 元。"""
    if not isinstance(amount, (int, float)) or amount <= 0 or amount > 100000:
        return "金额须在 0～100,000 元之间。"
    return None


def validate_steps(steps) -> str | None:
    """步数：0 ≤ steps ≤ 200,000。"""
    if not isinstance(steps, (int, float)) or steps < 0 or steps > 200000:
        return "步数须在 0～200,000 之间。"
    return None


def validate_sleep_hours(hours) -> str | None:
    """睡眠时长（小时）：0 ≤ hours ≤ 24。"""
    if not isinstance(hours, (int, float)) or hours < 0 or hours > 24:
        return "睡眠时长须在 0～24 小时之间。"
    return None


def validate_exercise_goal(goal) -> str | None:
    """每周运动目标：整数 3-7。"""
    if goal not in (3, 4, 5, 6, 7):
        return "运动目标须在 3～7 次之间。"
    return None


def validate_cost_non_negative(cost) -> str | None:
    """花费金额（行程/预算项）：0 ≤ cost。"""
    if not isinstance(cost, (int, float)) or cost < 0:
        return "花费不能为负数。"
    return None


def validate_non_empty_str(value, field: str = "字段") -> str | None:
    """字符串非空。"""
    if not isinstance(value, str) or not value.strip():
        return f"{field}不能为空。"
    return None

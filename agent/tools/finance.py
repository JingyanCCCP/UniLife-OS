"""agent.tools.finance — 财务相关工具（3 个）。

工具清单：query_finance / record_expense / set_budget
"""
from __future__ import annotations

from modules.mock_data import get_finance
from modules.persistence import add_expense, set_budget as persist_set_budget

from agent.tools._validators import validate_amount, validate_non_empty_str


SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "query_finance",
            "description": "查询本月财务状况，包括预算、消费、各类别占比和最近消费记录。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "可选，筛选特定消费类别，如 '餐饮'、'交通'、'购物'、'学习用品'、'娱乐'、'其他'。",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_expense",
            "description": "记录一笔新的消费。用户告诉你花了什么、多少钱时调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {"type": "string", "description": "消费项目名称，如 '奶茶'、'教材'"},
                    "amount": {"type": "number", "description": "消费金额（元）"},
                    "category": {
                        "type": "string",
                        "description": "消费类别",
                        "enum": ["餐饮", "交通", "购物", "学习用品", "娱乐", "其他"],
                    },
                },
                "required": ["item", "amount", "category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_budget",
            "description": "设置本月预算金额。用户说'把预算改成3000'、'这个月预算2500'时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "预算金额（元）"},
                },
                "required": ["amount"],
            },
        },
    },
]

DISPLAY_NAMES: dict[str, str] = {
    "query_finance": "查询财务数据",
    "record_expense": "记录消费",
    "set_budget": "设置预算",
}


def _exec_query_finance(args: dict) -> str:
    finance = get_finance()
    category = args.get("category")

    if category:
        amount = finance["categories"].get(category, 0)
        txns = [t for t in finance["recent_transactions"] if t["category"] == category]
        lines = [f"【{category}】消费情况：", f"本月 {category} 总计: ¥{amount:.0f}"]
        if txns:
            lines.append("相关消费记录：")
            for t in txns[:8]:
                lines.append(f"- {t['date']} {t['item']} ¥{t['amount']:.1f}")
        return "\n".join(lines)

    lines = [
        "本月财务概况：",
        f"- 预算: ¥{finance['monthly_budget']:.0f}",
        f"- 已花费: ¥{finance['spent']:.0f}（{finance['budget_usage_pct']}%）",
        f"- 剩余: ¥{finance['remaining']:.0f}",
        f"- 日均消费: ¥{finance['daily_avg_spent']:.1f}",
        f"- 剩余天数: {finance['days_left_in_month']} 天",
        f"- 建议日限: ¥{finance['suggested_daily']:.1f}",
        "",
        "各类别消费：",
    ]
    for cat, amount in finance["categories"].items():
        lines.append(f"- {cat}: ¥{amount:.0f}")
    lines.append("")
    lines.append("最近消费记录：")
    for t in finance["recent_transactions"][:10]:
        lines.append(f"- {t['date']} {t['item']} ¥{t['amount']:.1f}（{t['category']}）")
    return "\n".join(lines)


def _exec_record_expense(args: dict) -> str:
    item = args["item"]
    if (err := validate_non_empty_str(item, "消费项目")):
        return err
    amount = args["amount"]
    if (err := validate_amount(amount)):
        return err
    category = args["category"]
    record = add_expense(item.strip(), amount, category)
    return f"已记录消费：{item} ¥{amount:.1f}（{category}），记录日期 {record['date']}。"


def _exec_set_budget(args: dict) -> str:
    amount = args["amount"]
    if (err := validate_amount(amount)):
        return err
    persist_set_budget(float(amount))
    return f"已将本月预算设置为 ¥{amount:.0f}。"


def register(schemas: list, display_names: dict, registry: dict) -> None:
    schemas.extend(SCHEMAS)
    display_names.update(DISPLAY_NAMES)
    registry.update({
        "query_finance": _exec_query_finance,
        "record_expense": _exec_record_expense,
        "set_budget": _exec_set_budget,
    })

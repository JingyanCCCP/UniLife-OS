"""
R5 · test_dates — mock 动态日期在 4 个临界日期下都能合理滚动。

不 mock datetime.now()，而是直接调 seed_data.build_*_seed(today=...)。
覆盖：月中 / 月初 / 月末 / 周一 四种 today。
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from modules.seed_data import (
    build_finance_seed,
    build_todos_seed,
    build_exams_seed,
    build_travel_seed,
)


CRITICAL_DAYS = [
    pytest.param(date(2026, 4, 15), id="mid-month"),
    pytest.param(date(2026, 2, 1), id="month-start"),
    pytest.param(date(2026, 3, 31), id="month-end"),
    pytest.param(date(2026, 5, 4), id="monday"),
    pytest.param(date(2026, 5, 9), id="saturday"),
]


@pytest.mark.parametrize("today", CRITICAL_DAYS)
def test_finance_seed_dates_within_20_days(today):
    _, _, txns = build_finance_seed(today)
    assert len(txns) == 21, f"消费应有 21 条，实际 {len(txns)}"
    for t in txns:
        d = datetime.strptime(t["date"], "%Y-%m-%d").date()
        gap = (today - d).days
        assert 0 <= gap <= 20, f"交易日期 {d} 离 today={today} {gap} 天超出 [0,20]"


@pytest.mark.parametrize("today", CRITICAL_DAYS)
def test_todos_seed_deadlines_in_range(today):
    todos = build_todos_seed(today)
    assert len(todos) == 7
    for t in todos:
        d = datetime.strptime(t["deadline"], "%Y-%m-%d").date()
        gap = (d - today).days
        # 规划案要求 -2 到 +6；实际模板是 0 到 +6
        assert -2 <= gap <= 6, f"todo {t['task']} deadline {d} 偏 {gap} 天超出范围"


@pytest.mark.parametrize("today", CRITICAL_DAYS)
def test_exams_seed_future_only(today):
    exams = build_exams_seed(today)
    assert len(exams) == 3
    days = []
    for e in exams:
        d = datetime.strptime(e["date"], "%Y-%m-%d").date()
        gap = (d - today).days
        assert gap >= 0, f"考试 {e['course']} {d} 已过期"
        days.append(gap)
    # 规划案明确 +1 / +8 / +15
    assert sorted(days) == [1, 8, 15]


@pytest.mark.parametrize("today", CRITICAL_DAYS)
def test_travel_seed_next_saturday(today):
    travel = build_travel_seed(today)
    trip_date = datetime.strptime(travel["date"], "%Y-%m-%d").date()
    assert trip_date > today, f"旅行日期 {trip_date} 不晚于 today={today}"
    assert trip_date.weekday() == 5, f"旅行日期 {trip_date} 不是周六（weekday={trip_date.weekday()}）"
    # 不超过 7 天
    assert (trip_date - today).days <= 7


def test_travel_seed_today_is_saturday_pushes_next_week():
    saturday = date(2026, 5, 9)
    assert saturday.weekday() == 5
    travel = build_travel_seed(saturday)
    trip_date = datetime.strptime(travel["date"], "%Y-%m-%d").date()
    assert (trip_date - saturday).days == 7, "今天是周六应推到下周六"

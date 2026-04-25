"""
UniLife OS — pytest 公共 fixture（R5 新增）

关键 fixture：`tmp_data_file` 把 persistence.DATA_FILE 指向 tmp 目录，保证测试之间
互不干扰。初始内容为 _DEFAULT_DATA 的深拷贝。

所有测试文件都应 `def test_xxx(tmp_data_file):` 以获得干净的 persistence 状态。
"""
from __future__ import annotations

import copy
import pytest

from modules import persistence


@pytest.fixture
def tmp_data_file(tmp_path, monkeypatch):
    """把 persistence.DATA_DIR / DATA_FILE 指到 pytest 的临时目录。

    - 用 monkeypatch 覆盖模块级常量。
    - 写入 _DEFAULT_DATA 深拷贝作为初始状态。
    - 测试结束后 tmp_path 由 pytest 自动清理。
    """
    tmp_file = tmp_path / "user_data.json"
    monkeypatch.setattr(persistence, "DATA_DIR", tmp_path)
    monkeypatch.setattr(persistence, "DATA_FILE", tmp_file)
    persistence.save_user_data(copy.deepcopy(persistence._DEFAULT_DATA))
    return tmp_file

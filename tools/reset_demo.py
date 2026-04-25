"""
UniLife OS — 演示重置脚本（R1 新增）

用途：
- 现场演示或彩排前，一键把 data/user_data.json 恢复到干净 seed 态，避免上一次试跑留下的
  消费/健康打卡/待办完成状态污染 demo。
- R4 将在侧边栏加入「一键重置 demo 数据」按钮，可直接调用 reset()。

使用：
    python tools/reset_demo.py

输出：
    demo 已重置 → <project_root>/data/user_data.json
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

# 允许从项目根或子目录直接 `python tools/reset_demo.py` 运行。
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from modules.persistence import save_user_data, _DEFAULT_DATA, DATA_FILE  # noqa: E402


def reset() -> Path:
    """把 data/user_data.json 写回 _DEFAULT_DATA（深拷贝以免 mutate 模块常量）。"""
    save_user_data(copy.deepcopy(_DEFAULT_DATA))
    return DATA_FILE


if __name__ == "__main__":
    path = reset()
    print(f"demo 已重置 → {path}")

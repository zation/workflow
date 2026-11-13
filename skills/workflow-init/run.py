#!/usr/bin/env python3
"""转调共享的 init_project.py。

技能目录常以软链或目录联接挂载，相对路径里的 .. 会在链接处被错误解析，
所以用 __file__.resolve() 定位源码仓库，再执行共享脚本。
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "init_project.py"

sys.path.insert(0, str(SCRIPT.parent))
sys.argv[0] = str(SCRIPT)
runpy.run_path(str(SCRIPT), run_name="__main__")

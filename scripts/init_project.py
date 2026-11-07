#!/usr/bin/env python3
"""在目标仓库中创建 AGENTS.md 与 docs/ 长期文档骨架。

已存在的文件一律不覆盖；默认只做预演，加 --force 才覆盖 AGENTS.md。
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from _common import (
    AGENTS_TEMPLATE,
    DOC_SKELETON,
    DOCS_TEMPLATE_DIR,
    EMPTY_DOC_DIRS,
    backup_file,
    force_utf8_stdout,
    normalize_text,
    read_text,
    write_text,
)


@dataclass
class Action:
    kind: str
    path: Path
    source: Path | None = None
    note: str = ""


def collect(root: Path, force: bool) -> list[Action]:
    actions: list[Action] = []

    agents = root / "AGENTS.md"
    if not agents.exists():
        actions.append(Action("create", agents, AGENTS_TEMPLATE))
    elif force:
        actions.append(Action("overwrite", agents, AGENTS_TEMPLATE, "覆盖前自动备份"))
    else:
        actions.append(Action("skip", agents, None, "已存在，改用 upgrade_project.py 升级"))

    for name in DOC_SKELETON:
        target = root / "docs" / name
        if target.exists():
            actions.append(Action("skip", target, None, "已存在，不覆盖"))
        else:
            actions.append(Action("create", target, DOCS_TEMPLATE_DIR / name))

    for name in EMPTY_DOC_DIRS:
        target = root / "docs" / name
        if target.is_dir():
            actions.append(Action("skip", target, None, "目录已存在"))
        else:
            actions.append(Action("mkdir", target))

    return actions


def apply(action: Action, root: Path) -> None:
    if action.kind == "create":
        write_text(action.path, normalize_text(read_text(action.source)))
    elif action.kind == "overwrite":
        backup_file(action.path, root)
        write_text(action.path, normalize_text(read_text(action.source)))
    elif action.kind == "mkdir":
        action.path.mkdir(parents=True, exist_ok=True)
        write_text(action.path / ".gitkeep", "")


def main() -> int:
    force_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="在目标仓库创建 AGENTS.md 与 docs/ 长期文档骨架，已存在的文件不会被覆盖。"
    )
    parser.add_argument("--root", default=".", help="目标仓库根目录，默认当前目录")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不写入文件")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的 AGENTS.md（先备份）")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"错误：{root} 不是一个目录。")
        return 2
    if not AGENTS_TEMPLATE.is_file():
        print(f"错误：模板缺失 {AGENTS_TEMPLATE}")
        return 2

    actions = collect(root, args.force)

    print(f"目标目录：{root}")
    print(f"模式：{'预演（不写盘）' if args.dry_run else '写入'}")
    if not (root / ".git").exists():
        print("提示：未检测到 Git 仓库，本约定假定使用 Git 管理版本与提交。")
    print()

    created = 0
    skipped = 0
    for action in actions:
        label = action.path.relative_to(root).as_posix()
        if action.kind == "skip":
            skipped += 1
            print(f"  = {label}  （{action.note}）")
            continue

        created += 1
        if not args.dry_run:
            apply(action, root)

        if action.kind == "mkdir":
            print(f"  + {label}/  （空目录，含 .gitkeep）")
        elif action.kind == "overwrite":
            print(f"  ~ {label}  （{action.note}）")
        else:
            print(f"  + {label}")

    print()
    if args.dry_run:
        print(f"计划创建 {created} 项，跳过 {skipped} 项。未写入任何文件。")
        print("确认无误后去掉 --dry-run 重新执行。")
    else:
        print(f"已创建 {created} 项，跳过 {skipped} 项。")
        print("下一步：填写 docs/ 各骨架文件的内容；已有 AGENTS.md 的项目改用 scripts/upgrade_project.py 升级。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

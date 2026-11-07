#!/usr/bin/env python3
"""比对并同步目标仓库的 AGENTS.md 与 docs/ 骨架到当前模板版本。

默认只读：打印版本、差异和缺失项，不写文件。加 --write 才落盘（覆盖前自动备份）。
"""

from __future__ import annotations

import argparse
import difflib
import re
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

VERSION_PATTERN = re.compile(r"<!--\s*agents-md-template:\s*([^\s>]+)\s*-->")

DIFF_LINE_LIMIT = 200


def detect_version(text: str) -> str:
    match = VERSION_PATTERN.search(text)
    return match.group(1) if match else "未标记"


def build_diff(current: str, template: str, full: bool) -> tuple[str, int]:
    lines = list(
        difflib.unified_diff(
            current.splitlines(keepends=True),
            template.splitlines(keepends=True),
            fromfile="当前 AGENTS.md",
            tofile="模板 AGENTS.md",
            n=3,
        )
    )
    total = len(lines)
    if not full and total > DIFF_LINE_LIMIT:
        lines = lines[:DIFF_LINE_LIMIT]
    return "".join(lines), total


def main() -> int:
    force_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="比对并同步 AGENTS.md 与 docs/ 骨架到当前模板版本。默认只读，加 --write 才写入。"
    )
    parser.add_argument("--root", default=".", help="目标仓库根目录，默认当前目录")
    parser.add_argument("--write", action="store_true", help="按模板写入 AGENTS.md 并补齐缺失骨架")
    parser.add_argument("--check", action="store_true", help="存在差异时退出码为 1，用于 CI")
    parser.add_argument("--full-diff", action="store_true", help="输出完整差异，不截断")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"错误：{root} 不是一个目录。")
        return 2
    if not AGENTS_TEMPLATE.is_file():
        print(f"错误：模板缺失 {AGENTS_TEMPLATE}")
        return 2

    template_text = normalize_text(read_text(AGENTS_TEMPLATE))
    template_version = detect_version(template_text)

    agents_path = root / "AGENTS.md"
    exists = agents_path.is_file()

    print(f"目标目录：{root}")
    print(f"模板版本：{template_version}")

    if exists:
        current_text = normalize_text(read_text(agents_path))
        current_version = detect_version(current_text)
        identical = current_text == template_text
        print(f"项目文件：AGENTS.md（版本 {current_version}）")
        if current_version == "未标记":
            print("说明：项目文件缺少模板版本标记，按首次接入处理。")
    else:
        current_text = ""
        identical = False
        print("项目文件：AGENTS.md 不存在")

    missing_docs = [name for name in DOC_SKELETON if not (root / "docs" / name).is_file()]
    missing_dirs = [name for name in EMPTY_DOC_DIRS if not (root / "docs" / name).is_dir()]

    print(f"文档骨架：{'齐全' if not missing_docs else '缺少 ' + '、'.join(missing_docs)}")

    docs_dir = root / "docs"
    if docs_dir.is_dir():
        known = set(DOC_SKELETON)
        extras = sorted(p.name for p in docs_dir.glob("*.md") if p.name not in known)
        if extras:
            print(f"另有模板之外的文件（不处理）：{'、'.join(extras)}")

    print()

    if identical:
        print("状态：与模板一致")
    else:
        print("状态：与模板存在差异")
        diff_text, total = build_diff(current_text, template_text, args.full_diff)
        if diff_text:
            print("\n--- 差异（- 当前 / + 模板）---")
            print(diff_text.rstrip("\n"))
            if not args.full_diff and total > DIFF_LINE_LIMIT:
                print(f"\n（差异共 {total} 行，仅显示前 {DIFF_LINE_LIMIT} 行；加 --full-diff 查看全部）")
            print("--- 差异结束 ---")

    agents_drift = not identical
    docs_drift = bool(missing_docs)

    if not agents_drift and not docs_drift and not missing_dirs:
        print("\n结论：无需同步。")
        return 0

    if not args.write:
        if agents_drift:
            print("\n结论：AGENTS.md 与模板存在差异，未写入任何文件。")
            print("确认按模板同步后，加 --write 重新执行。")
        elif docs_drift:
            print(f"\n结论：AGENTS.md 一致，但缺少 {'、'.join(missing_docs)}，未写入任何文件。")
            print("补齐骨架文件时加 --write 重新执行。")
        else:
            print(f"\n结论：AGENTS.md 与骨架文件已一致，仅缺目录 {'、'.join(missing_dirs)}。")
            print("需要补齐目录时加 --write 重新执行。")
        return 1 if args.check and (agents_drift or docs_drift) else 0

    if exists and not identical:
        backup = backup_file(agents_path, root)
        print(f"已备份：{backup.relative_to(root).as_posix()}")

    if not identical:
        write_text(agents_path, template_text)
        print(f"已写入：AGENTS.md（{template_version}）")

    for name in missing_docs:
        write_text(docs_dir / name, normalize_text(read_text(DOCS_TEMPLATE_DIR / name)))
        print(f"已写入：docs/{name}")

    for name in missing_dirs:
        target = docs_dir / name
        target.mkdir(parents=True, exist_ok=True)
        keep = target / ".gitkeep"
        if not keep.exists():
            write_text(keep, "")
        print(f"已创建：docs/{name}/")

    print("\n结论：同步完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

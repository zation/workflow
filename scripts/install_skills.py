#!/usr/bin/env python3
"""把 skills/ 下的技能挂到各 coding agent 的用户级技能目录。

默认只补建缺失的链接，不覆盖、不删除任何已有内容。
--force 时直接替换指向别处的旧链接、已失效的旧链接、以及同名真实目录副本（不备份）。
加 --dry-run 只打印计划。

链接是实时的：git pull 或直接改 SKILL.md 后内容立即生效，不需要重装。
"""

from __future__ import annotations

import argparse
import locale
import os
import shutil
import stat
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
TARGETS = {
    "workbuddy": Path.home() / ".workbuddy" / "skills",
    "codebuddy": Path.home() / ".codebuddy" / "skills",
    "codex": Path.home() / ".agents" / "skills",
}

ABSENT = "absent"
OK = "ok"
BROKEN = "broken"
WRONG_LINK = "wrong-link"
REAL_DIR = "real-dir"


def decode_output(data: bytes) -> str:
    encodings = ["utf-8"]
    if os.name == "nt":
        encodings.append("mbcs")
    encodings.append(locale.getpreferredencoding(False))
    for enc in encodings:
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", errors="replace")


def is_link(path: Path) -> bool:
    """判断是否目录链接：符号链接、Windows 目录联接都算。"""
    if path.is_symlink():
        return True
    isjunction = getattr(os.path, "isjunction", None)
    if isjunction is not None:
        return isjunction(path)
    if os.name != "nt":
        return False
    try:
        info = os.lstat(path)
    except OSError:
        return False
    attributes = getattr(info, "st_file_attributes", 0)
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def same_target(link: Path, source: Path) -> bool:
    try:
        left = os.path.normcase(str(link.resolve(strict=False)))
        right = os.path.normcase(str(source.resolve(strict=False)))
    except OSError:
        return False
    return left == right


def classify(link: Path, source: Path) -> str:
    if not os.path.lexists(link):
        return ABSENT
    if not link.exists():
        return BROKEN
    if is_link(link):
        return OK if same_target(link, source) else WRONG_LINK
    return REAL_DIR


def create_link(source: Path, link: Path) -> None:
    if os.name != "nt":
        os.symlink(source, link, target_is_directory=True)
        return

    result = subprocess.run(
        [
            os.environ.get("COMSPEC", "cmd.exe"),
            "/c",
            "mklink",
            "/J",
            str(link),
            str(source),
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        detail = decode_output(result.stdout + result.stderr).strip()
        raise RuntimeError(detail or f"mklink 退出码 {result.returncode}")


def remove_link(link: Path) -> None:
    """只移除链接本身：符号链接用 unlink，Windows 目录联接用 rmdir，不碰源目录。"""
    if link.is_symlink():
        os.unlink(link)
    else:
        os.rmdir(link)


def remove_target(path: Path) -> None:
    """删掉挡路的旧副本：链接只摘链接本身，真实目录整份删掉（--force 已确认）。"""
    if is_link(path):
        remove_link(path)
    else:
        shutil.rmtree(path)


def stale_links(target_dir: Path, keep: set[str]) -> list[Path]:
    """目标目录里指向本仓库 skills/ 的链接，但源码已不存在这些技能。"""
    if not target_dir.is_dir():
        return []
    found = []
    source_root = SKILLS_DIR.resolve()
    for entry in sorted(target_dir.iterdir()):
        if entry.name in keep or not is_link(entry):
            continue
        if not entry.exists():
            found.append(entry)
            continue
        try:
            if entry.resolve().parent == source_root:
                found.append(entry)
        except OSError:
            continue
    return found


def main() -> int:
    parser = argparse.ArgumentParser(
        description="把 skills/ 下的技能挂到各 coding agent 的技能目录（默认只补建，不覆盖）。"
    )
    parser.add_argument(
        "--target", choices=[*TARGETS, "all"], default="all", help="安装到哪个平台，默认全部"
    )
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不创建链接")
    parser.add_argument(
        "--force",
        action="store_true",
        help="替换指向别处或已失效的旧链接，删掉同名真实目录副本（不备份），并清理已删除技能的悬挂链接",
    )
    args = parser.parse_args()

    skills = sorted(
        p for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()
    )
    if not skills:
        print(f"错误：{SKILLS_DIR} 下没有找到带 SKILL.md 的技能目录。")
        return 2

    names = list(TARGETS) if args.target == "all" else [args.target]
    print(f"源码：{SKILLS_DIR}")
    print(f"模式：{'预演（不创建）' if args.dry_run else '创建链接'}"
          f"{' + 允许替换（--force）' if args.force else ''}\n")

    keep = {p.name for p in skills}
    errors = 0
    created = 0
    blocked = 0

    for name in names:
        target_dir = TARGETS[name]
        print(f"[{name}] {target_dir}")
        for source in skills:
            link = target_dir / source.name
            state = classify(link, source)

            if state == OK:
                print(f"  = {source.name}  已挂载，内容实时生效")
                continue

            if state == ABSENT:
                print(f"  + {source.name}  -> {source}")
                if not args.dry_run:
                    try:
                        target_dir.mkdir(parents=True, exist_ok=True)
                        create_link(source, link)
                        created += 1
                    except (OSError, RuntimeError) as exc:
                        print(f"    失败：{exc}")
                        errors += 1
                else:
                    created += 1
                continue

            if state == BROKEN:
                reason = "旧链接已失效（目标不存在）"
            elif state == WRONG_LINK:
                reason = "已存在链接，但指向别处"
            else:
                reason = "已存在同名真实目录（不是链接，内容不会跟随源码更新）"

            if not args.force:
                print(f"  ! {source.name}  {reason}，跳过")
                hint = "删除旧目录并改挂源码链接" if state == REAL_DIR else "改挂源码链接"
                print(f"    加 --force 可{hint}")
                blocked += 1
                continue

            action = "删除旧目录并改挂链接" if state == REAL_DIR else "摘掉旧链接并重建"
            print(f"  ~ {source.name}  {reason}，{action}")
            if args.dry_run:
                created += 1
                continue
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                remove_target(link)
                create_link(source, link)
                created += 1
            except (OSError, RuntimeError) as exc:
                print(f"    失败：{exc}")
                errors += 1

        leftovers = stale_links(target_dir, keep)
        for entry in leftovers:
            if not args.force:
                print(f"  ! {entry.name}  源码里已没有这个技能，跳过（加 --force 清理）")
                blocked += 1
                continue
            print(f"  - {entry.name}  清理悬挂链接")
            if args.dry_run:
                continue
            try:
                remove_link(entry)
            except OSError as exc:
                print(f"    失败：{exc}")
                errors += 1
        print()

    if args.dry_run:
        print("预演完成，未做任何改动。确认后去掉 --dry-run 重新执行。")
    else:
        print("完成。链接是实时的，之后改 SKILL.md 或 git pull 都不必重装。")
        print("客户端里显示旧内容时，新开一个会话即可刷新技能列表。")
    print(f"新增 / 替换 {created} 项，跳过 {blocked} 项，失败 {errors} 项。")
    return 1 if errors or blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())

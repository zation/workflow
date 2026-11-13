#!/usr/bin/env python3
"""把 skills/ 下的技能挂到各 coding agent 的用户级技能目录。

只创建目录链接，不覆盖、不删除任何已有内容。加 --dry-run 只打印计划。
"""

from __future__ import annotations

import argparse
import locale
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
TARGETS = {
    "workbuddy": Path.home() / ".workbuddy" / "skills",
    "codebuddy": Path.home() / ".codebuddy" / "skills",
    "codex": Path.home() / ".agents" / "skills",
}


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


def points_to(link: Path, source: Path) -> bool:
    try:
        return link.resolve() == source.resolve()
    except OSError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="把 skills/ 下的技能挂到各 coding agent 的技能目录（只创建链接，不覆盖）。"
    )
    parser.add_argument(
        "--target", choices=[*TARGETS, "all"], default="all", help="安装到哪个平台，默认全部"
    )
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不创建链接")
    args = parser.parse_args()

    skills = sorted(
        p for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()
    )
    if not skills:
        print(f"错误：{SKILLS_DIR} 下没有找到带 SKILL.md 的技能目录。")
        return 2

    names = list(TARGETS) if args.target == "all" else [args.target]
    print(f"源码：{SKILLS_DIR}")
    print(f"模式：{'预演（不创建）' if args.dry_run else '创建链接'}\n")

    errors = 0
    for name in names:
        target_dir = TARGETS[name]
        print(f"[{name}] {target_dir}")
        for source in skills:
            link = target_dir / source.name
            if link.exists() or link.is_symlink():
                if points_to(link, source):
                    print(f"  = {source.name}  已安装")
                elif not link.exists():
                    print(f"  ! {source.name}  是失效链接，跳过（请手动移除后重试）")
                    errors += 1
                else:
                    print(f"  ! {source.name}  已存在且指向别处，跳过（不覆盖）")
                    errors += 1
                continue
            print(f"  + {source.name}  -> {source}")
            if not args.dry_run:
                try:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    create_link(source, link)
                except (OSError, RuntimeError) as exc:
                    print(f"    失败：{exc}")
                    errors += 1
        print()

    if args.dry_run:
        print("预演完成，未创建任何链接。确认后去掉 --dry-run 重新执行。")
    else:
        print("完成。新装的技能可能需要重启客户端或新开会话才会出现在列表里。")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

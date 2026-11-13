"""workflow skill 的公共工具。"""

from __future__ import annotations

import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = SKILL_DIR / "assets" / "templates"
AGENTS_TEMPLATE = TEMPLATES_DIR / "AGENTS.md"
DOCS_TEMPLATE_DIR = TEMPLATES_DIR / "docs"

DOC_SKELETON = (
    "product-brief.md",
    "technical-architecture.md",
    "data-model.md",
    "devops.md",
)

EMPTY_DOC_DIRS = ("backlog", "delivery")


def force_utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def normalize_text(text: str) -> str:
    text = text.lstrip("\ufeff")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).strip("\n") + "\n"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


#!/usr/bin/env python
"""临时检索：python tools/q.py books/<slug> 关键词1 [关键词2 ...]

中英通用的取句工具：打印同时包含所有关键词、长度 16–150（去空格计字）的句子，
带 md 页号与字数。关键词也去空格比较，故英文可写 "relative medium" 或 "relativemedium"。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPLIT = re.compile(r"(?<=[。！？；.!?;])[\s\u3000]*")
NOISE = re.compile(r"\[[a-z_]+\]|!\[[^\]]*\]\([^)]*\)|\*图注\*：")


def load_pages(book_md: Path):
    pages, cur, buf = [], None, []
    for line in book_md.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^## (p\d+)$", line.strip())
        if m:
            if cur:
                pages.append((cur, "\n".join(buf)))
            cur, buf = m.group(1), []
        elif cur:
            buf.append(line)
    if cur:
        pages.append((cur, "\n".join(buf)))
    return pages


def flat(s: str) -> str:
    return re.sub(r"\s+", "", s)


def main() -> int:
    if len(sys.argv) < 3:
        print("用法: python tools/q.py books/<slug> 词1 [词2 ...]")
        return 2
    pages = load_pages(ROOT / sys.argv[1] / "source" / "book.md")
    keys = [flat(k) for k in sys.argv[2:]]
    n = 0
    for pid, txt in pages:
        body = NOISE.sub("", txt)
        spaced = re.sub(r"[ \t\u3000]+", " ", body)
        for s in SPLIT.split(spaced):
            s = s.strip()
            body_flat = flat(s)
            if not (16 <= len(body_flat) <= 150):
                continue
            if all(k in body_flat for k in keys):
                print(f"{pid} [{len(body_flat)}] {s}")
                n += 1
                if n >= 30:
                    return 0
    if n == 0:
        print("（无命中）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

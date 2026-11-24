# -*- coding: utf-8 -*-
"""按页锚 dump book.md 指定页，带字数上限，用于精读而不必整本读。

用法： python tools\\peek.py linquan-gaozhi p047 p050 p054 [--cap 1400]
"""
import argparse
import re
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("slug")
ap.add_argument("pages", nargs="+")
ap.add_argument("--cap", type=int, default=1400)
a = ap.parse_args()

md = Path(f"books/{a.slug}/source/book.md").read_text(encoding="utf-8")
parts = re.split(r"^## (p\d+)$", md, flags=re.M)
pages = {}
for i in range(1, len(parts), 2):
    pages[parts[i]] = parts[i + 1]

for p in a.pages:
    body = (pages.get(p) or "").strip()
    body = re.sub(r"!\[[^\]]*\]\(images/[^)]*\)", "[图]", body)
    print(f"===== {p} ({len(body)} 字) =====")
    print(body[: a.cap])
    if len(body) > a.cap:
        print(f"…（余 {len(body) - a.cap} 字）")
    print()

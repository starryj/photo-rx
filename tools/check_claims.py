#!/usr/bin/env python
"""核对 claims.yaml 里每条引文是否真的出现在它标注的那一页。

用法：
    python tools/check_claims.py books/color-bible/claims/claims.yaml
    python tools/check_claims.py --all

判定三档：
    OK      引文在标注页内命中（宽松匹配：去标点、去空白）
    MOVED   引文在全书别处命中 —— 报真实页号，需要改 page
    MISSING 全书都没命中 —— 可能是 OCR 错字，也可能是引文记错
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

PUNCT = dict.fromkeys(
    map(ord, "，。、；：？！「」『』（）()《》〈〉“”‘’\"'.,;:?!-—…·　 \t\n\r*_`~[]{}<>/\\|"),
    None,
)


def norm(s: str) -> str:
    return (s or "").translate(PUNCT)


def load_pages(book_md: Path) -> list[tuple[str, str]]:
    """返回 [(page_id, text), ...]，按 book.md 顺序。"""
    pages: list[tuple[str, str]] = []
    cur = None
    buf: list[str] = []
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("claims", nargs="?", help="claims.yaml 路径")
    ap.add_argument("--all", action="store_true", help="扫描所有 books/*/claims/claims.yaml")
    ap.add_argument("--quiet-ok", action="store_true", default=True)
    args = ap.parse_args()

    targets: list[Path] = []
    if args.all:
        targets = sorted(ROOT.glob("books/*/claims/claims.yaml"))
    elif args.claims:
        targets = [Path(args.claims)]
    else:
        ap.error("需要 claims 路径或 --all")

    grand = {"OK": 0, "MOVED": 0, "MISSING": 0}
    for target in targets:
        slug = target.parents[1].name
        book_md = ROOT / "books" / slug / "source" / "book.md"
        if not book_md.exists():
            print(f"!! {slug}: 缺 source/book.md")
            continue
        pages = load_pages(book_md)
        npages = {pid: norm(txt) for pid, txt in pages}
        whole = norm("\n".join(t for _, t in pages))

        items = yaml.safe_load(target.read_text(encoding="utf-8")) or []
        stats = {"OK": 0, "MOVED": 0, "MISSING": 0}
        print(f"\n=== {slug} · {len(items)} 条 · {len(pages)} 页 ===")
        for it in items:
            cid = it.get("id", "?")
            page = str(it.get("page", "")).strip()
            quote = it.get("quote", "") or ""
            nq = norm(quote)
            if not nq:
                print(f"  MISSING {cid}  引文为空")
                stats["MISSING"] += 1
                continue
            if page in npages and nq in npages[page]:
                stats["OK"] += 1
                continue
            # 找真实页
            hits = [pid for pid, txt in npages.items() if nq in txt]
            if hits:
                stats["MOVED"] += 1
                print(f"  MOVED   {cid} 标注 {page} → 实际 {hits[0]}{' 等' if len(hits) > 1 else ''}")
                print(f"          {quote[:60]}")
            else:
                # 尝试前缀（引文被 OCR 截断/破坏）
                head = nq[:24]
                phits = [pid for pid, txt in npages.items() if head and head in txt]
                stats["MISSING"] += 1
                if phits:
                    print(f"  MISSING {cid} 全文未命中，但前 {len(head)} 字在 {phits[0]} 命中（多半是 OCR 错字）")
                else:
                    print(f"  MISSING {cid} 全书未命中 @{page}")
                print(f"          {quote[:70]}")
        print(f"  -- OK {stats['OK']} / MOVED {stats['MOVED']} / MISSING {stats['MISSING']}")
        for k in grand:
            grand[k] += stats[k]

    print(f"\n总计：OK {grand['OK']} / MOVED {grand['MOVED']} / MISSING {grand['MISSING']}")
    return 0 if grand["MOVED"] == 0 and grand["MISSING"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

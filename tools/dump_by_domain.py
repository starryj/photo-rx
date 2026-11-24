"""按 domain 汇总三本书的 claims，供阶段 1.6 归一判断。"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ["color-bible", "interacting-with-color", "interaction-of-color"]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    by_dom: dict[str, list[tuple[str, str, str, str, str]]] = defaultdict(list)
    for b in BOOKS:
        p = ROOT / "books" / b / "claims" / "claims.yaml"
        for c in yaml.safe_load(p.read_text(encoding="utf-8")):
            by_dom[c["domain"]].append(
                (b, c["id"], c["page"], c["operational"], c["claim"])
            )
    for dom in sorted(by_dom, key=lambda d: -len(by_dom[d])):
        rows = by_dom[dom]
        print(f"\n=== {dom} · {len(rows)} ===")
        for b, cid, page, op, claim in rows:
            print(f"  [{b[:4]}] {cid} {page} ({op}) {claim}")
    print(f"\n合计 {sum(len(v) for v in by_dom.values())} 条 · {len(by_dom)} 个 domain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

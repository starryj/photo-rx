"""补齐归一库缺少的 source 行（这些 id 已在 merged_from 里但没建 sources 行）。"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ["color-bible", "interacting-with-color", "interaction-of-color"]
NEED = {"C001": ["oc01"], "C006": ["hc19"], "C012": ["hc05", "hc06"], "C028": ["oc31"], "C048": ["cb26"]}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    book_of: dict[str, tuple[str, str, str]] = {}
    for b in BOOKS:
        for c in yaml.safe_load((ROOT / "books" / b / "claims" / "claims.yaml").read_text(encoding="utf-8")):
            book_of[c["id"]] = (b, str(c["page"]), c["quote"])

    norm_path = ROOT / "claims" / "claims.yaml"
    norm = yaml.safe_load(norm_path.read_text(encoding="utf-8"))
    added = 0
    for c in norm:
        have = {s.get("id") for s in c.get("sources", [])}
        for cid in NEED.get(c["id"], []):
            if cid in have:
                continue
            b, p, q = book_of[cid]
            c.setdefault("sources", []).append({"book": b, "id": cid, "page": p, "quote": q})
            added += 1
    norm_path.write_text(yaml.safe_dump(norm, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8")
    print(f"added {added} source rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

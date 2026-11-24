# -*- coding: utf-8 -*-
"""批八归一：把《观看之道》《秩序感》的单书 claim 并入归一库（知识层，不新增卡片）。

两本共 54 条：观看之道 24 条（C218–C241）、秩序感 30 条（C242–C271）。
归一主张文本沿用单书 claim（已过 20–60 字与 check_claims）；stance 按书分：
观看之道→相对派，秩序感→结构派；operational 由单书 type 映射。
"""
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
NORM = ROOT / "claims" / "claims.yaml"
BOOKS = [
    ("ways-of-seeing", "C218", "相对派"),
    ("sense-of-order", "C242", "结构派"),
]
OP = {
    "framework": "framework",
    "principle": "principle",
    "mechanism": "principle",
    "case": "case",
    "counter-example": "case",
}


def main():
    backup = NORM.with_name("claims.yaml.bak-20261124-b8")
    if not backup.exists():
        shutil.copy2(NORM, backup)
    rows = yaml.safe_load(NORM.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in rows}

    seq = 218
    added = 0
    for slug, start, stance in BOOKS:
        path = ROOT / "books" / slug / "claims" / "claims.yaml"
        book = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert start == f"C{seq}", (start, seq)
        for c in book:
            cid = f"C{seq}"
            assert cid not in by_id, cid
            item = dict(
                id=cid,
                claim=c["claim"],
                domain=c["domain"],
                stance=stance,
                operational=OP[c["type"]],
                merged_from=[c["id"]],
                single_source=True,
                sources=[{"book": slug, "id": c["id"], "page": c["page"], "quote": c["quote"]}],
            )
            rows.append(item)
            by_id[cid] = item
            seq += 1
            added += 1

    NORM.write_text(
        yaml.safe_dump(rows, allow_unicode=True, sort_keys=False, width=200),
        encoding="utf-8",
    )
    print(f"归一总数 {len(rows)} · 新增主张 {added} 条")
    for slug, _, _ in BOOKS:
        book = yaml.safe_load((ROOT / "books" / slug / "claims" / "claims.yaml").read_text(encoding="utf-8"))
        used = {s["id"] for c in rows for s in c["sources"] if s["book"] == slug}
        print(f"{slug} 覆盖 {len(used & {c['id'] for c in book})}/{len(book)}")
        miss = [c["id"] for c in book if c["id"] not in used]
        if miss:
            print("未被引用：", miss)
            sys.exit(1)


if __name__ == "__main__":
    main()
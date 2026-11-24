"""用三本书已校验过的 claims.yaml 回填归一库的 quote / page，避免凭记忆重写引文。

用法：
    python tools/sync_claim_quotes.py            # 回填并报告差异
    python tools/sync_claim_quotes.py --check    # 只报告不一致，不写回
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
def discover_books() -> list[str]:
    """扫 books/*/claims/claims.yaml，避免每加一本书都要改名单。"""
    return sorted(
        p.parents[1].name
        for p in (ROOT / "books").glob("*/claims/claims.yaml")
    )


BOOKS: list[str] = []
NORM = ROOT / "claims" / "claims.yaml"


def load_originals() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for b in discover_books():
        p = ROOT / "books" / b / "claims" / "claims.yaml"
        for c in yaml.safe_load(p.read_text(encoding="utf-8")):
            if c["id"] in out:
                raise SystemExit(f"重复 id: {c['id']}")
            c["_book"] = b
            out[c["id"]] = c
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    check_only = "--check" in sys.argv
    orig = load_originals()
    norm = yaml.safe_load(NORM.read_text(encoding="utf-8"))
    if not isinstance(norm, list):
        raise SystemExit(f"归一库格式应为 list，实际 {type(norm)}")

    seen: dict[str, str] = {}
    drift = 0
    for c in norm:
        for s in c.get("sources", []):
            cid = s.get("id")
            if not cid:
                continue
            if cid not in orig:
                raise SystemExit(f"{c['id']}: 未知原始 id {cid}")
            if cid in seen:
                raise SystemExit(f"原始 id {cid} 被 {seen[cid]} 与 {c['id']} 重复引用")
            seen[cid] = c["id"]
            o = orig[cid]
            if s.get("quote") != o["quote"] or str(s.get("page")) != str(o["page"]):
                drift += 1
                if check_only:
                    print(f"DRIFT {c['id']} <- {cid}: page {s.get('page')}->{o['page']}")
                s["quote"] = o["quote"]
                s["page"] = o["page"]
        lost = [i for i in c.get("merged_from", []) if i not in seen or seen[i] != c["id"]]
        if lost:
            print(f"WARN {c['id']}: merged_from 与 sources 不一致 {lost}")

    missing = sorted(set(orig) - set(seen))
    if missing:
        print(f"未归一的原始条目 {len(missing)}: {' '.join(missing)}")

    if not check_only:
        NORM.write_text(
            yaml.safe_dump(norm, allow_unicode=True, sort_keys=False, width=200),
            encoding="utf-8",
        )
    print(f"归一 {len(norm)} 条 · 引用原始 {len(seen)}/{len(orig)} · 回填 {drift} 处")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())

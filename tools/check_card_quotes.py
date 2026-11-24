"""校验能力卡里的引号内容确实逐字出自原书（或至少出自 claims 里已校验的引文）。

规则：卡片里凡被 「…」 或 "…" 包住、且长度 ≥8 的片段，都应能在下列任一处找到（去标点空白后比对）：
  1) 归一库 claims/claims.yaml 的任一 quote
  2) 任一本书 book.md 的正文
找不到就报 UNVERIFIED —— 这类残留通常是我按记忆重写的中文转述，必须去掉引号或改成「译」。

用法：python tools/check_card_quotes.py skills/color-decision.md
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BOOKS = sorted(x.parent.parent.name for x in (ROOT / "books").glob("*/source/book.md"))
PUNCT = "　 \t\r\n“”‘’「」『』\"'…—－-–·、，。；：！？（）()【】[]《》〈〉,.;:!?/\\|*_#`~+=<>"


def norm(s: str) -> str:
    return "".join(ch for ch in s if ch not in PUNCT)


def strip_md_marks(s: str) -> str:
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", s)
    s = re.sub(r"\[(p\d+)-f\d+[^\]]*\]", " ", s)
    s = re.sub(r"^\s*#+\s*", " ", s, flags=re.M)
    s = re.sub(r"\[[a-z_]+\]", " ", s)
    return s


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2:
        raise SystemExit("用法：python tools/check_card_quotes.py <card.md> [...]")

    corpus = []
    for b in BOOKS:
        p = ROOT / "books" / b / "source" / "book.md"
        corpus.append(norm(strip_md_marks(p.read_text(encoding="utf-8"))))
    claims = yaml.safe_load((ROOT / "claims" / "claims.yaml").read_text(encoding="utf-8"))
    for bp in sorted((ROOT / "books").glob("*/claims/claims.yaml")):
        d = yaml.safe_load(bp.read_text(encoding="utf-8")) or []
        if isinstance(d, dict):
            d = d.get("claims", [])
        for c in d:
            corpus.append(norm(c.get("quote") or ""))
    cq = [norm(c["quote"]) for c in claims for c in c.get("sources", [])]
    claims_dump = yaml.safe_dump(claims, allow_unicode=True)
    corpus.append(norm(claims_dump))
    corpus = "\n".join(corpus)
    allq = cq

    bad = total = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        text = path.read_text(encoding="utf-8")
        spans = re.findall(r"「([^」]{8,400})」", text) + re.findall(r'"([^"\n]{8,400})"', text)
        print(f"\n=== {path} · 引号片段 {len(spans)} ===")
        for s in spans:
            total += 1
            n = norm(s)
            if not n:
                continue
            if any(n in q or q in n for q in allq):
                continue
            if n in corpus:
                continue
            bad += 1
            print(f"  UNVERIFIED: {s[:80]}")
    print(f"\n合计 {total} 片段 · 未逐字命中 {bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

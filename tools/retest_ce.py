# -*- coding: utf-8 -*-
"""chinese-eye 定点复测：卡片 R/I/E 与描述改动后，只重跑与它相关的用例。

选取规则（去重后约 30 条）：
  1) expect == chinese-eye  —— 应被它接住
  2) src   == chinese-eye  —— 它自己出的题（含 6 条不该被它接住的）
  3) ACCEPT 里把 chinese-eye 列为并列接受的题 —— 改描述后最容易被它抢走的

用法：
  python tools\\retest_ce.py build      # 生成 out\\retest-ce\\{surface.md, cases.json, r1.txt..r4.txt}
  python tools\\retest_ce.py grade      # 读 out\\retest-ce\\r*.json 判卷
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "retest-ce"
BLIND = ROOT / "out" / "blind" / "cases.json"
DIST = ROOT / "out" / "dist"

# 与 build_blind_pv.py 保一致
ACCEPT = {
    "这张是不是太满了": {"chinese-eye", "structure-read"},
    "雾天怎么拍才有那个意境": {"chinese-eye", "shoot-plan"},
    "修掉细节之后反而更像了，这是为什么": {"ways-of-seeing", "chinese-eye"},
    "为什么留白会让人觉得安静": {"ways-of-seeing", "chinese-eye"},
    "画面太空了，是不是要加点东西进去": {"chinese-eye", "structure-read"},
    "为什么这张会让人觉得空": {"chinese-eye", "ways-of-seeing"},
    "留白不够的那张要不要删": {"chinese-eye", "cull-select"},
}
ENTRIES = [
    "color-decision",
    "structure-read",
    "shoot-plan",
    "ways-of-seeing",
    "chinese-eye",
    "sequence-edit",
    "cull-select",
    "photo-vision",
]


def surface() -> str:
    """从当前 dist 的 SKILL.md frontmatter 取描述，确保用的是改完卡之后的文本。"""
    blocks = ["# 可用入口清单（只给名称与描述）\n"]
    for e in ENTRIES:
        p = DIST / e / "SKILL.md"
        txt = p.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
        desc = ""
        if m:
            fm = yaml.safe_load(m.group(1)) or {}
            desc = (fm.get("description") or "").strip()
        blocks.append(f"### {e}\n{desc}\n")
    return "\n".join(blocks)


def build() -> None:
    items = json.loads(BLIND.read_text(encoding="utf-8"))["items"]
    pick, seen = [], set()
    for it in items:
        p = it["prompt"]
        if p in seen:
            continue
        if (
            it["expect"] == "chinese-eye"
            or it.get("src") == "chinese-eye"
            or (p in ACCEPT and "chinese-eye" in ACCEPT[p])
        ):
            seen.add(p)
            pick.append({"prompt": p, "expect": it["expect"], "src": it.get("src", "")})

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "surface.md").write_text(surface(), encoding="utf-8")
    (OUT / "cases.json").write_text(
        json.dumps(pick, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    n = len(pick)
    k = 4
    size = math.ceil(n / k)
    for i in range(k):
        chunk = pick[i * size : (i + 1) * size]
        lines = [f"{j+1}. {c['prompt']}" for j, c in enumerate(chunk)]
        (OUT / f"r{i+1}.txt").write_text("\n".join(lines), encoding="utf-8")
    acc = {
        f"r{i+1}": [
            {"prompt": c["prompt"], "accept": sorted(ACCEPT.get(c["prompt"], {c["expect"]}))}
            for c in pick[i * size : (i + 1) * size]
        ]
        for i in range(k)
    }
    (OUT / "accept.json").write_text(
        json.dumps(acc, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"用例 {n} 条 · 切 {k} 批（每批 ≤{size}）· 输出 {OUT}")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d, (c + m) / d)


def grade() -> None:
    acc = json.loads((OUT / "accept.json").read_text(encoding="utf-8"))
    ok = bad = 0
    rows = []
    for batch, items in acc.items():
        f = OUT / f"{batch}.json"
        if not f.exists():
            print(f"缺 {f.name}，跳过")
            continue
        ans = json.loads(f.read_text(encoding="utf-8"))
        got = {a["n"]: a["entry"] for a in ans}
        for i, it in enumerate(items, 1):
            g = got.get(i, "")
            good = g in it["accept"]
            ok += good
            bad += not good
            rows.append((batch, i, it["prompt"], g, "/".join(it["accept"]), good))
    print(f"\n{'批':<4}{'#':<4}{'prompt':<34}{'答':<16}{'应':<26}判")
    for b, i, p, g, e, good in rows:
        print(f"{b:<4}{i:<4}{p[:32]:<34}{g:<16}{e[:24]:<26}{'✓' if good else '✗'}")
    n = len(rows)
    lo, hi = wilson(ok, n)
    print(f"\n结果 {ok}/{n} = {ok/n:.1%} · Wilson 95% [{lo:.1%}, {hi:.1%}]")
    print(f"错 {bad} 条")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    build() if cmd == "build" else grade()

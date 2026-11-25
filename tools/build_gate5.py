# -*- coding: utf-8 -*-
"""gate5：六维口径与拒单边界的盲测用例生成与计分。

用法：
  python tools/build_gate5.py build     # 生成 out/gate5/cases.json 与 cases-blind.json
  python tools/build_gate5.py score     # 用 cases.json 的期望比对 judge.json

用例只覆盖「走哪个入口、用哪套口径、该不该拒」，不判分数是否合理。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "gate5"

CASES = [
    ("s01", "这张雪山片子能打几分？准备发朋友圈。", "frame-critique", "western", "默认口径；无中式语汇"),
    ("s02", "这张的留白是不是留得太大？能打个分吗，我想知道差在哪。", "frame-critique", "chinese", "用户自带「留白」语汇 → 中式"),
    ("s03", "这是我拍的水墨风山景，给个分。", "frame-critique", "chinese", "题材判断：水墨山景 → 中式"),
    ("s04", "这 20 张都给我打个分，然后按分数排个序，我要挑 5 张交。", "cull-select", "n/a", "一批 + 名额 → 先删后排"),
    ("s05", "颜色怎么调都不对，这张到底几分？", "frame-critique", "western", "要分数进本卡；色维引 color-decision"),
    ("s06", "这两张哪张强？各强在哪一维？", "frame-critique", "western", "两张同批比较，可打分"),
    ("s07", "这张放到国际影展里能排第几？", "refuse-cross-batch", "n/a", "跨批比较必须拒绝"),
    ("s08", "这张几分？", "ask-purpose", "pending", "用途未定 → 先问"),
    ("s09", "这张是手抖糊了，但还是给我打个分吧。", "frame-critique", "western", "硬缺陷 → 总分封顶 60"),
    ("s10", "这 12 张用你的尺子给我排个先后。", "sequence-edit", "n/a", "排序不是打分"),
    ("s11", "气韵生动到底什么意思？", "glossary", "n/a", "术语解释，不打分"),
    ("s12", "帮我把它凑到 85 分，告诉我该改哪几处。", "refuse-score-chasing", "n/a", "不许先定分再倒推"),
]


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    full = [
        {"id": i, "query": q, "expect_route": r, "expect_scale": s, "note": n}
        for i, q, r, s, n in CASES
    ]
    (OUT / "cases.json").write_text(json.dumps(full, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    blind = [{"id": i, "query": q} for i, q, _, _, _ in CASES]
    (OUT / "cases-blind.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(full)} cases -> {OUT}")


def score() -> int:
    judge = {d["id"]: d for d in json.loads((OUT / "judge.json").read_text(encoding="utf-8"))}
    ok = route_ok = scale_ok = 0
    for i, q, r, s, _ in CASES:
        got = judge.get(i, {})
        hit_route = got.get("route") == r
        hit_scale = got.get("scale") == s
        route_ok += hit_route
        scale_ok += hit_scale
        ok += hit_route and hit_scale
        mark = "OK " if hit_route and hit_scale else "MISS"
        print(f"{mark} {i}  expect {r}/{s}  got {got.get('route')}/{got.get('scale')}")
    n = len(CASES)
    print(f"\nroute {route_ok}/{n}  scale {scale_ok}/{n}  both {ok}/{n}")
    return 0 if ok == n else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        build()
    elif cmd == "score":
        sys.exit(score())
    else:
        print(__doc__)
        sys.exit(2)

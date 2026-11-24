"""批五（The Art of Pixar）归一 + 两条新对抗。

规则：
- 归一主张的引文一律按原初 id 从 books/art-of-pixar/claims/claims.yaml 搬运，不手抄。
- 归一主张 id 接续 C164；对抗接续 K14。
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BOOK = "art-of-pixar"

GROUPS = [
    ("C164", "序列的单位是「段」不是「张」：把全片每场压成邮票小图连成一条胶片，目的就是让人一眼看到色彩弧；导演第一次能在同一块板上看完自己整部片子的颜色。",
     "方法论", "规则派", "可操作",
     ["px01", "px02", "px19", "px20"]),
    ("C165", "情绪起伏靠换调色板制造（如作曲靠速度、节奏、配器），不靠单场把颜色堆满；下潜段把调色板逐步推到极简与不祥，即主角神经质的图形化。",
     "方法论", "规则派", "可操作",
     ["px03", "px07", "px08"]),
    ("C166", "序列编排的目标不是把各场打扮成最漂亮或最和谐的配色，也不是做漂亮的图，而是支撑故事；但它本身也可以是独立的作品。",
     "和谐与协调", "相对派", "描述性",
     ["px05", "px17", "px25"]),
    ("C167", "一场戏的力量有时不来自加了多少色，而来自减了多少色——减法与加法同等是一等手法。",
     "饱和度", "相对派", "可操作",
     ["px09"]),
    ("C168", "夜景不是「没有颜色」：在限定的调色板里同样能找到色彩机会。",
     "光与时段", "规则派", "可操作",
     ["px10"]),
    ("C169", "高明的序列建立全片性的对抗关系（灰暗日常对撞糖果色想象、冷调地下对暖调人间），用对比去挑动故事里本就存在的紧张。",
     "对比", "规则派", "可操作",
     ["px11", "px12"]),
    ("C170", "色彩可以被赋予只属于这一部作品的意义（粉＝毁灭、蓝＝安全与家），不必沿用通用象征；一旦定义，必须全片执行并在该缺席处刻意缺席。",
     "情绪与象征", "相对派", "可操作",
     ["px13", "px14", "px15"]),
    ("C171", "格式与风格没有标准做法——有多少作者就有多少种版本；但所有作者同意一条：它不在于画得多好，而在于能不能支撑故事。",
     "方法论", "相对派", "描述性",
     ["px16", "px21"]),
    ("C172", "在 Pixar 之前，没有动画公司把色彩与光线对着故事与人物系统排布过；colorscript 这一环节是它制度化出来的。",
     "方法论", "规则派", "描述性",
     ["px18"]),
    ("C173", "怀旧不必等于降饱和：婚后段落该被画成「像你第一次坠入爱河时那样鲜活」，这一处改写重排了全片色彩弧。",
     "饱和度", "规则派", "可操作",
     ["px22", "px23"]),
    ("C174", "最终形象是从无数可能性里削出来的；观众看到的「一直如此」，是筛选结果不是起点。",
     "方法论", "规则派", "描述性",
     ["px24"]),
    ("C175", "colorscript 是色彩（因而也是情绪）在全片如何铺设的一张路线图，同时给出各场的光线设想。",
     "方法论", "规则派", "可操作",
     ["px04"]),
    ("C176", "把序列编排比作作曲：调色板对应乐章与配器，色彩图可类比乐谱。",
     "方法论", "规则派", "描述性",
     ["px06"]),
]

COUNTERS = [
    {
        "id": "K14",
        "kind": "contested",
        "statement": "评价一张照片时，该用单张标准还是整体标准",
        "targets": ["C079", "C080", "C087", "C166"],
        "side_a": {
            "label": "单张要先立得住（结构派）",
            "quotes": [
                "C079", "C080", "C087",
            ],
        },
        "side_b": {
            "label": "序列里弱的单张可以是正确的（编排派）",
            "quotes": ["C166"],
        },
        "resolution": "both-valid-by-scale",
        "rationale": (
            "两把尺量的是不同对象：结构派问「这张自己成不成立」，编排派问「这张在一段里位置对不对」。"
            "同一张片子可以在单张标准下不及格、在序列里恰好承担过渡。"
            "把它裁成一方胜出会导致两种常见事故：用单张标准否掉整段（越挑越平）或用整体标准给单张背书（每张都说「它在组里有作用」而从不承认缺陷）。"
            "故运行时不裁决，按用户问的尺度分岔，并要求在回答开头声明用的是哪把尺。"
        ),
        "reverse_writable": (
            "把结构派写成编排派能接受的形式：「一张片子自身有可检验的缺陷（如无焦点、无平衡），"
            "但它在序列里可能因功能而值得保留——缺陷仍需被指出。」编排派能接受。"
            "反过来把编排派写成结构派能接受的形式：「序列里的位置是一场分配，"
            "但被分配的仍是可被单独评判的片子——位置不改变它的技术事实。」结构派也能接受。"
            "两边互写得通，说明这是真分歧而不是表述差异。"
        ),
        "runtime_action": "branch",
        "branch_condition": (
            "用户问「这张哪里不好／值几分」→ 单张标准（frame-critique、structure-read）。"
            "用户问「这组怎么排／留哪些」→ 整体标准（sequence-edit、cull-select），并在开头声明。"
            "两者同时被问到时串行：先判单张事实，再判序列功能，最后合成一页，不得互相抵扣。"
        ),
    },
    {
        "id": "K15",
        "kind": "contested",
        "statement": "色彩的意义是普遍通用的，还是由作品内部定义的",
        "targets": ["C064", "C170"],
        "side_a": {
            "label": "存在跨作品普遍的色彩效应（规则派）",
            "quotes": ["C064"],
        },
        "side_b": {
            "label": "意义可被作品重新定义（编排派）",
            "quotes": ["C170"],
        },
        "resolution": "split-by-layer",
        "rationale": (
            "两者不在同一层：C064 说的是知觉层（红与其他较弱势彩竞争注意力，这是可复现的观看事实），"
            "C170 说的是语义层（粉＝毁灭、蓝＝家，这是作品内部约定的符号）。"
            "知觉层普遍，语义层局部——把语义层当普遍规律会写出「红色代表危险」这类空话，"
            "把知觉层当约定会否认「红更抢眼」这个可测事实。"
            "故按层分：判断「会不会抢注意力」用知觉层；判断「它意味着什么」必须先问这是哪个作品、作者定义过没有。"
        ),
        "reverse_writable": (
            "把普遍派写成局部派能接受的形式：「某些色彩在注意力竞争上有跨作品的稳定性，但那是知觉机制，不是含义。」局部派能接受。"
            "反向把局部派写成普遍派能接受的形式：「作品可以重新定义色彩的含义，但无法推翻它与其他色彩的注意力竞争关系。」普遍派也能接受。"
            "互写成立，是真分歧。"
        ),
        "runtime_action": "branch",
        "branch_condition": (
            "问「哪个更抢眼／为什么先看到它」→ 知觉层（可用面积、亮度、饱和度、竞争关系解释）。"
            "问「这个颜色意味着什么／该用什么颜色表达某种情绪」→ 语义层，先查该作品是否定义过；未定义时给惯用含义并注明是惯例，不许当成事实。"
        ),
    },
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    raw = yaml.safe_load((ROOT / "books" / BOOK / "claims" / "claims.yaml").read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = raw.get("claims", [])
    by_id = {c["id"]: c for c in raw}

    claims = yaml.safe_load((ROOT / "claims" / "claims.yaml").read_text(encoding="utf-8"))
    if isinstance(claims, dict):
        claims = claims.get("claims", [])

    used = set()
    added = 0
    for cid, text, domain, stance, operational, ids in GROUPS:
        if any(c["id"] == cid for c in claims):
            continue
        sources = []
        for i in ids:
            c = by_id[i]
            used.add(i)
            sources.append({
                "book": BOOK,
                "id": i,
                "page": c["page"],
                "quote": c["quote"],
            })
        claims.append({
            "id": cid,
            "claim": text,
            "domain": domain,
            "stance": stance,
            "operational": operational,
            "merged_from": ids,
            "single_source": True,
            "sources": sources,
        })
        added += 1

    missing = [i for i in by_id if i not in used]
    if missing:
        print(f"[WARN] 未被任何归一主张引用的原初 id（{len(missing)}）：{', '.join(missing)}")

    io.open(ROOT / "claims" / "claims.yaml", "w", encoding="utf-8").write(
        yaml.safe_dump(claims, allow_unicode=True, sort_keys=False, width=100000)
    )

    counters = yaml.safe_load((ROOT / "counters" / "counters.yaml").read_text(encoding="utf-8"))
    if isinstance(counters, dict):
        counters = counters.get("counters", [])
    existing = {c["id"] for c in counters}
    cmap = {c["id"]: c for c in claims}

    def quote_of(cid: str) -> dict:
        c = cmap[cid]
        s = c["sources"][0]
        return {"claim": cid, "book": s["book"], "page": s["page"], "quote": s["quote"]}

    for spec in COUNTERS:
        if spec["id"] in existing:
            continue
        item = {
            "id": spec["id"],
            "kind": spec["kind"],
            "statement": spec["statement"],
            "targets": spec["targets"],
            "side_a": {
                "label": spec["side_a"]["label"],
                "quotes": [quote_of(x) for x in spec["side_a"]["quotes"]],
            },
            "side_b": {
                "label": spec["side_b"]["label"],
                "quotes": [quote_of(x) for x in spec["side_b"]["quotes"]],
            },
            "resolution": spec["resolution"],
            "resolution_by": "editor",
            "rationale": spec["rationale"],
            "reverse_writable": spec["reverse_writable"],
            "runtime_action": spec["runtime_action"],
            "branch_condition": spec["branch_condition"],
        }
        counters.append(item)

    io.open(ROOT / "counters" / "counters.yaml", "w", encoding="utf-8").write(
        yaml.safe_dump(counters, allow_unicode=True, sort_keys=False, width=100000)
    )

    print(f"追加归一 {added} 条 · 归一总数 {len(claims)} · 对抗总数 {len(counters)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

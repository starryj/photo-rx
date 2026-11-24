# -*- coding: utf-8 -*-
"""批六 verified.yaml 更新：把郭熙《林泉高致》接进包。

- book 元数据加第十一本；
- chinese-eye 的 source_evidence 加第一手出处，并在说明里点明「三远现在是第一手支撑」；
- entry.core_principles 增一条「三大」的量级判据。
幂等：重复运行不会重复插入。
"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / ".cangjie" / "capabilities" / "verified.yaml"

d = yaml.safe_load(P.read_text(encoding="utf-8"))

book = d["book"]
if "林泉高致" not in book["title"]:
    book["title"] = book["title"].replace(
        "批一至批五", "批一至批六"
    ) + " / 林泉高致"
if "郭熙" not in book["author"]:
    book["author"] += " / 郭熙（杨伯 编著）"
if "linquan-gaozhi" not in book["source_pack"]:
    book["source_pack"] = book["source_pack"].replace(
        "{color-bible", "{linquan-gaozhi,color-bible"
    )
if "中华书局" not in book["baseline_tag"]:
    book["baseline_tag"] += " / 中华书局（杨伯 编著，含注释·译文·点评）"

cap = next(c for c in d["capabilities"] if c["capability_id"].endswith(".chinese-eye"))
if not any(s["source_id"] == "src-linquan-gaozhi" for s in cap["source_evidence"]):
    cap["source_evidence"].insert(
        0,
        {
            "source_id": "src-linquan-gaozhi",
            "location": "林泉高致 p023、p027、p047、p050、p054、p063、p079、p081、p087、p108",
        },
    )
r = cap["importance_rationale"]
if "第一手" not in r:
    cap["importance_rationale"] = r + (
        " batch 6 把郭熙《林泉高致》收进来之后，三远、三大、远近分工、景外意都改由第一手支撑；"
        "此前全靠宗白华与叶朗的转引，且两处措辞与原文有差（「冲融而缥缈」「矫侈之目」），已按原文改正。"
    )
desc = cap["frontmatter"]["description"]
if "三大" not in desc:
    cap["frontmatter"]["description"] = desc.replace(
        "，或」", "，或用「三大」问比例对不对，或」"
    ) if "，或」" in desc else desc + " 也可用于按郭熙「三大」量级比例（山大于木、木大于人）自查主次。"

cp = d["entry"]["core_principles"]
if not any("三大" in x for x in cp):
    cp.append(
        "比例按量级算，不按观感算：山大于木、木大于人，且必须大出数十百倍才显其大（郭熙「三大」）；"
        "没有共同单位时先找最小可辨识物当尺。"
    )

P.write_text(
    yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8"
)
print("capabilities:", len(d["capabilities"]), "· core_principles:", len(cp))
print("book:", book["title"][:40], "…")

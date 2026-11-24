# -*- coding: utf-8 -*-
"""批六归一：把郭熙《林泉高致》的第一手引文并入既有归一库。

做两件事：
1) 给既有归一主张追加 linquan-gaozhi 的 source（第一手支撑），并同步 merged_from；
2) 为这一批真正新的内容新增 C177–C186 十条归一主张。

引文一律按 id 从 `books/linquan-gaozhi/claims/claims.yaml` 搬运，不经手抄。
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
NORM = ROOT / "claims" / "claims.yaml"
LQ = ROOT / "books" / "linquan-gaozhi" / "claims" / "claims.yaml"

# 既有归一主张 ← 追加的第一手 id
ATTACH = {
    "C144": ["lq19", "lq20"],
    "C148": ["lq26"],
    "C149": ["lq05"],
    "C150": ["lq06", "lq10"],
    "C151": ["lq03", "lq04"],
    "C152": ["lq14", "lq15"],
    "C153": ["lq08"],
    "C154": ["lq12", "lq13"],
}

# 新增归一主张（C177 起）
NEW = [
    dict(
        id="C177",
        claim="「三大」是比例纲领：山大于木、木大于人，且必须大出数十百倍才显出「大」；"
        "落地做法是以树叶作共同单位——若干木叶可敌一人之头，据此换算人、木、山的尺寸",
        domain="数量与面积",
        stance="中国观看",
        operational="framework",
        merged_from=["lq22", "lq23"],
    ),
    dict(
        id="C178",
        claim="三远各自配套人物尺度：高远者明了故不可画小，深远者细碎故不可画长，平远者冲澹故不可画大",
        domain="数量与面积",
        stance="中国观看",
        operational="principle",
        merged_from=["lq21"],
    ),
    dict(
        id="C179",
        claim="「远山无皴，远水无波，远人无目。非无也，如无尔」——远景不是真的没有细节，而是看起来像没有；"
        "距离本身就是一次简化",
        domain="空间",
        stance="中国观看",
        operational="principle",
        merged_from=["lq24"],
    ),
    dict(
        id="C180",
        claim="画面里每个元素都应承担一件判读任务：人物标道路、楼观标胜概、林木映蔽分远近、溪谷继续分深浅——"
        "元素不是填充，是标注",
        domain="构图与结构",
        stance="中国观看",
        operational="framework",
        merged_from=["lq11"],
    ),
    dict(
        id="C181",
        claim="用身体作画法判据：石为天地之骨（贵坚深而不浅露），水为天地之血（贵周流而不凝滞）；"
        "山得水而活、水得山而媚；山无烟云则如春无花草",
        domain="构图与结构",
        stance="中国观看",
        operational="principle",
        merged_from=["lq16", "lq17", "lq18"],
    ),
    dict(
        id="C182",
        claim="地貌决定林木形态：土山戴石则林瘦耸，石山戴土则林肥茂；土厚处有千尺之松，土薄处只有数尺之蘖",
        domain="构图与结构",
        stance="中国观看",
        operational="principle",
        merged_from=["lq25"],
    ),
    dict(
        id="C183",
        claim="尺度完整性的判据：铺成巨幅不显赘余，收成小景不觉得缺了什么——大小是完成度问题，不是画幅问题",
        domain="构图与结构",
        stance="中国观看",
        operational="principle",
        merged_from=["lq02"],
    ),
    dict(
        id="C184",
        claim="山水画的本意是替代性满足：让人「不下堂筵，坐穷泉壑」，在画中重新获得林泉之志",
        domain="情绪与象征",
        stance="中国观看",
        operational="framework",
        merged_from=["lq01"],
    ),
    dict(
        id="C185",
        claim="云气与烟岚都要求「见其大象而不为斩刻之形」「见其大意而不为刻画之迹」——抓总体气象、不做雕琢刻板的形，态度才活",
        domain="光与时段",
        stance="中国观看",
        operational="principle",
        merged_from=["lq07", "lq09"],
    ),
    dict(
        id="C186",
        claim="传世口诀（附录二《山水赋》，旧题荆浩，与传为王维《山水论》文字基本相同）："
        "「凡画山水，意在笔先。丈山尺树，寸马豆人」——非郭熙本文，收作旁证",
        domain="数量与面积",
        stance="中国观看",
        operational="framework",
        merged_from=["lq27"],
    ),
]


def main():
    rows = yaml.safe_load(NORM.read_text(encoding="utf-8"))
    lq = {c["id"]: c for c in yaml.safe_load(LQ.read_text(encoding="utf-8"))}
    by_id = {c["id"]: c for c in rows}

    def src(cid):
        c = lq[cid]
        return {"book": "linquan-gaozhi", "id": cid, "page": c["page"], "quote": c["quote"]}

    added_src = 0
    for cid, extras in ATTACH.items():
        n = by_id[cid]
        have = {s["id"] for s in n["sources"]}
        for e in extras:
            if e in have:
                continue
            if e in n["merged_from"]:
                continue
            n["sources"].append(src(e))
            n["merged_from"].append(e)
            added_src += 1
        n["single_source"] = False

    for item in NEW:
        assert item["id"] not in by_id, item["id"]
        item = dict(item)
        item["single_source"] = len(set(item["merged_from"])) == 1
        item["sources"] = [src(i) for i in item["merged_from"]]
        rows.append(item)

    # merged_from 顺序稳定，便于 diff
    for c in rows:
        c["merged_from"] = list(dict.fromkeys(c["merged_from"]))

    NORM.write_text(
        yaml.safe_dump(rows, allow_unicode=True, sort_keys=False, width=200),
        encoding="utf-8",
    )
    used = {i for c in rows for i in c["merged_from"]}
    miss = [k for k in lq if k not in used]
    print(f"归一总数 {len(rows)} · 追加 source {added_src} 条 · 新增主张 {len(NEW)} 条")
    print(f"linquan-gaozhi 覆盖 {len(used & set(lq))}/{len(lq)}")
    if miss:
        print("未被引用：", miss)
        sys.exit(1)


if __name__ == "__main__":
    main()

"""批五：把 sequence-edit 与 cull-select 加入 verified.yaml，并把 book/entry/router 更新为十本。"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / ".cangjie" / "capabilities" / "verified.yaml"

SEQ = {
    "capability_id": "cap.photo-vision.sequence-edit",
    "revision": 1,
    "status": "active",
    "slug": "sequence-edit",
    "title": "序列编排：色彩弧、减法与专有意义",
    "importance": "high",
    "importance_rationale": "前九本书全部在讲单张（怎么拍、怎么评、怎么配色），没有一本回答「一批照片怎么排」。批五的 Pixar colorscript 正好是唯一系统化讲这件事的材料：它把全片色彩压成一条胶片，靠换调色板制造起伏。缺了它，包只能评单张、不能评作品。",
    "one_liner": "先定用途与读者，再把每张压成只看色与明暗，读出当前弧的方向，定一对贯穿的对抗关系，做减法与位移，最后收成一句弧的描述加三条动作。",
    "intents": [
        "一批照片怎么排顺序",
        "整组照片色调该怎么走",
        "单张都不错放一起却显得散",
        "组照里该不该放一张明显较弱的片子",
        "要把照片配音乐或文字做成短片",
    ],
    "keywords": [
        "组照", "排序", "顺序", "序列", "色彩弧", "调性", "编排", "画册", "短片", "选片排序",
        "sequence", "edit", "color arc", "picture edit", "slideshow", "body of work",
    ],
    "also_read": ["cull-select", "frame-critique", "chinese-eye"],
    "card": "cards/sequence-edit.md",
    "frontmatter": {
        "description": "当用户手里有一批照片要排成组照、画册、网页或配乐短片，问「怎么排／顺序有没有讲究／放在一起为什么散」，或要给一部作品定整体色调走向时使用。做法是先定用途与读者，把每张压成只看色与明暗的三格数据，读出当前弧的升/降/平，定一对贯穿的对抗关系，再做减法与位移，最后交出一句弧的描述加至多三条动作。不适用于单张诊断与打分（用 frame-critique）、只问淘汰不问顺序（用 cull-select）、以及需要具体配乐或剪辑时间码的音视频制作。",
        "tags": ["sequence", "editing", "color-arc", "series"],
    },
    "source_evidence": [
        {"source_id": "src-pixar", "location": "The Art of Pixar p006、p007"},
    ],
    "promotion": {
        "destination": "promoted",
        "gate": {
            "independent_intent": True,
            "independent_contract": True,
            "independent_run": True,
            "independent_reuse": True,
            "independent_eval": False,
        },
        "notes": "独立意图＝「一批怎么排」；独立契约＝用途＋三格数据表＋弧方向＋对抗关系＋增删换位＋一句弧；独立运行＝用两张实拍（DSC_3836 / DSC_4902）已走通并写出两种顺序两种语义；复用＝任何有共同主题的一批片子都能用；评测未做——与批四同样的原因（单卡样本不足），统一留到全部批次结束后的盲测。",
    },
}

CULL = {
    "capability_id": "cap.photo-vision.cull-select",
    "revision": 1,
    "status": "active",
    "slug": "cull-select",
    "title": "选片：按用途取舍，而不是按好看排序",
    "importance": "high",
    "importance_rationale": "选片是摄影里发生频率最高的判断（每次都拍多于能用），但九本书里只有零散纪律（探索必须有界限、不要拿裁剪当借口、别把高饱和图当成品）。batch 5 的 Pixar 材料给出了一条最锋利的判据：这不是做漂亮的图。这条把选片从审美排序改写成功能取舍，是包里唯一能回答「留哪些」的能力。",
    "one_liner": "先问清用途与名额，再分组不排序，按重复/离题/技术不可用/破坏整体四类硬理由删，做缩略图复核，三轮停机，最后把留下的交给 sequence-edit。",
    "intents": [
        "拍了一堆挑不出来",
        "只能交五张，选哪五张",
        "这些里留哪几张",
        "两张之间选不出来",
        "整批都不满意但说不上为什么",
    ],
    "keywords": [
        "选片", "筛片", "留哪张", "删哪张", "挑照片", "淘汰", "名额", "投稿选片",
        "cull", "select", "pick", "narrow down", "keep or delete",
    ],
    "also_read": ["sequence-edit", "frame-critique", "shoot-plan"],
    "card": "cards/cull-select.md",
    "frontmatter": {
        "description": "当用户拍完一批要挑出能用的，问「这些留哪几张／只能交五张／这两张选哪个／拍了一堆挑不出来」，或要在组照前筛素材、给封面选一张时使用。做法是先问清用途与名额，再按内容/色彩/密度分堆（不排序），逐堆用重复、离题、技术不可用、破坏整体四类硬理由删，做缩略图复核，三轮停机后把留下的交给 sequence-edit。不适用于单张缺陷诊断与打分（用 frame-critique）、已定留片只问顺序（用 sequence-edit）、以及需要自动批量评分排序的场合（本包分数维度表尚未统一）。",
        "tags": ["culling", "selection", "workflow"],
    },
    "source_evidence": [
        {"source_id": "src-pixar", "location": "The Art of Pixar p007"},
        {"source_id": "src-freeman-sight", "location": "摄影师的视界 p021、p131、p167"},
        {"source_id": "src-color-bible", "location": "摄影色彩圣经 p060、p176"},
    ],
    "promotion": {
        "destination": "promoted",
        "gate": {
            "independent_intent": True,
            "independent_contract": True,
            "independent_run": True,
            "independent_reuse": True,
            "independent_eval": False,
        },
        "notes": "独立意图＝「留哪些」；独立契约＝用途＋分堆＋四类硬理由＋缩略图复核＋三轮停机＋交接；独立运行＝用日本和尚三张候选（两种尺同时成立）与两张实拍（三种用途三种答案）走通；复用＝任何批量拍摄都能用；评测未做，理由同上。",
    },
}


def main() -> int:
    d = yaml.safe_load(io.open(P, encoding="utf-8"))
    slugs = {c["slug"] for c in d["capabilities"]}
    added = 0
    for cap in (SEQ, CULL):
        if cap["slug"] not in slugs:
            d["capabilities"].append(cap)
            added += 1

    d["book"]["title"] = (
        "photo-vision 批一至批五：摄影色彩圣经 / Interacting with Color / Interaction of Color / "
        "摄影师的视界 / 光线与用光 / 艺术与视知觉 / 艺术与错觉 / 中国美学史大纲 / 美学散步 / The Art of Pixar"
    )
    d["book"]["author"] = (
        "Jeff Wignall / Fritz Horstman / Josef Albers / Michael Freeman / Michael Freeman & Catherine Quinn / "
        "Rudolf Arnheim / E.H. Gombrich / 叶朗 / 宗白华 / Amid Amidi"
    )
    d["book"]["source_pack"] = (
        "books/{color-bible,interacting-with-color,interaction-of-color,freeman-sight,freeman-light,"
        "arnheim-art,gombrich-illusion,chinese-aesthetics,meixue-sanbu,art-of-pixar}/source/book.md"
    )
    d["book"]["baseline_tag"] = (
        "人民邮电 2013 中译本（张悦时译）/ Yale UP 2024 / Yale UP 第50周年版 / 人民邮电 2020.10 中译本（梁波译）/ "
        "人民邮电 2013.1 中译本（梅菲译）/ 四川人民 2019 中译本（滕守尧译）/ 第六版 / 上海人民 1985（2006 印）/ "
        "上海人民 2015 彩图本 / Chronicle Books 2011（epub 转 HTML）"
    )

    cps = [
        "视觉里看到的色几乎从不是它物理上实际是的那色——色彩是最相对的媒介。",
        "任何色都能与任何色搭配，前提是数量合适；和谐不是唯一可欲的关系。",
        "看是建构不是接收：整体大于部分之和，第一层知觉是方向性的力。",
        "构图的两个基本原则是对比与平衡，但「功效不是规则」——规则是条件判词。",
        "光质决定阴影边缘，光位决定形状与质感，时段与天气决定可用范围。",
        "画幅先于一切，分割是比例，元素可降到点线面三级。",
        "视觉判断不能被照片裁决：数值以仪器为准，色相以眼睛为准，模型描述不得冒充测量。",
        "三远是三种观看方式而非三个机位；虚实相生，空要由实来显。",
        "逼真只是西方再现传统内的选择，不是评价照片的通用轴。",
        "单张有单张的尺，序列有序列的尺；序列里的弱帧可以是正确的，但它的缺陷仍要被指出。",
        "选片先定用途再定去留：删的理由只有重复、离题、技术不可用、破坏整体四类。",
    ]
    d["entry"]["core_principles"] = cps
    d["entry"]["description"] = (
        "把十本书蒸馏成「色彩—结构—光线—视看机制—中国观看—序列编排」六条判断线：色彩线量事实、定主导对比、判数量并按意图分岔；"
        "结构线判画幅、分割、平衡、纵深与引导；光线线定光质、光位、时段、曝光与白平衡；机制层回答「为什么会这样看」；"
        "中国观看线回答「为什么这张空／该怎么留」；序列线回答「一批怎么排、留哪些、删哪些」。"
        "跨书冲突（K1 和谐、K5 规则、K6 自我表达、K7 照片能否裁决、K11 视点、K12 虚实、K13 逼真、"
        "K14 单张与整体的尺、K15 色彩意义的层）在运行时按 branch / downgrade / qualify / split 处置，不做折中。"
    )
    d["router_entry"]["description"] = (
        "当用户拿照片问「哪里不对／怎么改」「为什么看着不舒服」「颜色怎么调」「留白该怎么留」，"
        "或要定拍摄计划、判断一张照片成不成立、给一批照片排序与取舍时使用；覆盖色彩关系、构图结构、光线时段、"
        "视看机制、中国观看与序列编排六条线。不适用于影像真伪鉴别、色彩管理工程、修图软件操作与纯器材评测。"
    )
    io.open(P, "w", encoding="utf-8").write(
        yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=1000))
    print(f"能力新增 {added} · 总能力 {len(d['capabilities'])} · core_principles {len(cps)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

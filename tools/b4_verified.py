"""批四：把 chinese-eye 加入 verified.yaml，并把 book/entry/router 更新为九本。"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / ".cangjie" / "capabilities" / "verified.yaml"

CAP = {
    "capability_id": "cap.photo-vision.chinese-eye",
    "revision": 1,
    "status": "active",
    "slug": "chinese-eye",
    "title": "中国观看体系：三远、留白与多角度观照",
    "importance": "high",
    "importance_rationale": "前八本书全部是西方的（色彩学、再现心理学、格式塔、器材实操），包在「空、散、气、意境」这类问法上完全无语料。批四补上的正是另一套空间观：三远、虚实相生、多角度观照。它不替代 structure-read，而是在用户问「为什么这张空」时给出结构派给不出的答案，并与 K11/K12 两条对抗绑定。",
    "one_liner": "先定这套画面走哪一套空间，再选一远、查远近分工、验虚实承重、找气眼，最后只给换机位与加减虚实两条动作。",
    "intents": [
        "判断一张照片为什么显得空或散",
        "决定留白留多少、往哪儿留",
        "想做出中国画式的空间感",
        "反复换机位却不知道换到哪",
        "被「压中线」与「留白」两种说法夹住时选边",
    ],
    "keywords": [
        "留白", "空白", "空", "散", "气韵", "意境", "三远", "高远", "深远", "平远",
        "散点透视", "以大观小", "虚实", "空亭", "气眼", "中国画",
        "negative space", "empty", "Chinese painting", "three distances", "shifting viewpoint",
    ],
    "also_read": ["structure-read", "ways-of-seeing", "color-decision"],
    "card": "cards/chinese-eye.md",
    "frontmatter": {
        "description": "当用户问「这张为什么显得空／散／没气」「留白该怎么留」「总想换机位但不知道换到哪」「想拍出中国画那种空间感」，或在中式观看与西式构图之间拿不定主意时使用。做法是先判这套画面走单点收束还是游走折返，再定哪一远、查远近分工（势与质）、验虚实承重（一鳞一爪能否使全体宛然）、找气眼，最后只给换机位与加减虚实两类动作。不适用于需要精确几何会聚的建筑与产品、曝光与色温问题、色彩面积配比，也不适用于用户明确只接受西式构图规则的场合。",
        "tags": ["chinese", "space", "composition", "negative-space"],
    },
    "source_evidence": [
        {"source_id": "src-meixue", "location": "美学散步 p102、p107、p108、p111、p112、p124、p129、p131、p132、p133、p138"},
        {"source_id": "src-chinese-aesthetics", "location": "中国美学史大纲 p287、p288、p290、p291、p293、p298"},
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
        "notes": "独立意图＝「这张为什么空／该怎么留」；独立契约＝空间归属判定＋一远＋远近分工＋虚实承重＋气眼＋两条动作；独立运行＝可用单张照片或一段画面描述走完六步；复用＝风景、建筑、静物、街拍都能用（人像需翻译，已在 B 段声明）；评测未做——批四只有单卡，样本不足，留到批五统一盲测。",
    },
}


def main() -> int:
    d = yaml.safe_load(io.open(P, encoding="utf-8"))
    slugs = {c["slug"] for c in d["capabilities"]}
    added = 0
    if "chinese-eye" not in slugs:
        d["capabilities"].append(CAP)
        added += 1

    d["book"]["title"] = (
        "photo-vision 批一至批四：摄影色彩圣经 / Interacting with Color / Interaction of Color / "
        "摄影师的视界 / 光线与用光 / 艺术与视知觉 / 艺术与错觉 / 中国美学史大纲 / 美学散步"
    )
    d["book"]["author"] = "Jeff Wignall / Fritz Horstman / Josef Albers / Michael Freeman / Michael Freeman & Catherine Quinn / Rudolf Arnheim / E.H. Gombrich / 叶朗 / 宗白华"
    d["book"]["source_pack"] = (
        "books/{color-bible,interacting-with-color,interaction-of-color,freeman-sight,"
        "freeman-light,arnheim-art,gombrich-illusion,chinese-aesthetics,meixue-sanbu}/source/book.md"
    )
    d["book"]["baseline_tag"] = (
        "人民邮电 2013 中译本（张悦时译）/ Yale UP 2024 / Yale UP 第50周年版 / 人民邮电 2020.10 中译本（梁波译）/ "
        "人民邮电 2013.1 中译本（梅菲译）/ 四川人民 2019 中译本（滕守尧译）/ 第六版 / 上海人民 1985（2006 印）/ 上海人民 2015 彩图本"
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
    ]
    d["entry"]["core_principles"] = cps
    d["entry"]["description"] = (
        "把九本书蒸馏成「色彩—结构—光线—视看机制—中国观看」五条判断线：色彩线量事实、定主导对比、判数量并按意图分岔；"
        "结构线判画幅、分割、平衡、纵深与引导；光线线定光质、光位、时段、曝光与白平衡；机制层回答「为什么会这样看」；"
        "中国观看线回答「为什么这张空／该怎么留」。四条跨书冲突（K1 和谐、K5 规则、K6 自我表达、K7 照片能否裁决、"
        "K11 视点、K12 虚实、K13 逼真）在运行时按 branch / downgrade / qualify 处置，不做折中。"
    )
    d["router_entry"]["description"] = (
        "当用户拿照片问「哪里不对／怎么改」「为什么看着不舒服」「颜色怎么调」「留白该怎么留」，"
        "或要定拍摄计划、判断一张照片成不成立、给一组照片排序时使用；覆盖色彩关系、构图结构、光线时段、"
        "视看机制与中国观看五条线。不适用于影像真伪鉴别、色彩管理工程、修图软件操作与纯器材评测。"
    )
    io.open(P, "w", encoding="utf-8").write(
        yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=1000))
    print(f"能力新增 {added} · 总能力 {len(d['capabilities'])} · core_principles {len(cps)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""批三：把 ways-of-seeing 加入 verified.yaml，并更新书名、路由描述与核心原则。"""
import io
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / ".cangjie" / "capabilities" / "verified.yaml"

NEW = {
    "capability_id": "cap.photo-vision.ways-of-seeing",
    "revision": 1,
    "status": "active",
    "slug": "ways-of-seeing",
    "title": "视看机制：为什么会被看成这样",
    "importance": "high",
    "importance_rationale": (
        "批三新增的机制层，来自阿恩海姆与贡布里希。它不产生新配方，而是给前四张卡提供上游解释："
        "当两条规则打架、当判断被质疑、当照片合规却不好看时，只有它能回答「为什么」。"
        "缺它则整个包只能给建议、不能自证，也无法处理「违规却站得住」这类真实情况。"
    ),
    "one_liner": "用格式塔与再现心理学解释一张照片为什么被读成这样，并只给一条能改变力结构的动作。",
    "intents": [
        "解释一张照片为什么看着别扭",
        "解释明明对称为什么不稳",
        "判断两条互相矛盾的建议该听哪条的上游",
        "说明一个判断凭什么成立",
        "向别人讲清原理而不是替别人做决定",
    ],
    "keywords": [
        "为什么", "原理", "机制", "格式塔", "张力", "视觉重量", "错觉", "图式",
        "why", "mechanism", "gestalt", "tension", "illusion", "schema",
    ],
    "card": "cards/ways-of-seeing.md",
    "also_read": ["structure-read", "color-decision"],
    "source_evidence": [
        {
            "source_id": "src-arnheim-art",
            "location": "艺术与视知觉 p011、p024、p030–p034、p045–p052、p056、p064、p108、p116、p118、p128、p146、p054",
        },
        {
            "source_id": "src-gombrich-illusion",
            "location": "艺术与错觉 p028、p180、p235、p016、p140",
        },
    ],
    "frontmatter": {
        "description": (
            "当用户问「为什么这张看着别扭」「为什么明明对称却不稳」「凭什么说这里重」「合规为什么不好看」"
            "「这条规则和那条打架听谁的」时使用。做法是先说力再说物体、找抵消点与不稳点、查分离线索、"
            "判读法是被图式带走还是被画面逼出，最后收成一句因果并至多给一条改变力结构的动作。"
            "不适用于要配方、要数值、要打分，也不适用于把照片当作测量或取证对象。"
        ),
        "tags": ["mechanism", "gestalt", "explanation", "critique"],
    },
    "promotion": {
        "destination": "promoted",
        "gate": {
            "independent_intent": True,
            "independent_contract": True,
            "independent_run": True,
            "independent_reuse": True,
            "independent_eval": False,
        },
        "notes": (
            "独立意图＝「为什么会这样」；独立契约＝五步流程＋只给一条动作＋不产出数值与分数；"
            "独立运行＝可对一张真实照片走完五步；复用＝同一流程用于解释位置、边界、冷暖、模糊度四类问题；"
            "评测未做（批三暂不重跑盲测，待批五统一验收）。"
        ),
    },
}


def main() -> int:
    d = yaml.safe_load(P.read_text(encoding="utf-8"))
    d["book"]["title"] = (
        "photo-vision 批一批二批三：摄影色彩圣经 / Interacting with Color / Interaction of Color / "
        "摄影师的视界 / 光线与用光 / 艺术与视知觉 / 艺术与错觉"
    )
    slugs = {c["slug"] for c in d["capabilities"]}
    if "ways-of-seeing" not in slugs:
        d["capabilities"].append(NEW)

    cp = d["entry"]["core_principles"]
    mech = "看是建构不是接收：先读到的是力，然后才归因给物体；因此解释一张照片要说到力、抵消点与分离线索，而不是堆形容词。"
    if mech not in cp:
        cp.append(mech)

    oos = d["entry"]["out_of_scope"]
    x = "不解释「照片为什么会被这样看」的知觉机制之外的美学流派争论"
    if x not in oos:
        oos.append(x)

    d["router_entry"]["description"] = (
        "摄影视觉判断总入口（批一批二批三：色彩、结构、光线、视看机制）。用于判断一张照片哪里不成立——"
        "颜色关系、画面骨架、还是光；给一组配色定方向；决定主体放哪、横竖怎么选、地平线放哪、裁到哪；"
        "计划一次拍摄的时段与用光；判断阴天正午逆光各自能拍什么；解释一张照片为什么被读成这样；"
        "以及要一份带测量的诊断报告。结构与色彩同时出问题时会串行判断但合成一页结论。"
        "编排、选片与视频叙事尚未覆盖，会说明并只给单张判断。"
    )

    P.write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")
    print(f"能力数 {len(d['capabilities'])} · core_principles {len(cp)} · out_of_scope {len(oos)}")
    print("slugs:", ", ".join(c["slug"] for c in d["capabilities"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

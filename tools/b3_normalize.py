"""批三归一：把阿恩海姆与贡布里希的原初主张合并进 claims/claims.yaml。

引文由脚本按 id 从两本已校验的库直接搬运，不经手抄。
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

RAW = {
    "arnheim-art": ROOT / "books" / "arnheim-art" / "claims" / "claims.yaml",
    "gombrich-illusion": ROOT / "books" / "gombrich-illusion" / "claims" / "claims.yaml",
}

GROUPS = [
    ("C116", "机制", "mechanism", "principle",
     "视觉不是对外界刺激的机械复制，而是抓结构特征的创造性把握；整体不能由部分相加得到，因此元素清单式的点评在原理上就不成立。",
     ["ar20", "ar21", "ar24"]),
    ("C117", "构图与结构", "mechanism", "principle",
     "视觉平衡只由重量与方向两件事决定，且视觉重量与物理量（面积、像素）并不一致——不能按大小直接换算平衡。",
     ["ar02", "ar03", "ar22", "ar23"]),
    ("C118", "构图与结构", "mechanism", "principle",
     "中心之所以稳定是因为各方向的力在这一点互相抵消，不是因为那里空；下方比上方稳定，上方位置天然不稳，需要更多支撑理由。",
     ["ar01", "ar04", "ar27"]),
    ("C119", "构图与结构", "mechanism", "procedure",
     "简化有两个方向——矫平（减少结构差异、提高对称、纠正倾斜）与增锐（强化差异、增加倾斜）；简化还分主观易识认与客观结构少两层。",
     ["ar05", "ar06", "ar07", "ar08"]),
    ("C120", "构图与结构", "mechanism", "principle",
     "轮廓线不等于形状，形状由结构骨架决定；形状越连贯越容易从背景中独立，越难分离的形状越容易和背景搅在一起。",
     ["ar09", "ar10"]),
    ("C121", "空间", "mechanism", "principle",
     "深度线索有两条硬路径：梯度（倾斜被读成梯度才产生深度，源头是吉布森）与重叠（被盖住的一层必须靠深度上的分离线索引才能摆脱干扰）。",
     ["ar11", "ar25"]),
    ("C122", "空间", "mechanism", "principle",
     "画框在图底关系里是「图」，画面空间是它下方的无边基底；这正是框架被称作窗口的心理学依据。世界上不存在真正二度的平面绘画。",
     ["ar12", "ar26"]),
    ("C123", "光与时段", "mechanism", "principle",
     "相对亮度只有在整个环境被同一强度光照亮时才能被稳定知觉；局部光比不同，亮度就会被读成别的属性。",
     ["ar13"]),
    ("C124", "光与时段", "mechanism", "principle",
     "明暗渐变一旦让观者读出一块面有曲率，它立刻被看成球体的一部分——阴影不是装饰，是形状的构造者。",
     ["ar14"]),
    ("C125", "色相与色环", "mechanism", "principle",
     "一切视觉形象只由色彩与亮度两种原料构成，没有第三种。",
     ["ar15"]),
    ("C126", "冷暖", "mechanism", "principle",
     "冷暖不是装饰性形容词：一个色的全部特性会单方面影响观者，并仅凭其出现就指向另一种不同的存在，所以冷暖永远是关系判断。",
     ["ar16"]),
    ("C127", "和谐与协调", "mechanism", "principle",
     "只让平衡与和谐主导作品，等于对人类经验做出片面解释——平衡是常态不是目标。",
     ["ar17"]),
    ("C128", "机制", "mechanism", "principle",
     "人看到的首先是方向性张力之间的相互作用，而不是事物、色彩、形状或大小；知觉力是所见事物的真实性质，叫不叫幻觉不影响这一点。艺术家的目的是让观者经验到各种力式样的表现性质。",
     ["ar18", "ar19"]),
    ("C129", "机制", "mechanism", "principle",
     "再现是「图式 + 矫正」：先有现成公式，再拿它去试错修正；制作永远先于匹配，像不像发生在做出来之后。一个时期风格相似，是因为大家学的是同一批公式。",
     ["go01", "go02", "go12"]),
    ("C130", "语境与相对性", "mechanism", "principle",
     "图像只有在观者肯承担「观看者的本分」时才成立——画面的完成有一半落在观看者身上。",
     ["go03"]),
    ("C131", "机制", "mechanism", "principle",
     "知觉是有选择的注意（心理定向）；看与看见、听与听见的差别来自这层过滤，没有它人会被刺激淹没。",
     ["go04"]),
    ("C132", "语境与相对性", "mechanism", "principle",
     "错觉的本质是相信眼前这个视觉模式只有一种解释方法——不是看错，而是排他；并且错觉必须与错误信念区分，知道娃娃是假的人照样会被舞台打动。",
     ["go05", "go06"]),
    ("C133", "机制", "mechanism", "principle",
     "符号靠区别性特征表达意义，其余一概不相干；照片被读成某物，靠的也是少数区别性特征而非全部细节。",
     ["go07"]),
    ("C134", "空间", "mechanism", "principle",
     "「透视只是一种程式」的信念来自把关系模型误当成图像；这种程式论有其根基，但不是对透视法的最终判断。",
     ["go08", "go22"]),
    ("C135", "机制", "mechanism", "principle",
     "知觉可以看作对一次预期所作出的矫正：先有预判，再看实际，差异驱动修正；检验解释时下一步几乎是可以预期到的。",
     ["go09", "go21"]),
    ("C136", "方法论", "mechanism", "principle",
     "人能学的是辨别而不是观看；学「看」很大程度上是学预测序列，而先例（看过什么程式）会直接塑造眼睛。",
     ["go10", "go17", "go18"]),
    ("C137", "机制", "mechanism", "principle",
     "投射：人会把熟悉的面目加到一个陌生形状上（云、汽车前脸），这是识别而非逐点比较。",
     ["go11"]),
    ("C138", "语境与相对性", "mechanism", "principle",
     "他不接受「根本没有视觉现实、任何再现都不必比较谁更逼真」的相对主义；同时指出中国传统不以求逼真为目标，因为书法与绘画休戚相关——逼真不是普遍标准。",
     ["go13", "go16"]),
    ("C139", "方法论", "mechanism", "principle",
     "只重复「观看 vs 知道」或「一切再现都基于程式」解决不了问题；程式论只是一半——有生命的错觉靠世代累积的图画经验与反复试验，不靠关于现实的错觉。",
     ["go14", "go15"]),
    ("C140", "语境与相对性", "mechanism", "principle",
     "行动的上下文会创造错觉条件：同一块色、同一个形，在「正在发生什么」里会被读成不同的东西。",
     ["go25"]),
    ("C141", "方法论", "mechanism", "principle",
     "一个公式若只能「不断修正以求与现象一致」，那种表面长处正是它致命的缺陷（托勒密体系）；而观众信不信服会反过来驱动作者修正公式。",
     ["go19", "go20"]),
    ("C142", "方法论", "mechanism", "principle",
     "他愿意用「试错过程」取代「解释」：靠试错清除错觉、检验并修改我们对世界的信念。",
     ["go24"]),
    ("C143", "语境与相对性", "mechanism", "principle",
     "「在生活情境里观察世界」与「读解绘画」这两件事是否可比，始终是他留作开放的问题，并不认为二者自动同一。",
     ["go23"]),
]


def main():
    raw = {}
    for book, path in RAW.items():
        for c in yaml.safe_load(path.read_text(encoding="utf-8")):
            raw[c["id"]] = (book, c)

    norm_path = ROOT / "claims" / "claims.yaml"
    norm = yaml.safe_load(norm_path.read_text(encoding="utf-8"))
    have = {c["id"] for c in norm}
    have |= {i for c in norm for i in c.get("merged_from", [])}

    used = set()
    added = []
    for cid, domain, stance, oper, text, ids in GROUPS:
        if cid in have:
            print(f"skip {cid} (already)")
            continue
        sources = []
        for i in ids:
            if i not in raw:
                raise SystemExit(f"未知原初 id: {i} ({cid})")
            book, c = raw[i]
            sources.append({"book": book, "id": i, "page": c["page"], "quote": c["quote"]})
            used.add(i)
        added.append({
            "id": cid,
            "claim": text,
            "domain": domain,
            "stance": stance,
            "operational": oper,
            "merged_from": list(ids),
            "single_source": False,
            "sources": sources,
        })

    missing = set(raw) - used - have
    if missing:
        print("⚠ 未被任何归一主张引用的原初 id：" + ", ".join(sorted(missing)))

    norm.extend(added)
    norm_path.write_text(
        yaml.safe_dump(norm, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
    )
    print(f"追加 {len(added)} 条归一主张（C116–C{116 + len(added) - 1}）· 覆盖原初 {len(used)} 条 · 归一总数 {len(norm)}")


if __name__ == "__main__":
    sys.exit(main())

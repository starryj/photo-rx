# -*- coding: utf-8 -*-
"""批七归一：把曼特《摄影构图与色彩设计》的第一手引文并入归一库。

做两件事：
1) 给既有归一主张追加 photo-composition-color 的 source，并同步 merged_from；
2) 新增 C187–C216 三十条归一主张（46 条单书 claim 中 10 条挂接、36 条归入 30 条新主张）。

引文一律按 id 从 `books/photo-composition-color/claims/claims.yaml` 搬运，不经手抄。
"""
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
NORM = ROOT / "claims" / "claims.yaml"
BOOK = ROOT / "books" / "photo-composition-color" / "claims" / "claims.yaml"
SLUG = "photo-composition-color"

ATTACH = {
    "C118": ["m02"],          # 中心点的力与稳定
    "C076": ["m10"],          # 黄金分割比例
    "C078": ["m16"],          # 框中框
    "C088": ["m22"],          # 焦距与透视/压缩
    "C093": ["m27", "m28"],   # 歌德亮度值与面积和谐比
    "C126": ["m30"],          # 冷暖的关系性
    "C017": ["m31"],          # 后像实验
    "C073": ["m37", "m39"],   # 画幅/格式
}

NEW = [
    dict(
        id="C187",
        claim="评价照片有两条互不替代的轴：内容与陈述（信息、情感反应），以及组织质量（结构与色彩设计）",
        domain="方法论", stance="规则派", operational="framework", merged_from=["m01"],
    ),
    dict(
        id="C188",
        claim="点不是小物体，而是相对面积足够小的形状；面积占比一大就已成面或形，点的位置张力不再适用",
        domain="构图与结构", stance="规则派", operational="principle", merged_from=["m03"],
    ),
    dict(
        id="C189",
        claim="显著的小点是强调还是干扰没有硬判据；可操作的替代判据是看拿掉它之后主题是否更纯粹",
        domain="方法论", stance="规则派", operational="principle", merged_from=["m04"],
    ),
    dict(
        id="C190",
        claim="两点放在虚拟对角线上时与相对的角张力最强；贴近水平或垂直边则像被边吸附，会干扰视线",
        domain="构图与结构", stance="规则派", operational="principle", merged_from=["m05"],
    ),
    dict(
        id="C191",
        claim="三点构图有两种读法：中间点连成视觉线、偏移过大则线感消失；成三角时若有边与画框平行则方向最强，三边都不平行则呈流动",
        domain="构图与结构", stance="规则派", operational="framework", merged_from=["m06", "m07"],
    ),
    dict(
        id="C192",
        claim="视觉系统按最省力原则补线：两点之间补直线，散点补成最简单的图形，所以暗示线几乎总是直线",
        domain="机制", stance="规则派", operational="principle", merged_from=["m08"],
    ),
    dict(
        id="C193",
        claim="重复的间距结构决定动静：等距同质最静，两两成组张力增强，不规则交替产生强动势",
        domain="构图与结构", stance="规则派", operational="principle", merged_from=["m09"],
    ),
    dict(
        id="C194",
        claim="水平线放在画面正中会把画面切成等份、缺乏张力；放在中间上下一个八分单元处较和谐，贴近边缘则张力最强",
        domain="构图与结构", stance="规则派", operational="principle", merged_from=["m11"],
    ),
    dict(
        id="C195",
        claim="下降对角线自带滑出画面的趋势，竖幅与陡角度会放大它；在右下放垂直物体作阻塞可把视线留在画面内",
        domain="构图与结构", stance="规则派", operational="principle", merged_from=["m12"],
    ),
    dict(
        id="C196",
        claim="一组线里主线条必须最粗；连贯且通常最长的线会被读成最重要的线，其余线需明显退为附属",
        domain="构图与结构", stance="规则派", operational="principle", merged_from=["m13"],
    ),
    dict(
        id="C197",
        claim="正负形按层级判定：重叠时前为正、后为负，背景相对所有形状都是负形；可由外到内或由内到外逐层分析，同一面在不同层级身份不同",
        domain="构图与结构", stance="规则派", operational="framework", merged_from=["m14", "m15"],
    ),
    dict(
        id="C198",
        claim="黑白摄影里色调是唯一可行的设计手段，色彩对比与纯度对比全部失效；明暗层级不够就撑不起画面",
        domain="明度", stance="规则派", operational="principle", merged_from=["m17"],
    ),
    dict(
        id="C199",
        claim="直射光、背景光和刺眼日光能支撑强色调对比，柔和迂回的光会降低色调对比与颜色强度；后期加对比不能替代光质",
        domain="光与时段", stance="规则派", operational="principle", merged_from=["m18"],
    ),
    dict(
        id="C200",
        claim="暗背景里的亮点会被串成一条穿过画面的「光通道」，视线逐点跳跃；应先排亮点顺序再检查是否指向主体",
        domain="构图与结构", stance="规则派", operational="principle", merged_from=["m19"],
    ),
    dict(
        id="C201",
        claim="地平线靠近上边框给人俯瞰大地的印象，靠近下边框则给人仰视苍穹的印象",
        domain="空间", stance="规则派", operational="principle", merged_from=["m20"],
    ),
    dict(
        id="C202",
        claim="纵深靠多手段叠加：重叠、大小/形状/虚实对比、冷暖与后退色、光影、暗边框；其中光影同时提供轮廓与前后层次",
        domain="空间", stance="规则派", operational="framework", merged_from=["m21"],
    ),
    dict(
        id="C203",
        claim="两个色相只算「有对比」，三种颜色以上才构成真正的色相对比；三原色最响亮，加入第二梯度色可缓和",
        domain="色相与色环", stance="规则派", operational="principle", merged_from=["m23"],
    ),
    dict(
        id="C204",
        claim="质量对比是纯色与同色系渐暗、渐淡色之间的对比；画面只有一种色彩时效果最好",
        domain="饱和度", stance="规则派", operational="principle", merged_from=["m24"],
    ),
    dict(
        id="C205",
        claim="曝光不足可视为加黑、过度视为加白，改变的主要是整体色彩平衡而非只动明度；要降纯度应改光或混合，不应靠欠曝",
        domain="饱和度", stance="规则派", operational="principle", merged_from=["m25"],
    ),
    dict(
        id="C206",
        claim="协调的判据是中性灰：多色交互融合成中性灰即平衡；人会在瞬间扫视全画，偏色即失衡",
        domain="和谐与协调", stance="规则派", operational="framework", merged_from=["m26", "m32"],
    ),
    dict(
        id="C207",
        claim="先算和谐比再有意偏离可制造张力：缩小亮色面积、倒置或夸大比例；偏离没有普适最优值",
        domain="对比", stance="规则派", operational="principle", merged_from=["m29"],
    ),
    dict(
        id="C208",
        claim="色相环几何取色给出协调组合：三色用互补替换法，四色用内接正方形或长方形，各得数组；前提是纯色相",
        domain="和谐与协调", stance="规则派", operational="framework", merged_from=["m33", "m34"],
    ),
    dict(
        id="C209",
        claim="按快门前要逐项拍板八件事：相机、镜头、胶片/数码设置、光线、时间、视角、快门与光圈；每项同时是技术与艺术选择",
        domain="方法论", stance="规则派", operational="framework", merged_from=["m35"],
    ),
    dict(
        id="C210",
        claim="照片成功与否取决于内容而非画面质量；设计出众但内容平庸仍可能失败",
        domain="方法论", stance="规则派", operational="principle", merged_from=["m36"],
    ),
    dict(
        id="C211",
        claim="失衡要分两组力看：元素与画框边、角、中点的张力，以及元素彼此之间的张力；两组修法不同",
        domain="构图与结构", stance="规则派", operational="framework", merged_from=["m38"],
    ),
    dict(
        id="C212",
        claim="虚实对比主要作用于前景与背景：焦点对前景则前景凸显，焦点透过前景对背景则前景成虚化引导层，全幅失焦则转为氛围",
        domain="空间", stance="规则派", operational="principle", merged_from=["m40"],
    ),
    dict(
        id="C213",
        claim="想保持运动主体清晰又要动感，就让镜头跟随主体摇摄：主体相对静止、背景拉成方向性模糊",
        domain="器材与后期", stance="规则派", operational="principle", merged_from=["m41"],
    ),
    dict(
        id="C214",
        claim="组照以整组为标准，单张标准随整体重定；常见主题十到十五张起，张数取决于主题可得性与可选池",
        domain="方法论", stance="规则派", operational="framework", merged_from=["m42", "m43"],
    ),
    dict(
        id="C215",
        claim="连续摄影冻结除时间外的一切技术条件——视点、取景、曝光都不变，只让时间与自然条件改变画面",
        domain="方法论", stance="规则派", operational="principle", merged_from=["m44"],
    ),
    dict(
        id="C216",
        claim="分析彩色照片先定主导对比；并用黑白/彩色双版本分开评估构图与色彩，判断两者是加强还是抵消",
        domain="方法论", stance="规则派", operational="framework", merged_from=["m45", "m46"],
    ),
]


def main():
    backup = NORM.with_name("claims.yaml.bak-20261124-b7")
    if not backup.exists():
        shutil.copy2(NORM, backup)
    rows = yaml.safe_load(NORM.read_text(encoding="utf-8"))
    book = {c["id"]: c for c in yaml.safe_load(BOOK.read_text(encoding="utf-8"))}
    by_id = {c["id"]: c for c in rows}

    def src(cid):
        c = book[cid]
        return {"book": SLUG, "id": cid, "page": c["page"], "quote": c["quote"]}

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

    for c in rows:
        c["merged_from"] = list(dict.fromkeys(c["merged_from"]))

    NORM.write_text(
        yaml.safe_dump(rows, allow_unicode=True, sort_keys=False, width=200),
        encoding="utf-8",
    )
    used = {i for c in rows for i in c["merged_from"]}
    miss = [k for k in book if k not in used]
    print(f"归一总数 {len(rows)} · 追加 source {added_src} 条 · 新增主张 {len(NEW)} 条")
    print(f"{SLUG} 覆盖 {len(used & set(book))}/{len(book)}")
    if miss:
        print("未被引用：", miss)
        sys.exit(1)


if __name__ == "__main__":
    main()

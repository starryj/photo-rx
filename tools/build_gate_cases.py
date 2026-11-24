"""反证闸：30 条用例的生成与判卷。

设计：每条给一个具体请求，测试者必须读该卡 B 段后判断「按这张卡，该拦还是该放」，
并指出依据的那一条。

- expect=block 落的都是卡 B 段明确写过的禁用情形／作者警告的失败模式／盲点。
- expect=pass 都是「看起来像边界但卡的 B 段并未覆盖」的请求，用来测误拦。
- 两类 15:15 各半：一个永远答 block 的策略只能拿 50%，不能靠倾向刷分。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "gate"

B, P = "block", "pass"

CASES = [
    # ---- chinese-eye ----
    ("ce-01", "chinese-eye", B,
     "客户要一张产品图，完全对称、垂直线绝对平行、还原准确。请用「三远」里的平远给它重排构图。",
     "B 段禁用第 1 条：需要精确几何会聚的题材（产品还原）→ structure-read"),
    ("ce-02", "chinese-eye", B,
     "把这张照片的天空全部抹成纯白，这样就有留白了。",
     "B 段失败模式 2「空本难图」：留白不是省掉不画；留白前须验实部够硬"),
    ("ce-03", "chinese-eye", P,
     "这张是黄山的云海，我想让视线从我脚下往远处走，能按三远来组织吗？",
     "B 段未覆盖：山水正是本卡的适用面"),
    ("ce-04", "chinese-eye", P,
     "这张地平线在很低处，天空占三分之二，地平线上有一艘小船。更接近哪一种「远」？",
     "B 段未覆盖：可答的平远取向判断，船可作气眼"),
    # ---- color-decision ----
    ("cd-01", "color-decision", B,
     "帮我调一下显示器的 ICC 配置，让出片颜色更准。",
     "B 段禁用第 2 条：色彩管理流程是工程问题，本卡不给流程"),
    ("cd-02", "color-decision", B,
     "这张是纯黑白照片，评一下它的色彩关系。",
     "B 段禁用第 1 条：纯黑白照片色相七型不适用 → frame-critique 明暗轨"),
    ("cd-03", "color-decision", B,
     "这张照片内容其实挺空的，但色彩看着挺和谐，你就按色彩给个好评吧。",
     "B 段禁用第 3 条：不要拿色彩替内容辩护"),
    ("cd-04", "color-decision", P,
     "这条红裙在灰墙前，红大概占画面 8%，其余都是低饱和。红色在这里起什么作用？",
     "B 段未覆盖：知觉层的色彩强调判断（小区域对比色聚焦）"),
    ("cd-05", "color-decision", P,
     "这张里红和绿面积差不多 1:1，但红色明显更抢眼，为什么？",
     "B 段未覆盖：互补色面积相等时的知觉判断，可答"),
    # ---- cull-select ----
    ("cs-01", "cull-select", B,
     "这 20 张我已经定了留哪 12 张，帮我排个顺序。",
     "B 段禁用第 3 条：已定留哪些、只问顺序 → sequence-edit"),
    ("cs-02", "cull-select", B,
     "把这两百张自动打个分，我按分数一刀切删掉低分的。",
     "B 段禁用第 4 条：本包不做自动评分（维度表未统一）"),
    ("cs-03", "cull-select", P,
     "这 40 张里我要挑 6 张发小红书九宫格，帮我决定哪 6 张。",
     "B 段未覆盖：有筛选空间且有明确用途，正是本卡主场景"),
    ("cs-04", "cull-select", P,
     "这 30 张婚礼跟拍，我要挑 15 张进相册，怎么挑？",
     "B 段未覆盖：用途明确、数量充足，属本卡"),
    # ---- sequence-edit ----
    ("se-01", "sequence-edit", B,
     "这 15 张是同一天在城里扫街随手拍的，帮我排出一个叙事顺序。",
     "B 段禁用第 3 条：没有共同主题、只是同一段时间拍的，那是素材不是序列"),
    ("se-02", "sequence-edit", B,
     "给这组照片配段音乐，标出每张停留几秒。",
     "B 段禁用第 4 条：需要配乐或剪辑时间码，本包不涉音视频"),
    ("se-03", "sequence-edit", P,
     "这 8 张都是同一条河，分别拍在清晨、正午、黄昏、入夜。帮我排出从早到晚的变化。",
     "B 段未覆盖：共同主题 + 天然时间序，属序列编辑"),
    ("se-04", "sequence-edit", P,
     "这 6 张都是同一个空亭，四季各一张，帮我排个顺序。",
     "B 段未覆盖：同一主体、可比较，属序列编辑"),
    # ---- shoot-plan ----
    ("sp-01", "shoot-plan", B,
     "推荐我买哪个牌子的 85mm 定焦，预算五千。",
     "B 段禁用第 5 条：纯器材购买咨询不做推荐，只说判据"),
    ("sp-02", "shoot-plan", B,
     "把这张的构图和颜色一起评一下，最后打个总分。",
     "B 段禁用第 3 条：要事后诊断或打分 → frame-critique"),
    ("sp-03", "shoot-plan", P,
     "明天下午去海边拍人像，几点到、主要靠什么光、要不要带柔光板？",
     "B 段未覆盖：典型本卡主场景（时段 + 光质 + 配件判据）"),
    ("sp-04", "shoot-plan", P,
     "阴天在室内窗边拍人，光太软了没层次，怎么办？",
     "B 段未覆盖：正是本卡「把阴天当坏天气」的正面场景"),
    # ---- structure-read ----
    ("sr-01", "structure-read", B,
     "这张是地震现场的照片，你帮我看看构图有什么问题。",
     "B 段禁用第 5 条：内容为灾难/新闻事件时，结构判断让位于「该不该拍」"),
    ("sr-02", "structure-read", P,
     "同一处风景，我拍成横幅还是竖幅更好？",
     "B 段未覆盖：画幅与观看方式是本卡第一件事"),
    ("sr-03", "structure-read", P,
     "这张我裁掉了右边三分之一，现在重心是不是偏了？",
     "B 段未覆盖：问的是已裁之后的重心判断，不是「该不该裁」"),
    ("sr-04", "structure-read", P,
     "这张里一排柱子越远越密，这种纵深是真实透视还是镜头压缩造成的？",
     "B 段未覆盖：纵深与焦距对结构的影响是本卡正文内容"),
    # ---- ways-of-seeing ----
    ("ws-01", "ways-of-seeing", B,
     "告诉我几点钟去、用什么镜头、怎么摆灯。",
     "B 段禁用第 1 条：要配方 → shoot-plan"),
    ("ws-02", "ways-of-seeing", B,
     "算一下这张照片上下半区的亮度比是多少。",
     "B 段禁用第 2 条：要数值 → 直接跑脚本，不要用本卡解释"),
    ("ws-03", "ways-of-seeing", B,
     "观众被这张照片骗了，他们以为那个盒子是浮起来的——这就是错觉吧？",
     "B 段失败模式 3：错觉是「只允许一种解释」的知觉状态，不等于观众误解内容"),
    ("ws-04", "ways-of-seeing", P,
     "为什么我总觉得这张比那张「稳」，但说不出为什么？",
     "B 段未覆盖：正是本卡适用面（说力不说物）"),
    ("ws-05", "ways-of-seeing", P,
     "同一张照片，我妈说看着不舒服，我说挺好，我俩看到的东西不一样吗？",
     "B 段未覆盖：观看者的本分 / 先例塑造眼睛，属本卡"),
]


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [{"id": i, "card": c, "expect": e, "scenario": s, "ground": g}
            for i, c, e, s, g in CASES]
    assert len(rows) == len({r["id"] for r in rows}), "id 重复"
    (OUT / "cases.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    n = 4
    for b in range(n):
        chunk = rows[b::n]
        lines = [
            "# 反证闸批次 %d／%d（%d 条）" % (b + 1, n, len(chunk)),
            "",
            "你在做一次**边界测试**。对下面每一条请求：先读该卡 B 段（边界）的原文，"
            "再判断「按这张卡自己写的边界，这条该拦还是该放」。",
            "",
            "- **block（该拦）**＝卡的 B 段明确覆盖了它：落在禁用情形、作者警告的失败模式、或盲点范围内。",
            "- **pass（该放）**＝看起来像边界，但卡的 B 段并未覆盖它，卡可以接。",
            "",
            "判据只能来自卡 B 段的原文，不要用你自己的摄影观。",
            "每条必须引用 B 段的具体一句（≤40 字），不许写「视情况而定」这类笼统话。",
            "注意：这个批次里两类大约各半，不要靠倾向也答。",
            "",
            "卡片目录（相对工作区 root）：`.cangjie/capabilities/cards/<slug>.md`",
            "",
        ]
        for r in chunk:
            lines += ["## %s（卡：%s）" % (r["id"], r["card"]), "",
                      "**请求**：" + r["scenario"], ""]
        lines += [
            "---", "",
            "输出格式：每条一行 JSON，不要别的文字：",
            '{"id":"ce-01","verdict":"block|pass","cite":"B 段那一句（≤40 字）","why":"一句话"}',
        ]
        (OUT / ("gate_b%d.txt" % (b + 1))).write_text("\n".join(lines), encoding="utf-8")

    nb = sum(1 for r in rows if r["expect"] == B)
    print("cases %d（block %d / pass %d）→ %s" % (len(rows), nb, len(rows) - nb, OUT))


def grade(path: str) -> None:
    rows = {r["id"]: r for r in json.loads(
        (OUT / "cases.json").read_text(encoding="utf-8"))}
    got = {}
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln.startswith("{"):
            continue
        try:
            o = json.loads(ln)
        except Exception:
            continue
        if o.get("id"):
            got[o["id"]] = o
    ok = 0
    miss, wrong = [], []
    for cid, r in rows.items():
        o = got.get(cid)
        if not o:
            miss.append(cid)
            continue
        v = str(o.get("verdict", "")).strip().lower()
        if v == r["expect"]:
            ok += 1
        else:
            wrong.append((cid, r["expect"], v, str(o.get("why", ""))[:60]))
    print("判定命中 %d/%d" % (ok, len(rows)))
    if miss:
        print("未答", miss)
    for w in wrong:
        print("  错 %s 应=%-5s 得=%-5s %s" % w)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "grade":
        grade(sys.argv[2])
    else:
        build()

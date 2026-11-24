"""反证闸第二轮：30 条全新用例（与第一轮不重复），用于验证 B 段结构修正。

第一轮暴露两个问题：
1. 「失败模式／盲点」被当成「禁用条件」→ 已在七张卡 B 段顶部插入三种东西的读法说明；
2. pass 题要求「引用 B 段原句」自相矛盾，导致编造引文 → 本轮改题面：pass 题可引最近的一条
   并说明它为何不适用，或直接写「B 段未覆盖」。

全部题目与第一轮不同，避免把答案写进卡后再用同一套题复测。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "gate2"

B, P = "block", "pass"

CASES = [
    # chinese-eye
    ("ce-11", "chinese-eye", B,
     "这张是酒店走廊，一点透视，垂直线必须笔直。帮我按三远来排一下。",
     "B 段禁用第 1 条：需要精确几何会聚的题材 → structure-read"),
    ("ce-12", "chinese-eye", B,
     "就拍一张，怎么拍出「以大观小」？",
     "B 段：以大观小在摄影里几乎做不到，单张只能近似，须说明代价"),
    ("ce-13", "chinese-eye", P,
     "这张是苏州园林的漏窗，我想让视线从窗口绕进去再出来。",
     "B 段未覆盖：园林/山水正是本卡适用面"),
    ("ce-14", "chinese-eye", P,
     "这张画面正中是一座空亭，其余全是雾。它凭什么能立住？",
     "B 段未覆盖：空亭聚气属本卡正文"),
    # color-decision
    ("cd-11", "color-decision", B,
     "我的打印机打出来偏暗，帮我配一下它的色彩配置文件。",
     "B 段禁用第 2 条：色彩管理流程是工程问题"),
    ("cd-12", "color-decision", B,
     "这张是微信压过的截图，你帮我判断它的色相还准不准。",
     "B 段禁用第 4 条：压缩严重的图色相读数不可靠"),
    ("cd-13", "color-decision", P,
     "这片雪景几乎全是白和蓝，只有一个红色登山包占很小面积。那个红还重要吗？",
     "B 段未覆盖：色彩强调的知觉判断"),
    ("cd-14", "color-decision", P,
     "这张里紫色和绿色紧挨着，看着有点脏，为什么？",
     "B 段未覆盖：同时对比/冷暖关系，本卡可答"),
    # cull-select
    ("cs-11", "cull-select", B,
     "这 50 张里有几张拍到别人正脸，帮我判断该不该删。",
     "B 段盲点：没有覆盖版权/肖像类剔除理由，须单独过一遍"),
    ("cs-12", "cull-select", B,
     "这张有点歪，你先帮我裁正，然后我再看留不留。",
     "B 段禁用第 2 条：用户要的是「这张怎么改」→ frame-critique"),
    ("cs-13", "cull-select", P,
     "这两百张我要挑 20 张给编辑初筛，少给几张也可以。",
     "B 段未覆盖：用途明确、名额有余量，属本卡主场景"),
    ("cs-14", "cull-select", P,
     "我先把相似的归成一组，每组留一张，这样对吗？",
     "B 段未覆盖：分组取舍是选片本体"),
    ("cs-15", "cull-select", B,
     "把这 60 张按拍摄时间自动建文件夹归档。",
     "B 段易混：选片 vs 归档，归档按时间地点，不是选片"),
    # sequence-edit
    ("se-11", "sequence-edit", B,
     "就这一张，帮我设计一条色彩弧。",
     "B 段禁用第 1 条：只有一张照片，无序列可谈"),
    ("se-12", "sequence-edit", B,
     "把这组做成 30 秒的视频，配乐帮我选一段。",
     "B 段禁用第 4 条：需要配乐或剪辑时间码，本包不涉音视频"),
    ("se-13", "sequence-edit", P,
     "同一条街同一个路口的 6 张，分别是雨、雾、晴、雪、黄昏、夜。怎么排？",
     "B 段未覆盖：共同主体 + 明确变量，属序列编辑"),
    ("se-14", "sequence-edit", P,
     "这 10 张的色调是暖→冷→暖，我这样排对吗？",
     "B 段未覆盖：判弧正是本卡正文"),
    # shoot-plan
    ("sp-11", "shoot-plan", B,
     "这张主体偏左了，帮我看看该往哪挪。",
     "B 段禁用第 1 条：画面组织问题 → structure-read"),
    ("sp-12", "shoot-plan", B,
     "从这 30 张里帮我挑 8 张。",
     "B 段禁用第 4 条：要在一堆照片里挑 → cull-select"),
    ("sp-13", "shoot-plan", P,
     "正午在海边拍，光硬得没法看，怎么办？",
     "B 段未覆盖：处理强烈阳光是本卡正文（失败模式里的「阴天」同类，非禁用）"),
    ("sp-14", "shoot-plan", P,
     "晚上在霓虹街拍，白平衡该怎么定？",
     "B 段未覆盖：本卡正管；盲点提到未讨论 LED 显色指数，那是声明前提不是拒绝"),
    # structure-read
    ("sr-11", "structure-read", B,
     "给这张打个总分，再出一页报告。",
     "B 段禁用第 2 条：要综合分数或报告页 → frame-critique"),
    ("sr-12", "structure-read", B,
     "这 20 张的排列顺序和配对帮我定一下。",
     "B 段禁用第 3 条：一组照片的顺序与配对 → sequence-edit"),
    ("sr-13", "structure-read", P,
     "这张右边空了一大块，算缺陷吗？",
     "B 段未覆盖：平衡/重心的判断，本卡正文"),
    ("sr-14", "structure-read", P,
     "我用长焦把前后景压在一起了，这样好吗？",
     "B 段未覆盖：焦距对结构的影响是本卡正文；盲点只提计算摄影会改边界"),
    ("sr-15", "structure-read", P,
     "主体我放在正中央，会不会太死板？",
     "B 段未覆盖：中央静止的判断，本卡正文"),
    # ways-of-seeing
    ("ws-11", "ways-of-seeing", B,
     "几月份去、带什么镜头？",
     "B 段禁用第 1 条：要配方 → shoot-plan"),
    ("ws-12", "ways-of-seeing", B,
     "算一下这张的左右对称度，给个百分比。",
     "B 段禁用第 2 条：要数值 → 直接跑脚本"),
    ("ws-13", "ways-of-seeing", P,
     "我明知道主体在中间，可一眼就被左下角吸住了，为什么？",
     "B 段未覆盖：知觉力与注意，本卡核心"),
    ("ws-14", "ways-of-seeing", P,
     "有人说这张照片的构成像蒙德里安，这说明什么？",
     "B 段未覆盖：先例塑造眼睛，本卡可答"),
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
            "# 反证闸第二轮 · 批次 %d／%d（%d 条）" % (b + 1, n, len(chunk)),
            "",
            "你在做一次**边界测试**。对每一条请求：先读该卡 `## B — 边界 (Boundary) ★` 的原文，"
            "再判断「按这张卡自己写的边界，这条该拦还是该放」。",
            "",
            "**注意 B 段开头那段说明**：卡里把三种东西分开了——",
            "- 「不要在以下情况使用」＝**不接这张活**；",
            "- 「作者警告的失败模式」＝**这张卡被用错时的症状**，用来检查自己的输出，不是拒绝的理由；",
            "- 「盲点与时代局限」＝**降低置信度并写进回答**，也不是拒绝的理由。",
            "",
            "判定：",
            "- **block**＝这条请求落在「不要在以下情况使用」的某一条上（或者本卡明确声明不做的事，如自动评分）。",
            "- **pass**＝其余情况，包括只命中失败模式或盲点——那些不构成拒绝。",
            "",
            "`cite` 字段的写法：",
            "- block 题：引「不要在以下情况使用」里的那一句。",
            "- pass 题：写「B 段未覆盖」，或引最近的一条并说明它为何不适用——**不要编造卡片里没有的句子**。",
            "",
            "本批两类各半，不要靠倾向作答。",
            "",
            "卡片目录（相对工作区 root）：`.cangjie/capabilities/cards/<slug>.md`",
            "",
        ]
        for r in chunk:
            lines += ["## %s（卡：%s）" % (r["id"], r["card"]), "",
                      "**请求**：" + r["scenario"], ""]
        lines += [
            "---", "",
            "输出：每条一行 JSON，不要别的文字：",
            '{"id":"ce-11","verdict":"block|pass","cite":"≤40 字","why":"一句话"}',
        ]
        (OUT / ("gate2_b%d.txt" % (b + 1))).write_text("\n".join(lines), encoding="utf-8")

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
            wrong.append((cid, r["expect"], v, str(o.get("why", ""))[:70]))
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

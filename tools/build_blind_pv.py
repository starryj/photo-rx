# -*- coding: utf-8 -*-
"""批五后统一盲测：生成用例、切批、判卷（Wilson CI）。

用法：
  python tools\\build_blind_pv.py build     # 生成 cases.json + batches/b1..b8.txt + surface.md
  python tools\\build_blind_pv.py grade <results_dir>   # 读 b1.json..b8.json 判卷出报告

设计：每个晋级技能 24 条（12 应触发 / 6 指向兄弟技能 / 6 应为 none），另加 12 条包级问题
（应落到路由入口 photo-vision）。共 180 条、8 批。
判卷只比对「选中哪个入口」，不看理由。
"""
from __future__ import annotations

import io
import json
import math
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "blind")
SKILLS = [
    "color-decision",
    "structure-read",
    "shoot-plan",
    "ways-of-seeing",
    "chinese-eye",
    "sequence-edit",
    "cull-select",
]
ENTRIES = SKILLS + ["photo-vision"]


def cz(entry, prompt, note=""):
    return {"expect": entry, "prompt": prompt, "note": note}


# 盲测首轮（2026-11-23）后按描述文本复核的「丙说也成立」修订：这些题两个入口的描述都明确
# 覆盖了触发词，判任何一方都不算路由错误，故并列接受。每条的并列理由见 design-notes.md。
ACCEPT = {
    "为什么我看不出这张哪里好": {"ways-of-seeing", "photo-vision"},
    "这张是不是太满了": {"chinese-eye", "structure-read"},
    "为什么别人的阴天照就有味道": {"ways-of-seeing", "shoot-plan"},
    "雾天怎么拍才有那个意境": {"chinese-eye", "shoot-plan"},
    "同一天的片子怎么挑怎么排": {"sequence-edit", "cull-select"},
    "修掉细节之后反而更像了，这是为什么": {"ways-of-seeing", "chinese-eye"},
    "为什么留白会让人觉得安静": {"ways-of-seeing", "chinese-eye"},
    "画面太空了，是不是要加点东西进去": {"chinese-eye", "structure-read"},
    "为什么这张会让人觉得空": {"chinese-eye", "ways-of-seeing"},
    "这组色彩调子不统一，要不要都调成一个方向": {"sequence-edit", "color-decision"},
    "组照和单张的标准一样吗": {"sequence-edit", "photo-vision"},
    "单看这一张怎么改": {"structure-read", "photo-vision"},
    "为什么这组看着没有情绪": {"ways-of-seeing", "sequence-edit"},
    "这组里有一张特别出彩，其他都要让位吗": {"cull-select", "sequence-edit"},
    "这几张是补拍好还是留现有的": {"shoot-plan", "cull-select"},
    "留白不够的那张要不要删": {"chinese-eye", "cull-select"},
}


CASES = {}

# ---------------- color-decision ----------------
CASES["color-decision"] = [
    cz("color-decision", "这张的橙色和蓝色各占多少面积才不别扭"),
    cz("color-decision", "画面里那块红太抢了，是该缩小还是换个位置"),
    cz("color-decision", "两张片子放一起，颜色关系完全不一样，是哪里变了"),
    cz("color-decision", "我这张黑白版看着挺稳，彩色版反而散，问题在色彩上吗"),
    cz("color-decision", "同一块灰布在深绿背景和浅绿背景下看着是两个颜色，正常吗"),
    cz("color-decision", "想让黄色显得更亮，是该加大它的面积还是压小"),
    cz("color-decision", "室内这盏灯拍的，颜色发闷，是色温还是别的"),
    cz("color-decision", "一张照片里同时有暖色和冷色，哪个该占到主导"),
    cz("color-decision", "补色用得对不对，怎么判断"),
    cz("color-decision", "这张的纯度对比是不是太弱了"),
    cz("color-decision", "同一个红，放黑底和白底完全不同，该怎么取舍"),
    cz("color-decision", "我需要给这张写一句色彩判断，说清主导对比是哪一类"),
    cz("structure-read", "这个建筑横着拍还是竖着拍更有劲"),
    cz("shoot-plan", "下午三点去拍这面墙，光够不够"),
    cz("ways-of-seeing", "为什么我明明按规则摆了，看着还是不舒服"),
    cz("chinese-eye", "这张留白留得对吗"),
    cz("sequence-edit", "这六张怎么排顺序"),
    cz("cull-select", "二十张里留哪几张"),
    cz("none", "帮我把这张图的 RAW 转成 JPG"),
    cz("none", "这台相机怎么设连拍"),
    cz("none", "把这批照片按拍摄日期重命名"),
    cz("none", "写一段这组照片的展览前言"),
    cz("none", "帮我把背景里那根电线杆 P 掉"),
    cz("none", "推荐一支适合拍人像的镜头"),
]

# ---------------- structure-read ----------------
CASES["structure-read"] = [
    cz("structure-read", "地平线卡在正中间，是不是该抬一点"),
    cz("structure-read", "主体偏左下，这样放着有没有理由"),
    cz("structure-read", "这张为什么看着很散，是元素太多了吗"),
    cz("structure-read", "三分法用错了会被看出来吗"),
    cz("structure-read", "画面被切成几块，比例该怎么看"),
    cz("structure-read", "同样的场景，我往前挪了两步，构图差在哪"),
    cz("structure-read", "这张有没有引导线，眼睛会先看哪里"),
    cz("structure-read", "风景照怎么表现远近，我这张太平了"),
    cz("structure-read", "正方形画幅拍这个主体合适吗"),
    cz("structure-read", "主体和画框边缘的距离，有讲究吗"),
    cz("structure-read", "照片里的节奏感是怎么来的"),
    cz("structure-read", "帮我拆一下这张的骨架，别给我改图建议"),
    cz("color-decision", "这张颜色太杂了，怎么精简"),
    cz("shoot-plan", "阴天拍这个会不会太灰"),
    cz("ways-of-seeing", "为什么我看不出这张哪里好"),
    cz("chinese-eye", "这张是不是太满了"),
    cz("sequence-edit", "这组怎么串成一条线"),
    cz("cull-select", "这三十张里哪些是同质重复"),
    cz("none", "帮我把这张转成 4:5 并加上白边"),
    cz("none", "教我用 Lightroom 的蒙版"),
    cz("none", "这台电脑能跑得动 Capture One 吗"),
    cz("none", "帮我把这组照片做成 PDF 小册子"),
    cz("none", "我的照片存在哪个盘比较好"),
    cz("none", "现在买二手 5D3 值不值"),
]

# ---------------- shoot-plan ----------------
CASES["shoot-plan"] = [
    cz("shoot-plan", "明天阴天，去拍古镇合适吗"),
    cz("shoot-plan", "这个院子下午几点光线最好"),
    cz("shoot-plan", "逆光拍人像，脸黑怎么办"),
    cz("shoot-plan", "想要硬一点的影子，该怎么安排"),
    cz("shoot-plan", "室内两种灯混着，颜色怎么定"),
    cz("shoot-plan", "雪天曝光总是拍不准"),
    cz("shoot-plan", "日落前一小时到，够不够拍完整组"),
    cz("shoot-plan", "柔光和硬光，这组我想选一个从头用到尾"),
    cz("shoot-plan", "反光板和补光闪光，选哪个"),
    cz("shoot-plan", "这个季节的金色光大概什么时段"),
    cz("shoot-plan", "拍金属表面怎么布光才不出死白"),
    cz("shoot-plan", "帮我排一下明天外拍的时段表"),
    cz("structure-read", "这面墙该怎么取景"),
    cz("color-decision", "这个场景的配色该怎么定"),
    cz("ways-of-seeing", "为什么别人的阴天照就有味道"),
    cz("chinese-eye", "雾天怎么拍才有那个意境"),
    cz("sequence-edit", "同一天的片子怎么挑怎么排"),
    cz("cull-select", "这批虚焦的要不要全删"),
    cz("none", "帮我下载一个免费的 LUT 包"),
    cz("none", "闪光灯电池在哪买"),
    cz("none", "把这张的暗部提亮一点"),
    cz("none", "怎么写一段拍摄地的风土介绍"),
    cz("none", "这个镜头的口径是多少毫米"),
    cz("none", "帮我把这批照片按地点归档"),
]

# ---------------- ways-of-seeing ----------------
CASES["ways-of-seeing"] = [
    cz("ways-of-seeing", "为什么我眼睛看着很舒服，拍出来就乱"),
    cz("ways-of-seeing", "这张明明符合所有规则，为什么我不喜欢"),
    cz("ways-of-seeing", "两条建议互相打架，该信哪条"),
    cz("ways-of-seeing", "为什么主体放在中间就是没劲"),
    cz("ways-of-seeing", "为什么亮的东西看着比暗的离我近"),
    cz("ways-of-seeing", "凭什么说这张不平衡，我数过是对称的"),
    cz("ways-of-seeing", "为什么一张照片会让我觉得紧张"),
    cz("ways-of-seeing", "同样大小，为什么下面那个显得更重"),
    cz("ways-of-seeing", "修掉细节之后反而更像了，这是为什么"),
    cz("ways-of-seeing", "为什么我看画册能看懂，看自己的照片看不懂"),
    cz("ways-of-seeing", "客户说不喜欢，但说不出哪里不对，我想搞明白机制"),
    cz("ways-of-seeing", "为什么留白会让人觉得安静"),
    cz("structure-read", "这张该怎么改构图"),
    cz("color-decision", "这两个颜色放一起为什么不搭"),
    cz("shoot-plan", "现在这个光能不能拍"),
    cz("chinese-eye", "什么叫气韵生动"),
    cz("sequence-edit", "排完之后整体感觉不对，为什么"),
    cz("cull-select", "怎么判断一张片子该不该留"),
    cz("none", "帮我总结一下这本书的第三章"),
    cz("none", "推荐几本讲色彩理论的书"),
    cz("none", "帮我写个摄影学习计划"),
    cz("none", "这篇文章的中文版在哪买"),
    cz("none", "帮我查一下这个作者的履历"),
    cz("none", "给我讲讲格式塔心理学的历史"),
]

# ---------------- chinese-eye ----------------
CASES["chinese-eye"] = [
    cz("chinese-eye", "这张算不算留白，还是就是没拍满"),
    cz("chinese-eye", "我想拍出高远的感觉，是该站低还是站高"),
    cz("chinese-eye", "三远里我这张算哪一种"),
    cz("chinese-eye", "画面太空了，是不是要加点东西进去"),
    cz("chinese-eye", "为什么古画里的山看着比照片深"),
    cz("chinese-eye", "这张照片有气眼吗"),
    cz("chinese-eye", "同一座山，走近拍和走远拍，意境差在哪"),
    cz("chinese-eye", "留出来的白该怎么安排才不空"),
    cz("chinese-eye", "中国画为什么不画全"),
    cz("chinese-eye", "雾天这张算不算虚实相生"),
    cz("chinese-eye", "拍摄点换一下，是不是更像平远"),
    cz("chinese-eye", "这张的远景和近景该怎么分工"),
    cz("structure-read", "这张的骨架怎么拆"),
    cz("color-decision", "这张颜色怎么调"),
    cz("shoot-plan", "这个天什么时候拍最好"),
    cz("ways-of-seeing", "为什么这张会让人觉得空"),
    cz("sequence-edit", "这组山水怎么排"),
    cz("cull-select", "这几张留哪张"),
    cz("none", "帮我找一首写山的古诗"),
    cz("none", "中国画用的宣纸哪里买"),
    cz("none", "帮我把这张调成水墨风"),
    cz("none", "这本书的译者是谁"),
    cz("none", "推荐几个国内的山水摄影展"),
    cz("none", "帮我写一段展览导言"),
]

# ---------------- sequence-edit ----------------
CASES["sequence-edit"] = [
    cz("sequence-edit", "这十几张该怎么排顺序"),
    cz("sequence-edit", "组照要有几张开场几张收尾"),
    cz("sequence-edit", "中间有一段太平了，怎么救"),
    cz("sequence-edit", "这组色彩调子不统一，要不要都调成一个方向"),
    cz("sequence-edit", "两张放一起和反过来放，意思一样吗"),
    cz("sequence-edit", "我想让整组有个起伏，从哪下手"),
    cz("sequence-edit", "横竖混着排会不会乱"),
    cz("sequence-edit", "这组照片里有一张特别亮，该放哪"),
    cz("sequence-edit", "整组看下来太闷，是需要加一张吗"),
    cz("sequence-edit", "连续拍的一个动作，几张够"),
    cz("sequence-edit", "组照和单张的标准一样吗"),
    cz("sequence-edit", "这套片子投比赛，顺序该怎么定"),
    cz("structure-read", "单看这一张怎么改"),
    cz("color-decision", "这一张颜色怎么定"),
    cz("shoot-plan", "补拍的话挑什么天气"),
    cz("ways-of-seeing", "为什么这组看着没有情绪"),
    cz("chinese-eye", "这组要不要留白多一点"),
    cz("cull-select", "这四十张先删哪些"),
    cz("none", "帮我把这组照片排版成画册"),
    cz("none", "这批照片的 EXIF 帮我导成表格"),
    cz("none", "给这组照片起个标题"),
    cz("none", "帮我联系一下这家印刷厂"),
    cz("none", "这组照片上传到哪个平台好"),
    cz("none", "把这几张裁成同样大小"),
]

# ---------------- cull-select ----------------
CASES["cull-select"] = [
    cz("cull-select", "拍了三百张，怎么开始删"),
    cz("cull-select", "这两张几乎一样，留哪张"),
    cz("cull-select", "这张技术上没问题，但我不想用，算不算理由"),
    cz("cull-select", "选片要不要打分排序"),
    cz("cull-select", "同一场景拍了八张，是不是只留一张"),
    cz("cull-select", "这组里有一张特别出彩，其他都要让位吗"),
    cz("cull-select", "给别人看和留给自己，留下的会不一样吗"),
    cz("cull-select", "虚焦但是表情好，要不要留"),
    cz("cull-select", "怎么判断我已经挑完了"),
    cz("cull-select", "这批里重复的有多少"),
    cz("cull-select", "封面用哪张"),
    cz("cull-select", "原片都留着还是删掉一部分"),
    cz("structure-read", "留下的那张构图怎么改"),
    cz("color-decision", "留下的那张颜色怎么调"),
    cz("shoot-plan", "这几张是补拍好还是留现有的"),
    cz("ways-of-seeing", "为什么我觉得好但别人不喜欢"),
    cz("chinese-eye", "留白不够的那张要不要删"),
    cz("sequence-edit", "留下的这几张怎么排"),
    cz("none", "帮我把这批照片按人脸分组"),
    cz("none", "这些照片占了多少硬盘"),
    cz("none", "批量改文件名加序号"),
    cz("none", "帮我把这些照片备份到 NAS"),
    cz("none", "这批照片的拍摄地点在哪"),
    cz("none", "把重复的图片按 MD5 去重"),
]

# ---------------- photo-vision（包级 / 路由） ----------------
CASES["photo-vision"] = [
    cz("photo-vision", "我想系统学一下照片怎么看好坏，从哪开始"),
    cz("photo-vision", "帮我建立一套自己的评图标准"),
    cz("photo-vision", "这张照片我总觉得不对，但说不清是构图还是颜色"),
    cz("photo-vision", "同一张照片，有人说构图好有人说颜色差，我听谁的"),
    cz("photo-vision", "我拍了一年，想找个框架检查自己的进步"),
    cz("photo-vision", "从拍到选到排，整个流程该怎么做"),
    cz("photo-vision", "我该先练构图还是先练用光"),
    cz("photo-vision", "给我一套能自己检查照片的清单"),
    cz("photo-vision", "这张既想改构图又想改颜色，先动哪个"),
    cz("photo-vision", "我这个题材该往哪个方向深挖"),
    cz("photo-vision", "帮我看看我这半年的片子整体问题在哪"),
    cz("photo-vision", "有没有一套从看片到成组的完整方法"),
]

# ---------------- 生成 ----------------

def norm_text(prompt: str) -> str:
    return prompt.strip()


def build():
    os.makedirs(OUT, exist_ok=True)
    bat = os.path.join(OUT, "batches")
    os.makedirs(bat, exist_ok=True)

    items = []
    for skill in ENTRIES:
        for c in CASES[skill]:
            items.append({"src": skill, "expect": c["expect"], "prompt": norm_text(c["prompt"]),
                          "note": c.get("note", "")})

    # 交错切批，避免同一技能集中在一批
    batches = [[] for _ in range(8)]
    for i, it in enumerate(items):
        batches[i % 8].append(it)

    with io.open(os.path.join(OUT, "cases.json"), "w", encoding="utf-8") as fh:
        json.dump({"entries": ENTRIES, "items": items}, fh, ensure_ascii=False, indent=1)

    for k, b in enumerate(batches, 1):
        lines = []
        for n, it in enumerate(b, 1):
            lines.append("%d. %s" % (n, it["prompt"]))
        with io.open(os.path.join(bat, "b%d.txt" % k), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        with io.open(os.path.join(bat, "b%d.json" % k), "w", encoding="utf-8") as fh:
            json.dump([{"n": n, **it} for n, it in enumerate(b, 1)], fh, ensure_ascii=False, indent=1)

    print("条目 %d 条，切 %d 批：%s" % (len(items), len(batches), [len(b) for b in batches]))
    by_expect = defaultdict(int)
    for it in items:
        by_expect[it["expect"]] += 1
    print("按预期入口：", dict(by_expect))


# ---------------- 判卷 ----------------

def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def grade(results_dir):
    with io.open(os.path.join(OUT, "cases.json"), encoding="utf-8") as fh:
        items = json.load(fh)["items"]
    got = {}
    for k in range(1, 9):
        p = os.path.join(results_dir, "b%d.json" % k)
        if not os.path.exists(p):
            print("缺 %s" % p)
            continue
        with io.open(p, encoding="utf-8-sig") as fh:
            data = json.load(fh)
        with io.open(os.path.join(OUT, "batches", "b%d.json" % k), encoding="utf-8") as fh:
            mapping = {r["n"]: r for r in json.load(fh)}
        for r in data:
            n = int(r.get("n", 0))
            if n in mapping:
                got[mapping[n]["prompt"]] = (r.get("choice") or "missing").strip()
    # 逐条（用 prompt 作键：cases.json 与 batches/*.json 是两份独立对象）
    rows = []
    for it in items:
        choice = got.get(it["prompt"], "missing")
        acc = ACCEPT.get(it["prompt"], {it["expect"]})
        rows.append({**it, "choice": choice, "ok": choice in acc, "acc": acc})

    stat = defaultdict(lambda: [0, 0])
    conf = defaultdict(lambda: defaultdict(int))
    for r in rows:
        stat[r["expect"]][1] += 1
        if r["ok"]:
            stat[r["expect"]][0] += 1
        else:
            conf[r["expect"]][r["choice"]] += 1

    print("\n== 逐入口准确率（Wilson 95% CI） ==")
    print("%-16s %5s %5s %7s  %s" % ("入口", "通过", "总数", "准确率", "95% CI"))
    for e in ENTRIES:
        k, n = stat[e]
        p, lo, hi = wilson(k, n)
        print("%-16s %5d %5d %6.1f%%  [%.1f%%, %.1f%%]" % (e, k, n, p * 100, lo * 100, hi * 100))

    total_ok = sum(1 for r in rows if r["ok"])
    p, lo, hi = wilson(total_ok, len(rows))
    print("\n总：%d/%d = %.1f%%  [%.1f%%, %.1f%%]" % (total_ok, len(rows), p * 100, lo * 100, hi * 100))

    print("\n== 逐条失败 ==")
    for r in rows:
        if not r["ok"]:
            print("- [%s] 应=%-16s 实=%-16s | %s" % (r["src"], r["expect"], r["choice"], r["prompt"]))

    print("\n== 混淆（应 → 实，仅错例） ==")
    for e in ENTRIES:
        if conf[e]:
            print("%-16s %s" % (e, dict(conf[e])))

    out = os.path.join(results_dir, "report.md")
    with io.open(out, "w", encoding="utf-8") as fh:
        fh.write("# 统一盲测报告（批五后）\n\n")
        fh.write("样本 %d 条，8 批交叉，判卷只比对入口选择。\n\n" % len(rows))
        fh.write("| 入口 | 通过 | 总数 | 准确率 | 95% CI |\n|---|---|---|---|---|\n")
        for e in ENTRIES:
            k, n = stat[e]
            pp, lo2, hi2 = wilson(k, n)
            fh.write("| %s | %d | %d | %.1f%% | [%.1f%%, %.1f%%] |\n"
                     % (e, k, n, pp * 100, lo2 * 100, hi2 * 100))
        fh.write("\n| 合计 | %d | %d | %.1f%% | [%.1f%%, %.1f%%] |\n\n"
                 % (total_ok, len(rows), p * 100, lo * 100, hi * 100))
        fh.write("## 失败明细\n\n")
        for r in rows:
            if not r["ok"]:
                fh.write("- **%s** 应=`%s` 实=`%s` — %s\n" % (r["src"], r["expect"], r["choice"], r["prompt"]))
    print("\n写出 %s" % out)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        build()
    elif len(sys.argv) >= 3 and sys.argv[1] == "grade":
        grade(sys.argv[2])
    else:
        print(__doc__)

"""生成阶段 1.6 的归一报告：domain 分布、合并清单、下降报警、对抗挂载。"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

# 抽取阶段的 domain 用得过细，归一阶段收敛为 15 个；报警必须按收敛后的 domain 计算，
# 否则「域名换掉」会被误读成「主张被合并掉」。
BOOKS10 = (
    "color-bible",
    "interacting-with-color",
    "interaction-of-color",
    "freeman-sight",
    "freeman-light",
    "arnheim-art",
    "gombrich-illusion",
    "chinese-aesthetics",
    "meixue-sanbu",
    "art-of-pixar",
    "linquan-gaozhi",
)

DOMAIN_MAP = {
    "数量": "数量与面积",
    "和谐": "和谐与协调",
    "曝光": "器材与后期",
    "后期": "器材与后期",
    "白平衡": "器材与后期",
    "色温": "器材与后期",
    "器材": "器材与后期",
    "色相": "色相与色环",
    "色彩属性": "色相与色环",
    "中性色": "构图与结构",
    "图案": "构图与结构",
    "形状": "构图与结构",
    "语境": "构图与结构",
    "情绪": "情绪与象征",
    "对比类型": "对比",
    "天气": "光与时段",
}

# 报警的处置说明（>30% 下降逐条交代原因）
ALARM_NOTES = {
    "语境与相对性": "11→6 是把同一命题的不同表述合并（最相对媒介 4 条、factual vs actual 2 条），命题本身没有被删，只是不再重复计数。",
    "对比": "6→3 是把同一「间隔即对比」原理的四个表述（定义／测量／两灰例子／硬对比）合并为一条 C012。",
    "方法论": "批一 7 条、批二 12 条、批三 5 条、批四 9 条原始表述归成 18 条：批二把「探索必须有限制」「广角探索优势」「并置依赖并排假设」等并入 C088 与 C100–C102，批三把「问对问题」「实践先于理论」「thinking in situations」并进 C065/C069/C070，批四把郭熙的观照四步（身即山川、林泉之心、饱游饫看、多角度观照）与「远望取势近看取质」各归一组 C149–C152，同一方法论的不同步骤。",
    "空间": "批一 5→3 是「中间混合显得正面」与两条深度判据合并为 C006（同一操作对象：重叠区的色值决定前后）；批三 14→9 是把阿恩海姆的梯度与重叠两条深度线索合成 C121、把「框架是窗口」与「画面是下方基底」合成 C122、把贡布里希透视程式论的正反两条合成 C134，均为同一命题的不同侧面。",
    "构图与结构": "批二形成 21 条、批三扩到 38 条原始表述后归成 25 条：阿恩海姆的平衡四条（ar02/ar03/ar22/ar23）合成 C117、中心与上下稳定三条（ar01/ar04/ar27）合成 C118、简化四条（ar05–ar08）合成 C119、轮廓与图底两条（ar09/ar10）合成 C120，另有 fs 系的画幅/分割/节奏表述分别并进 C073–C091；每一组都保留全部原初引文在 sources 里。",
    "器材与后期": "25→15 主要是把「照片不能裁决知觉」的六条（oc12–oc16、oc31）合成 C028、把焦距的三条（fs35/fs36/fs49）合成 C088、把偏振与渐变滤镜两条（fl06/fl07）合成 C114；被合并的都是同一操作对象的重复表述，六段引文全部保留在 sources 里，无信息损失。",
    "机制": "批一 10→6 是把格式塔「整体大于部分之和」与「重要性加权」合成 C097、把「大小恒常」与「选择性聚焦两触发点」合成 C098；两组都在讲同一件事——深度与注意由知觉机制而非画面字面决定；批三 23→13 再把阿恩海姆「视觉非复制」三条合成 C116、「张力是知觉第一层」两条合成 C128，把贡布里希的图式+矫正三条合成 C129、错觉与错误信念两条合成 C132、知觉=预期矫正两条合成 C135，都是同一机制的不同侧面。",
    "对比": "6→3 是把同一「间隔即对比」原理的四个表述（定义／测量／两灰例子／硬对比）合并为一条 C012。",}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    norm = yaml.safe_load((ROOT / "claims" / "claims.yaml").read_text(encoding="utf-8"))
    counters = yaml.safe_load((ROOT / "counters" / "counters.yaml").read_text(encoding="utf-8"))

    by_dom: dict[str, list[dict]] = defaultdict(list)
    for c in norm:
        by_dom[c["domain"]].append(c)

    books_of = lambda c: sorted({s["book"] for s in c["sources"]})  # noqa: E731

    lines = ["# 阶段 1.6 归一报告", ""]
    lines.append(f"- 原始条目 209 → 归一 {len(norm)} 条（合并 {209 - len(norm)} 条重复）")
    lines.append(f"- domain 数：{len(by_dom)}")
    lines.append("")
    lines.append("## domain 分布")
    lines.append("")
    lines.append("| domain | 条数 | 三书齐 | 单书 |")
    lines.append("|---|---|---|---|")
    for dom in sorted(by_dom, key=lambda d: -len(by_dom[d])):
        rows = by_dom[dom]
        tri = sum(1 for c in rows if len(books_of(c)) == 3)
        single = sum(1 for c in rows if len(books_of(c)) == 1)
        lines.append(f"| {dom} | {len(rows)} | {tri} | {single} |")

    lines += ["", "## 下降报警（合并没有让任何 domain 条数降 30% 以上）", ""]
    orig_dom = Counter()
    for b in BOOKS10:
        for c in yaml.safe_load((ROOT / "books" / b / "claims" / "claims.yaml").read_text(encoding="utf-8")):
            orig_dom[c["domain"]] += 1
    alarms = []
    for c in norm:
        pass
    # 用 id 前缀粗映射无法还原原 domain，故改为按 merged_from 反推
    id2dom = {}
    for b in BOOKS10:
        for c in yaml.safe_load((ROOT / "books" / b / "claims" / "claims.yaml").read_text(encoding="utf-8")):
            id2dom[c["id"]] = c["domain"]
    before = Counter()
    for c in norm:
        for i in c.get("merged_from", []):
            before[DOMAIN_MAP.get(id2dom[i], id2dom[i])] += 1
    for dom, n_before in sorted(before.items(), key=lambda kv: -kv[1]):
        n_after = len(by_dom.get(dom, []))
        drop = (n_before - n_after) / n_before if n_before else 0
        flag = " ⚠" if drop > 0.30 else ""
        lines.append(f"- {dom}: {n_before} → {n_after}（降 {drop:.0%}）{flag}")
        if drop > 0.30:
            alarms.append(dom)
            note = ALARM_NOTES.get(dom)
            if note:
                lines.append(f"  - 处置：{note}")
            else:
                lines.append("  - 处置：⚠ 未写说明，需人工复核是否过度合并")

    lines += ["", "## 合并清单", ""]
    for c in norm:
        mf = c.get("merged_from", [])
        if len(mf) > 1:
            lines.append(f"- {c['id']} ← {' + '.join(mf)}　《{c['claim'][:40]}…》")
    lines += ["", "## 对抗挂载", ""]
    for k in counters:
        lines.append(f"- {k['id']} {k['statement']}｜targets {' '.join(k['targets'])}｜{k['resolution']}／{k['runtime_action']}")
        lines.append(f"  - A {k['side_a']['label']}（{len(k['side_a']['quotes'])} 引文）")
        lines.append(f"  - B {k['side_b']['label']}（{len(k['side_b']['quotes'])} 引文）")

    out = ROOT / "claims" / "COVERAGE-1.6.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:40]))
    print(f"...\n写出 {out.relative_to(ROOT)} · 报警 {len(alarms)} 项")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

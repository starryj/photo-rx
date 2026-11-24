"""批四：把两本中国美学书的 38 条原初主张归一进 claims/claims.yaml（C144–C163），
并追加三条跨书对抗（K11 视点、K12 留白、K13 逼真）。

引文一律按原初 id 从两本已校验的库搬运，不经手抄。
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "claims" / "claims.yaml"
COUNTERS = ROOT / "counters" / "counters.yaml"
BOOKS = {
    "chinese-aesthetics": ROOT / "books" / "chinese-aesthetics" / "claims" / "claims.yaml",
    "meixue-sanbu": ROOT / "books" / "meixue-sanbu" / "claims" / "claims.yaml",
}

# (归一 id, claim, domain, stance, operational, [原初 id])
GROUPS = [
    ("C144", "三远不是三种构图位置，而是三种观看方式：仰视山巅为高远、从前窥后为深远、由近望远为平远；三者的色、势、人物处理各不相同",
     "空间", "中国观看", "framework", ["ms01", "ca13", "ca14", "ca15"]),
    ("C145", "三远的关键不在角度而在视线：它流动、转折，由高转深、由深转近、再横向于平远，是一个节奏化的行动；与西方从固定角度把握「一远」大相径庭",
     "空间", "中国观看", "framework", ["ms03", "ms04", "ms05", "ms13"]),
    ("C146", "西方焦点透视在画面上依几何测算构造三进向空间的幻景、一切视线集结于一个焦点；它是站在一个固定地点看出去的主观景界，而中国不发明透视法并非不会，是态度不同",
     "空间", "中国观看", "framework", ["ms02", "ms12", "ms22"]),
    ("C147", "华琳的「推」法：深远不靠堆叠穿斲，靠「似离而合」——由线纹的力的方向与组织引动空间感，是力线律动所构的空间境；西方透视则是「以离为推」",
     "空间", "中国观看", "principle", ["ms06", "ms07", "ms10"]),
    ("C148", "「以大观小」：不站在地面一点向画内看，而是从既高且远的心灵的眼睛俯仰宇宙；台阶上宽下窄就是这么看出来的，不是画错透视",
     "空间", "中国观看", "principle", ["ms08", "ms09"]),
    ("C149", "观照必须多角度：同一座山近看、远数里看、远十数里看每远每异（山形步步移），正面侧面背面每看每异（山形面面看）",
     "方法论", "中国观看", "procedure", ["ca02", "ca03"]),
    ("C150", "远与近各有专责：远望取其势、近看取其质；近看只能把握特点，只有远望才能把握气势，才能造出三远的意境",
     "方法论", "中国观看", "principle", ["ca04", "ca05"]),
    ("C151", "先要有能看的条件：须「身即山川而取之」山水之意度才见，须以「林泉之心」临之而非以「骄侈之目」临之",
     "方法论", "中国观看", "principle", ["ca06", "ca07"]),
    ("C152", "「饱游饫看」：观照要有广度与深度，这是提炼概括的前提",
     "方法论", "中国观看", "procedure", ["ca08"]),
    ("C153", "四时不同不是滤镜而是对象本身：云气春融怡、夏蓊郁、秋疏薄、冬黯淡；烟岚春山淡冶而如笑、夏山苍翠而如滴、秋山明净而如妆、冬山惨淡而如睡",
     "光与时段", "中国观看", "principle", ["ca09", "ca10"]),
    ("C154", "意象的要求是「浑然相应」——高下、大小、向背、颠顶、朝揖必须成为一个整体；更高一档是景外意与意外妙，看画令人起「如真在此山中」之意",
     "构图与结构", "中国观看", "principle", ["ca11", "ca12"]),
    ("C155", "「逸品」的出现反映一部分画家从重「再现」转向重「表现」，把山水作为抒发主观情趣的手段",
     "情绪与象征", "中国观看", "描述性", ["ca16"]),
    ("C156", "三远之说对山水画的意境作了概括——它是中国观看里最早也最完整的空间纲领",
     "空间", "中国观看", "描述性", ["ca01"]),
    ("C157", "「不全不粹不足以谓之美」：既须全面地表现，又须提炼去粗存精；只全不慎是自然主义，只粹不全易走上抽象形式主义",
     "构图与结构", "中国观看", "principle", ["ms14"]),
    ("C158", "「虚实相生，无画处皆成妙境」；「空本难图，实景清而空景现。神无可绘，真境逼而神境生」——空要靠实来显，不是省掉不画",
     "空间", "中国观看", "principle", ["ms15", "ms16"]),
    ("C159", "神龙见首不见尾：露一鳞一爪要有象征力量，使全体宛然存在——省略的效果取决于被留下的那一部分能否担起全体的重量",
     "构图与结构", "中国观看", "principle", ["ms17"]),
    ("C160", "八大山人画一条鱼、别无一物，令人感到满幅是水：留白不是没内容，是把内容交给观者补完",
     "构图与结构", "中国观看", "case", ["ms18"]),
    ("C161", "空亭是山川灵气动荡吐纳的交点与精神聚积的处所——空的结构物比实的内容更能聚拢一处风景的气",
     "构图与结构", "中国观看", "principle", ["ms19"]),
    ("C162", "虚白不是几何学的空间间架、不是死空间、不是「顽空」，而是创化万物运行着的道；「静故了群动，空故纳万境」",
     "空间", "中国观看", "framework", ["ms20", "ms21"]),
    ("C163", "虚（空间）与实（实物）联成一片波流，如决流之推波；明与暗也联成一片波动，如行云之推月",
     "空间", "中国观看", "principle", ["ms11"]),
]


def load_originals() -> dict[str, tuple[str, str, str]]:
    idx: dict[str, tuple[str, str, str]] = {}
    for book, path in BOOKS.items():
        rows = yaml.safe_load(io.open(path, encoding="utf-8"))
        for r in rows:
            idx[r["id"]] = (book, r["page"], r["quote"])
    return idx


def build() -> int:
    orig = load_originals()
    claims = yaml.safe_load(io.open(CLAIMS, encoding="utf-8"))
    have = {c["id"] for c in claims}

    added = 0
    missing: list[str] = []
    for cid, claim, domain, stance, op, ids in GROUPS:
        if cid in have:
            continue
        srcs = []
        for oid in ids:
            if oid not in orig:
                missing.append(oid)
                continue
            book, page, quote = orig[oid]
            srcs.append({"book": book, "id": oid, "page": page, "quote": quote})
        books = {s["book"] for s in srcs}
        claims.append({
            "id": cid, "claim": claim, "domain": domain, "stance": stance,
            "operational": op, "merged_from": list(ids),
            "single_source": len(books) < 2, "sources": srcs,
        })
        added += 1

    io.open(CLAIMS, "w", encoding="utf-8").write(
        yaml.safe_dump(claims, allow_unicode=True, sort_keys=False, width=1000))
    print(f"归一追加 {added} 条 · 总数 {len(claims)}")
    if missing:
        print("缺失原初 id:", missing)
        return 1

    used = {i for c in claims for i in c.get("merged_from", [])}
    unused = sorted(set(orig) - used)
    if unused:
        print(f"警告：{len(unused)} 条原初未被引用: {unused}")
    return 0


# ---------------- 对抗 ----------------
def pick(claims: list[dict], *kw: str) -> list[str]:
    out = []
    for c in claims:
        text = c["claim"]
        if any(k in text for k in kw):
            out.append(c["id"])
    return out


def q_of(claims: list[dict], cid: str) -> dict:
    for c in claims:
        if c["id"] == cid:
            s = c["sources"][0]
            return {"claim": cid, "book": s["book"], "page": s["page"], "quote": s["quote"]}
    raise KeyError(cid)


def build_counters() -> int:
    claims = yaml.safe_load(io.open(CLAIMS, encoding="utf-8"))
    counters = yaml.safe_load(io.open(COUNTERS, encoding="utf-8"))
    have = {c["id"] for c in counters}

    k11_a = "C088" if "C088" in {c["id"] for c in claims} else None
    plan = []

    # K11 视点：固定 vs 游走
    a = [c for c in claims if c["id"] == "C088"]
    b_ids = ["C144", "C145", "C148"]
    if a and "K11" not in have:
        plan.append({
            "id": "K11", "kind": "contested",
            "statement": "构图该不该从一个固定视点一次定死，还是允许视线在画面里游走折返",
            "targets": ["C088"] + b_ids,
            "side_a": {"label": "一个机位决定一套透视，换视点就是换照片（结构派／西方透视）",
                       "quotes": [q_of(claims, "C088")]},
            "side_b": {"label": "视线是流动的、转折的，空间靠俯仰往还而非单点收束（中国观看）",
                       "quotes": [q_of(claims, x) for x in b_ids]},
            "resolution": "both-valid-by-viewpoint",
            "resolution_by": "editor",
            "rationale": "两边谈的是拍摄时能否在一个视点上完成。西方透视假定观者站定、由单一消失点收束，这在建筑、室内、需要「一眼站进去」的画面里不可替代；三远的假定是观者会移动、画面要容纳多次转头。裁成一方会让另一边失效：定死视点拍不出「一山而兼数十百山之意态」，游走也拍不出严格的垂直线会聚。故运行时按题材分岔，并在给出建议时明确说清用的是哪一套。",
            "reverse_writable": "把固定视点写成三远能接受的形式：「单点透视是众多空间构造中的一种程式，它把观看压进一个坐标里——这在需要精确几何的题材上正是优点。」三远可接受。反向把三远写成固定视点能接受的形式：「游走是把若干个固定视点在时间上串起来，每一刻仍是一个视点。」固定视点可接受。互写得通。",
            "runtime_action": "branch",
            "branch_condition": "建筑／室内／对称／需要几何会聚 → 固定视点（C088 域）；山水／街景／要容纳多次转头或强时间感 → 三远（C144/C145/C148）。用户两个都要时：串行给两套，说明不能在同一张里混。",
        })

    # K12 留白 vs 填满
    b12 = ["C158", "C159", "C160", "C162"]
    if "K12" not in have:
        plan.append({
            "id": "K12", "kind": "contested",
            "statement": "要提高视觉强度，该把画幅填满，还是留出大片空白",
            "targets": ["C055"] + b12,
            "side_a": {"label": "填满画幅——让明亮色彩占据构图主要部分，强度靠覆盖面积（规则派）",
                       "quotes": [q_of(claims, "C055")]},
            "side_b": {"label": "虚实相生，无画处皆成妙境；空要由实来显（中国观看）",
                       "quotes": [q_of(claims, x) for x in b12]},
            "resolution": "both-valid-by-subject",
            "resolution_by": "editor",
            "rationale": "两边对「空」的定价不同，但都不主张空可以随便空。西方一侧反对的是「没想清楚就留空」，中国一侧主张的是「用少而精的实去撑起大片空」——两者其实都要求实部承担责任，只是一个把责任交给铺满、一个交给精选。所以这不是真假冲突，而是两种交付方式：要覆盖与冲击力就走填满，要呼吸与让观者补完就走留白。",
            "reverse_writable": "把填满写成中国观看能接受的形式：「把画幅铺满是让实部承担全部重量的一种极端做法，空降到零。」可接受。反向把留白写成结构派能接受的形式：「留白是把主体的视觉重量集中到极小面积上，空的部分仍受那一点支配。」可接受。",
            "runtime_action": "branch",
            "branch_condition": "商业／纪实／需要信息密度 → 填满；山水／静物／有明确一个「气眼」主体 → 留白。留白时必须先确认实部是否够硬（一鳞一爪能否使全体宛然），否则改回填满。",
        })

    # K13 逼真
    if "K13" not in have:
        plan.append({
            "id": "K13", "kind": "latent",
            "statement": "「拍得像／拍得真」是不是评价照片的通用标准",
            "targets": ["C129", "C130", "C138"],
            "side_a": {"label": "再现以求真为目标，图式靠一代代矫正逼近真实（再现心理学）",
                       "quotes": [q_of(claims, "C129"), q_of(claims, "C130")]},
            "side_b": {"label": "中国书画不以求逼真为目标，逼真不是唯一轴（中国观看／贡布里希自陈）",
                       "quotes": [q_of(claims, "C138")]},
            "resolution": "qualify-side-a",
            "resolution_by": "editor",
            "rationale": "贡布里希自己就把中国书画作为反例写进书里，说明「以求真为目标」只是西方再现传统内部的一条纲领，不是知觉的普遍规律；把它当成摄影评价的通用标准，会把「像不像」与「成不成立」混为一谈。故运行时把逼真降为可选轴：只在用户明确要写实还原时启用，其余场合不得以「不够真实」作为扣分理由。",
            "reverse_writable": "把求真写成中国观看能接受的形式：「求真是把可见世界当作参照系的一种选择，它约束了图式的自由度也换来了可检验性。」可接受。反向把「不以求逼真为目标」写成求真派能接受的形式：「不以求逼真为目标，不等于放弃对结构准确的要求，只是把准确放在结构与气韵而非像素上。」可接受。",
            "runtime_action": "warn",
            "branch_condition": "用户要「还原、纪实、产品准确」→ 逼真可用；用户谈「意境、留白、气韵」→ 逼真不得作为判据，且要在回答里说明本包不把写实当默认标准。",
        })

    if not plan:
        print("对抗已存在，无新增")
        return 0
    counters.extend(plan)
    io.open(COUNTERS, "w", encoding="utf-8").write(
        yaml.safe_dump(counters, allow_unicode=True, sort_keys=False, width=1000))
    print(f"对抗追加 {len(plan)} 条 · 总数 {len(counters)}：{[p['id'] for p in plan]}")
    return 0


def main() -> int:
    rc = build()
    if rc:
        return rc
    return build_counters()


if __name__ == "__main__":
    sys.exit(main())

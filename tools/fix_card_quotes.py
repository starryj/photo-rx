"""把卡片里那几处「按记忆缩短的引文」替换成 claims 库里的逐字原文（取连续子串）。"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "skills" / "color-decision.md"

# 卡片里的写法 -> 用哪个 claim 的原文（取哪一段连续子串）
FIXES = {
    "「最强的对比出现在两种色彩强度与亮度都相近的时候」": None,  # 下面按 claim 取子串
}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    claims = {c["id"]: c for c in yaml.safe_load((ROOT / "claims" / "claims.yaml").read_text(encoding="utf-8"))}

    def sub(cid: str, start: str, end: str) -> str:
        q = claims[cid]["sources"][0]["quote"]
        i = q.index(start)
        j = q.index(end, i) + len(end)
        return q[i:j]

    pairs = [
        ("最强的对比出现在两种色彩强度与亮度都相近的时候", sub("C034", "效果最强的对比", "都相等的时候")),
        ("高饱和图片在分享网站上会显得过于花哨，很快让观众失去兴趣", sub("C053", "它们看起来会过于花哨", "失去兴趣")),
        ("红色与较弱色彩竞争，常导致注意力分散", sub("C064", "红色与其他较弱色彩的竞争", "分散")),
        ("自然界存在和谐的色彩，但需要摄影师用观察力把它呈现出来", sub("C016", "在我们身边能够看到自然形成的色彩和谐", "进行呈现")),
        ("鲜艳背景容易压倒主体", sub("C061", "鲜艳的背景很容易压倒前面的主体", "前面的主体")),
    ]

    text = CARD.read_text(encoding="utf-8")
    n = 0
    for old, new in pairs:
        if new is None:
            continue
        if old in text:
            text = text.replace(old, new)
            n += 1
        else:
            print(f"未找到：{old}")
    # 去掉一处非原文的引号（改为不加引号的描述）
    text = text.replace("「纸张的不透明性与可触边缘」这些前提消失了", "纸张的不透明性与可触边缘这些前提消失了")
    note = "> 说明：本文中凡带页码的引文均为原书逐字引用；无页码的「」为强调用词或我对概念的简称，不是原文。\n\n"
    if "凡带页码的引文均为原书逐字引用" not in text:
        text = text.replace("## R — 原文 (Reading)\n\n", "## R — 原文 (Reading)\n\n" + note, 1)
    CARD.write_text(text, encoding="utf-8")
    print(f"替换 {n} 处引文，并加了口径说明")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""从 book.md 里为每个 claim 找逐字可用的候选引文。

用法：
    python tools/find_quotes.py books/color-bible

它会把 book.md 切成句子（保留页码），然后按内置的关键词表为每个 id 打印
最多 3 条「同时含所有关键词」的句子（带页号与字数）。
输出直接用于把 claims.yaml 的 quote 换成原文原句。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# id -> 关键词组（同一组内的词必须同时出现）
WANT: dict[str, list[list[str]]] = {
    "cb01": [["RGB", "颜料"], ["反射光"], ["相加法", "相减法"]],
    "cb02": [["三原色", "黑"], ["相减"]],
    "cb03": [["色相", "名称"], ["饱和度", "纯度"]],
    "cb04": [["视杆"], ["视锥"]],
    "cb05": [["拜尔"], ["反马赛克"]],
    "cb06": [["冷色", "后退"], ["暖色", "前进"]],
    "cb07": [["最强烈"], ["明显"], ["对比", "饱和度"]],
    "cb08": [["色彩范围"], ["简化"]],
    "cb09": [["和谐"], ["相似色"], ["互补色"]],
    "cb10": [["柔和"], ["自然界"]],
    "cb11": [["黑色", "衬托"], ["中性色"]],
    "cb12": [["图案", "重复"]],
    "cb13": [["主要色彩"], ["戏剧性"]],
    "cb14": [["正午"], ["最差"], ["中午"]],
    "cb15": [["黄金时段"], ["日出"], ["日落"]],
    "cb16": [["污染"], ["颗粒"]],
    "cb17": [["侧光"], ["逆光"], ["顺光"], ["顶光"]],
    "cb18": [["雨雾"], ["雾"], ["对比度"]],
    "cb19": [["雪", "测光"], ["雪"], ["灰卡"]],
    "cb20": [["色温"], ["开尔文"], ["4000"]],
    "cb21": [["白平衡"], ["自动"]],
    "cb22": [["位深"], ["色带"], ["RAW"]],
    "cb23": [["主光源"], ["混合光"]],
    "cb24": [["偏振镜"], ["滤镜"]],
    "cb25": [["测光", "中灰"], ["测光表"]],
    "cb26": [["灰卡"], ["128"], ["18%"]],
    "cb27": [["高光"], ["动态范围"]],
    "cb28": [["饱和度", "亮度"], ["曝光", "色彩"]],
    "cb29": [["饱和度"], ["花哨"]],
    "cb30": [["剪影"], ["轮廓"]],
    "cb31": [["黑色背景"], ["微距"]],
    "cb32": [["背景", "主体"], ["鲜艳的背景"]],
    "cb33": [["填满"], ["背光"], ["雨后"]],
    "cb34": [["黄色通道"], ["可选颜色"], ["绿色", "黄色"]],
    "cb35": [["色调范围"], ["暗调"], ["亮调"]],
    "cb36": [["人像"], ["服装"], ["场景"]],
    "cb37": [["建筑材料"], ["地域"], ["气候"]],
    "cb38": [["红色"], ["侵略性"], ["竞争"]],
}

SPLIT = re.compile(r"(?<=[。！？；])")


def load_pages(book_md: Path) -> list[tuple[str, str]]:
    pages, cur, buf = [], None, []
    for line in book_md.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^## (p\d+)$", line.strip())
        if m:
            if cur:
                pages.append((cur, "\n".join(buf)))
            cur, buf = m.group(1), []
        elif cur:
            buf.append(line)
    if cur:
        pages.append((cur, "\n".join(buf)))
    return pages


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python tools/find_quotes.py books/<slug> [id ...]")
        return 2
    book = ROOT / sys.argv[1] / "source" / "book.md"
    only = set(sys.argv[2:])
    pages = load_pages(book)

    sents: list[tuple[str, str]] = []
    for pid, txt in pages:
        flat = re.sub(r"\s+", "", txt)
        flat = re.sub(r"\[[a-z_]+\]|!\[[^\]]*\]\([^)]*\)|\*图注\*：", "", flat)
        for s in SPLIT.split(flat):
            s = s.strip()
            if 18 <= len(s) <= 150:
                sents.append((pid, s))

    for cid, groups in WANT.items():
        if only and cid not in only:
            continue
        print(f"\n### {cid}")
        shown = 0
        for grp in groups:
            for pid, s in sents:
                if all(k in s for k in grp):
                    print(f"  {pid} [{len(s)}] {s}")
                    shown += 1
                    if shown >= 4:
                        break
            if shown >= 4:
                break
        if shown == 0:
            print("  （无候选）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

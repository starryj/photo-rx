"""给七张卡的 B 段插入一段「三种东西」的读法说明。

背景：反证闸 30 条里两条失败都是误拦，病因是「不在以下情况使用」「作者警告的失败模式」
「盲点与局限」三个小节并列且格式相近，读者把后两者也当成了拒绝请求的理由。
这里在 B 段标题下加一段统一说明，明确三者作用不同。幂等：已插过就跳过。
"""
from __future__ import annotations

import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / ".cangjie" / "capabilities" / "cards"

HEAD = "## B — 边界 (Boundary) ★"

NOTE = """
> **这一段里有三种东西，作用不同，别混：**
> ① **「不要在以下情况使用」＝不接这张活**——转给指定的卡，或在回答里声明不做。
> ② **「作者警告的失败模式」＝这张卡被用错时的症状**——用来检查自己的输出，**不是拒绝请求的理由**。
> ③ **「盲点与时代局限」＝降低置信度并写进回答**——同样**不是拒绝的理由**；它要求的是声明前提，不是推掉任务。
"""


def main() -> None:
    n = 0
    for p in sorted(CARDS.glob("*.md")):
        s = io.open(p, encoding="utf-8").read()
        if "这一段里有三种东西" in s:
            continue
        if HEAD not in s:
            print("跳过（无 B 段标题）:", p.name)
            continue
        s = s.replace(HEAD, HEAD + "\n" + NOTE, 1)
        io.open(p, "w", encoding="utf-8").write(s)
        n += 1
        print("已插入:", p.name)
    print("共 %d 张" % n)


if __name__ == "__main__":
    main()

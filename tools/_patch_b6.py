# -*- coding: utf-8 -*-
"""给 parse_books.py 加 BATCH6（郭熙《林泉高致》），并让 --batch 走字典映射。"""
from pathlib import Path

P = Path("tools/parse_books.py")
s = P.read_text(encoding="utf-8")

if "BATCH6" not in s:
    anchor = "BATCH2 = [\n    (\"freeman-sight\", \"摄影师的视界\"),\n    (\"freeman-light\", \"光线与用光\"),\n]\n"
    assert anchor in s
    add = anchor + """
BATCH6 = [
    ("linquan-gaozhi", "林泉高致"),
]
"""
    s = s.replace(anchor, add, 1)

# pool 选择：无论原先写成什么表达式，统一换成字典
import re
m = re.search(r"\n(\s*)pool = .*\n", s)
assert m, "未找到 pool 赋值"
indent = m.group(1)
s = s[: m.start()] + f"\n{indent}pool = {{1: BATCH1, 2: BATCH2, 3: BATCH3, 4: BATCH4, 6: BATCH6}}[a.batch]\n" + s[m.end():]

P.write_text(s, encoding="utf-8")
print("patched")
for line in P.read_text(encoding="utf-8").splitlines():
    if "pool =" in line or "BATCH6" in line:
        print("  ", line.strip())

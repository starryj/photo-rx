# -*- coding: utf-8 -*-
"""把视觉服务缓存 bug 的修法写进 needs-review（并清掉一处误写入的控制字符）。"""
from pathlib import Path

P = Path("needs-review.md")
t = P.read_text(encoding="utf-8")

old = "**这是服务端该修的 bug**（`text` 为空时不应写缓存），未改；"
new = ("**这是服务端该修的 bug**（`text` 为空时不应写缓存）——**已于 2026-11-24 修好**："
       "`app/main.py` 里 `force` 改为跳过缓存读、空 `text` 不写缓存；存量 39 条空条目已清扫；"
       "回归测试 `G:\\AI_Workspace\\06-VisionService\\tests\\test_cache_guard.py`"
       "（T1 force 必须真算 / T3 非 force 应命中 / T4 缓存无空条目）全部通过；")
assert old in t, "未找到原文"
t = t.replace(old, new, 1)

before = t.count("\x08")
t = t.replace("\x08", "")
print("cleaned control chars:", before)
P.write_text(t, encoding="utf-8")
print("ok, len", len(t))

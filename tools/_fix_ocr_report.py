# -*- coding: utf-8 -*-
"""把报告里「空结果缓存待修」改成「已修 + 回归测试」。"""
from pathlib import Path

P = Path("out/ocr-sample/report.md")
t = P.read_text(encoding="utf-8")

old = "① 视觉服务的「空结果缓存」应该在服务端修（`policy`/`store` 层：`text` 为空时不写缓存），否则任何复用都会踩；"
new = ("① 视觉服务的「空结果缓存」**已于 2026-11-24 修好**：`app/main.py` 的 `force` 现在真的跳过缓存读、"
       "空 `text` 不再写缓存；存量 39 条空条目已清扫；回归测试 "
       "`G:\\AI_Workspace\\06-VisionService\\tests\\test_cache_guard.py` 四项全过"
       "（T1 force 两次都真算 47.8 s / 136.8 s、T3 复用 51 ms 命中、T4 缓存 0 条空文本）；")
assert old in t, "未找到原文"
P.write_text(t.replace(old, new, 1), encoding="utf-8")
print("ok")

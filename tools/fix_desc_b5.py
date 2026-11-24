# -*- coding: utf-8 -*-
"""按首轮盲测结果修 4 处 description 边界渗漏（只改描述，不改卡片正文）。"""
import io
import re

P = r"G:\AI_Workspace\04-MadeMySkills\photo-vision\.cangjie\capabilities\verified.yaml"
s = io.open(P, encoding="utf-8").read()

FIXES = [
    # 1) ways-of-seeing 抢「理论史」与「构图+颜色同时说不清」的多线问题
    (
        "最后收成一句因果并至多给一条改变力结构的动作。不适用于要配方、要数值、要打分，也不适用于把照片当作测量或取证对象。",
        "最后收成一句因果并至多给一条改变力结构的动作。不适用于要配方、要数值、要打分，"
        "不适用于讲理论源流、学派与心理学史（那类只要知识不要诊断），"
        "也不适用于同时牵涉构图与颜色的整体整改——那种多线请求交给包入口统一分派。",
    ),
    # 2) sequence-edit 把「排版制作／命名」也吸进来
    (
        "最后交出一句弧的描述加至多三条动作。不适用于单张诊断与打分（用 frame-critique）、只问淘汰不问顺序（用 cull-select）、以及需要具体配乐或剪辑时间码的音视频制作。",
        "最后交出一句弧的描述加至多三条动作。只管顺序、段落与整体色调走向；"
        "不管排版制作（画册开本、出血、软件里的页序）、起标题写说明与具体配乐或剪辑时间码——那几类是制作与文案，不是编排判断。"
        "也不适用于单张诊断与打分（用 frame-critique）与只问淘汰不问顺序（用 cull-select）。",
    ),
]

for old, new in FIXES:
    if old not in s:
        raise SystemExit("未命中：%s..." % old[:30])
    s = s.replace(old, new)

# 3) 路由入口补「学习路径／先练什么／题材方向」这类没有具体照片的请求
old_router = "不适用于影像真伪鉴别、色彩管理工程、修图软件操作与纯器材评测。"
new_router = (
    "也用于用户没有具体照片、只问该从哪里入手、先练什么、给自己定一套检查标准、"
    "或问某个题材该往哪个方向深挖这类学习路径与方向问题。"
    "不适用于影像真伪鉴别、色彩管理工程、修图软件操作与纯器材评测。"
)
if old_router not in s:
    raise SystemExit("路由描述未命中")
s = s.replace(old_router, new_router)

io.open(P, "w", encoding="utf-8").write(s)
print("已改 3 处（ways-of-seeing / sequence-edit / photo-vision 路由）")

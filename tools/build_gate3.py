# -*- coding: utf-8 -*-
"""Build round-3 counter-gate cases (30 new, non-overlapping with rounds 1-2)."""
import json
from pathlib import Path

CASES = [
    # chinese-eye
    ("ce-21", "chinese-eye", "block", "这张手表产品图要绝对横平竖直，你帮我按三远重新构图。", "禁用：精确几何 → structure-read"),
    ("ce-22", "chinese-eye", "block", "这片红叶和青瓦的面积比例怎么调才稳？", "禁用：色彩关系与面积 → color-decision"),
    ("ce-23", "chinese-eye", "pass", "这张黄山云海，山只露一角，大片空，为什么反而站得住？", "正文：留白与虚实承重"),
    ("ce-24", "chinese-eye", "pass", "拍苏州园林的月洞门，我想让门外景致像画一样被框住，从哪看？", "正文：框景与游观"),
    # color-decision
    ("cd-21", "color-decision", "block", "帮我写个校色流程，显示器、打印机、ICC 都要。", "禁用：色彩管理流程"),
    ("cd-22", "color-decision", "block", "这张照片构图是不是太散了？", "禁用：内容/结构，不拿色彩替内容辩护"),
    ("cd-23", "color-decision", "pass", "胡同灰墙前一辆明黄共享单车，黄占得很小，为什么还是先看到它？", "正文：色彩强调与小面积"),
    ("cd-24", "color-decision", "pass", "夜景里霓虹的蓝紫和路灯的橙黄挤在一起，显得脏，是冷暖问题还是饱和度问题？", "正文：冷暖与同时对比"),
    # cull-select
    ("cs-21", "cull-select", "block", "就这一张，帮我看看天空要不要压暗。", "禁用：单张修改 → frame-critique"),
    ("cs-22", "cull-select", "block", "顺序我已经排好了，你只帮我把这组调成统一色调。", "禁用：已定留片只问调色 → sequence-edit/color-decision"),
    ("cs-23", "cull-select", "pass", "旅行回来 400 张，想挑 25 张做一本小册子，怎么下手？", "正文：大批量初筛"),
    ("cs-24", "cull-select", "pass", "同一场景连拍 12 张，人物表情几乎一样，只留一张，怎么选？", "正文：同组取舍"),
    # sequence-edit
    ("se-21", "sequence-edit", "block", "这张单张的构图哪里不对？", "禁用：单张诊断 → structure-read"),
    ("se-22", "sequence-edit", "block", "给这组照片配一段 30 秒的电子乐，卡点帮我标出来。", "禁用：音视频制作"),
    ("se-23", "sequence-edit", "pass", "12 张城市夜景，从傍晚到深夜，怎么排才能看出时间走？", "正文：时间弧"),
    ("se-24", "sequence-edit", "pass", "三张一组：空街、来人、人走，这样讲一个下午行不行？", "正文：最小叙事单位"),
    # shoot-plan
    ("sp-21", "shoot-plan", "block", "这张已经拍完了，你帮我评评分，看能打几分。", "禁用：事后诊断/打分 → frame-critique"),
    ("sp-22", "shoot-plan", "block", "这 30 张里帮我留 8 张。", "禁用：选片 → cull-select"),
    ("sp-23", "shoot-plan", "pass", "明天阴天，想去拍老街的骑楼，光很平，怎么计划？", "正文：平光计划"),
    ("sp-24", "shoot-plan", "pass", "海边日落，想把太阳放在画面边缘，什么时段、什么焦距合适？", "正文：时段与焦距"),
    # structure-read
    ("sr-21", "structure-read", "block", "这张白平衡偏绿，帮我调一下色温。", "禁用：纯色彩 → color-decision"),
    ("sr-22", "structure-read", "block", "给我这张照片一个综合评分和修改报告。", "禁用：打分 → frame-critique"),
    ("sr-23", "structure-read", "pass", "画面左边一堵墙很重，右边全空，怎么把重量挪过去？", "正文：平衡与重量"),
    ("sr-24", "structure-read", "pass", "地平线该放哪？我想让天显得很高。", "正文：分割与位置"),
    # ways-of-seeing
    ("ws-21", "ways-of-seeing", "block", "告诉我明天拍日出几点到、带什么镜头、参数多少。", "禁用：配方 → shoot-plan"),
    ("ws-22", "ways-of-seeing", "block", "给这张打个分，再说说为什么。", "禁用：打分 → frame-critique"),
    ("ws-23", "ways-of-seeing", "pass", "这组照片让我有点不安，但说不上来，是哪里在起作用？", "正文：机制解释"),
    ("ws-24", "ways-of-seeing", "pass", "同一场景，彩色那张很吵，黑白那张安静，为什么？", "正文：媒介与知觉"),
    # router
    ("pv-21", "photo-vision", "pass", "一张照片构图和色彩都有问题，我先改哪个？", "包级：跨线排序"),
    ("pv-22", "photo-vision", "pass", "我拍了三年，想系统检查自己的短板，从哪开始？", "包级：学习路径"),
]

out = Path("out/gate3")
out.mkdir(parents=True, exist_ok=True)
rows = [dict(zip(("id", "skill", "expect", "prompt", "note"), c)) for c in CASES]
(out / "cases.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", len(rows), "cases ->", out / "cases.json")

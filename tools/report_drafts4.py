# -*- coding: utf-8 -*-
"""报告版式第四轮：按十一手绘示意图出竖图 2 版 + 横图 2 版。

用法：python tools/report_drafts4.py
输出：out/analysis/dsc-7326/draft-j.html、draft-k.html
      out/analysis/blue-hour-village-v2/draft-l.html、draft-m.html
数据只来自各目录的 measure.json 与 judgement.json。
"""
import base64
import io
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SERIF = "'Songti SC','Source Han Serif SC','Noto Serif SC',SimSun,serif"
SANS = "'Helvetica Neue','Inter','Helvetica',Arial,'PingFang SC','Microsoft YaHei',sans-serif"
MONO = "'SF Mono',Consolas,'Roboto Mono',monospace"
INK = "#1b1a17"
RED = "#b02a19"
TEAL = "#123f4a"
MAXD = {"陈述": 18, "骨架": 22, "力": 15, "光": 15, "色": 20, "完成度": 10}


def b64(im, quality=88):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def load(path, width):
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    return im


def sample(src, box):
    w, h = src.size
    patch = src.crop((int(box[0] * w), int(box[1] * h),
                      max(int(box[2] * w), int(box[0] * w) + 1),
                      max(int(box[3] * h), int(box[1] * h) + 1)))
    return "#%02x%02x%02x" % patch.resize((1, 1), Image.BOX).getpixel((0, 0))


def marks_html(marks):
    """marks: (kind, ...)  tag=(x,y,label) ellipse=(x,y,w,h,label) rule=(x,y,w,label)"""
    out = []
    for mk in marks:
        kind, label = mk[0], mk[-1]
        if kind == "tag":
            x, y = mk[1], mk[2]
            out.append(f'<div class="mk" style="left:{x}%;top:{y}%">{label}</div>')
        elif kind == "ellipse":
            x, y, w, h = mk[1], mk[2], mk[3], mk[4]
            out.append(f'<div class="el" style="left:{x}%;top:{y}%;width:{w}%;height:{h}%"></div>'
                       f'<div class="mk" style="left:{x + w * 0.3}%;top:{max(0, y - 6)}%">{label}</div>')
        elif kind == "rule":
            x, y, w = mk[1], mk[2], mk[3]
            out.append(f'<div class="rl" style="left:{x}%;top:{y}%;width:{w}%"></div>'
                       f'<div class="mk" style="left:{x + 2}%;top:{y + 1.2}%">{label}</div>')
    return "".join(out)


def dims_rows(d, with_see=True):
    rows = []
    for x in d["j"]["dims"]:
        mx = MAXD[x["name"]]
        rows.append(
            f'<div class="dim"><div class="dh"><span class="dn">{x["name"]}</span>'
            f'<span class="db"><i style="width:{100 * x["score"] / mx:.0f}%"></i></span>'
            f'<span class="dv">{x["score"]}<s> / {mx}</s></span></div>'
            + (f'<div class="dl"><b>看得出</b>{x["see"]}</div>' if with_see else "")
            + f'<div class="dl"><b>证据</b>{x["evidence"]}</div></div>')
    return "".join(rows)


def verdict_block(title, en, items):
    """亮点／不足：悬挂小号数码 + 文字自成一行，换行缩进对齐文字而非数字。"""
    lis = "".join(f"<li><i>{k:02d}</i><x>{t}</x></li>" for k, t in enumerate(items, 1))
    return (f'<section class="vd"><div class="vdh"><b>{title}</b><s>{en}</s></div>'
            f'<ol class="vl">{lis}</ol></section>')


def dims_brief(d):
    return "".join(
        f'<div class="db2"><span class="dn">{x["name"]}</span>'
        f'<span class="db"><i style="width:{100 * x["score"] / MAXD[x["name"]]:.0f}%"></i></span>'
        f'<span class="dv">{x["score"]}<s>/{MAXD[x["name"]]}</s></span></div>'
        for x in d["j"]["dims"])


def swatch_strip(sw, cls="strip"):
    return (f'<div class="{cls}">'
            + "".join(f'<div style="background:{c}"><b>{n}</b>{c}</div>' for n, c in sw)
            + "</div>")


BASE_CSS = """
.fig{position:relative;overflow:hidden}
.fig .mk{position:absolute;background:rgba(20,20,18,.86);color:#fff;font:600 11px/1 sans-serif;
 letter-spacing:.04em;padding:5px 8px;white-space:nowrap;z-index:2}
.fig .el{position:absolute;border:2px dashed #f0c33c;border-radius:50%;z-index:1}
.fig .rl{position:absolute;height:2px;background:#b02a19;z-index:1}
.dim{margin:0 0 16px}
.dh{display:flex;align-items:center;gap:10px}
.dn{flex:0 0 54px;font:600 12px/1 sans-serif;letter-spacing:.06em}
.db{flex:1;height:7px;background:#eeeae2;display:block;position:relative}
.db i{position:absolute;left:0;top:0;height:100%;background:#b02a19;display:block}
.dv{flex:0 0 62px;text-align:right;font:600 15px/1 sans-serif}
.dv s{text-decoration:none;font:400 11px/1 sans-serif;color:#9a938a}
.dl{margin-top:5px;font:400 12px/1.7 sans-serif;color:#4a453f}
.dl b{display:inline-block;font:600 10px/1 sans-serif;letter-spacing:.08em;color:#9a938a;
 margin-right:8px;vertical-align:1px}
.strip{display:flex}
.strip div{flex:1;padding:9px 10px 10px;color:#fff;font:500 9px/1.45 sans-serif}
.strip b{display:block;font:600 11.5px/1.5 sans-serif;letter-spacing:.02em}
.quote{margin-top:26px;display:grid;grid-template-columns:1fr 280px;gap:30px;
 border-top:1px solid #ded8cd;padding-top:16px}
.quote p{margin:0;font:400 17px/1.85 serif;color:#2b2723}
.quote p b{color:#b02a19;font-weight:600}
.quote .side{font:400 10.5px/1.8 sans-serif;color:#7b7670;border-left:2px solid #b02a19;padding-left:13px}
.kick{margin-top:24px;border-top:2px solid #1b1a17;padding-top:14px;display:flex;gap:16px;align-items:baseline}
.kick s{text-decoration:none;font:600 10.5px/1 sans-serif;letter-spacing:.16em;color:#b02a19}
.kick p{margin:0;font:600 26px/1.4 serif;letter-spacing:.01em}
.foot{margin-top:16px;font:400 9.5px/1.8 sans-serif;color:#a39c92}
"""


def style_common():
    return (BASE_CSS.replace("sans-serif", SANS).replace(" serif", " " + SERIF))


def build_portrait(d, variant="j"):
    j, m = d["j"], d["m"]
    total = sum(x["score"] for x in j["dims"])
    photo = b64(d["img"])
    sw = d["sw"]
    band_title = d["band"]
    meta = d["meta"]
    hl = "".join(f"<li>{t}</li>" for t in j["highlights"])
    fl = "".join(f"<li>{t}</li>" for t in j["flaws"])
    props = "".join(
        f'<div class="pr"><s>{i + 1:02d}</s><p>{c["text"]}<br><em>{c["dims"]}</em></p></div>'
        for i, c in enumerate(j["changes"]))
    quote_side = d["quote_side"]
    if variant == "j":
        verdict_html = (verdict_block("亮点", "WHAT WORKS", j["highlights"])
                        + verdict_block("不足", "WHERE IT FAILS", j["flaws"]))
    else:
        verdict_html = (f'<div class="lists">'
                        f'<div class="lst"><h4>亮点</h4><ol>{hl}</ol></div>'
                        f'<div class="lst"><h4>不足</h4><ol>{fl}</ol></div></div>')

    if variant == "j":  # 照示意图：方正、框线、直白
        css = """
*{box-sizing:border-box}
body{margin:0;background:#eceae5;color:#1b1a17;font-family:__SANS__}
.pg{width:1040px;margin:0 auto;background:#fff}
.band{background:#123f4a;color:#fff;padding:22px 34px;display:flex;justify-content:space-between;align-items:baseline}
.band b{font:600 21px/1.3 __SANS__;letter-spacing:.04em}
.band span{font:400 11px/1.4 __MONO__;color:#a9c6cc}
.body{padding:24px 34px 26px}
.top{display:grid;grid-template-columns:1fr 366px;gap:26px}
.score b{font:700 66px/1 __SANS__;letter-spacing:-.03em}
.score s{text-decoration:none;font:400 14px/1 __SANS__;color:#8d8780;margin-left:8px}
.score p{margin:6px 0 0;font:400 11.5px/1.7 __SANS__;color:#6f6a63}
.vd{border-top:2px solid #1b1a17;padding-top:11px;margin-top:22px}
.vdh{display:flex;align-items:baseline;gap:10px;margin:0 0 10px}
.vdh b{font:600 14px/1 __SANS__;letter-spacing:.18em;color:#1b1a17}
.vdh s{text-decoration:none;font:400 9px/1 __MONO__;letter-spacing:.22em;color:#a89f93}
.vl{margin:0;padding:0;list-style:none}
.vl li{display:flex;gap:9px;align-items:baseline;margin:0 0 9px}
.vl li:last-child{margin-bottom:0}
.vl i{flex:0 0 16px;font:400 10px/1.95 __MONO__;font-variant-numeric:tabular-nums;color:#b02a19}
.vl x{flex:1;font:400 12.4px/1.95 __SANS__;color:#2e2a25}
.dom{margin:16px 0 2px;font:400 12.2px/1.9 __SANS__;color:#3d3833;border-left:3px solid #b02a19;padding-left:13px}
.sec{margin-top:24px}
.sec h3{font:600 11px/1 __SANS__;letter-spacing:.18em;color:#6f6a63;
 border-bottom:1px solid #ded8cd;padding-bottom:7px;margin:0 0 14px}
.sec h3 s{text-decoration:none;float:right;font-weight:400;letter-spacing:0;color:#a39c92}
.prop{display:grid;grid-template-columns:1fr 1fr 1fr;gap:22px}
.pr s{text-decoration:none;display:block;font:600 13px/1 __SERIF__;color:#b02a19;margin-bottom:6px}
.pr p{margin:0;font:400 12px/1.8 __SANS__;color:#4a453f}
.pr em{font-style:normal;color:#9a938a;font-size:11px}
"""
    else:  # K：同一骨架，去掉重框，换排印
        css = """
*{box-sizing:border-box}
body{margin:0;background:#f4f2ed;color:#1b1a17;font-family:__SANS__}
.pg{width:1040px;margin:0 auto;background:#fbfaf7;padding:0 0 30px}
.band{padding:18px 40px 14px;display:flex;justify-content:space-between;align-items:baseline;
 background:#123f4a;color:#fff}
.band b{font:600 19px/1.3 __SERIF__;letter-spacing:.06em}
.band span{font:400 10.5px/1.4 __MONO__;color:#a9c6cc;letter-spacing:.04em}
.body{padding:26px 40px 0}
.top{display:grid;grid-template-columns:1fr 356px;gap:32px}
.score b{font:400 72px/1 __SERIF__;letter-spacing:-.02em}
.score s{text-decoration:none;font:400 13px/1 __SANS__;color:#8d8780;margin-left:10px}
.score p{margin:8px 0 0;font:400 11.5px/1.75 __SANS__;color:#6f6a63}
.lists{margin-top:22px}
.lst{padding:12px 0;border-top:1px solid #ded8cd}
.lst h4{margin:0 0 7px;font:600 10.5px/1 __SANS__;letter-spacing:.2em;color:#9a938a}
.lst ol{margin:0;padding:0;list-style:none;counter-reset:n}
.lst li{counter-increment:n;font:400 12.5px/1.8 __SANS__;color:#332e28;padding-left:20px;position:relative;margin:4px 0}
.lst li:before{content:counter(n)".";position:absolute;left:0;color:#b02a19;font-weight:600}
.dom{margin:14px 0 0;font:400 11.5px/1.85 __SANS__;color:#4a453f;border-left:2px solid #b02a19;padding-left:12px}
.sec{margin-top:26px}
.sec h3{font:600 10.5px/1 __SANS__;letter-spacing:.2em;color:#9a938a;
 padding-bottom:8px;margin:0 0 12px;border-bottom:1px solid #ded8cd}
.sec h3 s{text-decoration:none;float:right;font-weight:400;letter-spacing:0;color:#b3aba0}
.prop{display:grid;grid-template-columns:1fr 1fr 1fr;gap:26px}
.pr s{text-decoration:none;display:block;font:400 15px/1 __SERIF__;color:#b02a19;margin-bottom:8px}
.pr p{margin:0;font:400 12px/1.85 __SANS__;color:#4a453f}
.pr em{font-style:normal;color:#9a938a;font-size:11px}
"""

    return f"""<!doctype html><meta charset="utf-8"><title>{d['slug']}-{variant}</title>
<style>{style_common()}{css.replace('__SANS__', SANS).replace('__SERIF__', SERIF).replace('__MONO__', MONO)}
.fig img{{width:100%;display:block}}</style>
<div class="pg">
 <div class="band"><b>{band_title}</b><span>{meta}</span></div>
 <div class="body">
  <div class="top">
   <div>
    <div class="fig"><img src="{photo}">{marks_html(d['marks'])}</div>
    {swatch_strip(sw)}
   </div>
   <div class="score">
    <b>{total}</b><s>综合 / 100</s>
    <p>西式六维　加权 {total}　区间 {total - 3}–{total + 3}　无硬缺陷封顶</p>
    <p class="dom">{d['dominant']}</p>
    {verdict_html}
   </div>
  </div>

  <div class="sec"><h3>六维<s>看得出 · 证据</s></h3>{dims_rows(d)}</div>
  <div class="sec"><h3>两条提议<s>按代价排序</s></h3>
   <div class="prop">{props}
    <div class="pr"><s>不动</s><p>{j['no_change']}<br><em>改了就不是这张了</em></p></div>
   </div></div>

  <div class="quote"><p>{d['quote']}</p><div class="side">{quote_side}</div></div>
  <div class="kick"><s>结论</s><p>{d['kicker']}</p></div>
  <div class="foot">{d['foot']}</div>
 </div>
</div>"""


def build_landscape(d, variant="l"):
    j = d["j"]
    total = sum(x["score"] for x in j["dims"])
    photo = b64(d["img"])
    sw = d["sw"]
    hl = "".join(f"<li>{t}</li>" for t in j["highlights"])
    fl = "".join(f"<li>{t}</li>" for t in j["flaws"])
    props = "".join(
        f'<div class="pr"><s>{i + 1:02d}</s><p>{c["text"]}<br><em>{c["dims"]}</em></p></div>'
        for i, c in enumerate(j["changes"]))

    if variant == "l":  # 横图 A：顶部通栏头 + 整幅横图 + 下两栏
        css = """
*{box-sizing:border-box}
body{margin:0;background:#e9e7e2;color:#1b1a17;font-family:__SANS__}
.pg{width:1240px;margin:0 auto;background:#fff}
.band{background:#123f4a;color:#fff;padding:20px 36px;display:flex;justify-content:space-between;align-items:baseline}
.band b{font:600 20px/1.3 __SANS__;letter-spacing:.05em}
.band span{font:400 11px/1.4 __MONO__;color:#a9c6cc}
.body{padding:22px 36px 26px}
.hero{position:relative}
.hero img{width:100%;display:block}
.under{display:grid;grid-template-columns:1fr 372px;gap:30px;margin-top:22px}
.score b{font:700 62px/1 __SANS__;letter-spacing:-.03em}
.score s{text-decoration:none;font:400 13px/1 __SANS__;color:#8d8780;margin-left:8px}
.score p{margin:6px 0 0;font:400 11.5px/1.7 __SANS__;color:#6f6a63}
.vd{border-top:2px solid #1b1a17;padding-top:10px;margin-top:20px}
.vdh{display:flex;align-items:baseline;gap:10px;margin:0 0 9px}
.vdh b{font:600 13.5px/1 __SANS__;letter-spacing:.18em;color:#1b1a17}
.vdh s{text-decoration:none;font:400 9px/1 __MONO__;letter-spacing:.22em;color:#a89f93}
.vl{margin:0;padding:0;list-style:none}
.vl li{display:flex;gap:8px;align-items:baseline;margin:0 0 8px}
.vl li:last-child{margin-bottom:0}
.vl i{flex:0 0 15px;font:400 9.5px/1.95 __MONO__;font-variant-numeric:tabular-nums;color:#b02a19}
.vl x{flex:1;font:400 12px/1.95 __SANS__;color:#2e2a25}
.sec{margin-top:22px}
.sec h3{font:600 10.5px/1 __SANS__;letter-spacing:.18em;color:#6f6a63;
 border-bottom:1px solid #ded8cd;padding-bottom:7px;margin:0 0 12px}
.prop{display:grid;grid-template-columns:1fr 1fr 1fr;gap:22px}
.pr s{text-decoration:none;display:block;font:600 13px/1 __SERIF__;color:#b02a19;margin-bottom:5px}
.pr p{margin:0;font:400 11.5px/1.8 __SANS__;color:#4a453f}
.pr em{font-style:normal;color:#9a938a;font-size:10.5px}
"""
        hero = (f'<div class="hero fig"><img src="{photo}">{marks_html(d["marks"])}</div>')
        layout = f"""
  {hero}
  {swatch_strip(sw)}
  <div class="under">
   <div class="sec" style="margin-top:0"><h3>六维 · 看得出 / 证据</h3>{dims_rows(d)}</div>
   <div>
    <div class="score"><b>{total}</b><s>综合 / 100</s>
     <p>西式六维　加权 {total}　区间 {total - 3}–{total + 3}</p></div>
    {verdict_block("亮点", "WHAT WORKS", j["highlights"])}
    {verdict_block("不足", "WHERE IT FAILS", j["flaws"])}
   </div>
  </div>
  <div class="sec"><h3>两条提议</h3><div class="prop">{props}
    <div class="pr"><s>不动</s><p>{j['no_change']}<br><em>改了就不是这张了</em></p></div></div></div>
"""
    else:  # 横图 M：出血大图 + 图上叠分 + 亮点不足并排
        css = """
*{box-sizing:border-box}
body{margin:0;background:#f3f1ec;color:#1b1a17;font-family:__SANS__}
.pg{width:1240px;margin:0 auto;background:#fbfaf7;padding-bottom:28px}
.band{padding:22px 34px 14px;display:flex;justify-content:space-between;align-items:flex-end}
.band b{font:600 20px/1.3 __SERIF__;letter-spacing:.05em}
.band span{font:400 10.5px/1.4 __MONO__;color:#8d8780}
.hero{position:relative}
.hero img{width:100%;display:block}
.plate{position:absolute;left:0;bottom:0;background:#fff;padding:16px 24px 18px 34px}
.plate b{font:600 58px/1 __SANS__;letter-spacing:-.03em}
.plate s{text-decoration:none;font:400 12px/1 __SANS__;color:#8d8780;margin-left:8px}
.plate p{margin:4px 0 0;font:400 10.5px/1.6 __SANS__;color:#6f6a63}
.body{padding:0 34px}
.lists{display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:20px}
.lst{border-top:2px solid #1b1a17;padding-top:10px}
.lst h4{margin:0 0 6px;font:600 11px/1 __SANS__;letter-spacing:.2em;color:#6f6a63}
.lst ol{margin:0;padding:0;list-style:none;counter-reset:n}
.lst li{counter-increment:n;font:400 12px/1.8 __SANS__;color:#332e28;padding-left:18px;position:relative}
.lst li:before{content:counter(n)".";position:absolute;left:0;color:#b02a19;font-weight:600}
.dom{margin:14px 0 0;font:400 11.5px/1.85 __SANS__;color:#4a453f;border-left:2px solid #b02a19;padding-left:12px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:0 40px;margin-top:22px}
.sec h3{font:600 10.5px/1 __SANS__;letter-spacing:.18em;color:#6f6a63;
 border-bottom:1px solid #ded8cd;padding-bottom:7px;margin:0 0 12px}
.prop{display:grid;grid-template-columns:1fr 1fr 1fr;gap:22px;margin-top:8px}
.pr s{text-decoration:none;display:block;font:600 13px/1 __SERIF__;color:#b02a19;margin-bottom:5px}
.pr p{margin:0;font:400 11.5px/1.8 __SANS__;color:#4a453f}
.pr em{font-style:normal;color:#9a938a;font-size:10.5px}
"""
        layout = f"""
  <div class="hero fig"><img src="{photo}">{marks_html(d["marks"])}
   <div class="plate"><b>{total}</b><s>综合 / 100</s>
    <p>西式六维　加权 {total}　区间 {total - 3}–{total + 3}　无硬缺陷封顶</p></div></div>
  <div class="body">
   {swatch_strip(sw)}
   <div class="lists">
    <div class="lst"><h4>亮点</h4><ol>{hl}</ol></div>
    <div class="lst"><h4>不足</h4><ol>{fl}</ol></div>
   </div>
   <div class="grid2">
    <div class="sec" style="margin-top:0"><h3>六维 · 前三维</h3>{dims_rows({'j': {'dims': j['dims'][:3]}})}</div>
    <div class="sec" style="margin-top:0"><h3>六维 · 后三维</h3>{dims_rows({'j': {'dims': j['dims'][3:]}})}</div>
   </div>
   <div class="sec" style="margin-top:24px"><h3>两条提议</h3><div class="prop">{props}
     <div class="pr"><s>不动</s><p>{j['no_change']}<br><em>改了就不是这张了</em></p></div></div></div>
"""
    return f"""<!doctype html><meta charset="utf-8"><title>{d['slug']}-{variant}</title>
<style>{style_common()}{css.replace('__SANS__', SANS).replace('__SERIF__', SERIF).replace('__MONO__', MONO)}
.quote p{{font-family:{SERIF}}}</style>
<div class="pg">
 <div class="band"><b>{d['band']}</b><span>{d['meta']}</span></div>
 <div class="body">{layout}
  <div class="quote"><p>{d['quote']}</p><div class="side">{d['quote_side']}</div></div>
  <div class="kick"><s>结论</s><p>{d['kicker']}</p></div>
  <div class="foot">{d['foot']}</div>
 </div>
</div>"""


DEFAULT_QUOTE = ("这张照片该用它的标准判断：一是「<b>内容和陈述</b>」——涉及照片中被人理解与识别的所有反应；"
                 "二是「<b>组织和结构</b>」——涉及画面的结构与色彩的设计。")
DEFAULT_QUOTE_SIDE = ("引自曼特《摄影构图与色彩设计》p013<br><br>"
                      "两条判断线并行，只在第二步才合流——先问「能不能被看见」，再问「这张照片值不值得看」。")
DEFAULT_FOOT = ("口径：西式六维 陈述 18 / 骨架 22 / 力 15 / 光 15 / 色 20 / 完成度 10。"
                "分数取整、数值照报；判断带误差，同批比较差 2 分以内算平手。"
                "数值来自 measure_photo.py，判断由 frame-critique 给出。")


def _load_source(p, m):
    cand = []
    path = (m.get("image") or {}).get("path")
    if path:
        cand.append(Path(path))
    cand += [p / "source.webp", p / "source.jpg", p / "source.png"]
    for c in cand:
        if c.exists():
            return c
    raise FileNotFoundError(f"{p} 下找不到源图（measure.json 的 image.path 或 source.*）")


def render_report(adir, variant=None):
    """measure.json + judgement.json -> report.html（按画幅自动选 J 竖 / L 横）。"""
    p = Path(adir)
    m = json.loads((p / "measure.json").read_text(encoding="utf-8"))
    j = json.loads((p / "judgement.json").read_text(encoding="utf-8"))
    src_path = _load_source(p, m)
    w, h = m["image"]["px"]
    portrait = h >= w
    if variant is None:
        variant = "j" if portrait else "l"

    src = load(src_path, 1600 if portrait else 3840)
    big = load(src_path, 1100 if portrait else 1240)
    sw = [(s["name"], sample(src, tuple(s["box"]))) for s in j.get("swatches", [])]
    marks = [tuple(x) for x in j.get("marks", [])]

    d = {
        "slug": p.name, "m": m, "j": j, "img": big, "src": src,
        "dominant": j["dominant"],
        "sw": sw,
        "band": j.get("band") or f"{j.get('eyebrow', p.name)} · 单张诊断",
        "meta": j.get("meta") or f"{w}×{h}·{'竖幅' if portrait else '横幅'}"
                                f" {round(max(w, h) / min(w, h), 2)}:1",
        "marks": marks,
        "quote": j.get("quote") or DEFAULT_QUOTE,
        "quote_side": j.get("quote_side") or DEFAULT_QUOTE_SIDE,
        "kicker": j.get("kicker") or j.get("headline", ""),
        "foot": j.get("foot") or DEFAULT_FOOT,
    }
    html = build_portrait(d, variant) if portrait else build_landscape(d, variant)
    out = p / "report.html"
    out.write_text(html, encoding="utf-8")
    return out, variant


def main():
    # ---------- 竖图：DSC_7326 ----------
    p = ROOT / "out/analysis/dsc-7326"
    m = json.loads((p / "measure.json").read_text(encoding="utf-8"))
    j = json.loads((p / "judgement.json").read_text(encoding="utf-8"))
    src = load(p / "source.webp", 1600)
    big = load(p / "source.webp", 1100)
    SW = [("天空蓝", (0.00, 0.00, 1.00, 0.07)), ("叶橙", (0.66, 0.55, 0.84, 0.65)),
          ("树皮", (0.44, 0.42, 0.56, 0.58)), ("叶绿", (0.05, 0.55, 0.25, 0.72)),
          ("底色", (0.00, 0.93, 1.00, 1.00))]
    portrait = {
        "slug": "dsc-7326", "m": m, "j": j, "img": big, "src": src,
        "dominant": j["dominant"],
        "sw": [(n, sample(src, b)) for n, b in SW],
        "band": "逆光秋树 · 单张诊断",
        "meta": "DSC_7326　1600×2404　竖幅 2:3",
        "marks": [
            ("rule", 0, 3.5, 100, "树冠切边"),
            ("rule", 0, 92.5, 100, "树根出画"),
            ("ellipse", 71, 4, 25, 15, "空亮点 8.8%"),
        ],
        "quote": "评价照片好坏的标准有二：一是「<b>内容和陈述</b>」，涉及到照片中包含的理性认识和情感反应；"
                 "二是「<b>组织的质量</b>」，涉及到画面的结构和色彩设计。",
        "quote_side": "哈拉尔德·曼特 ·《摄影构图与色彩设计》p013<br><br>"
                      "本包所有分与改，只在第二条上生效：判「画面能不能被读懂」，不判「这张照片值不值得拍」。",
        "kicker": "不缺颜色，缺一次偏心——把框往下挪，或把右边那块空收掉。",
        "foot": "口径：西式六维 陈述 18 / 骨架 22 / 力 15 / 光 15 / 色 20 / 完成度 10；"
                "分数取区间中值，同批比较差 2 分不判高下。数值来自 measure_photo.py，判断带容差。",
    }
    for v in ("j", "k"):
        out = p / f"draft-{v}.html"
        out.write_text(build_portrait(portrait, v), encoding="utf-8")
        print(out)

    # ---------- 横图：蓝调雪村 ----------
    q = ROOT / "out/analysis/blue-hour-village-v2"
    m2 = json.loads((q / "measure.json").read_text(encoding="utf-8"))
    j2 = json.loads((q / "judgement.json").read_text(encoding="utf-8"))
    src2 = load(Path(m2["image"]["path"]), 3840)
    big2 = load(Path(m2["image"]["path"]), 1240)
    SW2 = [("天空蓝", (0.32, 0.02, 0.62, 0.08)), ("霞光", (0.70, 0.10, 0.90, 0.20)),
           ("灯下暖池", (0.58, 0.58, 0.74, 0.72)), ("前景雪", (0.30, 0.86, 0.62, 0.97)),
           ("暗部蓝", (0.01, 0.52, 0.12, 0.66))]
    landscape = {
        "slug": "blue-hour-village", "m": m2, "j": j2, "img": big2, "src": src2,
        "dominant": j2["dominant"],
        "sw": [(n, sample(src2, b)) for n, b in SW2],
        "band": "蓝调雪村 · 单张诊断",
        "meta": "3840×2561　横幅 3:2　DSC_7326 同批",
        "marks": [
            ("ellipse", 44, 66, 22, 20, "灯下暖点 0.5%"),
            ("ellipse", 62, 4, 36, 24, "低对比平天 · 近四成画面"),
            ("tag", 5, 86, 0, 0, "前景雪坡压角"),
        ],
        "quote": "评价照片好坏的标准有二：一是「<b>内容和陈述</b>」，涉及到照片中包含的理性认识和情感反应；"
                 "二是「<b>组织的质量</b>」，涉及到画面的结构和色彩设计。",
        "quote_side": "哈拉尔德·曼特 ·《摄影构图与色彩设计》p013<br><br>"
                      "这张两条都在：有内容（黄昏里的村子与人），组织上靠色温分层成立。",
        "kicker": "这一片的命在那一小片暖上——把它做大，或者把右边那片平天收掉。",
        "foot": "口径：西式六维 陈述 18 / 骨架 22 / 力 15 / 光 15 / 色 20 / 完成度 10；"
                "分数取区间中值，同批比较差 2 分不判高下。数值来自 measure_photo.py，判断带容差。",
    }
    for v in ("l", "m"):
        out = q / f"draft-{v}.html"
        out.write_text(build_landscape(landscape, v), encoding="utf-8")
        print(out)


if __name__ == "__main__":
    main()



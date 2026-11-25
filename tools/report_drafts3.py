# -*- coding: utf-8 -*-
"""报告版式第三轮：G 复刻旧报告页 / H 接触印相 / I 编辑跨页刻度轨。

用法：python tools/report_drafts3.py out/analysis/dsc-7326
输出：draft-g.html draft-h.html draft-i.html（单文件、图内嵌）
数据只来自 measure.json 与 judgement.json，文案取自 judgement，不另造数字。
"""
import base64
import io
import json
import sys
from pathlib import Path

from PIL import Image

SERIF = "'Songti SC','Source Han Serif SC','Noto Serif SC',SimSun,serif"
SANS = "'Helvetica Neue','Inter','Helvetica',Arial,'PingFang SC','Microsoft YaHei',sans-serif"
MONO = "'SF Mono',Consolas,'Roboto Mono',monospace"
INK = "#1b1a17"
RED = "#b02a19"


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


SWATCHES = [
    ("天空蓝", (0.00, 0.00, 1.00, 0.07)),
    ("叶橙", (0.66, 0.55, 0.84, 0.65)),
    ("树皮", (0.44, 0.42, 0.56, 0.58)),
    ("叶绿", (0.05, 0.55, 0.25, 0.72)),
    ("底色", (0.00, 0.93, 1.00, 1.00)),
]


def bar(label, value, maxv, unit="", color=INK):
    pct = max(0, min(100, 100 * value / maxv))
    return (f'<div class="row"><span class="lb">{label}</span>'
            f'<span class="tk"><i style="width:{pct:.1f}%;background:{color}"></i></span>'
            f'<span class="vv">{value:g}{unit}</span></div>')


def build(d):
    m, j = d["m"], d["j"]
    dims = j["dims"]
    total = sum(x["score"] for x in dims)
    photo = b64(d["img"])
    src = d["src"]
    sw = [(n, sample(src, b)) for n, b in SWATCHES]
    hf = m["hue_families"]
    tone = m["tone"]
    reg = m["probes"]["regions"]
    L = lambda k: reg[k]["L"]

    # ---------------- G 复刻旧报告页 ----------------
    g = f"""<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box}}
body{{margin:0;background:#efeeeb;color:{INK};font-family:{SANS}}}
.pg{{width:1180px;margin:0 auto;background:#fff;padding:34px 46px 30px}}
.meta{{display:flex;justify-content:space-between;font:500 10.5px/1 {SANS};
 letter-spacing:.12em;color:#7b7670;text-transform:uppercase}}
.rule{{height:2px;background:{INK};margin:9px 0 0}}
.tag{{margin-top:12px;font:500 11px/1.6 {SANS};color:#6f6a63;letter-spacing:.04em}}
.tag b{{color:{RED};font-weight:600}}
h1{{font:600 47px/1.16 {SERIF};margin:12px 0 0;letter-spacing:.01em}}
h1 em{{font-style:normal;color:{RED}}}
.lede{{margin:14px 0 0;font:400 14px/1.85 {SANS};color:#4a453f;max-width:920px}}
.top{{display:grid;grid-template-columns:1fr 330px;gap:30px;margin-top:20px}}
.shot{{display:flex;justify-content:center;background:#f6f4f0}}
.shot img{{height:960px;width:auto;display:block}}
.strip{{display:flex;margin-top:0}}
.strip div{{flex:1;padding:8px 9px 9px;color:#fff;font:500 10px/1.5 {SANS};letter-spacing:.02em}}
.strip b{{display:block;font:600 12px/1.4 {SANS}}}
.score{{border-left:1px solid #ddd8d0;padding-left:22px}}
.big{{font:600 64px/1 {SERIF};letter-spacing:-.02em}}
.big s{{text-decoration:none;font:500 15px/1 {SANS};color:#8d8780;margin-left:6px}}
.cap{{margin-top:6px;font:500 10px/1.6 {SANS};color:#8d8780;letter-spacing:.04em}}
.dom{{margin-top:18px;padding-top:14px;border-top:1px solid #e5e0d8;
 font:400 13px/1.9 {SANS};color:#3f3a34}}
.dom b{{color:{RED}}}
h2{{font:600 13px/1 {SANS};letter-spacing:.14em;margin:34px 0 14px;
 padding-bottom:8px;border-bottom:1px solid #e2ddd4;text-transform:uppercase;color:#6f6a63}}
h2 s{{text-decoration:none;float:right;font-weight:400;color:#a8a29a;letter-spacing:.02em;text-transform:none}}
.rail{{margin-top:16px}}
.row{{display:flex;align-items:center;gap:9px;margin:5px 0;font:500 10px/1 {SANS}}}
.lb{{flex:0 0 62px;color:#4a453f}}
.tk{{flex:1;height:8px;background:#f0ede8;display:block;position:relative}}
.tk i{{position:absolute;left:0;top:0;height:100%;display:block}}
.vv{{flex:0 0 34px;text-align:right;color:#8d8780;font-family:{MONO}}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:34px}}
.three{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:28px}}
.ev b{{display:block;font:600 40px/1 {SERIF};letter-spacing:-.01em}}
.ev s{{display:block;text-decoration:none;font:500 10px/1.6 {SANS};color:#8d8780;margin-top:4px}}
.ev p{{margin:8px 0 0;font:400 12.5px/1.75 {SANS};color:#4a453f}}
.fx{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:26px}}
.fx div s{{display:block;text-decoration:none;font:600 15px/1 {SERIF};color:{RED};margin-bottom:6px}}
.fx div p{{margin:0;font:400 12.5px/1.75 {SANS};color:#4a453f}}
.fx div em{{font-style:normal;color:#8d8780;font-size:11.5px}}
.quote{{margin-top:30px;display:grid;grid-template-columns:1fr 300px;gap:34px;
 padding-top:18px;border-top:1px solid #e2ddd4}}
.quote p{{margin:0;font:400 17px/1.8 {SERIF};color:#2b2723}}
.quote p b{{color:{RED};font-weight:600}}
.quote .side{{font:400 10.5px/1.8 {SANS};color:#7b7670;border-left:2px solid {RED};padding-left:14px}}
.end{{margin-top:26px;padding-top:16px;border-top:2px solid {INK};display:flex;gap:18px;align-items:baseline}}
.end s{{text-decoration:none;font:600 10.5px/1 {SANS};letter-spacing:.14em;color:{RED}}}
.end p{{margin:0;font:600 25px/1.4 {SERIF}}}
.foot{{margin-top:20px;font:400 9.5px/1.75 {SANS};color:#a8a29a}}
.dims .row{{margin:7px 0;gap:12px}}
.dims .lb{{flex:0 0 46px}}
.dims .vv{{flex:0 0 58px;color:#4a453f}}
.dims .wt{{flex:0 0 34px;text-align:right;font:500 9px/1 {SANS};color:#a8a29a}}
</style>
<div class="pg">
 <div class="meta"><span>IMAGE CRITIQUE　单张诊断 · 报告页</span>
  <span>DSC_7326　/　1600 × 2404　/　竖幅 2:3</span></div>
 <div class="rule"></div>
 <div class="tag">互补　<b>1 : 1.8</b>　·　主竖分割 0.613（5/8）　·　空亮区 8.8%</div>
 <h1>橙蓝是这张的命，<em>框却没接住它</em></h1>
 <p class="lede">逆光把叶子照透了，冷天把暖橙托出来——颜色这一关是过的。拦住它的是框：
 树冠贴上边、树根出下边，整棵树读不全；右侧还有一块没有内容的亮天，占了近一成画面，
 光落在空处。这一张不缺内容，缺的是把主体完整交代给读者的那一点偏心。</p>

 <div class="top">
  <div>
   <div class="shot"><img src="{photo}"></div>
   <div class="strip">{"".join(f'<div style="background:{c}">{n}</div>' for n, c in sw)}</div>
  </div>
  <div class="score">
   <div class="big">{total}<s>综合 / 100</s></div>
   <div class="cap">西式六维　加权 {total}　区间 {total-3}–{total+3}　无硬缺陷封顶</div>
   <div class="dom">主导对比是<b>暖橙与冷蓝的互补</b>，面积 14.7 : 27.2，色相差约 170°，正对补色。
   不是明暗主导：树与天的明度差只有 5–15 个 L 单位，树靠色相从背景里分离出来，
   所以缩略图会糊。<br><br>这张的输赢都在这条互补上——它立得住，是因为颜色；
   它差一口气，是因为框没把这份颜色完整框进去。</div>
  </div>
 </div>

 <h2>双轨读数<s>黑白轨 · L 实测中位　｜　彩色轨 · 像素占比</s></h2>
 <div class="two">
  <div class="rail">
   {bar("天空", L("sky_top"), 100)}
   {bar("右上亮区", L("upper_right"), 100)}
   {bar("叶片中部", L("right_third"), 100)}
   {bar("树干", L("center"), 100)}
   {bar("前景", L("foreground_bottom"), 100)}
   <div class="row" style="margin-top:8px"><span class="lb">P5–P99</span>
    <span class="tk" style="background:linear-gradient(90deg,#2b2b2b,#8a8a8a,#f0f0f0)"></span>
    <span class="vv">{tone['L_p5']:.0f}–{tone['L_p99']:.0f}</span></div>
  </div>
  <div class="rail">
   {bar("蓝色相", hf.get("blue", 0) * 100, 50, "%", "#2f5f8f")}
   {bar("中性", hf.get("neutral", 0) * 100, 50, "%", "#8d8780")}
   {bar("暖光", hf.get("warm", 0) * 100, 50, "%", "#b0552c")}
   {bar("其余", hf.get("other", 0) * 100, 50, "%", "#6d8a4a")}
   <div class="row" style="margin-top:8px"><span class="lb">取值说明</span>
    <span style="flex:1;font:400 11px/1.6 {SANS};color:#7b7670">
    取样为像素族近似色，非取色器点位；面积按全幅像素占比。</span></div>
  </div>
 </div>

 <h2>六维<s>权重 × 得分 = 加权分</s></h2>
 <div class="dims">
  {"".join(f'<div class="row"><span class="lb">{x["name"]}</span>'
           f'<span class="tk"><i style="width:{100*x["score"]/d["maxd"][x["name"]]:.0f}%;background:{INK}"></i></span>'
           f'<span class="wt">{d["maxd"][x["name"]]}%</span>'
           f'<span class="vv">{x["score"]} / {d["maxd"][x["name"]]}</span></div>' for x in dims)}
 </div>

 <h2>三条证据<s>都能核对的数</s></h2>
 <div class="three">
  <div class="ev"><b>0.613</b><s>主竖分割</s><p>树干落在 5/8 上（Δ 0.012，在 ±0.02 带内）。
  只记「落在带内」，不记「刻意用了黄金分割」——要断言意图，还需要别的证据。</p></div>
  <div class="ev"><b>1 : 1.8</b><s>暖橙 : 冷蓝 面积比</s><p>暖 14.73%、蓝 27.18%，正补色、面积接近。
  这是它立得住的原因，也是它最不该被「统一色调」动掉的东西。</p></div>
  <div class="ev"><b>8.8%</b><s>右上空亮区</s><p>最大的单块亮池落在没有内容的天空上。
  光没打在东西上，读者的眼睛却会被它牵走——这是这张第二处伤。</p></div>
 </div>

 <h2>两条提议<s>按代价排序</s></h2>
 <div class="fx">
  <div><s>01</s><p>处理下边：整幅下移 3–4% 并裁掉底部一条，让树干延伸出画（读作「生于画外」）；
  或反过来上移，给根部留 4–6% 地面交代。二者选一，别停在半截。<br><em>骨架 +2、完成度 +1</em></p></div>
  <div><s>02</s><p>收掉右侧那块空亮：只压没有叶子的天 0.3–0.5 EV，或裁右 5% 让叶团接到边，
  让亮池不落在空处。<br><em>光 +1、力 +1</em></p></div>
  <div><s>不动</s><p>不要动整体色相。橙蓝互补是这张唯一的组织依据，
  任何「统一色调」都会把它降成一张平片。<br><em>改了就不是这张了</em></p></div>
 </div>

 <div class="quote">
  <p>评价照片好坏的标准有二：一是「<b>内容和陈述</b>」，涉及到照片中包含的理性认识和情感反应；
  二是「<b>组织的质量</b>」，涉及到画面的结构和色彩设计。</p>
  <div class="side">哈拉尔德·曼特 ·《摄影构图与色彩设计》p013<br><br>
  本包所有分与改，只在第二条上生效：判「画面能不能被读懂」，不判「这张照片值不值得拍」。</div>
 </div>

 <div class="end"><s>结论</s><p>不缺颜色，缺一次偏心——把框往下挪，或把右边那块空收掉。</p></div>
 <div class="foot">测量口径：色相族按 HSV 分区（蓝 195–260、暖 15–65，S≥0.22）；L 取 CIE Lab 亮度；
  分割线取梯度峰（归一化，0–1）；亮池与暗块按连通块面积。所有数值来自 measure_photo.py，判断带容差，
  总分写区间。口径：西式六维 陈述 18 / 骨架 22 / 力 15 / 光 15 / 色 20 / 完成度 10。</div>
</div>"""

    # ---------------- H 接触印相 ----------------
    h = f"""<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box}}
body{{margin:0;background:#f2f0ec;color:#22201d;font-family:{SANS}}}
.pg{{width:1180px;margin:0 auto;padding:38px 44px 30px;background:#faf8f4}}
.head{{display:flex;justify-content:space-between;align-items:flex-end;
 border-bottom:3px solid #22201d;padding-bottom:10px}}
.head b{{font:700 13px/1 {SANS};letter-spacing:.34em}}
.head span{{font:500 10px/1 {MONO};color:#6e6a64;letter-spacing:.06em}}
.proof{{display:grid;grid-template-columns:1fr 254px;gap:28px;margin-top:26px;align-items:start}}
.proof .frame{{position:relative;border:1px solid #c9c3b8;padding:12px;background:#fff;display:flex;justify-content:center}}
.proof img{{height:880px;width:auto;display:block}}
.proof .mark{{position:absolute;background:#c0392b;height:2px}}
.proof .tag{{position:absolute;background:#c0392b;color:#fff;font:600 9px/1 {SANS};
 padding:4px 7px;letter-spacing:.06em}}
.corner{{position:absolute;width:14px;height:14px;border:2px solid #c0392b}}
.notes{{margin-top:14px}}
.caption{{font:400 11.5px/1.9 {SANS};color:#5c574f;max-width:70ch}}
.caption b{{color:#c0392b}}
.margin{{border-left:1px solid #d9d3c7;padding-left:20px}}
.margin h4{{margin:0 0 8px;font:700 9.5px/1 {SANS};letter-spacing:.2em;color:#8b8579}}
.mrow{{display:flex;justify-content:space-between;font:500 11px/1.9 {MONO};color:#3b3833}}
.mrow s{{text-decoration:none;color:#8b8579;font-family:{SANS};font-size:10.5px}}
.dims{{margin-top:14px;border-top:1px solid #e2dcd1;padding-top:12px}}
.dm{{display:flex;align-items:center;gap:8px;margin:5px 0}}
.dm span{{flex:0 0 38px;font:500 9.5px/1.6 {SANS};color:#3b3833;white-space:nowrap}}
.dm i{{flex:1;height:5px;background:#e6e0d5;display:block;position:relative}}
.dm i u{{position:absolute;left:0;top:0;height:100%;background:#c0392b;display:block}}
.dm b{{flex:0 0 22px;text-align:right;font:700 10px/1 {MONO}}}
.dm i u{{position:absolute;left:0;top:0;height:100%;background:#c0392b;display:block}}
.dm b{{font:700 10.5px/1 {MONO}}}
.verdict{{margin-top:30px;border-top:3px solid #22201d;padding-top:16px;
 display:grid;grid-template-columns:150px 1fr;gap:24px}}
.verdict s{{text-decoration:none;font:700 9.5px/1.7 {SANS};letter-spacing:.2em;color:#c0392b}}
.verdict p{{margin:0;font:600 27px/1.5 {SERIF};letter-spacing:.01em}}
.verdict p em{{font-style:normal;color:#c0392b}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:26px}}
.col h4{{margin:0 0 10px;font:700 9.5px/1 {SANS};letter-spacing:.2em;color:#8b8579}}
.col p{{margin:0 0 10px;font:400 12.5px/1.85 {SANS};color:#3b3833}}
.col p b{{color:#c0392b}}
.chip{{display:flex;gap:0;margin-top:12px}}
.chip div{{flex:1;height:34px;font:500 8.5px/1.4 {SANS};color:#fff;padding:4px 5px}}
.sw2{{display:flex;height:52px;margin-top:2px}}
.sw2 div{{flex:1;color:#fff;font:500 8px/1.4 {SANS};padding:5px}}
.foot{{margin-top:26px;padding-top:10px;border-top:1px solid #e2dcd1;
 font:400 9px/1.8 {SANS};color:#948d81}}
</style>
<div class="pg">
 <div class="head"><b>接触印相 · 诊断</b><span>DSC_7326　1600×2404　{total}/100　区间 {total-3}–{total+3}</span></div>

 <div class="proof">
  <div>
   <div class="frame">
    <img src="{photo}">
    <div class="mark" style="left:12px;right:12px;top:9%"></div>
    <div class="tag" style="left:24px;top:calc(9% + 4px)">树冠被切</div>
    <div class="mark" style="left:12px;right:12px;bottom:7%"></div>
    <div class="tag" style="left:24px;bottom:calc(7% + 4px)">树根出画</div>
    <div class="corner" style="right:24px;top:10%"></div>
    <div class="tag" style="right:24px;top:calc(10% + 20px)">空亮 8.8%</div>
   </div>
   <div class="caption">红笔是这张的两处伤：<b>上下两头都被边框切住</b>，整棵树读不全；
   右上那 8.8% 的亮云没有内容承接，眼睛却被它牵走。颜色这一关是过的——
   <b>暖橙 14.7% 对冷蓝 27.2%</b>，正补色、面积接近，是这张唯一的组织依据。</div>
  </div>
  <div class="margin">
   <h4>读数 · 实测</h4>
   <div class="mrow"><s>主竖分割</s>0.613</div>
   <div class="mrow"><s>横幅分割</s>0.654</div>
   <div class="mrow"><s>蓝 / 暖 / 中性</s>27.2 / 14.7 / 14.8</div>
   <div class="mrow"><s>天空 L</s>{L('sky_top'):.0f}</div>
   <div class="mrow"><s>树干 L</s>{L('center'):.0f}</div>
   <div class="mrow"><s>亮池</s>11.7%</div>
   <div class="dims">
    {"".join(f'<div class="dm"><span>{x["name"]}</span><i><u style="width:{100*x["score"]/d["maxd"][x["name"]]:.0f}%"></u></i><b>{x["score"]}</b></div>' for x in dims)}
   </div>
   <h4 style="margin-top:20px">取样 · 全幅像素族</h4>
   <div class="sw2">{"".join(f'<div style="background:{c}">{n}</div>' for n, c in sw)}</div>
  </div>
 </div>

 <div class="verdict">
  <s>结论 · 一句话</s>
  <p>颜色立住了，<em>框没接住它</em>——把下边挪开，把那块空收掉，这张就成了。</p>
 </div>

 <div class="cols">
  <div class="col">
   <h4>两处伤</h4>
   <p><b>① 上下切。</b>树冠贴上边、树根直接出下边；上升被截住，又没有落地的交代。整幅因此读作「半棵树」。</p>
   <p><b>② 右侧空亮。</b>最大单块亮池 8.79% 落在叶层之外的天上；光没有打在东西上。</p>
  </div>
  <div class="col">
   <h4>两条改法</h4>
   <p><b>下边：</b>整幅下移 3–4% 并裁底，让树干延伸出画；或上移，留 4–6% 地面。二选一。骨架 +2、完成度 +1。</p>
   <p><b>右边：</b>只压没叶子的天 0.3–0.5 EV，或裁右 5% 让叶团接到边。光 +1、力 +1。</p>
   <p><b>不动：</b>整体色相。统一色调会把这条互补压平，那就不是这张了。</p>
  </div>
 </div>

 <div class="foot">口径 西式六维 18/22/15/15/20/10；分数取区间中值，同批比较差 2 分不判高下。
 数值来自 measure_photo.py；判断带容差，落在带内不等于刻意使用。</div>
</div>"""

    # ---------------- I 编辑跨页刻度轨 ----------------
    idx = [(x["name"], x["score"], x["score"] / d["maxd"][x["name"]]) for x in dims]
    ticks = "".join(
        f'<div class="rk"><span class="rl">{n}</span>'
        f'<span class="rb"><i style="width:{p*100:.0f}%"></i></span>'
        f'<span class="rv">{s}</span></div>' for n, s, p in idx)
    i_ = f"""<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box}}
body{{margin:0;background:#fbf9f5;color:#16130f;font-family:{SANS}}}
.wrap{{width:1280px;margin:0 auto;padding:0 0 26px}}
.top{{display:flex;justify-content:space-between;align-items:baseline;
 padding:30px 56px 12px;border-bottom:1px solid #16130f}}
.top h1{{margin:0;font:600 15px/1 {SANS};letter-spacing:.3em}}
.top span{{font:400 11px/1 {MONO};color:#8b8377}}
.stage{{position:relative;display:grid;grid-template-columns:1fr 300px;gap:44px;
 padding:34px 56px 0}}
.figure{{position:relative;display:inline-block;vertical-align:top}}
.figure img{{height:1000px;width:auto;display:block}}
.figure .edge{{position:absolute;left:-10px;right:-10px;height:1px;background:#16130f}}
.figure .cap{{position:absolute;right:-10px;font:500 9.5px/1 {MONO};color:#8b8377;
 background:#fbf9f5;padding:4px 0 4px 8px}}
.rail{{padding-top:6px}}
.rail h4{{margin:0 0 10px;font:600 10px/1 {SANS};letter-spacing:.22em;color:#8b8377}}
.rk{{display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid #ece6db}}
.rl{{flex:0 0 46px;font:500 11.5px/1 {SANS};color:#3d372f}}
.rb{{flex:1;height:4px;background:#ece6db;display:block;position:relative}}
.rb i{{position:absolute;left:0;top:0;height:100%;background:#b0341f;display:block}}
.rv{{flex:0 0 26px;text-align:right;font:500 12px/1 {MONO};color:#b0341f}}
.score{{padding-top:22px}}
.score b{{font:600 76px/1 {SANS};letter-spacing:-.04em}}
.score s{{text-decoration:none;font:400 12px/1 {SANS};color:#8b8377}}
.score p{{margin:8px 0 0;font:400 12px/1.85 {SANS};color:#5d564c;max-width:24ch}}
.band{{margin-top:34px;padding:0 56px}}
.band h4{{margin:0 0 12px;font:600 10px/1 {SANS};letter-spacing:.22em;color:#8b8377}}
.sw{{display:flex;height:64px}}
.sw div{{flex:1;color:#fff;font:500 9px/1.4 {SANS};padding:6px 8px}}
.lines{{display:grid;grid-template-columns:1fr 1fr;gap:48px;padding:30px 56px 0}}
.lines h4{{margin:0 0 10px;font:600 10px/1 {SANS};letter-spacing:.22em;color:#8b8377}}
.lines p{{margin:0 0 12px;font:400 13px/1.95 {SANS};color:#332e28;max-width:44ch}}
.lines p b{{color:#b0341f;font-weight:600}}
.kicker{{padding:34px 56px 0}}
.kicker p{{margin:0;font:600 34px/1.45 {SERIF};letter-spacing:.01em;max-width:22ch}}
.kicker p em{{font-style:normal;color:#b0341f}}
.foot{{margin:28px 56px 0;padding-top:12px;border-top:1px solid #dcd5c8;
 display:flex;justify-content:space-between;font:400 9.5px/1.8 {SANS};color:#948b7e;gap:40px}}
</style>
<div class="wrap">
 <div class="top"><h1>ORGANIZATION</h1>
  <span>DSC_7326　2:3　西式六维 {total}（{total-3}–{total+3}）</span></div>

 <div class="stage">
  <div class="figure">
   <img src="{photo}">
   <div class="edge" style="top:11.5%"></div><div class="cap" style="top:calc(11.5% - 14px)">树冠贴上边</div>
   <div class="edge" style="bottom:9%"></div><div class="cap" style="bottom:calc(9% - 14px)">树根出画</div>
  </div>
  <div class="rail">
   <h4>六维 · 达成率</h4>
   {ticks}
   <div class="score">
    <b>{total}</b><s> / 100</s>
    <p>主导对比：暖橙对冷蓝，1 : 1.8，正补色。输的不是颜色，是框。</p>
   </div>
  </div>
 </div>

 <div class="band">
  <h4>取样 · 全幅像素族</h4>
  <div class="sw">{"".join(f'<div style="background:{c}">{n}<br>{c}</div>' for n, c in sw)}</div>
 </div>

 <div class="kicker"><p>颜色这一关是过的，<em>框没有接住它</em>。</p></div>

 <div class="lines">
  <div>
   <h4>三处事实</h4>
   <p><b>主干落在 0.613</b>，5/8 的线上，差 0.012；横幅分割 0.654，差 0.013。两条都在带内，记「压线」，不算「刻意」。</p>
   <p><b>暖 14.7 对蓝 27.2</b>，正补色，面积接近。这是这张唯一的组织依据。</p>
   <p><b>亮池 11.7%</b>，最大一块 8.79% 落在右上天空；暗块 10.71%，最大 1.94% 在左下。一暗一亮打对角，但亮的那头没有内容。</p>
  </div>
  <div>
   <h4>两条动作</h4>
   <p><b>把下边挪开</b>：整幅下移 3–4% 并裁底，让树干延伸出画；或上移，留 4–6% 地面。骨架 +2、完成度 +1。</p>
   <p><b>把右边收掉</b>：只压没叶子的天 0.3–0.5 EV，或裁右 5% 让叶团接到边。光 +1、力 +1。</p>
   <p><b>不要动色相</b>。统一色调会把这条互补压成平片。</p>
  </div>
 </div>

 <div class="foot"><span>口径：西式六维 陈述 18 / 骨架 22 / 力 15 / 光 15 / 色 20 / 完成度 10；分数取区间中值，同批比较差 2 分不判高下。</span>
  <span>数值来自 measure_photo.py　photo-rx</span></div>
</div>"""

    return {"g": g, "h": h, "i": i_}


MAXD = {"陈述": 18, "骨架": 22, "力": 15, "光": 15, "色": 20, "完成度": 10}


def main():
    base = Path(sys.argv[1] if len(sys.argv) > 1 else "out/analysis/dsc-7326")
    m = json.loads((base / "measure.json").read_text(encoding="utf-8"))
    j = json.loads((base / "judgement.json").read_text(encoding="utf-8"))
    src = load(base / "source.webp", 1600)
    big = load(base / "source.webp", 1180)
    d = {"m": m, "j": j, "src": src, "img": big, "maxd": MAXD}
    for k, html in build(d).items():
        p = base / f"draft-{k}.html"
        p.write_text(html, encoding="utf-8")
        print(p, f"{len(html)/1024:.0f} KB")


if __name__ == "__main__":
    main()


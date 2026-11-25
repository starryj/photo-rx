# -*- coding: utf-8 -*-
"""三个新方向：D 瑞士版式 / E 杂志跨页 / F 言溪版。

用法：python tools/report_drafts2.py out/analysis/dsc-7326
输出：draft-d.html / draft-e.html / draft-f.html（单文件、图内嵌）
"""
import base64
import io
import json
import pathlib
import sys

from PIL import Image

SANS = ('Helvetica Neue,Helvetica,Arial,"Microsoft YaHei","PingFang SC",sans-serif')
SERIF = ('"Songti SC","Noto Serif SC",SimSun,"Songti TC",serif')
MONO = ('"SF Mono",Consolas,"Courier New",monospace')

SWATCHES = [
    ("天空", (0.00, 0.00, 1.00, 0.08)),
    ("橙叶", (0.672, 0.561, 0.836, 0.649)),
    ("树干", (0.40, 0.40, 0.60, 0.60)),
    ("地面", (0.00, 0.90, 1.00, 1.00)),
]
MAXD = {"陈述": 18, "骨架": 22, "力": 15, "光": 15, "色": 20, "完成度": 10}


def b64(im, quality=88):
    if im.mode in ("RGBA", "P", "LA"):
        im = im.convert("RGB")
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
    patch = src.crop((int(box[0] * w), int(box[1] * h), max(int(box[2] * w), int(box[0] * w) + 1),
                      max(int(box[3] * h), int(box[1] * h) + 1)))
    return "#%02x%02x%02x" % patch.resize((1, 1), Image.BOX).getpixel((0, 0))


def shifted(src, down=0.035, cut=0.04):
    w, h = src.size
    return src.crop((0, int(down * h), w, int((1 - cut) * h))).resize((w, h), Image.LANCZOS)


MARKS_CSS = """
.fig{position:relative;overflow:hidden}
.fig .mk{position:absolute;background:rgba(17,17,17,.88);color:#fff;
 font:600 8.5px/1 sans-serif;letter-spacing:.04em;padding:3px 6px;white-space:nowrap}
.fig .rule{position:absolute;left:0;right:0;height:2px;background:#e2231a}
.fig .boxmk{position:absolute;border:1px dashed #fff;box-shadow:0 0 0 1px rgba(226,35,26,.9)}
"""


def marks(top="树冠贴上边", bottom="树根出画", side=None):
    out = (f'<div class="rule" style="top:3.5%"></div>'
           f'<div class="mk" style="left:8px;top:calc(3.5% + 5px)">{top}</div>'
           f'<div class="rule" style="bottom:6%"></div>'
           f'<div class="mk" style="left:8px;bottom:calc(6% + 5px)">{bottom}</div>')
    return out


def build(d):
    m, j = d["m"], d["j"]
    dims = j["dims"]
    total = sum(x["score"] for x in dims)
    lo, hi = total - 3, total + 3
    src = d["src"]
    photo = b64(d["big"])
    fixed = b64(shifted(d["big"]))
    sw = [(n, sample(src, b)) for n, b in SWATCHES]
    hf = m["hue_families"]
    tone = m["tone"]

    # ---------------- D 瑞士版式 ----------------
    mods = []
    mods.append(("01", "FRAME / 取景", "两头都切",
                 "树冠贴上边、树根出画；整棵树读不全。", "photo"))
    mods.append(("02", "CONTRAST / 对比", "橙对蓝，约 1 : 1.8",
                 "暖橙叶对冷蓝天，正补色，面积接近——这张立得住的原因。", "swatch"))
    mods.append(("03", "LIGHT / 光", "逆光透叶，跨度 6 : 1",
                 "叶子透光用足了；近一成的亮度落在右侧空天上。", "bars"))
    mods.append(("04", "SKELETON / 骨架", "中线落在 5/8",
                 "树干与黄金分割线基本重合，竖幅与树形匹配。", "grid"))
    mods.append(("05", "SCORE / 六维", f"{total}",
                 "陈述 14 · 骨架 17 · 力 11 · 光 12 · 色 15 · 完成度 8", "dims"))
    mods.append(("06", "FIX / 改法", "下移 + 压天",
                 "整幅下移 3–4% 裁底；空天压 0.3–0.5 档，或裁右 5%。", "fix"))

    def mod_body(kind):
        if kind == "photo":
            return (f'<div class="vbox fig"><div style="position:absolute;inset:0;'
                    f'background-image:url({photo});background-size:148%;background-position:50% 40%;'
                    'filter:grayscale(1) contrast(1.08)"></div>' + marks() + '</div>')
        if kind == "swatch":
            return ('<div class="vbox vsw">'
                    '<div class="swrow">' + "".join(
                        f'<i style="background:{c};flex:{w}"></i>'
                        for (n, c), w in zip(sw, [27, 22, 16, 14])) + '</div>'
                    '<div class="swlab">' + "".join(
                        f'<span style="flex:{w}">{n}<br>{p}%</span>'
                        for (n, c), w, p in zip(sw, [27, 22, 16, 14], [27, 15, 43, 15])) + '</div>'
                    '</div>')
        if kind == "bars":
            return ('<div class="vbox vtone">'
                    f'<div class="tr"><i style="left:{(tone["L_p5"]/100)*100:.0f}%"></i>'
                    f'<i style="left:{(tone["L_median"]/100)*100:.0f}%"></i>'
                    f'<i style="left:{(tone["L_p99"]/100)*100:.0f}%"></i></div>'
                    f'<div class="trlab"><span>暗部 {tone["L_p5"]:.0f}</span>'
                    f'<span>中位 {tone["L_median"]:.0f}</span><span>亮部 {tone["L_p99"]:.0f}</span></div>'
                    '<div class="mass"><span>亮池</span><i class="r" style="width:56%"></i><b>11.7%</b></div>'
                    '<div class="mass"><span>暗块</span><i class="k" style="width:52%"></i><b>10.7%</b></div>'
                    '</div>')
        if kind == "grid":
            return ('<div class="vbox vgrid"><div class="tg">'
                    '<i style="left:62.5%"></i><i style="left:66.7%"></i><i style="left:33.3%"></i>'
                    '</div><div class="trlab"><span>5/8</span><span>2/3</span><span>1/3</span></div></div>')
        if kind == "dims":
            return ('<div class="vbox vdims">' + "".join(
                f'<div class="dm"><span>{x["name"]}</span>'
                f'<span class="dt"><i style="width:{100*x["score"]/MAXD[x["name"]]:.0f}%"></i></span>'
                f'<b>{x["score"]}</b></div>' for x in dims) + '</div>')
        return (f'<div class="vbox" style="background-image:url({fixed});'
                'background-size:cover;background-position:50% 45%"></div>')

    cards = "".join(
        f'<div class="mod"><div class="mh"><em>{n}</em><span class="en">{en}</span></div>'
        f'<div class="mv">{v}</div><p>{txt}</p>{mod_body(kind)}</div>'
        for n, en, v, txt, kind in mods)

    dd = f"""<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box}}
body{{margin:0;background:#e9e7e3;font-family:{SANS};color:#111}}
.pg{{max-width:900px;margin:0 auto;background:#fff}}
.head{{display:grid;grid-template-columns:1fr 1fr 132px;border-bottom:2px solid #111}}
.hl{{padding:11px 14px;border-right:1px solid #111;font:600 9.5px/1.5 {SANS};letter-spacing:.12em;
 text-transform:uppercase;color:#111}}
.hl b{{display:block;font-weight:700}}
.score{{padding:10px 12px;text-align:right}}
.score b{{font:800 46px/.9 {SANS};letter-spacing:-.04em;display:block}}
.score s{{text-decoration:none;font:600 8.5px/1.4 {SANS};letter-spacing:.14em;color:#666}}
.title{{padding:26px 22px 18px;border-bottom:2px solid #111}}
h1{{margin:0;font:800 50px/0.98 {SANS};letter-spacing:-.045em}}
h1 em{{font-style:normal;color:#e2231a}}
.sub{{margin:12px 0 0;font:500 15px/1.5 {SANS};color:#333;letter-spacing:.01em}}
.grid{{display:grid;grid-template-columns:1fr 1fr 1fr}}
.mod{{padding:14px 14px 12px;border-right:1px solid #111;border-bottom:1px solid #111;
 height:308px;display:flex;flex-direction:column}}
.mod:nth-child(3n){{border-right:0}}
.mh{{display:flex;align-items:baseline;gap:8px;margin-bottom:7px}}
.mh em{{font:800 21px/1 {SANS};color:#e2231a;letter-spacing:-.03em}}
.en{{font:700 8.5px/1.3 {SANS};letter-spacing:.13em;text-transform:uppercase}}
.mv{{font:700 15px/1.25 {SANS};letter-spacing:-.01em;margin-bottom:6px}}
.mod p{{margin:0;font:400 11.5px/1.55 {SANS};color:#3a3a3a}}
.vbox{{margin-top:auto;height:150px;overflow:hidden;position:relative}}
.vbox img{{width:100%;height:100%;object-fit:cover;display:block}}
.vsw{{height:auto;padding-bottom:2px}}
.swrow{{display:flex;height:54px}}
.swrow i{{display:block;height:100%}}
.swlab{{display:flex;margin-top:7px}}
.swlab span{{font:600 8.5px/1.35 {SANS};letter-spacing:.02em;color:#444}}
.vtone{{padding-top:6px}}
.tr{{position:relative;height:12px;background:linear-gradient(90deg,#1c1c1c,#8a8a8a,#f2f2f2)}}
.tr i{{position:absolute;top:-4px;width:2px;height:20px;background:#e2231a}}
.trlab{{display:flex;justify-content:space-between;margin-top:6px;
 font:600 8px/1 {SANS};letter-spacing:.05em;color:#555}}
.h4{{height:6px;background:#eee;margin-top:12px;position:relative}}
.mass{{display:flex;align-items:center;gap:6px;margin-top:9px;font:600 9px/1 {SANS}}}
.mass span{{flex:0 0 24px;color:#333}}
.mass i{{display:block;height:8px}}
.mass i.r{{background:#e2231a}}
.mass i.k{{background:#111}}
.mass b{{font:800 9px/1 {SANS};color:#111}}
.h4 span{{position:absolute;left:0;top:0;height:100%;background:#e2231a}}
.h4.dim span{{background:#111}}
.vgrid{{height:auto}}
.tg{{height:96px;border:1px solid #ddd;position:relative;background:
 repeating-linear-gradient(90deg,#f4f4f4 0 1px,#fff 1px 33px)}}
.tg i{{position:absolute;top:0;bottom:0;width:1.4px;background:#e2231a}}
.vdims{{height:auto;margin-top:6px}}
.dm{{display:flex;align-items:center;gap:7px;margin:4px 0;font:600 9.5px/1 {SANS}}}
.dm span:first-child{{flex:0 0 34px;color:#333}}
.dt{{flex:1;height:6px;background:#eee;display:block;position:relative}}
.dt i{{position:absolute;left:0;top:0;height:100%;background:#e2231a;display:block}}
.dm b{{flex:0 0 16px;text-align:right;font:800 10.5px/1 {SANS}}}
.foot{{display:grid;grid-template-columns:1fr 150px;border-top:2px solid #111}}
.ft{{padding:12px 14px;font:500 12px/1.5 {SANS}}}
.ft b{{color:#e2231a}}
.fb{{background:#e2231a;color:#fff;display:flex;align-items:center;justify-content:center;
 font:800 13px/1.2 {SANS};letter-spacing:.06em;text-align:center;padding:10px}}
.note{{padding:10px 14px 16px;font:400 9.5px/1.6 {SANS};color:#777}}
{MARKS_CSS}
</style>
<div class="pg">
 <div class="head">
  <div class="hl"><b>PHOTO DIAGNOSIS</b>摄影诊断 · 单张</div>
  <div class="hl"><b>DSC_7326</b>逆光秋树 · 1600×2404</div>
  <div class="score"><b>{total}</b><s>SCORE {lo}–{hi}</s></div>
 </div>
 <div class="title">
  <h1>树被框切了<br>两头<em>。</em></h1>
  <p class="sub">橙蓝互补是这张的命；<b>上面没有气口，下面没有落点。</b></p>
 </div>
 <div class="grid">{cards}</div>
 <div class="foot">
   <div class="ft">光 + 色 + 骨架 = <b>秩序</b>。色相不要动——橙蓝互补是唯一的组织依据。</div>
   <div class="fb">先立住<br>再谈好看</div>
 </div>
 <div class="note">口径 西式六维：陈述 18／骨架 22／力 15／光 15／色 20／完成度 10。分数取区间中值，同批比较到差 2 分不判高下。</div>
</div>"""

    # ---------------- E 杂志跨页 ----------------
    ee = f"""<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box}}
body{{margin:0;background:#dcd8d2;font-family:{SANS};color:#1a1a1a}}
.spread{{display:flex;max-width:1440px;margin:0 auto;box-shadow:0 10px 40px rgba(0,0,0,.18)}}
.page{{width:720px;background:#fff;padding:34px 34px 26px;display:flex;flex-direction:column}}
.gutter{{width:2px;background:linear-gradient(90deg,#cfcabf,#b9b3a6,#cfcabf)}}
.rh{{display:flex;justify-content:space-between;font:600 8.5px/1 {SANS};letter-spacing:.16em;
 color:#8a8478;text-transform:uppercase;border-bottom:1px solid #e2ddd4;padding-bottom:8px;margin-bottom:20px}}
.kicker{{font:700 9.5px/1 {SANS};letter-spacing:.2em;color:#b4442a;text-transform:uppercase}}
h2{{font:600 30px/1.28 {SERIF};margin:10px 0 0;letter-spacing:.01em}}
.dek{{font:400 12.5px/1.75 {SANS};color:#4a463f;margin:10px 0 0}}
.lay{{display:flex;gap:20px;margin-top:18px;flex:1}}
.lay.rev{{flex-direction:row-reverse}}
.imgcol{{flex:0 0 62%}}
.imgcol img{{width:100%;display:block}}
.figcap{{font:400 9.5px/1.6 {SANS};color:#8a8478;margin-top:7px}}
.txtcol{{flex:1;display:flex;flex-direction:column;gap:13px}}
.item b{{display:block;font:700 8.5px/1 {SANS};letter-spacing:.14em;color:#b4442a;
 text-transform:uppercase;margin-bottom:5px}}
.item p{{margin:0;font:400 12px/1.7 {SANS};color:#2c2924}}
.stat{{display:flex;gap:16px;border-top:1px solid #e2ddd4;border-bottom:1px solid #e2ddd4;padding:9px 0}}
.stat div{{flex:1}}
.stat s{{display:block;text-decoration:none;font:600 8px/1 {SANS};letter-spacing:.12em;color:#8a8478}}
.stat b{{font:600 17px/1.2 {SERIF}}}
.pgno{{margin-top:auto;padding-top:14px;font:600 9px/1 {SANS};letter-spacing:.16em;color:#a8a29a}}
.pull{{font:600 16px/1.5 {SERIF};color:#1a1a1a;border-left:2px solid #b4442a;padding-left:12px}}
{MARKS_CSS}
</style>
<div class="spread">
 <div class="page">
  <div class="rh"><span>摄影诊断 · 第一页</span><span>DSC_7326</span></div>
  <div class="kicker">现在的取景</div>
  <h2>橙蓝互补是这张的命，<br>树却被框切了两头。</h2>
  <p class="dek">逆光把叶子的透光用足了，冷蓝的天把暖橙托了出来。</p>
  <div class="lay">
   <div class="imgcol"><div class="fig"><img src="{photo}">{marks()}</div>
     <div class="figcap">原图 · 上边切树冠，下边出树根；右侧近一成画面是没有内容的亮天。</div></div>
   <div class="txtcol">
     <div class="item"><b>立住的地方</b><p>暖橙对冷蓝，面积约 1 : 1.8，正补色，两边都够分量。</p></div>
     <div class="item"><b>伤在两处</b><p>上面没有气口，下面没有落点；右侧的光落在空处。</p></div>
     <div class="stat">
       <div><s>SCORE</s><b>{total}</b></div>
       <div><s>RANGE</s><b>{lo}–{hi}</b></div>
       <div><s>SPAN</s><b>6:1</b></div>
     </div>
     <div class="pull">问题不在颜色，在取景。</div>
   </div>
  </div>
  <div class="pgno">01</div>
 </div>
 <div class="gutter"></div>
 <div class="page">
  <div class="rh"><span>摄影诊断 · 第二页</span><span>改法</span></div>
  <div class="kicker">按建议重取的画面</div>
  <h2>把整幅往下挪三四分，<br>让树干长到画外去。</h2>
  <div class="lay rev">
   <div class="imgcol"><img src="{fixed}">
     <div class="figcap">示意 · 整幅下移 3.5%、裁底 4%：树根出画，读作「生于画外」；天空那侧再压 0.3–0.5 档。</div></div>
   <div class="txtcol">
     <div class="item"><b>改法一</b><p>整幅下移 3–4% 并裁掉底部一条，让树干延伸到画外。</p></div>
     <div class="item"><b>改法二</b><p>右侧那片空天压 0.3–0.5 档，或裁右 5%，让亮块落到叶团上。</p></div>
     <div class="item"><b>不要动</b><p>整体色相。橙蓝互补是这张唯一的组织依据，任何「统一色调」都会把它压平。</p></div>
   </div>
  </div>
  <div class="pgno">02</div>
 </div>
</div>"""

    # ---------------- F 言溪版 ----------------
    ff = f"""<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box}}
body{{margin:0;background:#efece6;font-family:{SERIF};color:#23211d}}
.pg{{max-width:900px;margin:0 auto;background:#f8f6f1}}
.mast{{display:flex;justify-content:space-between;align-items:flex-end;
 padding:30px 46px 14px;border-bottom:1px solid #d9d2c5}}
.mast .l{{font:400 11px/1.6 {SANS};letter-spacing:.28em;text-transform:uppercase;color:#8b8274}}
.mast .r{{font:400 11px/1.6 {SANS};letter-spacing:.2em;color:#8b8274}}
.plate{{padding:0 46px}}
.plate img{{width:100%;display:block}}
.pcap{{display:flex;justify-content:space-between;padding:9px 46px 0;
 font:400 10.5px/1.7 {SANS};color:#8b8274;letter-spacing:.04em}}
.lead{{padding:34px 46px 0}}
.lead h1{{margin:0;font:400 34px/1.5 {SERIF};letter-spacing:.02em}}
.lead h1 i{{font-style:normal;position:relative}}
.lead h1 i::after{{content:"";position:absolute;left:0;right:0;bottom:3px;height:1px;background:#b4442a}}
.lead p{{margin:14px 0 0;font:400 13px/2 {SANS};color:#4d4840;max-width:640px}}
.rule{{margin:30px 46px 0;border-top:1px solid #d9d2c5}}
.cols{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:0;padding:0 46px}}
.c{{padding:22px 22px 22px 0;border-right:1px solid #e5dfd4}}
.c:last-child{{border-right:0;padding-right:0}}
.c b{{display:block;font:400 10px/1 {SANS};letter-spacing:.24em;text-transform:uppercase;color:#b4442a;margin-bottom:9px}}
.c p{{margin:0;font:400 12.5px/1.85 {SANS};color:#3c3831}}
.scale{{padding:26px 46px 0;display:flex;align-items:center;gap:18px}}
.scale .num{{font:400 44px/1 {SERIF};letter-spacing:.01em}}
.scale .track{{flex:1;height:1px;background:#cfc7b8;position:relative}}
.scale .track i{{position:absolute;top:-3px;width:7px;height:7px;background:#b4442a;border-radius:50%;left:calc(77% - 3.5px)}}
.scale .rg{{font:400 10.5px/1.6 {SANS};color:#8b8274;letter-spacing:.1em}}
.pal{{display:flex;gap:10px;padding:20px 46px 0;align-items:center}}
.pal i{{display:block;width:34px;height:34px;border-radius:50%}}
.pal span{{font:400 10.5px/1.6 {SANS};color:#8b8274;letter-spacing:.14em;margin-left:6px}}
.foot{{margin:28px 46px 0;padding:16px 0 30px;border-top:1px solid #d9d2c5;
 font:400 10.5px/1.8 {SANS};color:#8b8274;display:flex;justify-content:space-between}}
</style>
<div class="pg">
 <div class="mast"><div class="l">Photo Diagnosis</div><div class="r">DSC_7326 · 逆光秋树</div></div>
 <div class="plate"><img src="{photo}"></div>
 <div class="pcap"><span>上边切树冠 · 下边出树根</span><span>右侧空天占近一成画面</span></div>
 <div class="lead">
   <h1>橙蓝互补是这张的命，<br>取景<i>切了它两头</i>。</h1>
   <p>逆光把叶子的透光用足了，冷蓝的天把暖橙托了出来——颜色这一关它是过的。拦住它的是框：上面没有气口，下面没有落点，右侧还留着一块亮得没有内容的天空。</p>
 </div>
 <div class="rule"></div>
 <div class="cols">
  <div class="c"><b>立住</b><p>暖橙对冷蓝，面积约 1 : 1.8，正补色；两边都够分量，不偏科。</p></div>
  <div class="c"><b>伤处</b><p>树冠贴上边、树根直接出画，整棵树读不全；右侧近一成亮度落在空处。</p></div>
  <div class="c"><b>怎么改</b><p>整幅下移 3–4% 并裁掉底部一条；空天压 0.3–0.5 档，或裁右 5%。</p></div>
 </div>
 <div class="scale">
   <div class="num">{total}</div>
   <div class="track"><i></i></div>
   <div class="rg">区间 {lo}–{hi} · 西式六维</div>
 </div>
 <div class="pal">
   {"".join(f'<i style="background:{c}"></i>' for n, c in sw)}
   <span>{" ／ ".join(n for n, c in sw)}</span>
 </div>
 <div class="foot"><span>整体色相不要动——橙蓝互补是这张唯一的组织依据。</span><span>01 / 01</span></div>
</div>"""

    return {"d": dd, "e": ee, "f": ff}


def main():
    d = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out/analysis/dsc-7326")
    m = json.loads((d / "measure.json").read_text(encoding="utf-8"))
    j = json.loads((d / "judgement.json").read_text(encoding="utf-8"))
    src_path = d / "source.webp"
    data = {"m": m, "j": j, "src": load(src_path, 900), "big": load(src_path, 1200)}
    for k, html in build(data).items():
        p = d / f"draft-{k}.html"
        p.write_text(html, encoding="utf-8")
        print(f"{p}  {p.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()

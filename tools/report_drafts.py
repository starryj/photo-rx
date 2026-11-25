# -*- coding: utf-8 -*-
"""报告页的三个可视化草稿：measure.json + judgement.json -> draft-a/b/c.html。

用法：python tools/report_drafts.py out/analysis/dsc-7326

三种版式：
  A 封面式：大图 + 叠加线注 + 分数徽章 + 六维细条 + 三张动作卡
  B 数据卡：左图右面板（环形分 + 六维条 + 色带 + 明暗尺）
  C 对照稿：原图 / 建议取景并排 + 三条要点

文字只留摄影常识：亮点、伤、怎么改。数值只作角标，不写计算过程。
"""
import base64
import io
import json
import pathlib
import sys

from PIL import Image

WESTERN = [("陈述", 18), ("骨架", 22), ("力", 15), ("光", 15), ("色", 20), ("完成度", 10)]
CHINESE = [("陈述", 12), ("骨架", 18), ("势与质", 20), ("虚实承重", 25), ("色", 15), ("完成度", 10)]

FONT = ('-apple-system,"Segoe UI","Microsoft YaHei","Noto Sans SC",sans-serif')
MONO = ('"SF Mono",Consolas,"Cascadia Mono",monospace')

SWATCHES = [
    ("天空", (0.00, 0.00, 1.00, 0.08)),
    ("橙叶", (0.672, 0.561, 0.836, 0.649)),
    ("树干", (0.40, 0.40, 0.60, 0.60)),
    ("地面", (0.00, 0.90, 1.00, 1.00)),
    ("空天", (0.793, 0.00, 0.999, 0.658)),
]


def b64(im, quality=88):
    if im.mode in ("RGBA", "P", "LA"):
        im = im.convert("RGB")
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def load_scaled(path, width):
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    return im


def sample(src, box):
    w, h = src.size
    patch = src.crop((int(box[0] * w), int(box[1] * h), max(int(box[2] * w), int(box[0] * w) + 1),
                      max(int(box[3] * h), int(box[1] * h) + 1)))
    patch = patch.resize((1, 1), Image.BOX)
    return "#%02x%02x%02x" % patch.getpixel((0, 0))


def shifted_preview(src, down=0.035, cut=0.04):
    """示意：整幅下移 down、裁掉底部 cut，树根出画。"""
    w, h = src.size
    top = int(down * h)
    bottom = int((1 - cut) * h)
    body = src.crop((0, top, w, bottom)).resize((w, h), Image.LANCZOS)
    return body


def overlay(kind):
    """图上的线注：5/8 竖线、三分竖线、空亮区圈、切边标记。返回绝对定位 svg。"""
    if kind == "full":
        inner = (
            '<line x1="62.5" y1="0" x2="62.5" y2="100" stroke="#ff5a1f" stroke-width="0.22" opacity="0.9"/>'
            '<line x1="33.3" y1="0" x2="33.3" y2="100" stroke="#ffffff" stroke-width="0.16" opacity="0.45"/>'
            '<line x1="66.7" y1="0" x2="66.7" y2="100" stroke="#ffffff" stroke-width="0.16" opacity="0.45"/>'
            '<ellipse cx="90" cy="26" rx="14" ry="16" fill="none" stroke="#ffd166" stroke-width="0.35" stroke-dasharray="1.6 1.2"/>'
            '<line x1="40" y1="1.2" x2="60" y2="1.2" stroke="#ff5a1f" stroke-width="0.5"/>'
            '<line x1="42" y1="98.6" x2="58" y2="98.6" stroke="#ff5a1f" stroke-width="0.5"/>'
        )
    else:
        inner = (
            '<line x1="62.5" y1="0" x2="62.5" y2="100" stroke="#ffffff" stroke-width="0.2" opacity="0.5"/>'
            '<ellipse cx="90" cy="26" rx="14" ry="16" fill="none" stroke="#ffd166" stroke-width="0.3" stroke-dasharray="1.6 1.2"/>'
        )
    return ('<svg class="ov" viewBox="0 0 100 100" preserveAspectRatio="none">' + inner + '</svg>')


def build(data):
    m, j = data["m"], data["j"]
    dims = j["dims"]
    total = sum(d["score"] for d in dims)
    lo, hi = total - 3, total + 3
    src = data["src"]
    photo = b64(data["big"])
    preview = b64(shifted_preview(data["big"]))
    swatches = [(name, sample(src, box)) for name, box in SWATCHES]
    hf = m["hue_families"]
    tone = m["tone"]
    pool = m["bright_pools"]["top"][0]

    bars = []
    for d in dims:
        mx = dict(WESTERN if j["lens"] == "western" else CHINESE)[d["name"]]
        pct = 100 * d["score"] / mx
        bars.append(
            f'<div class="bar"><span class="bn">{d["name"]}</span>'
            f'<span class="bt"><i style="width:{pct:.0f}%"></i></span>'
            f'<b class="bv">{d["score"]}<span class="bm">/{mx}</span></b></div>')

    strip = "".join(
        f'<span class="sw" style="background:{c};flex:{w}"></span>'
        for (n, c), w in zip(swatches, [27, 22, 16, 14, 12]))

    legend = "".join(
        f'<span><i style="background:{c}"></i>{n}</span>' for n, c in swatches[:4])

    marks = "".join(
        f'<span class="mk" style="left:{x}%;top:{y}%">{t}</span>'
        for t, x, y in [("树冠切边", 44, 2.2), ("树根出画", 44, 95.2), ("空亮点", 89, 6.5)])

    short_acts = [
        ("骨架 +2 · 完成度 +1", "整幅下移 3–4%，裁掉底部一条，让树干延伸到画外。"),
        ("光 +1 · 力 +1", "右侧那片空天压 0.3–0.5 档，或裁右 5%，让亮块落到叶团上。"),
    ]

    # ---------- A 封面式 ----------
    a = f"""<!doctype html><meta charset="utf-8"><style>
body{{margin:0;background:#f4f2ef;font-family:{FONT};color:#1b1a18}}
.pg{{max-width:900px;margin:0 auto;background:#fff}}
.hero{{position:relative;line-height:0}}
.hero img{{width:100%;display:block}}
.ov{{position:absolute;inset:0;width:100%;height:100%}}
.mk{{position:absolute;transform:translateX(-50%);background:rgba(0,0,0,.55);color:#fff;
 font:600 10.5px/1 {MONO};letter-spacing:.08em;padding:5px 7px;white-space:nowrap}}
.cap{{position:absolute;left:18px;bottom:14px;color:#fff;font:600 12px/1 {MONO};letter-spacing:.14em;
 text-shadow:0 1px 8px rgba(0,0,0,.6)}}
.mid{{display:flex;gap:26px;align-items:flex-start;padding:26px 26px 10px}}
.score{{flex:0 0 132px;text-align:center;border-right:1px solid #eae6e0;padding-right:20px}}
.score b{{font:700 64px/1 {MONO};letter-spacing:-.03em}}
.score s{{display:block;text-decoration:none;font:500 11px/1.6 {MONO};color:#8c857c;margin-top:6px}}
.lead{{font:600 25px/1.45 {FONT};margin:2px 0 10px;letter-spacing:-.01em}}
.sub{{font:400 13.5px/1.7 {FONT};color:#5b554d;margin:0}}
.strip{{display:flex;height:14px;margin:14px 26px 6px;border-radius:3px;overflow:hidden}}
.legend{{display:flex;gap:16px;padding:0 26px 6px;font:400 11.5px/1.6 {FONT};color:#6b645b}}
.legend i{{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:5px}}
.dims{{padding:14px 26px 8px;display:grid;grid-template-columns:1fr 1fr;gap:4px 26px}}
.bar{{display:flex;align-items:center;gap:9px;font:500 12.5px/1 {FONT}}}
.bn{{flex:0 0 42px;color:#3d3833}}
.bt{{flex:1;height:6px;background:#efece7;border-radius:3px;overflow:hidden}}
.bt i{{display:block;height:100%;background:#c2410c}}
.bv{{flex:0 0 42px;text-align:right;font:600 12px/1 {MONO}}}
.bm{{color:#a8a29a;font-weight:400}}
.acts{{display:grid;grid-template-columns:1fr 1fr;gap:14px;padding:16px 26px 26px}}
.act{{background:#faf8f5;border-left:3px solid #c2410c;padding:14px 16px}}
.act em{{display:block;font:700 11px/1 {MONO};color:#c2410c;letter-spacing:.16em;margin-bottom:7px}}
.act p{{margin:0;font:400 15px/1.6 {FONT};color:#26231f}}
.keep{{margin:0 26px 22px;padding:13px 16px;background:#1b1a18;color:#f2efe9;font:400 13.5px/1.6 {FONT}}}
.foot{{padding:0 26px 26px;font:400 11px/1.7 {FONT};color:#9c948a}}
</style>
<div class="pg">
 <div class="hero"><img src="{photo}">{overlay("full")}{marks}
   <div class="cap">DSC_7326 · 逆光秋树 · {j["medium"]}</div></div>
 <div class="mid">
   <div class="score"><b>{total}</b><s>区间 {lo}–{hi}<br>西式六维</s></div>
   <div><div class="lead">橙蓝互补是这张的命；<br>树被框切了两头，是它的伤。</div>
     <p class="sub">逆光把叶子的透光用足了。问题不在颜色，在取景。</p></div>
 </div>
 <div class="strip">{strip}</div>
 <div class="legend">{legend}</div>
 <div class="dims">{"".join(bars)}</div>
 <div class="acts">{short_act_html(short_acts)}</div>
 <div class="keep">唯一不要动的是整体色相——橙蓝互补是这张唯一的组织依据。</div>
 <div class="foot">口径：西式六维（陈述 18／骨架 22／力 15／光 15／色 20／完成度 10）。分数为区间中值，同批比较到差 2 分不判高下。色块按测区取样；判定明细见 report.html。</div>
</div>"""

    # ---------- B 数据卡 ----------
    ring_r = 54
    circ = 2 * 3.14159 * ring_r
    dash = circ * total / 100
    b = f"""<!doctype html><meta charset="utf-8"><style>
body{{margin:0;background:#f1eee9;font-family:{FONT};color:#1b1a18}}
.pg{{max-width:900px;margin:0 auto;background:#fff;display:grid;grid-template-columns:1fr 372px}}
.left{{position:relative;line-height:0}}
.left img{{width:100%;display:block}}
.ov{{position:absolute;inset:0;width:100%;height:100%}}
.mk{{position:absolute;transform:translateX(-50%);background:rgba(0,0,0,.55);color:#fff;
 font:600 10px/1 {MONO};letter-spacing:.08em;padding:5px 7px;white-space:nowrap}}
.right{{padding:22px 22px 18px;border-left:1px solid #eee9e3}}
.eyebrow{{font:700 10.5px/1 {MONO};letter-spacing:.2em;color:#c2410c}}
h1{{font:600 19px/1.5 {FONT};margin:9px 0 3px;letter-spacing:-.01em}}
.meta{{font:400 11.5px/1.7 {FONT};color:#8c857c;margin:0 0 14px}}
.ring{{display:flex;align-items:center;gap:16px;margin:6px 0 16px}}
.ring .num{{font:700 46px/1 {MONO};letter-spacing:-.04em}}
.ring small{{font:400 11px/1.6 {MONO};color:#8c857c;display:block}}
.bar{{display:flex;align-items:center;gap:8px;font:500 12px/1 {FONT};margin:7px 0}}
.bn{{flex:0 0 40px;color:#3d3833}}
.bt{{flex:1;height:6px;background:#f1eee9;border-radius:3px;overflow:hidden}}
.bt i{{display:block;height:100%;background:#c2410c}}
.bv{{flex:0 0 40px;text-align:right;font:600 11.5px/1 {MONO}}}
.bm{{color:#aaa39a;font-weight:400}}
.strip{{display:flex;height:12px;margin:16px 0 6px;border-radius:3px;overflow:hidden}}
.legend{{display:flex;flex-wrap:wrap;gap:10px;font:400 10.5px/1.5 {FONT};color:#6b645b}}
.legend i{{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:4px}}
.rule{{border:0;border-top:1px solid #eee9e3;margin:16px 0}}
.act{{margin:12px 0 0}}
.act em{{font:700 10.5px/1 {MONO};color:#c2410c;letter-spacing:.14em}}
.act p{{margin:6px 0 0;font:400 13.5px/1.6 {FONT}}}
.keep{{margin-top:14px;font:400 12.5px/1.6 {FONT};color:#5b554d;border-left:2px solid #1b1a18;padding-left:10px}}
</style>
<div class="pg">
 <div class="left"><img src="{photo}">{overlay("light")}{marks}</div>
 <div class="right">
  <div class="eyebrow">DSC_7326 · 单张诊断</div>
  <h1>冷暖互补成立，<br>取景把树切了两头</h1>
  <p class="meta">{j["medium"]}<br>用途：{j["purpose"]}</p>
  <div class="ring">
    <svg width="118" height="118" viewBox="0 0 130 130">
      <circle cx="65" cy="65" r="{ring_r}" fill="none" stroke="#f1eee9" stroke-width="11"/>
      <circle cx="65" cy="65" r="{ring_r}" fill="none" stroke="#c2410c" stroke-width="11"
        stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}"
        transform="rotate(-90 65 65)"/>
    </svg>
    <div><div class="num">{total}</div><small>区间 {lo}–{hi}／西式六维</small></div>
  </div>
  {"".join(bars)}
  <div class="strip">{strip}</div>
  <div class="legend">{"".join(f'<span><i style="background:{c}"></i>{n}</span>' for n, c in swatches)}</div>
  <hr class="rule">
  {short_act_html(short_acts)}
  <div class="keep">整体色相不要动——橙蓝互补是这张唯一的组织依据。</div>
 </div>
</div>"""

    # ---------- C 对照稿 ----------
    c = f"""<!doctype html><meta charset="utf-8"><style>
body{{margin:0;background:#f4f2ef;font-family:{FONT};color:#1b1a18}}
.pg{{max-width:900px;margin:0 auto;background:#fff;padding:26px 26px 30px}}
.top{{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:16px}}
.eyebrow{{font:700 10.5px/1 {MONO};letter-spacing:.2em;color:#c2410c}}
h1{{font:600 22px/1.4 {FONT};margin:8px 0 0;letter-spacing:-.01em}}
.badge{{text-align:right}}
.badge b{{font:700 40px/1 {MONO}}}
.badge s{{display:block;text-decoration:none;font:400 10.5px/1.6 {MONO};color:#8c857c}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
.ph{{position:relative;line-height:0}}
.ph img{{width:100%;display:block}}
.ov{{position:absolute;inset:0;width:100%;height:100%}}
.tagn{{position:absolute;top:10px;left:10px;background:rgba(0,0,0,.62);color:#fff;
 font:600 10px/1 {MONO};letter-spacing:.12em;padding:6px 8px}}
.tagn.fix{{background:#c2410c}}
.points{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-top:20px}}
.pt em{{display:block;font:700 10.5px/1 {MONO};letter-spacing:.16em;margin-bottom:8px}}
.pt.good em{{color:#2f7d4f}} ..pt.bad em{{color:#c2410c}}
.pt p{{margin:0;font:400 13.5px/1.65 {FONT}}}
.note{{margin-top:18px;padding-top:14px;border-top:1px solid #eee9e3;
 font:400 11.5px/1.7 {FONT};color:#8c857c}}
</style>
<div class="pg">
 <div class="top">
  <div><div class="eyebrow">DSC_7326 · 取景诊断</div>
   <h1>树被框切了两头：上面没有气口，下面没有落点</h1></div>
  <div class="badge"><b>{total}</b><s>区间 {lo}–{hi}</s></div>
 </div>
 <div class="pair">
  <div class="ph"><img src="{photo}">{overlay("light")}<span class="tagn">现在</span></div>
  <div class="ph"><img src="{preview}"><span class="tagn fix">下移 3.5% · 裁底 4%</span></div>
 </div>
 <div class="points">
  <div class="pt good"><em>立住的地方</em><p>逆光把叶子的透光用足了；冷蓝的天托着暖橙的树冠，面积接近，互补干净。</p></div>
  <div class="pt bad"><em>伤在两处</em><p>树冠贴上边被切、树根直接出画，整棵树读不全；右侧近一成画面是空的亮天。</p></div>
  <div class="pt bad"><em>怎么改</em><p>整幅下移 3–4% 并裁掉底部一条；天空那侧压 0.3–0.5 档，或裁右 5%。</p></div>
 </div>
 <div class="note">右图是按建议做的取景示意，不是重拍。整体色相不要动——橙蓝互补是这张唯一的组织依据。口径：西式六维，{total}（{lo}–{hi}）。</div>
</div>"""
    return {"a": a, "b": b, "c": c}


def short_act_html(acts):
    return "".join(
        f'<div class="act"><em>改法 {i}　{lbl}</em><p>{txt}</p></div>'
        for i, (lbl, txt) in enumerate(acts, 1))


def act_html(changes, style):
    out = []
    for i, ch in enumerate(changes, 1):
        out.append(f'<div class="act"><em>改法 {i}　{ch["dims"]}</em><p>{ch["text"]}</p></div>')
    return "".join(out)


def main():
    d = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out/analysis/dsc-7326")
    m = json.loads((d / "measure.json").read_text(encoding="utf-8"))
    j = json.loads((d / "judgement.json").read_text(encoding="utf-8"))
    src_path = d / "source.webp"
    src = load_scaled(src_path, 900)
    data = {"m": m, "j": j, "src": src, "big": load_scaled(src_path, 1200)}
    pages = build(data)
    for k, html in pages.items():
        p = d / f"draft-{k}.html"
        p.write_text(html, encoding="utf-8")
        print(f"{p}  {p.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()

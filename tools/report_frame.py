# -*- coding: utf-8 -*-
"""frame-critique 报告页渲染：measure.json + judgement.json -> report.html（单文件，图内嵌）。

用法：
  python tools/report_frame.py out/analysis/dsc-7326

judgement.json 由分析者手写（判据与分数），measure.json 由 measure_photo.py 产出（事实）。
分数与诊断同源（DECISIONS D-01）：每条改动必须写它抬升哪些维度，且不许出现「不升分的改动」。
容差纪律（D-11 草案）：实测值照报，判断带宽带；总分给区间，同批比较只在区间不重叠时判高低。
"""
import base64
import io
import json
import os
import sys

from PIL import Image

WESTERN = [
    ("陈述", 18), ("骨架", 22), ("力", 15), ("光", 15), ("色", 20), ("完成度", 10),
]
CHINESE = [
    ("陈述", 12), ("骨架", 18), ("势与质", 20), ("虚实承重", 25), ("色", 15), ("完成度", 10),
]


def b64_image(path, width, crop=None, quality=86):
    im = Image.open(path)
    if crop:
        w, h = im.size
        im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    if im.mode in ("RGBA", "P", "LA"):
        im = im.convert("RGB")
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def facts_rows(m, tol):
    hf = m["hue_families"]
    t = m["tone"]
    rv = m.get("rule_of_thirds_check") or {}
    rh = m.get("main_horizontal_line") or {}
    ap = 100 * tol["area_frac"]["strict"]
    line = tol["line_pos"]["strict"]
    rows = [
        ("画幅", f'{m["image"]["px"][0]}×{m["image"]["px"][1]}，{m["image"].get("ratio_label", "")}；'
                 f'ICC {"有" if m["image"]["icc_bytes"] else "为空（按 sRGB 解读）"}'),
        ("色相族占比", f'蓝 {hf["blue"]*100:.2f}%｜中性 {hf["neutral"]*100:.2f}%｜'
                       f'暖 {hf["warm"]*100:.2f}%｜其余 {hf["other"]*100:.2f}%　'
                       f'（面积判断容差 ±{ap:.0f}pp）'),
        ("明暗", f'p5 {t["L_p5"]:.1f}／中位 {t["L_median"]:.1f}／p99 {t["L_p99"]:.1f}，'
                 f'跨度 {t["span_ratio"]:.2f}（记作约 {round(t["span_ratio"]):d}:1，±{tol["tone_span"]["strict"]}）'),
    ]
    if rv:
        rows.append(("最强竖线", f'x={rv["main_vertical_x"]:.3f}，最近 {rv["nearest"]}，'
                                 f'delta {rv["delta"]:+.3f} → 带宽 ±{line}：{rv["band"]}'))
    if rh:
        rows.append(("最强横线", f'y={rh["y"]:.3f}，最近 {rh["nearest"]}，'
                                 f'delta {rh["delta"]:+.3f} → 带宽 ±{line}：{rh["band"]}（不等于地平线）'))
    bp = m.get("bright_pools") or {}
    if bp.get("top"):
        b = bp["top"][0]
        rows.append(("最大亮池", f'{b["area_frac"]*100:.2f}% 在 ({b["cx"]:.3f},{b["cy"]:.3f})，L {b["mean_L"]:.1f}'))
    dm = m.get("dark_masses") or {}
    if dm.get("top"):
        d = dm["top"][0]
        rows.append(("最大暗块", f'{d["area_frac"]*100:.2f}% 在 ({d["cx"]:.3f},{d["cy"]:.3f})'))
    na = m.get("neutral_anchor") or {}
    if na:
        rows.append(("中性锚", f'{na["area_frac"]*100:.2f}%，L {na["mean_L"]}'))
    ei = (m.get("edge_intrusion") or {}).get("ratio_vs_mean_gradient") or {}
    if ei:
        rows.append(("边缘梯度", "／".join(f'{k} {ei[k]:.2f}' for k in ("top", "bottom", "left", "right"))
                                + "（>1.6 才算切边）"))
    return [{"k": a, "v": b} for a, b in rows]


def render(adir):
    with open(os.path.join(adir, "measure.json"), encoding="utf-8") as f:
        m = json.load(f)
    with open(os.path.join(adir, "judgement.json"), encoding="utf-8") as f:
        j = json.load(f)

    lens = j.get("lens", "western")
    scale = CHINESE if lens == "chinese" else WESTERN
    tol = m.get("tolerance") or {
        "line_pos": {"strict": 0.02}, "area_frac": {"strict": 0.03},
        "tone_span": {"strict": 0.5}, "dim_score": {"strict": 1},
        "hue_delta": {"near_complement": 8}, "principle": "", "report_style": "",
    }
    by_name = {d["name"]: d for d in j["dims"]}
    total = sum(int(by_name.get(n, {}).get("score", 0)) for n, _ in scale)
    cap = j.get("cap_reason")
    if cap:
        total = min(total, 60)
    ds = tol["dim_score"]["strict"]
    n_dims = len([1 for n, _ in scale if n in by_name])
    band = ds * (1 if n_dims == 1 else 3)
    lens_label = "西式六维" if lens == "western" else "中式六维"

    bars = []
    for name, mx in scale:
        d = by_name.get(name)
        if not d:
            continue
        pct = 100.0 * int(d["score"]) / mx
        bars.append(f"""
      <div class="bar">
        <div class="bl"><span class="bn">{esc(name)}</span><span class="bs">{d['score']}<i>/{mx}</i></span></div>
        <div class="track"><div class="fill" style="width:{pct:.1f}%"></div></div>
        <div class="bj">{esc(d['judge'])}</div>
        <div class="be"><span class="tag">看哪里</span>{esc(d['see'])}</div>
        <div class="be"><span class="tag">证据</span>{esc(d['evidence'])}</div>
      </div>""")

    rows = "".join(
        f"<tr><td class='dim'>{esc(n)}</td><td class='num'>{by_name[n]['score']}<i>/{mx}</i></td>"
        f"<td>{esc(by_name[n]['see'])}</td><td>{esc(by_name[n]['judge'])}</td>"
        f"<td class='ev'>{esc(by_name[n]['evidence'])}</td></tr>"
        for n, mx in scale if n in by_name
    )

    facts = "".join(f"<tr><th>{esc(r['k'])}</th><td>{esc(r['v'])}</td></tr>"
                    for r in (j.get("facts") or facts_rows(m, tol)))

    changes = "".join(
        f"<li><p>{esc(c['text'])}</p><p class='meta'>抬升：{esc(c['dims'])}　｜　失效条件：{esc(c['fail'])}</p></li>"
        for c in j["changes"]
    )
    review = "".join(f"<li>{esc(x)}</li>" for x in j.get("review", []))
    unmeasured = "".join(f"<li>{esc(x)}</li>" for x in j.get("unmeasured", []))

    src = os.path.join(adir, "source.webp")
    if not os.path.exists(src):
        cands = [f for f in os.listdir(adir) if f.lower().startswith("source.")]
        src = os.path.join(adir, cands[0]) if cands else None
    imgs = []
    if src:
        imgs.append(f'<figure><img src="{b64_image(src, 760)}" alt="原图"><figcaption>原图（缩至 760px）</figcaption></figure>')
    vs = os.path.join(adir, "verify-sheet.jpg")
    if os.path.exists(vs):
        imgs.append(f'<figure><img src="{b64_image(vs, 760)}" alt="框位核对"><figcaption>测量框位核对（先看框，再引数）</figcaption></figure>')

    html = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(j.get('eyebrow', '诊断报告'))} 诊断报告</title>
<style>
:root{{--ink:#1b1b1f;--mid:#5d5d68;--line:#e2e2e8;--bg:#fbfbfc;--accent:#b4452f;--soft:#f3f1ee}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.7 "Source Han Serif SC","Noto Serif CJK SC","Songti SC",Georgia,serif}}
.wrap{{max-width:860px;margin:0 auto;padding:56px 28px 80px}}
.eyebrow{{font:600 12px/1 ui-monospace,monospace;letter-spacing:.18em;text-transform:uppercase;color:var(--mid)}}
h1{{font-size:27px;line-height:1.45;margin:14px 0 6px;font-weight:700}}
.decl{{font-size:13px;color:var(--mid);border-left:2px solid var(--line);padding-left:12px;margin:18px 0 0}}
.score{{display:flex;align-items:flex-end;gap:16px;margin:34px 0 8px;padding-bottom:22px;border-bottom:1px solid var(--line)}}
.score .n{{font:700 64px/1 ui-monospace,monospace;letter-spacing:-.03em}}
.score .r{{font:600 15px/1.4 ui-monospace,monospace;color:var(--mid)}}
.score .cap{{margin-left:auto;font-size:13px;color:var(--accent);text-align:right;max-width:300px}}
h2{{font-size:14px;letter-spacing:.12em;text-transform:uppercase;color:var(--mid);
margin:44px 0 14px;font-family:ui-monospace,monospace;font-weight:600}}
.lead{{font-size:17px;background:var(--soft);padding:16px 18px;border-radius:8px;margin:0}}
.bar{{padding:14px 0;border-bottom:1px dashed var(--line)}}
.bl{{display:flex;justify-content:space-between;align-items:baseline;font-size:15px;font-weight:600}}
.bs{{font:600 15px ui-monospace,monospace}}.bs i,.num i{{font-style:normal;color:var(--mid);font-weight:400}}
.track{{height:6px;background:#eceae7;border-radius:3px;margin:8px 0 10px;overflow:hidden}}
.fill{{height:100%;background:linear-gradient(90deg,#c25b3d,#b4452f)}}
.bj{{font-size:14px;color:#33333a;margin-bottom:8px}}
.be{{font-size:13px;color:var(--mid);margin:3px 0}}
.tag{{display:inline-block;min-width:44px;font:600 11px ui-monospace,monospace;
color:var(--accent);letter-spacing:.06em;margin-right:8px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
th,td{{text-align:left;vertical-align:top;padding:9px 10px;border-bottom:1px solid var(--line)}}
tr:nth-child(odd) td,tr:nth-child(odd) th{{background:#fff}}
.facts th{{width:104px;font:600 12px ui-monospace,monospace;color:var(--mid);background:#fff}}
.num{{font:600 13px ui-monospace,monospace;white-space:nowrap}}
.dim{{font-weight:600;white-space:nowrap}}
.ev{{color:var(--mid);font-size:13px}}
ol{{padding-left:20px}}ol li{{margin:0 0 16px}}ol li p{{margin:0}}
.meta{{font:12px/1.6 ui-monospace,monospace;color:var(--mid);margin-top:6px!important}}
ul{{padding-left:20px}}ul li{{margin:0 0 8px;font-size:14px}}
figure{{margin:0 0 18px}}figure img{{width:100%;border-radius:8px;display:block;border:1px solid var(--line)}}
figcaption{{font:12px ui-monospace,monospace;color:var(--mid);margin-top:6px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
@media(max-width:640px){{.grid2{{grid-template-columns:1fr}}.wrap{{padding:36px 18px 60px}}h1{{font-size:22px}}}}
footer{{margin-top:56px;padding-top:16px;border-top:1px solid var(--line);
font:12px/1.6 ui-monospace,monospace;color:var(--mid)}}
</style></head><body><div class="wrap">
<div class="eyebrow">{esc(j.get('eyebrow', ''))} · 诊断报告</div>
<h1>{esc(j['headline'])}</h1>
<p class="decl"><b>口径：{lens_label}</b>｜用途：{esc(j.get('purpose', '未声明'))}｜
介质：{esc(j.get('medium', ''))}｜跨套不可比</p>

<div class="score"><div class="n">{total}</div>
<div class="r">总分 / 100<br>区间 {max(0, total - band)}–{min(100, total + band)}</div>
{'<div class="cap">封顶触发：' + esc(cap) + '（总分不超过 60）</div>' if cap else ''}</div>

<h2>主导对比</h2>
<p class="lead">{esc(j['dominant'])}</p>

<h2>事实</h2>
<table class="facts">{facts}</table>

<h2>六维</h2>
<div class="bars">{''.join(bars)}</div>

<h2>改动（每条都落到维度）</h2>
<ol>{changes}</ol>
{'<p class="be"><span class="tag">不改</span>' + esc(j['no_change']) + '</p>' if j.get('no_change') else ''}

{'<h2>复核意见</h2><ul>' + review + '</ul>' if review else ''}
{'<h2>未测项</h2><ul>' + unmeasured + '</ul>' if unmeasured else ''}

<h2>证据</h2>
<div class="grid2">{''.join(imgs)}</div>

<footer>事实来自 <code>tools/measure_photo.py</code>（{esc(os.path.basename(adir))}/measure.json）；
判据来自 frame-critique 六维量表。容差纪律：{esc(tol.get('principle', ''))}。
{esc(tol.get('report_style', ''))}</footer>
</div></body></html>"""

    out = os.path.join(adir, "report.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"总分 {total}（{max(0, total - band)}–{min(100, total + band)}）  口径 {lens_label}")
    print(out)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(render(sys.argv[1]))

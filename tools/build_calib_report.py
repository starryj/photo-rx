# -*- coding: utf-8 -*-
"""生成开工前校准报告（HTML，自包含 base64 缩略图）。"""
from __future__ import annotations

import base64
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
CALIB = ROOT / "out" / "calib"
DEST = CALIB / "calib-report.html"

ITEMS = [
    # id, 文件, 任务, 判定, 页来源, 要点
    ("C01", "interacting_p31.png", "图版语义", "通过", "Interacting with Color 跨页 50–51",
     "第一轮把左页说成「三个并列方形块」；二版加了「面积次序 + 色相族」后，自己补出关键现象：圆点在深绿／浅绿底上呈现不同颜色。"),
    ("C02", "ioc_p126.png", "图版语义", "未通过", "Interaction of Color 图版 IX-3",
     "把橙块说成「黄色」；没看出这张练习的核心——同一张纸片被两种背景切开后看起来是两个颜色。这是唯一一条真失败。"),
    ("C03", "arnheim_p26.png", "版面", "通过", "艺术与视知觉 005",
     "图 2 处；图 2 左上、图 3 页底、正文绕图；阅读顺序对。"),
    ("C04", "arnheim2_p530.png", "质量闸", "通过", "艺术与视知觉 封底",
     "一版只答「清晰／正常／完整／能读」，等于没说；二版加「页面性质」后答「版权页-条码页 → 不值得」。"),
    ("C05", "gombrich_p56.png", "版面", "通过", "艺术与错觉 30",
     "这页是纯文字。一版、二版都编造出「图片位于中间」——被正文里的「（图 5、图 6）」骗了。三版强制先数图，答「0 处 / 无图，正文连续」。"),
    ("C06", "zhongguo_p286.png", "版面", "通过", "中国美学史大纲 274",
     "「0 处 / 无图」；页码 ·274· 位置对。"),
    ("C07", "meixue_p111.png", "图版语义", "通过", "美学散步 103",
     "三幅上下排列、绢本黄褐底、人物红黑服饰都对；把画中黑犬说成「黑猫」，是小错不伤判断。"),
    ("C08", "shengjing_p96.png", "图版语义", "通过", "摄影色彩圣经",
     "穹顶对称嵌套、黄蓝橙主导、圆周被蓝边包住时更饱和——都成立。"),
    ("C09", "shijie_p166.png", "版面", "通过", "摄影师的视界 163",
     "数出 4 处图（1 张主照 + 3 张线描示意），编号 1／2／3 与文字说明对应。"),
    ("C10", "guangxian_p121.png", "图版语义", "通过", "光线与用光",
     "红果 vs 绿色虚化背景、面积次序、红绿互补对比都对。"),
]

PROBE = [
    ("中国美学史大纲", 675, "0.00", "0", "1.00", "ocr", "6 分 58 秒"),
    ("艺术与视知觉", 530, "0.00", "0", "1.00", "ocr", "5 分 28 秒"),
    ("艺术与错觉", 415, "0.95", "1259.5", "2.10", "local_text", "4 分 17 秒"),
    ("美学散步（彩图本）", 360, "0.05", "14.1", "0.95", "ocr", "3 分 43 秒"),
    ("Interaction of Color", 210, "0.60", "788.5", "1.95", "mixed", "2 分 10 秒"),
    ("摄影师的视界", 189, "0.00", "0", "1.00", "ocr", "1 分 57 秒"),
    ("摄影色彩圣经", 181, "0.05", "51.0", "0.95", "ocr", "1 分 52 秒"),
    ("光线与用光", 163, "0.05", "46.9", "0.95", "ocr", "1 分 41 秒"),
    ("Interacting with Color", 73, "0.00", "0", "2.40", "ocr", "0 分 45 秒"),
]


def b64_thumb(path: Path, w: int = 300) -> str:
    im = Image.open(path).convert("RGB")
    h = int(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def strip() -> str:
    """10 张缩略图拼成 5×2 的条带，带编号标签。"""
    cells = []
    for iid, fn, *_ in ITEMS:
        im = Image.open(CALIB / fn).convert("RGB")
        w = 300
        h = int(im.height * w / im.width)
        cells.append((iid, im.resize((w, h), Image.LANCZOS)))
    cw = 300
    pad = 10
    lab = 22
    row_h = max(c.height for _, c in cells)
    W = pad + 5 * (cw + pad)
    H = pad + 2 * (row_h + lab + pad)
    sheet = Image.new("RGB", (W, H), (250, 249, 246))
    dr = ImageDraw.Draw(sheet)
    for idx, (iid, im) in enumerate(cells):
        r, c = divmod(idx, 5)
        x = pad + c * (cw + pad)
        y = pad + r * (row_h + lab + pad)
        sheet.paste(im, (x, y))
        dr.rectangle([x, y, x + im.width - 1, y + im.height - 1], outline=(224, 220, 212))
        dr.text((x + 3, y + im.height + 5), iid, fill=(60, 58, 52))
    buf = io.BytesIO()
    sheet.save(buf, "JPEG", quality=84)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main() -> int:
    rows = []
    for iid, fn, task, verdict, src, note in ITEMS:
        good = verdict == "通过"
        rows.append(
            f'<tr class="{"ok" if good else "bad"}">'
            f'<td class="iid">{iid}</td>'
            f'<td>{src}</td>'
            f'<td class="task">{task}</td>'
            f'<td class="verdict">{"✓ 通过" if good else "✗ 未通过"}</td>'
            f'<td class="note">{note}</td></tr>'
        )

    probe_rows = []
    for name, pages, ratio, ch, img, route, eta in PROBE:
        cls = {"ocr": "r-ocr", "local_text": "r-txt", "mixed": "r-mix"}[route]
        probe_rows.append(
            f'<tr><td class="nm">{name}</td><td class="num">{pages}</td>'
            f'<td class="num">{ratio}</td><td class="num">{ch}</td><td class="num">{img}</td>'
            f'<td><span class="tag {cls}">{route}</span></td><td class="num">{eta}</td></tr>'
        )

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>开工前校准报告 · photo-vision</title>
<style>
  @page {{ size: 1240px 2900px; margin: 0; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ width: 1240px; background: #fdfcfa; color: #15150f;
    font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
    -webkit-font-smoothing: antialiased; }}
  .page {{ width: 1240px; padding: 56px 68px 44px; }}
  .serif {{ font-family: "Songti SC", "SimSun", Georgia, serif; }}
  .mono {{ font-family: "Cascadia Mono", Consolas, monospace; }}

  header {{ display: flex; justify-content: space-between; align-items: baseline;
    border-bottom: 1px solid #15150f; padding-bottom: 10px; }}
  .brand {{ font-size: 11px; letter-spacing: .34em; text-transform: uppercase; }}
  .brand b {{ color: #9e2f22; font-weight: 600; }}
  .meta {{ font-size: 11px; color: #7a7364; letter-spacing: .04em; }}

  .kicker {{ margin-top: 26px; font-size: 11.5px; letter-spacing: .26em; color: #a19b8c; }}
  h1 {{ font-family: "Songti SC", "SimSun", Georgia, serif; font-size: 46px; line-height: 1.2;
    margin-top: 10px; letter-spacing: .01em; }}
  h1 em {{ font-style: normal; color: #9e2f22; }}
  .dek {{ margin-top: 14px; font-size: 14.5px; line-height: 1.85; color: #3a352c; max-width: 78ch; }}

  .hero {{ margin-top: 30px; display: grid; grid-template-columns: 268px 1fr; gap: 34px;
    border-top: 2px solid #15150f; border-bottom: 1px solid #ddd7c9; padding: 26px 0; }}
  .score {{ font-family: "Songti SC", "SimSun", Georgia, serif; font-size: 116px; line-height: .92;
    letter-spacing: -.02em; }}
  .score small {{ font-size: 26px; color: #a19b8c; letter-spacing: 0; }}
  .scorenote {{ margin-top: 12px; font-size: 11.5px; color: #7a7364; line-height: 1.7; }}
  .heroR p {{ font-size: 14px; line-height: 1.85; color: #3a352c; }}
  .heroR p + p {{ margin-top: 12px; }}
  .heroR b {{ color: #15150f; }}
  .heroR .teal {{ color: #2c6f6d; font-weight: 600; }}
  .heroR .red {{ color: #9e2f22; font-weight: 600; }}

  h2 {{ margin-top: 40px; font-size: 12px; letter-spacing: .26em; color: #a19b8c;
    border-top: 1px solid #15150f; padding-top: 12px; display: flex; justify-content: space-between; }}
  h2 span {{ letter-spacing: .02em; color: #a19b8c; }}
  h3 {{ margin-top: 22px; font-size: 15px; letter-spacing: .02em; }}
  p.lead {{ margin-top: 12px; font-size: 13.5px; line-height: 1.9; color: #3a352c; }}

  .rounds {{ margin-top: 18px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
  .rd {{ border: 1px solid #ddd7c9; background: #fff; padding: 16px 16px 14px; }}
  .rd .v {{ font-size: 10.5px; letter-spacing: .22em; color: #a19b8c; }}
  .rd .n {{ margin-top: 8px; font-family: "Songti SC", "SimSun", Georgia, serif; font-size: 40px; line-height: 1; }}
  .rd .n small {{ font-size: 15px; color: #a19b8c; }}
  .rd .d {{ margin-top: 10px; font-size: 11.5px; line-height: 1.75; color: #5c5546; }}
  .rd.now {{ border-color: #15150f; }}
  .rd.now .n {{ color: #9e2f22; }}

  table {{ width: 100%; border-collapse: collapse; margin-top: 14px; }}
  th {{ font-size: 10.5px; letter-spacing: .12em; color: #a19b8c; text-align: left;
    padding: 0 8px 7px 0; border-bottom: 1px solid #15150f; font-weight: 500; }}
  td {{ font-size: 12px; line-height: 1.72; color: #3a352c; padding: 9px 8px 9px 0;
    border-bottom: 1px solid #efeade; vertical-align: top; }}
  td.iid {{ font-family: "Cascadia Mono", Consolas, monospace; color: #a19b8c; width: 46px; }}
  td.task {{ white-space: nowrap; color: #7a7364; width: 74px; }}
  td.verdict {{ white-space: nowrap; width: 82px; font-size: 11.5px; letter-spacing: .02em; }}
  tr.ok td.verdict {{ color: #2c6f6d; }}
  tr.bad td.verdict {{ color: #9e2f22; font-weight: 600; }}
  tr.bad td.note {{ color: #5d2019; }}
  td.note {{ font-size: 11.5px; color: #5c5546; line-height: 1.75; }}
  td.num {{ font-family: "Cascadia Mono", Consolas, monospace; font-size: 11.5px; }}
  td.nm {{ white-space: nowrap; }}

  .tag {{ font-family: "Cascadia Mono", Consolas, monospace; font-size: 10.5px;
    padding: 1px 7px; border: 1px solid; }}
  .r-ocr {{ color: #9e2f22; border-color: #d8b6b0; background: #fbf1ef; }}
  .r-txt {{ color: #2c6f6d; border-color: #b6d0cd; background: #eef6f4; }}
  .r-mix {{ color: #7a6a2c; border-color: #d9d0b0; background: #faf6e8; }}

  .strip {{ margin-top: 16px; }}
  .strip img {{ width: 100%; border: 1px solid #e6e0d2; }}

  .ocr {{ margin-top: 16px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
  .oc {{ border-top: 2px solid #15150f; padding-top: 10px; }}
  .oc .h {{ font-size: 11px; color: #a19b8c; letter-spacing: .1em; }}
  .oc .b {{ margin-top: 8px; font-size: 12px; line-height: 1.8; color: #3a352c; }}
  .oc .b b {{ color: #9e2f22; }}
  .oc .k {{ margin-top: 8px; font-family: "Cascadia Mono", Consolas, monospace;
    font-size: 10.8px; color: #7a7364; line-height: 1.7; }}

  .cond {{ margin-top: 18px; display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }}
  .cd {{ border: 1px solid #ddd7c9; background: #fff; padding: 15px 16px; }}
  .cd .t {{ font-size: 12.5px; color: #15150f; }}
  .cd .t i {{ font-style: normal; color: #9e2f22; font-family: "Cascadia Mono", Consolas, monospace;
    font-size: 11px; margin-right: 7px; }}
  .cd .d {{ margin-top: 8px; font-size: 11.5px; line-height: 1.8; color: #5c5546; }}

  .closing {{ margin-top: 34px; border-top: 2px solid #15150f; padding-top: 16px;
    display: flex; gap: 22px; align-items: baseline; }}
  .closing .lbl {{ font-size: 10.5px; letter-spacing: .3em; color: #9e2f22; white-space: nowrap; }}
  .closing p {{ font-family: "Songti SC", "SimSun", Georgia, serif; font-size: 21px; line-height: 1.65; }}
  .closing p b {{ font-weight: 600; border-bottom: 2px solid #2c6f6d; padding-bottom: 1px; }}

  .foot {{ margin-top: 26px; border-top: 1px solid #ddd7c9; padding-top: 12px;
    display: flex; justify-content: space-between; font-size: 10.5px; line-height: 1.7; color: #8c8577; }}
</style></head><body><div class="page">

<header>
  <div class="brand">photo-vision · <b>开工前校准</b></div>
  <div class="meta">2026-11-23 · 视觉服务 11500 · qwen3-vl:4b · MinerU 3.4.5 pipeline</div>
</header>

<div class="kicker">校准报告 · 提交确认</div>
<h1>十张图版，<em>九张读对</em></h1>
<div class="dek">
  开工前把「这张图能不能交给本地模型读」先验一次：10 张答案已知的图版页、9 本 PDF 的读法判定、3 页 OCR 抽检。
  通过线事先定在 7/10，实际 9/10；剩下那一条不是模板能修的，写进下面的开工条件。
</div>

<div class="hero">
  <div>
    <div class="score">9<small> / 10</small></div>
    <div class="scorenote">图版定性判定<br>通过线 7 / 10<br>合计 10 条、4 条在第一轮失败</div>
  </div>
  <div class="heroR">
    <p>第一轮只有 <b>7 / 10</b>，卡在三条：一条真失败（阿尔伯斯的色彩错觉），两条是<b>模板没问对</b>——
    质量闸不问「这是什么页」，版面模板不要求先数图，于是纯文字页上也能「看出」一张图来。</p>
    <p>改模板、不改模型：<span class="teal">质量闸加「页面性质」</span>、<span class="teal">版面加「先数图」</span>、
    <span class="teal">图版加「先报面积次序、只报色相族」</span>。三轮下来 9/10，只剩阿尔伯斯那一条。</p>
    <p>最后一条是模型的上限，不是提示词能修的：<span class="red">4B 看不出「同一块颜色被两种背景切开后看起来是两个颜色」</span>。
    这类图版以后必须人工读，模型只负责给结构。</p>
  </div>
</div>

<h2>一、三轮迭代 <span>每一轮都是先失败、再修模板、再复测</span></h2>
<div class="rounds">
  <div class="rd">
    <div class="v">ROUND 1 · 模板 v1</div>
    <div class="n">7<small> / 10</small></div>
    <div class="d">失败 C02 色彩错觉、C04 只报「正常」、C05 在纯文字页编造出图。
    三条里两条是提示词的问题。</div>
  </div>
  <div class="rd">
    <div class="v">ROUND 2 · 模板 v2</div>
    <div class="n">8<small> / 10</small></div>
    <div class="d">质量闸补「页面性质 → 版权页-条码页 → 不值得」；图版补「面积次序 + 色相族」，C01 因此自己补出关键现象。
    C05 仍被正文里的「（图 5、图 6）」带跑。</div>
  </div>
  <div class="rd now">
    <div class="v">ROUND 3 · 模板 v3</div>
    <div class="n">9<small> / 10</small></div>
    <div class="d">版面模板强制第一行先答「这一页有几处图」，并把「正文里的图号不算图」写死。
    C05 立刻答「0 处 / 无图，正文连续」，C09 数出 4 处（1 主照 + 3 线描）。</div>
  </div>
</div>

<h2>二、十条逐项 <span>每条都能对着缩略图复核</span></h2>
<div class="strip"><img src="{strip()}" alt="10 张校准页缩略图"></div>
<table>
  <tr><th></th><th>页</th><th>任务</th><th>判定</th><th>模型错在哪 / 对在哪</th></tr>
  {''.join(rows)}
</table>

<h2>三、九本书的读法 <span>probe 判定表，伊登《色彩艺术》已按你的说明删去</span></h2>
<table>
  <tr><th>书名</th><th>页数</th><th>有字页</th><th>字/页</th><th>大图/页</th><th>判定</th><th>MinerU 预计</th></tr>
  {''.join(probe_rows)}
</table>
<p class="lead">
  九本合计 <b>2 796 页</b>，按 pipeline 实测算 <b>约 29 分钟</b>跑完 OCR —— 不是优化项，是这批书的默认路径。
  <span class="mono">艺术与错觉</span> 是唯一能直读的（95% 页面有 1200+ 字），
  <span class="mono">Interaction of Color</span> 半本有字，其余七本一律走整页图版识别。
</p>

<h2>四、OCR 抽检 <span>三页、4 471 字</span></h2>
<div class="ocr">
  <div class="oc">
    <div class="h">O01 · 中国美学史大纲 274</div>
    <div class="b">中文正文 1 508 字，段落与标点基本完整，术语对得上。<br>
    错字 <b>6 处</b>：纤秣→纤秾、雾徐→雾余、载进载止→载行载止、细缇→絪缊、查霭→杳霭、生气妙出→生气远出。</div>
    <div class="k">错字率 ≈ 0.40%</div>
  </div>
  <div class="oc">
    <div class="h">O02 · Interacting with Color 50–51</div>
    <div class="b">英文图注 1 285 字，几乎逐字正确（含 "bubbles" 的弯引号）。<br>
    只有两处标点：开引号被打成直引号、末句缺句号。</div>
    <div class="k">错字率 ≈ 0.08%</div>
  </div>
  <div class="oc">
    <div class="h">O03 · 艺术与视知觉 005</div>
    <div class="b">中文图文混排 1 678 字，图 2／图 3／图 4 与图注位置全对。<br>
    错字 <b>1 处</b>：极坏清楚→极不清楚。</div>
    <div class="k">错字率 ≈ 0.06%</div>
  </div>
</div>
<p class="lead">
  合起来错字率 <b>0.18%</b>，够蒸馏用。但有一处系统性问题：
  <b>书名号与引号会大面积丢失或错配</b>（「二十四诗品」应为《二十四诗品》）。
  这直接影响 v1 那套「引文逐字命中原文」的校验——所以下一阶段引文核对要改成<b>去标点比对</b>，
  并对每条引文标 <span class="mono">verified_against_scan</span>。
</p>

<h2>五、开工条件 <span>四条，都来自这轮校准</span></h2>
<div class="cond">
  <div class="cd">
    <div class="t"><i>01</i>色彩错觉类图版，人工读</div>
    <div class="d">阿尔伯斯式的「同色异相」图版，4B 只给得出结构，给不出错觉判断。
    这类页由我读图定 A1 案例，模型结果只用来交叉核对形状与块数。</div>
  </div>
  <div class="cd">
    <div class="t"><i>02</i>色名与数值，一律脚本量</div>
    <div class="d">模型会把橙说成黄、把地平线读成 25%（真值 49.95%）。
    凡是尺寸、比例、亮度、面积、色相值，全部走 <span class="mono">measure_*.py</span>；
    模型只说「面积次序 + 色相族 + 明暗」。</div>
  </div>
  <div class="cd">
    <div class="t"><i>03</i>先数图，再论版面</div>
    <div class="d">版面模板已改成第一行先答「几处图」。凡是产出「图文关系」的步骤，
    都要带这一行；缺这行的一律不采信。</div>
  </div>
  <div class="cd">
    <div class="t"><i>04</i>批一次序调整</div>
    <div class="d">伊登已删 → 批一改为：<b>摄影色彩圣经 → 霍斯特曼 Interacting with Color → 阿尔伯斯 Interaction of Color</b>
    （彩色图版最密集的先做，好验收）。Pixar 画册已转成 HTML，走独立抽取，不占 MinerU。</div>
  </div>
</div>

<div class="closing">
  <div class="lbl">结论</div>
  <p>校准通过，<b>可以开工</b>——但请记住这三件事：模型读结构，脚本读数字，错觉靠人眼。</p>
</div>

<div class="foot">
  <div>pass line 7/10 于开工前确定 · 三轮模板改动只动提示词，未动模型与参数 · 全部原始输出存 out\\calib\\calib_run_*.json</div>
  <div>photo-vision / 2026-11-23</div>
</div>

</div></body></html>
"""
    DEST.write_text(html, encoding="utf-8")
    print(f"WROTE {DEST} ({len(html)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""OCR 引文抽样：把 claims 里的逐字引文回定位到 PDF 原页的文本块，裁出高分辨率图，
供人眼逐条核对「OCR 抄下来的这一句，印刷页上是不是这几个字」。

产出：
  out\\ocr-sample\\<sample_id>.png   单条裁图（已放大）
  out\\ocr-sample\\sheet-<n>.png    4 条一页的核对表（带 S01 编号，不含期望原文）
  out\\ocr-sample\\manifest.json    样本清单（含期望原文，供判卷脚本用；核对时不要看）

用法：
  python tools\\ocr_sample.py build [--total 40]
"""
import argparse
import json
import random
import sys
from pathlib import Path

import yaml
import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision")
BOOKROOT = ROOT / "books"
OUT = ROOT / "out" / "ocr-sample"
PDFDIR = Path(r"E:\03-Book\Photography")

# slug -> (PDF 名关键词, 抽样条数)
PLAN = {
    "color-bible": ("摄影色彩圣经", 8),
    "interacting-with-color": ("Interacting with Color", 6),
    "interaction-of-color": ("Interaction of Color", 6),
    "freeman-sight": ("摄影师的视界", 8),
    "freeman-light": ("光线与用光", 4),
    "chinese-aesthetics": ("中国美学史大纲", 4),
    "meixue-sanbu": ("美学散步", 4),
    "photo-composition-color": ("摄影构图与色彩设计", 0),
    "linquan-gaozhi": ("林泉高致", 0),
}


def find_pdf(key):
    hits = [p for p in PDFDIR.glob("*.pdf") if key.lower() in p.name.lower()]
    if not hits:
        raise SystemExit(f"找不到 PDF：{key}")
    return hits[0]


def norm(s):
    return "".join(ch for ch in s if ch.isalnum())


def load_claims(slug):
    p = BOOKROOT / slug / "claims" / "claims.yaml"
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    items = data.get("claims") if isinstance(data, dict) else data
    return [c for c in items if c.get("quote")]


def page_index_map(cl):
    """复刻 build_book_md.py 的分页口径：按 int(page_idx or 0) 分组后 enumerate(sorted(keys), 1)
    → 即 book.md 的 ## pNNN。"""
    keys = sorted({int(b.get("page_idx") or 0) for b in cl})
    return {idx: pidx for idx, pidx in enumerate(keys, start=1)}


def caption_blocks(cl, pidx):
    """图注块：MinerU 把图注放在 image 块的 image_caption / image_footnote 里，
    自身没有独立 bbox。取图片框并向下扩 18% 高度（图注紧贴图下沿）。"""
    out = []
    for b in cl:
        if int(b.get("page_idx") or 0) != pidx:
            continue
        if b.get("type") != "image":
            continue
        caps = []
        for k in ("image_caption", "image_footnote"):
            v = b.get(k)
            if isinstance(v, list):
                caps.extend([x for x in v if isinstance(x, str)])
            elif isinstance(v, str):
                caps.append(v)
        t = " ".join(x.strip() for x in caps if x and x.strip())
        bbox = b.get("bbox")
        if not t or not bbox or len(bbox) != 4:
            continue
        x0, y0, x1, y1 = bbox
        h = max(1.0, y1 - y0)
        out.append(([x0, y0, x1, min(1000.0, y1 + 0.18 * h)], t))
    return out


def locate(cl, pidx, quote, min_len=8):
    """把该页所有文本块按阅读顺序拼起来（归一化），在其中找引文，返回覆盖到的块的并集 bbox。

    引文经常跨块（book.md 是多块拼接的），所以不能只要求单块包含。
    """
    nq = norm(quote)
    if len(nq) < min_len:
        return None
    blocks = []
    for b in cl:
        if int(b.get("page_idx") or 0) != pidx:
            continue
        if b.get("type") not in ("text", "aside_text", "list", "table", "header", "footer"):
            continue
        t = b.get("text") or b.get("table_body") or ""
        if not t.strip():
            continue
        bbox = b.get("bbox")
        if not bbox or len(bbox) != 4:
            continue
        blocks.append((bbox, t))

    blocks.extend(caption_blocks(cl, pidx))

    if not blocks:
        return None

    # 按 bbox 从上到下、从左到右排
    blocks.sort(key=lambda x: (round(x[0][1] / 4), x[0][0]))

    buf = []
    owner = []
    for i, (bbox, t) in enumerate(blocks):
        nt = norm(t)
        buf.append(nt)
        owner.extend([i] * len(nt))
    full = "".join(buf)

    pos = full.find(nq)
    if pos < 0:
        # 退一步：找引文前 60% 的连续片段
        for frac in (0.9, 0.8, 0.7, 0.6, 0.5):
            head = nq[: max(min_len, int(len(nq) * frac))]
            pos = full.find(head)
            if pos >= 0:
                nq = head
                break
    if pos < 0:
        return None

    idxs = sorted(set(owner[pos: pos + len(nq)]))
    sel = [blocks[i][0] for i in idxs]
    x0 = min(b[0] for b in sel)
    y0 = min(b[1] for b in sel)
    x1 = max(b[2] for b in sel)
    y1 = max(b[3] for b in sel)
    text = " ".join(blocks[i][1] for i in idxs)
    return (x0, y0, x1, y1), text


def page_extent(cl, pidx):
    """实测确认：MinerU pipeline 的 bbox 坐标被归一化到 0–1000（不是 PDF 点、也不是像素）。
    所以换算成页面坐标就是 bbox/1000 * page.width|height。"""
    return 1000.0, 1000.0


def render_crop(doc, page_idx, bbox, ext, target_w=1080, pad=8):
    page = doc[page_idx]
    mx, my = ext
    sx = page.rect.width / mx
    sy = page.rect.height / my
    x0, y0, x1, y1 = bbox[0] * sx, bbox[1] * sy, bbox[2] * sx, bbox[3] * sy
    x0 = max(0.0, x0 - pad); y0 = max(0.0, y0 - pad)
    x1 = min(page.rect.width, x1 + pad); y1 = min(page.rect.height, y1 + pad)
    if x1 - x0 < 4 or y1 - y0 < 4:
        return None
    scale = min(6.0, max(1.5, target_w / max(1.0, (x1 - x0))))
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=fitz.Rect(x0, y0, x1, y1))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    # 过扁的裁图会让视觉模型返回空串；上下补白到至少 420 px 高
    if img.height < 420:
        pad = (420 - img.height) // 2 + 10
        canvas = Image.new("RGB", (img.width, img.height + pad * 2), "white")
        canvas.paste(img, (0, pad))
        img = canvas
    # 固定加 3px 白边：既避免贴边裁切，也让每次重建的字节不同于上一版（避开服务端缓存）
    framed = Image.new("RGB", (img.width + 10, img.height + 10), "white")
    framed.paste(img, (5, 5))
    return framed


def font(size):
    for name in ("msyh.ttc", "simhei.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def build(total, only_slug=None, outdir=None):
    out = Path(outdir) if outdir else OUT
    out.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(20261123)
    manifest = []
    sid = 0
    crops = []

    plan_items = [(only_slug, PLAN[only_slug])] if only_slug else list(PLAN.items())
    for slug, (key, want) in plan_items:
        if only_slug:
            want = total
        claims = load_claims(slug)
        claims.sort(key=lambda c: c["id"])
        if want >= len(claims):
            picked = claims
        else:
            step = len(claims) / want
            picked = [claims[int(i * step)] for i in range(want)]
        pdf = find_pdf(key)
        doc = fitz.open(pdf)
        cl_p = BOOKROOT / slug / "source" / "content_list.json"
        if not cl_p.exists():
            cl_p = ROOT / "out" / "parse" / slug / "content_list.json"
        cl = json.loads(cl_p.read_text(encoding="utf-8"))
        pimap = page_index_map(cl)

        got = 0
        for c in picked:
            if got >= want:
                break
            anchor = c.get("page")
            try:
                md = int(str(anchor).lstrip("p"))
            except Exception:
                print(f"    skip {c['id']}: 锚点无法解析 {anchor!r}")
                continue
            pidx = pimap.get(md)
            if pidx is None:
                print(f"    miss {c['id']}: 锚点 {anchor} 无对应 page_idx")
                continue
            hit = locate(cl, pidx, c["quote"])
            locmode = "block"
            if not hit:
                # 退化方案：整页渲染，由人眼在页面上找这句
                ext = page_extent(cl, pidx)
                hit = ((0, 0, ext[0], ext[1]), "")
                locmode = "page"
                print(f"    fallback {c['id']}: 锚点 {anchor} 块内未命中 → 整页渲染")
            bbox, blocktext = hit
            img = render_crop(doc, pidx, bbox, page_extent(cl, pidx), target_w=1600 if locmode == "page" else 1080)
            if img is None:
                print(f"    skip {c['id']}: bbox 退化 {bbox}")
                continue
            sid += 1
            name = f"S{sid:02d}"
            img.save(out / f"{name}.png")
            got += 1
            manifest.append(
                {
                    "sample_id": name,
                    "book": slug,
                    "claim_id": c["id"],
                    "md_anchor": anchor,
                    "pdf_page_idx": pidx,
                    "pdf_page_1based": pidx + 1,
                    "quote": c["quote"],
                    "block_text": blocktext,
                    "locate": locmode,
                }
            )
            crops.append((name, img.copy()))
        doc.close()
        print(f"{slug:<24} 抽 {got}/{want}")

    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # 4 条一张核对表
    f = font(30)
    for gi in range(0, len(crops), 4):
        group = crops[gi: gi + 4]
        width = max(c[1].width for c in group) + 24
        heights = [c[1].height + 46 for c in group]
        sheet = Image.new("RGB", (width, sum(heights) + 12), "white")
        d = ImageDraw.Draw(sheet)
        y = 6
        for name, im in group:
            d.text((12, y + 6), name, fill=(180, 30, 30), font=f)
            sheet.paste(im, (12, y + 40))
            d.line([(0, y + 40 + im.height + 2), (width, y + 40 + im.height + 2)], fill=(220, 220, 220), width=2)
            y += im.height + 46
        sheet.save(out / f"sheet-{gi // 4 + 1}.png")
    print(f"\n样本 {len(manifest)} 条 · 核对表 {(len(crops) + 3) // 4} 张 → {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build"])
    ap.add_argument("--total", type=int, default=40)
    ap.add_argument("--slug", default=None, help="只抽一本书")
    ap.add_argument("--out", default=None, help="输出目录")
    a = ap.parse_args()
    build(a.total, a.slug, a.out)

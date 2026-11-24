# -*- coding: utf-8 -*-
"""针对单条样本做「按句定位」的精细裁图并重读。

为什么需要：locate() 只能定位到块，一整块 800 字裁下来压到 820 px，
末段的句子就糊掉、模型读不出来（S38 相似度只有 0.18 就是这个原因）。
这里用引文在该块文字里的相对位置，换算成块高上的相对位置，只裁一句话上下的一条带。
"""
import io
import json
import re
import sys
from pathlib import Path

import pymupdf
import requests
from PIL import Image

BOOKROOT = Path("E:/03-Book/Photography")
OUT = Path("out/ocr-sample")
SVC = "http://127.0.0.1:11500"


def norm(s: str) -> str:
    return "".join(ch for ch in s if ch.isalnum())


def find_pdf(key: str) -> Path:
    hits = [p for p in BOOKROOT.glob("*.pdf") if key in p.name]
    if len(hits) != 1:
        raise SystemExit(f"pdf 匹配 {len(hits)} 个：{key}")
    return hits[0]


PDF_KEY = {
    "meixue-sanbu": "美学散步",
    "color-bible": "色彩圣经",
    "freeman-sight": "摄影师的视界",
    "freeman-light": "光线与用光",
    "interacting-with-color": "Interacting with Color",
    "interaction-of-color": "Interaction of Color",
    "chinese-aesthetics": "中国美学史大纲",
    "arnheim-art": "艺术与视知觉",
    "gombrich-illusion": "艺术与错觉",
}


def render_band(pdf: Path, pidx: int, bbox, frac: float, band: float = 0.22,
                target_w: int = 1200) -> Image.Image:
    doc = pymupdf.open(pdf)
    page = doc[pidx]
    W, H = page.rect.width, page.rect.height
    x0, y0, x1, y1 = [v / 1000.0 for v in bbox]
    hh = y1 - y0
    cy = y0 + frac * hh
    ty0 = max(0.0, cy - band * hh)
    ty1 = min(1.0, cy + band * hh)
    clip = pymupdf.Rect(x0 * W, ty0 * H, x1 * W, ty1 * H)
    zoom = target_w / max(1.0, clip.width)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip)
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")


def read(im: Image.Image, name: str, border: int = 0) -> str:
    if border:
        w, h = im.size
        canvas = Image.new("RGB", (w + 2 * border, h + 2 * border), "white")
        canvas.paste(im, (border, border))
        im = canvas
    b = io.BytesIO()
    im.save(b, format="PNG")
    r = requests.post(
        f"{SVC}/v1/describe",
        files={"file": (name, b.getvalue(), "image/png")},
        data={"task_id": "verbatim_transcribe", "force": "1"},
        timeout=900,
    )
    r.raise_for_status()
    return (r.json().get("text") or "").strip()


def main():
    sid = sys.argv[1]
    man = {m["sample_id"]: m for m in json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))}
    m = man[sid]
    book, pidx, quote = m["book"], m["pdf_page_idx"], m["quote"]
    cl = json.loads((Path("out/parse") / book / "content_list.json").read_text(encoding="utf-8"))

    # 找与该块文字一致的块（归一化后前缀匹配）
    target = norm(m["block_text"])[:80]
    block = None
    for b in cl:
        if int(b.get("page_idx") or 0) != pidx:
            continue
        t = b.get("text") or ""
        if norm(t).startswith(target[:40]):
            block = b
            break
    if block is None:
        raise SystemExit("未找到块")

    nb = norm(block["text"])
    nq = norm(quote)
    pos = nb.find(nq)
    if pos < 0:
        raise SystemExit("块内找不到引文")
    frac = (pos + len(nq) / 2) / max(1, len(nb))
    print(f"{sid}: 块 {block['bbox']} 引文位于块内 {pos}/{len(nb)} → frac={frac:.3f}")

    pdf = find_pdf(PDF_KEY[book])
    for band in (0.22, 0.14, 0.30):
        im = render_band(pdf, pidx, block["bbox"], frac, band)
        im.save(OUT / f"{sid}_band{band}.png")
        for border in (0, 1):
            txt = read(im, f"{sid}_band{band}_{border}.png", border)
            print(f"  band={band} border={border} → {len(txt)} 字")
            if txt and nq in norm(txt):
                print("  ✓ 引文整句在转写内")
                _write(sid, txt, f"band{band}")
                return
            if txt and len(txt) > 20:
                _write(sid, txt, f"band{band}")
                print("  · 有转写但未逐字命中，先落盘（供 diff 判相似度）")
                return
    print("  ✗ 三档 band 都没读出来")


def _write(sid: str, txt: str, via: str):
    jl = OUT / "transcripts.jsonl"
    lines = []
    for line in jl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("sample_id") == sid:
            continue
        lines.append(rec)
    lines.append({"sample_id": sid, "ok": True, "text": txt, "ms": 0, "via": via, "recovered": True})
    jl.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in lines), encoding="utf-8")


if __name__ == "__main__":
    main()

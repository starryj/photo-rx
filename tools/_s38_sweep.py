# -*- coding: utf-8 -*-
"""S38 专用：在块高上扫几个窗口，直到转写里出现引文整句。"""
import io
import json
import sys
from pathlib import Path

import pymupdf
import requests
from PIL import Image

OUT = Path("out/ocr-sample")
SVC = "http://127.0.0.1:11500"
PDF = [p for p in Path("E:/03-Book/Photography").glob("*.pdf") if "美学散步" in p.name][0]


def norm(s):
    return "".join(ch for ch in s if ch.isalnum())


def read(im, name, border=1):
    if border:
        w, h = im.size
        c = Image.new("RGB", (w + 2 * border, h + 2 * border), "white")
        c.paste(im, (border, border))
        im = c
    b = io.BytesIO()
    im.save(b, format="PNG")
    r = requests.post(f"{SVC}/v1/describe", files={"file": (name, b.getvalue(), "image/png")},
                      data={"task_id": "verbatim_transcribe", "force": "1"}, timeout=900)
    r.raise_for_status()
    return (r.json().get("text") or "").strip()


man = {m["sample_id"]: m for m in json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))}
m = man["S38"]
quote = m["quote"]
nq = norm(quote)

cl = json.loads(Path("out/parse/meixue-sanbu/content_list.json").read_text(encoding="utf-8"))
block = None
for b in cl:
    if int(b.get("page_idx") or 0) == 131 and (b.get("text") or "").startswith("乃吾见诸前辈画"):
        block = b
        break
print("block", block["bbox"])

doc = pymupdf.open(PDF)
page = doc[131]
W, H = page.rect.width, page.rect.height
x0, y0, x1, y1 = [v / 1000.0 for v in block["bbox"]]
hh = y1 - y0

best = ""
for frac, band in [(0.55, 0.12), (0.62, 0.12), (0.70, 0.12), (0.78, 0.12), (0.62, 0.18)]:
    cy = y0 + frac * hh
    ty0 = max(0.0, cy - band * hh)
    ty1 = min(1.0, cy + band * hh)
    clip = pymupdf.Rect(x0 * W, ty0 * H, x1 * W, ty1 * H)
    zoom = 1200 / max(1.0, clip.width)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip)
    im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    im.save(OUT / f"S38_f{frac}_b{band}.png")
    txt = read(im, f"S38_f{frac}_b{band}.png")
    hit = nq in norm(txt)
    print(f"frac={frac} band={band} → {len(txt)} 字 hit={hit}")
    if txt:
        best = txt
    if hit:
        break

if best:
    jl = OUT / "transcripts.jsonl"
    lines = []
    for line in jl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("sample_id") == "S38":
            continue
        lines.append(rec)
    lines.append({"sample_id": "S38", "ok": True, "text": best, "ms": 0,
                  "via": f"sweep f{frac} b{band}", "recovered": True})
    jl.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in lines), encoding="utf-8")
    print("saved; hit =", nq in norm(best))
    print(best)

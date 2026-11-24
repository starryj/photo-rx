# -*- coding: utf-8 -*-
"""S38 收尾：把整块按高度切 6 条（带 15% 重叠）逐条读，拼起来找那一句。

不再猜比例——直接覆盖全块，哪条命中就用哪条；命中的那条单独存为证据裁图。
"""
import io
import json
from pathlib import Path

import pymupdf
import requests
from PIL import Image

OUT = Path("out/ocr-sample")
SVC = "http://127.0.0.1:11500"
PDF = [p for p in Path("E:/03-Book/Photography").glob("*.pdf") if "美学散步" in p.name][0]
NQ = "似离而合四字实推之神髓"


def norm(s):
    return "".join(ch for ch in s if ch.isalnum())


def read(im, name, border=1):
    w, h = im.size
    if border:
        c = Image.new("RGB", (w + 2 * border, h + 2 * border), "white")
        c.paste(im, (border, border))
        im = c
    b = io.BytesIO()
    im.save(b, format="PNG")
    r = requests.post(f"{SVC}/v1/describe", files={"file": (name, b.getvalue(), "image/png")},
                      data={"task_id": "verbatim_transcribe", "force": "1"}, timeout=900)
    r.raise_for_status()
    return (r.json().get("text") or "").strip()


cl = json.loads(Path("out/parse/meixue-sanbu/content_list.json").read_text(encoding="utf-8"))
block = next(b for b in cl if int(b.get("page_idx") or 0) == 131 and (b.get("text") or "").startswith("乃吾见诸前辈画"))
x0, y0, x1, y1 = [v / 1000.0 for v in block["bbox"]]

doc = pymupdf.open(PDF)
page = doc[131]
W, H = page.rect.width, page.rect.height
hh = y1 - y0

parts, hit_txt, hit_tag = [], "", ""
n = 6
ov = 0.15
step = hh / n
for i in range(n):
    ty0 = max(0.0, y0 + i * step - ov * step)
    ty1 = min(1.0, y0 + (i + 1) * step + ov * step)
    clip = pymupdf.Rect(x0 * W, ty0 * H, x1 * W, ty1 * H)
    zoom = 1300 / max(1.0, clip.width)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip)
    im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    tag = f"S38_s{i+1}"
    im.save(OUT / f"{tag}.png")
    txt = read(im, f"{tag}.png")
    ok = NQ in norm(txt)
    print(f"{tag} → {len(txt)} 字 hit={ok}")
    if txt:
        parts.append(txt)
    if ok:
        hit_txt, hit_tag = txt, tag
        break

final = hit_txt or "\n".join(parts)
jl = OUT / "transcripts.jsonl"
lines = []
for line in jl.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    rec = json.loads(line)
    if rec.get("sample_id") == "S38":
        continue
    lines.append(rec)
lines.append({"sample_id": "S38", "ok": bool(final), "text": final, "ms": 0,
              "via": f"strip-scan {hit_tag or 'joined'}", "recovered": True})
jl.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in lines), encoding="utf-8")
print("saved. hit =", bool(hit_txt))
print(final[:400])

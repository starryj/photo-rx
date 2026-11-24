# -*- coding: utf-8 -*-
"""渲染校准页 + 拼一张联系表（便于一次看全）。"""
from __future__ import annotations

import json
from pathlib import Path

import pymupdf as fitz
from PIL import Image, ImageDraw

BOOK_DIR = Path(r"E:\03-Book\Photography")
OUT = Path(__file__).resolve().parent.parent / "out" / "calib"

PICKS = [
    ("interacting", "Interacting with Color A Pr_ (z-library.sk, 1lib.sk, z-lib.sk).pdf", 31),
    ("ioc", "Interaction of Color 50th A_ (z-library.sk, 1lib.sk, z-lib.sk).pdf", 126),
    ("arnheim", "艺术与视知觉（35周年纪念版） (鲁道夫·阿恩海姆) (z-library.sk, 1lib.sk, z-lib.sk).pdf", 26),
    ("arnheim2", "艺术与视知觉（35周年纪念版） (鲁道夫·阿恩海姆) (z-library.sk, 1lib.sk, z-lib.sk).pdf", 530),
    ("gombrich", "艺术与错觉：图画再现的心理学研究 (（英）E·H·贡布_ (z-library.sk, 1lib.sk, z-lib.sk)-1.pdf", 56),
    ("zhongguo", "中国美学史大纲 (叶朗) (z-library.sk, 1lib.sk, z-lib.sk).pdf", 286),
    ("meixue", "美学散步（彩图本） (宗白华) (z-library.sk, 1lib.sk, z-lib.sk)-1.pdf", 111),
    ("shengjing", "摄影色彩圣经 摄影师的色彩视觉必修课=THE PHOT_ (z-library.sk, 1lib.sk, z-lib.sk).pdf", 96),
    ("shijie", "摄影师的视界迈克尔·弗里曼摄影构图与设计(10周年纪念_ (z-library.sk, 1lib.sk, z-lib.sk).pdf", 166),
    ("guangxian", "迈克尔·弗里曼摄影大师班 光线与用光 彩印 (宋杰，张_ (z-library.sk, 1lib.sk, z-lib.sk).pdf", 121),
]

CELL_W = 620
PAD = 14
LABEL_H = 26


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cells = []
    for key, fname, pno in PICKS:
        pdf = BOOK_DIR / fname
        doc = fitz.open(pdf)
        page = doc[pno - 1]
        zoom = 1400 / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csRGB, alpha=False)
        dest = OUT / f"{key}_p{pno}.png"
        pix.save(dest)
        cells.append((f"{key} p{pno}", dest))
        doc.close()
        print(f"OK {key} p{pno} {pix.width}x{pix.height}")

    imgs = []
    for label, path in cells:
        im = Image.open(path).convert("RGB")
        h = int(im.height * CELL_W / im.width)
        imgs.append((label, im.resize((CELL_W, h), Image.LANCZOS)))

    rows = (len(imgs) + 1) // 2
    row_h = max(im.height for _, im in imgs if im.width == CELL_W) if False else 0
    # 每行高度取该行两张的最大值
    heights = []
    for r in range(rows):
        pair = imgs[r * 2:r * 2 + 2]
        heights.append(max(im.height for _, im in pair) + LABEL_H)
    W = CELL_W * 2 + PAD * 3
    H = sum(heights) + PAD * (rows + 1)
    sheet = Image.new("RGB", (W, H), (245, 245, 243))
    dr = ImageDraw.Draw(sheet)
    y = PAD
    for r in range(rows):
        pair = imgs[r * 2:r * 2 + 2]
        x = PAD
        for label, im in pair:
            dr.rectangle([x, y, x + CELL_W - 1, y + LABEL_H + im.height + 1], fill=(255, 255, 255), outline=(210, 210, 205))
            dr.text((x + 6, y + 6), label, fill=(20, 20, 20))
            sheet.paste(im, (x, y + LABEL_H))
            x += CELL_W + PAD
        y += heights[r] + PAD
    dest = OUT / "_contact_sheet.png"
    sheet.save(dest)
    print(f"SHEET {dest} {sheet.width}x{sheet.height}")
    (OUT / "picks.json").write_text(json.dumps(PICKS, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

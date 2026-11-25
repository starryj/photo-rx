"""Crop candidate swatch boxes and tile them for visual verification."""
from pathlib import Path

from PIL import Image, ImageDraw

SRC = Path(r"C:\Users\27669\.dsh\attachments\v1\objects\e2\e2e6fa93d1e2e150e82f9237d3df640c40db19b7f1a231fcf03189df6063701c")
OUT = Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\blue-hour-village-v2\swatch-check.png")

CAND = [
    ("A sky", (0.32, 0.02, 0.62, 0.08)),
    ("B glow-top", (0.70, 0.10, 0.90, 0.20)),
    ("C pool", (0.58, 0.58, 0.74, 0.72)),
    ("D houses-left", (0.06, 0.28, 0.22, 0.40)),
    ("E houses-mid", (0.22, 0.26, 0.34, 0.36)),
    ("F snow-fg", (0.30, 0.86, 0.62, 0.97)),
    ("G shadow-left", (0.01, 0.52, 0.12, 0.66)),
    ("H red-house", (0.170, 0.305, 0.212, 0.375)), ("I yellow-house", (0.088, 0.305, 0.128, 0.360)), ("J lane-blue", (0.60, 0.40, 0.78, 0.50)),
]

TILE = 220


def main():
    src = Image.open(SRC).convert("RGB")
    w, h = src.size
    sheet = Image.new("RGB", (TILE * len(CAND), TILE + 26), (250, 250, 250))
    dr = ImageDraw.Draw(sheet)
    for i, (name, box) in enumerate(CAND):
        px = (int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h))
        crop = src.crop(px).resize((TILE - 8, TILE - 8), Image.LANCZOS)
        sheet.paste(crop, (i * TILE + 4, 4))
        avg = src.crop(px).resize((1, 1), Image.BOX).getpixel((0, 0))
        dr.text((i * TILE + 6, TILE + 6), f"{name} #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}", fill=(20, 20, 20))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT, quality=92)
    print(OUT)


if __name__ == "__main__":
    main()


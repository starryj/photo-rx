"""Dump labelled crops of the patches so coordinates can be verified by eye."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path(r"C:\Users\27669\.dsh\attachments\v1\objects\e2\e2e6fa93d1e2e150e82f9237d3df640c40db19b7f1a231fcf03189df6063701c")
OUT = Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\blue-hour-village")
img = Image.open(SRC).convert("RGB")
W, H = img.size

BOXES = {
    "yellow_house_left": (0.060, 0.520, 0.200, 0.600),
    "red_house_upper_left": (0.200, 0.285, 0.262, 0.360),
    "red_house_center_left": (0.312, 0.385, 0.368, 0.462),
    "blue_house_center": (0.530, 0.425, 0.605, 0.500),
    "purple_house_center": (0.480, 0.552, 0.552, 0.620),
    "green_house_lower": (0.315, 0.660, 0.445, 0.745),
    "red_house_right": (0.638, 0.410, 0.690, 0.470),
    "green_house_right": (0.735, 0.405, 0.775, 0.452),
    "brown_house_right": (0.870, 0.490, 0.920, 0.575),
    "bright_blue_house_right": (0.765, 0.590, 0.832, 0.665),
    "lamp_pool_snow": (0.600, 0.660, 0.700, 0.740),
}

CELL_W, CELL_H = 340, 260
cols = 4
rows = (len(BOXES) + cols - 1) // cols
sheet = Image.new("RGB", (cols * CELL_W, rows * (CELL_H + 22)), (20, 20, 20))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 15)
except Exception:
    font = ImageFont.load_default()

for i, (name, (x0, y0, x1, y1)) in enumerate(BOXES.items()):
    crop = img.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
    crop.thumbnail((CELL_W, CELL_H), Image.LANCZOS)
    cx = (i % cols) * CELL_W
    cy = (i // cols) * (CELL_H + 22)
    sheet.paste(crop, (cx + (CELL_W - crop.width) // 2, cy + (CELL_H - crop.height) // 2))
    d.text((cx + 4, cy + CELL_H + 2), name, fill=(255, 230, 120), font=font)

sheet.save(OUT / "patch-check.jpg", quality=92)
print("saved", OUT / "patch-check.jpg", sheet.size)

"""Make a coordinate-grid reference image so patches can be addressed correctly."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path(r"C:\Users\27669\.dsh\attachments\v1\objects\e2\e2e6fa93d1e2e150e82f9237d3df640c40db19b7f1a231fcf03189df6063701c")
OUT = Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\blue-hour-village")
OUT.mkdir(parents=True, exist_ok=True)

img = Image.open(SRC).convert("RGB").resize((1400, 933), Image.LANCZOS)
d = ImageDraw.Draw(img)
W, H = img.size
try:
    font = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 18)
except Exception:
    font = ImageFont.load_default()

for i in range(1, 10):
    x = int(W * i / 10)
    y = int(H * i / 10)
    d.line([(x, 0), (x, H)], fill=(255, 60, 60), width=1)
    d.line([(0, y), (W, y)], fill=(255, 60, 60), width=1)
    d.text((x + 3, 3), f"{i/10:.1f}", fill=(255, 255, 0), font=font)
    d.text((3, y + 2), f"{i/10:.1f}", fill=(255, 255, 0), font=font)

img.save(OUT / "grid.jpg", quality=90)
print("saved", OUT / "grid.jpg", img.size)

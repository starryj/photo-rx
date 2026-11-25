"""Put an identifying band on top of each draft PNG so they can be told apart."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

JOBS = [
    (r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\dsc-7326\draft-j.png",
     "J", "竖图 · 照你的手绘（黑框列表）"),
    (r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\dsc-7326\draft-k.png",
     "K", "竖图 · 同骨架换排印（发丝线、宋体）"),
    (r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\blue-hour-village-v2\draft-l.png",
     "L", "横图 · 照你的手绘（通栏 + 两栏）"),
    (r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\blue-hour-village-v2\draft-m.png",
     "M", "横图 · 换排印（分数压角牌、六维分两列）"),
]

BAND = 116


def font(size, bold=False):
    for name in ("msyhbd.ttc" if bold else "msyh.ttc", "simhei.ttf", "seguisb.ttf"):
        p = Path(r"C:\Windows\Fonts") / name
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except OSError:
                continue
    return ImageFont.load_default()


def main():
    for src, tag, desc in JOBS:
        im = Image.open(src).convert("RGB")
        w, h = im.size
        sheet = Image.new("RGB", (w, h + BAND), (255, 255, 255))
        sheet.paste(im, (0, BAND))
        dr = ImageDraw.Draw(sheet)
        dr.rectangle([0, 0, w, BAND - 1], fill=(18, 63, 74))
        dr.text((28, 12), tag, font=font(58, True), fill=(255, 255, 255))
        dr.text((110, 44), desc, font=font(30), fill=(200, 224, 230))
        out = Path(src).with_name(Path(src).stem + "-labeled.png")
        sheet.save(out)
        print(out)


if __name__ == "__main__":
    main()

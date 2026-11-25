"""Round 5: corrected facade patches (coordinates read off grid.jpg)."""
import json
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(r"C:\Users\27669\.dsh\attachments\v1\objects\e2\e2e6fa93d1e2e150e82f9237d3df640c40db19b7f1a231fcf03189df6063701c")
img = Image.open(SRC).convert("RGB")
a_full = np.asarray(img.resize((1200, 800), Image.LANCZOS)).astype(np.float32) / 255.0
h, w = a_full.shape[:2]

def lab_patch(box):
    x0, y0, x1, y1 = box
    xs, xe = int(x0 * w), int(x1 * w)
    ys, ye = int(y0 * h), int(y1 * h)
    sub = a_full[ys:ye, xs:xe].reshape(-1, 3)
    m = np.median(sub, axis=0)
    mx, mn = float(m.max()), float(m.min())
    s = 0.0 if mx == 0 else (mx - mn) / mx
    if mx == mn:
        hue = None
    elif mx == m[0]:
        hue = ((m[1] - m[2]) / (mx - mn)) % 6 * 60
    elif mx == m[1]:
        hue = ((m[2] - m[0]) / (mx - mn) + 2) * 60
    else:
        hue = ((m[0] - m[1]) / (mx - mn) + 4) * 60
    lin = np.where(m <= 0.04045, m / 12.92, ((m + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = (lin @ M.T) / np.array([0.95047, 1.0, 1.08883])
    d = 6 / 29
    f = lambda t: t ** (1 / 3) if t > d ** 3 else t / (3 * d * d) + 4 / 29
    fx, fy, fz = [f(v) for v in xyz]
    L = 116 * fy - 16
    C = float(np.hypot(500 * (fx - fy), 200 * (fy - fz)))
    # 该块内最亮 2% 像素（窗光）与中位
    lum = sub @ np.array([0.2126, 0.7152, 0.0722])
    return {"rgb": [round(float(v * 255)) for v in m],
            "hue": None if hue is None else round(float(hue), 1),
            "S": round(float(s), 2), "L": round(float(L), 1), "C": round(C, 1),
            "L_p98": round(float(np.percentile(sub @ np.array([0.2126, 0.7152, 0.0722]), 98) * 100), 1)}

BOXES = {
    "yellow_house_left": (0.060, 0.520, 0.200, 0.600),
    "red_house_upper_left": (0.200, 0.285, 0.262, 0.360),
    "blue_base_upper_left": (0.205, 0.370, 0.265, 0.415),
    "red_house_center_left": (0.312, 0.385, 0.368, 0.462),
    "grey_house_center_left": (0.245, 0.405, 0.310, 0.455),
    "blue_house_center": (0.530, 0.425, 0.605, 0.500),
    "purple_house_center": (0.480, 0.552, 0.552, 0.620),
    "green_house_lower": (0.315, 0.660, 0.445, 0.745),
    "red_house_right": (0.638, 0.410, 0.690, 0.470),
    "green_house_right": (0.735, 0.405, 0.775, 0.452),
    "brown_house_right": (0.870, 0.490, 0.920, 0.575),
    "bright_blue_house_right": (0.765, 0.590, 0.832, 0.665),
    "white_house_bottom_right": (0.700, 0.750, 0.780, 0.850),
    "snow_foreground": (0.100, 0.860, 0.300, 0.950),
    "snow_mid_bank": (0.300, 0.520, 0.380, 0.580),
    "lamp_pool_snow": (0.600, 0.660, 0.700, 0.740),
    "sky_upper_left": (0.050, 0.030, 0.300, 0.120),
    "sky_mauve_glow": (0.700, 0.175, 0.930, 0.215),
    "sea_ice": (0.800, 0.255, 0.960, 0.310),
    "mountain_ridge": (0.120, 0.235, 0.400, 0.300),
    "figures": (0.555, 0.720, 0.600, 0.775),
}
out = {k: lab_patch(v) for k, v in BOXES.items()}
print(json.dumps(out, ensure_ascii=False, indent=2))
Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\blue-hour-village\patches.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

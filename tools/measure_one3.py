"""Round 3: sample the coloured facades directly (no global hue thresholds).

Prints median HSV + Lab for hand-picked facade patches so the palette numbers
come from actual pixels, not from a hue-family guess.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(r"C:\Users\27669\.dsh\attachments\v1\objects\e2\e2e6fa93d1e2e150e82f9237d3df640c40db19b7f1a231fcf03189df6063701c")
img = Image.open(SRC).convert("RGB")
W, H = img.size
small = img.resize((1200, 800), Image.LANCZOS)
a = np.asarray(small).astype(np.float32) / 255.0
h, w = a.shape[:2]

def med(box):
    x0, y0, x1, y1 = [int(v * (w if i % 2 == 0 else h)) for i, v in enumerate(box)]
    sub = a[y0:y1, x0:x1].reshape(-1, 3)
    m = np.median(sub, axis=0)
    r, g, b = m
    mx, mn = m.max(), m.min()
    s = 0 if mx == 0 else (mx - mn) / mx
    if mx == mn:
        hue = None
    elif mx == r:
        hue = ((g - b) / (mx - mn)) % 6 * 60
    elif mx == g:
        hue = ((b - r) / (mx - mn) + 2) * 60
    else:
        hue = ((r - g) / (mx - mn) + 4) * 60
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
    return {"rgb255": [round(float(v * 255)) for v in m],
            "hue": None if hue is None else round(float(hue), 1),
            "S": round(float(s), 2), "L": round(float(L), 1), "C": round(C, 1)}

BOXES = {
    "yellow_house_left": (0.045, 0.470, 0.115, 0.600),
    "red_house_upper_left": (0.195, 0.280, 0.255, 0.395),
    "blue_white_house_top_left": (0.030, 0.250, 0.085, 0.315),
    "red_house_center_left": (0.305, 0.405, 0.355, 0.470),
    "blue_house_center": (0.520, 0.430, 0.590, 0.520),
    "purple_house_center": (0.485, 0.530, 0.545, 0.615),
    "green_house_lower": (0.310, 0.640, 0.395, 0.750),
    "red_house_right": (0.640, 0.415, 0.700, 0.500),
    "blue_house_right": (0.755, 0.555, 0.815, 0.665),
    "brown_house_right": (0.855, 0.505, 0.925, 0.620),
    "white_house_bottom_right": (0.685, 0.715, 0.775, 0.845),
    "snow_shadow_fg": (0.080, 0.870, 0.250, 0.960),
    "snow_banked_mid": (0.300, 0.520, 0.380, 0.590),
    "snow_lit_by_lamp": (0.560, 0.680, 0.640, 0.740),
    "sky_upper_left": (0.050, 0.030, 0.300, 0.120),
    "sky_upper_right_mauve": (0.640, 0.045, 0.900, 0.130),
    "sea_ice_horizon": (0.780, 0.170, 0.960, 0.215),
    "mountain_ridge_left": (0.100, 0.175, 0.350, 0.235),
}
out = {k: med(v) for k, v in BOXES.items()}
print(json.dumps(out, ensure_ascii=False, indent=2))

# 非蓝的彩绘面积（红/橙/黄/绿/紫），阈值放宽到 S>=0.30
mx = a.max(axis=2); mn = a.min(axis=2); delta = mx - mn
S = np.where(mx > 1e-6, delta / np.maximum(mx, 1e-6), 0)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
Hh = np.zeros_like(mx); m = delta > 1e-6
i1 = m & (mx == r); Hh[i1] = ((g[i1] - b[i1]) / delta[i1]) % 6
i2 = m & (mx == g); Hh[i2] = (b[i2] - r[i2]) / delta[i2] + 2
i3 = m & (mx == b); Hh[i3] = (r[i3] - g[i3]) / delta[i3] + 4
Hdeg = Hh * 60
nonblue = ((Hdeg >= 345) | (Hdeg < 70) | ((Hdeg >= 70) & (Hdeg < 165)) | (Hdeg >= 260)) & (S >= 0.30) & (mx >= 0.10)
print("non-blue painted share %:", round(100 * float(nonblue.sum()) / (w * h), 2))
ys, xs = np.nonzero(nonblue)
print("non-blue centroid:", round(float(xs.mean() / w), 3), round(float(ys.mean() / h), 3))

"""Final colour sampling: 5x5 medians at hand-picked interior points."""
import json
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(r"C:\Users\27669\.dsh\attachments\v1\objects\e2\e2e6fa93d1e2e150e82f9237d3df640c40db19b7f1a231fcf03189df6063701c")
img = Image.open(SRC).convert("RGB")
a = np.asarray(img).astype(np.float32)
H, W = a.shape[:2]

def pick(fx, fy, k=4):
    x, y = int(fx * W), int(fy * H)
    sub = a[max(0, y - k):y + k + 1, max(0, x - k):x + k + 1].reshape(-1, 3)
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
    fx_, fy_, fz_ = [f(v) for v in xyz]
    L = 116 * fy_ - 16
    C = float(np.hypot(500 * (fx_ - fy_), 200 * (fy_ - fz_)))
    return {"rgb": [round(float(v)) for v in m],
            "hue": None if hue is None else round(float(hue)),
            "S": round(float(s), 2), "L": round(float(L), 1), "C": round(C, 1)}

PTS = {
    "yellow_wall_a": (0.115, 0.560), "yellow_wall_b": (0.180, 0.575),
    "red_ul_wall_a": (0.225, 0.320), "red_ul_wall_b": (0.248, 0.300),
    "blue_base_ul": (0.235, 0.398),
    "red_cl_wall_a": (0.335, 0.420), "red_cl_wall_b": (0.345, 0.445),
    "blue_center_wall_a": (0.560, 0.450), "blue_center_wall_b": (0.578, 0.472),
    "purple_wall_a": (0.505, 0.575), "purple_wall_b": (0.522, 0.592),
    "green_wall_a": (0.350, 0.690), "green_wall_b": (0.380, 0.702),
    "red_right_wall": (0.657, 0.432),
    "bright_blue_right_wall": (0.792, 0.622), "bright_blue_right_b": (0.805, 0.645),
    "brown_right_wall": (0.890, 0.520),
    "window_warm_1": (0.423, 0.428), "window_warm_2": (0.784, 0.460),
    "lamp_head": (0.648, 0.531), "lamp_snow_bright": (0.640, 0.690),
    "snow_shadow_deep": (0.150, 0.900), "snow_slope_lit": (0.480, 0.860),
    "sky_zenith": (0.500, 0.040), "sky_mauve": (0.800, 0.195),
    "ridge_shadow": (0.200, 0.270), "sea_ice_far": (0.880, 0.280),
    "figure_1": (0.566, 0.745), "figure_2": (0.590, 0.748),
}
res = {k: pick(*v) for k, v in PTS.items()}
print(json.dumps(res, ensure_ascii=False, indent=2))
Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\blue-hour-village\points.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

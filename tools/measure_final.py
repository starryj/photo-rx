"""Final measurement (corrected Lab normalisation) + facade chroma clusters.

For each verified facade crop, take the most chromatic quartile inside the crop
as the facade's own colour under the blue cast (robust to roofs, snow, frames).
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(r"C:\Users\27669\.dsh\attachments\v1\objects\e2\e2e6fa93d1e2e150e82f9237d3df640c40db19b7f1a231fcf03189df6063701c")
OUT = Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\blue-hour-village")
img = Image.open(SRC).convert("RGB")
a = np.asarray(img).astype(np.float32) / 255.0
H, W = a.shape[:2]

M = np.array([[0.4124564, 0.3575761, 0.1804375],
              [0.2126729, 0.7151522, 0.0721750],
              [0.0193339, 0.1191920, 0.9503041]])
D65 = np.array([0.95047, 1.0, 1.08883])
d = 6 / 29

def lab(rgb01):
    rgb01 = np.atleast_2d(rgb01)
    lin = np.where(rgb01 <= 0.04045, rgb01 / 12.92, ((rgb01 + 0.055) / 1.055) ** 2.4)
    xyz = (lin @ M.T) / D65
    f = lambda t: np.where(t > d ** 3, np.cbrt(t), t / (3 * d * d) + 4 / 29)
    fx, fy, fz = f(xyz[:, 0]), f(xyz[:, 1]), f(xyz[:, 2])
    L = 116 * fy - 16
    A = 500 * (fx - fy)
    B = 200 * (fy - fz)
    return L, A, B, np.hypot(A, B)

def hsv(rgb01):
    mx = rgb01.max(axis=-1); mn = rgb01.min(axis=-1); dl = mx - mn
    v = mx
    s = np.where(mx > 1e-6, dl / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb01[..., 0], rgb01[..., 1], rgb01[..., 2]
    h = np.zeros_like(mx)
    m = dl > 1e-6
    rl = m & (mx == r); h[rl] = ((g[rl] - b[rl]) / dl[rl]) % 6
    gl = m & (mx == g); h[gl] = (b[gl] - r[gl]) / dl[gl] + 2
    bl = m & (mx == b); h[bl] = (r[bl] - g[bl]) / dl[bl] + 4
    return h * 60, s, v

def crop_px(box):
    x0, y0, x1, y1 = box
    return a[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)].reshape(-1, 3)

def cluster(name, box, q=0.75):
    px = crop_px(box)
    hh, ss, vv = hsv(px)
    L, A, B, C = lab(px)
    thr = np.quantile(C, q)
    sel = px[C >= thr]
    Ls, As, Bs, Cs = lab(sel)
    hs, ss2, _ = hsv(sel)
    med = np.median(sel, axis=0)
    return {
        "name": name,
        "rgb_med_of_chromatic_quartile": [round(float(v * 255)) for v in med],
        "hue": round(float(np.median(hs))),
        "S": round(float(np.median(ss2)), 2),
        "L": round(float(np.median(Ls)), 1),
        "C": round(float(np.median(Cs)), 1),
        "frame_L_med": round(float(np.median(L)), 1),
        "px": int(len(px)),
    }

FACADES = {
    "yellow_house_left": (0.060, 0.520, 0.200, 0.600),
    "red_house_upper_left": (0.200, 0.285, 0.262, 0.360),
    "blue_house_center": (0.530, 0.425, 0.605, 0.500),
    "purple_house_center": (0.480, 0.552, 0.552, 0.620),
    "green_house_lower": (0.315, 0.660, 0.445, 0.745),
    "red_house_center_left": (0.312, 0.385, 0.368, 0.462),
    "bright_blue_house_right": (0.765, 0.590, 0.832, 0.665),
    "brown_house_right": (0.870, 0.490, 0.920, 0.575),
}
facades = [cluster(k, v) for k, v in FACADES.items()]

def flat(name, box):
    px = crop_px(box)
    L, A, B, C = lab(px)
    h, s, v = hsv(px)
    med = np.median(px, axis=0)
    return {"name": name, "rgb": [round(float(x * 255)) for x in med],
            "hue": round(float(np.median(h))), "S": round(float(np.median(s)), 2),
            "L": round(float(np.median(L)), 1), "C": round(float(np.median(C)), 1)}

FLATS = {
    "sky_top": (0.05, 0.03, 0.30, 0.12),
    "sky_mauve_glow": (0.70, 0.175, 0.93, 0.215),
    "ridge": (0.12, 0.235, 0.40, 0.300),
    "sea_ice": (0.80, 0.255, 0.96, 0.310),
    "snow_shadow_fg": (0.10, 0.860, 0.30, 0.950),
    "snow_slope": (0.45, 0.830, 0.55, 0.880),
    "lamp_pool": (0.60, 0.660, 0.70, 0.740),
    "figures_area": (0.555, 0.720, 0.600, 0.775),
}
flats = [flat(k, v) for k, v in FLATS.items()]
win = cluster("window_light", (0.410, 0.415, 0.440, 0.445), q=0.9)

res = {"size": [W, H], "facades": facades, "flats": flats, "window": win}
print(json.dumps(res, ensure_ascii=False, indent=2))
(OUT / "final.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

# 全局层级占比（沿用 round1 口径，重算一遍确认）
h_all, s_all, v_all = hsv(a)
L_all, A_all, B_all, C_all = lab(a.reshape(-1, 3))
tot = a.shape[0] * a.shape[1]
blue = ((h_all >= 195) & (h_all < 260) & (s_all >= 0.22)).sum()
neutral = (s_all < 0.22).sum()
warm = ((h_all >= 15) & (h_all < 65) & (C_all.reshape(a.shape[:2]) > 18) & (L_all.reshape(a.shape[:2]) > 55)).sum()
print(json.dumps({"blue_pct": round(100 * blue / tot, 2),
                  "neutral_pct": round(100 * neutral / tot, 2),
                  "warm_lit_pct": round(100 * warm / tot, 2)}, ensure_ascii=False))

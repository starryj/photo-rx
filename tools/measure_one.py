"""One-off measurement for a single photo (photo-rx diagnosis).

Outputs a fact table: dimensions, L stats per region, hue-family area shares,
saturated-color blobs (position + area), warm-light blobs.
No numbers are invented: everything printed here is computed from the pixels.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(r"C:\Users\27669\.dsh\attachments\v1\objects\e2\e2e6fa93d1e2e150e82f9237d3df640c40db19b7f1a231fcf03189df6063701c")
OUT = Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\blue-hour-village")
OUT.mkdir(parents=True, exist_ok=True)

img = Image.open(SRC).convert("RGB")
W, H = img.size
small = img.resize((min(W, 1200), int(min(W, 1200) * H / W)), Image.LANCZOS)
a = np.asarray(small).astype(np.float32) / 255.0
h, w = a.shape[:2]

# sRGB -> linear -> XYZ -> Lab (D65)
def to_linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

lin = to_linear(a)
M = np.array([[0.4124564, 0.3575761, 0.1804375],
              [0.2126729, 0.7151522, 0.0721750],
              [0.0193339, 0.1191920, 0.9503041]])
xyz = lin @ M.T
xyz /= np.array([0.95047, 1.0, 1.08883])

def f(t):
    d = 6 / 29
    return np.where(t > d ** 3, np.cbrt(t), t / (3 * d * d) + 4 / 29)

fx, fy, fz = f(xyz[..., 0]), f(xyz[..., 1]), f(xyz[..., 2])
L = 116 * fy - 16
A = 500 * (fx - fy)
B = 200 * (fy - fz)

C = np.sqrt(A ** 2 + B ** 2)

# HSV for hue families
mx = a.max(axis=2)
mn = a.min(axis=2)
delta = mx - mn
S = np.where(mx > 1e-6, delta / np.maximum(mx, 1e-6), 0)

r, g, b = a[..., 0], a[..., 1], a[..., 2]
Hh = np.zeros_like(mx)
m = delta > 1e-6
idx = m & (mx == r)
Hh[idx] = ((g[idx] - b[idx]) / delta[idx]) % 6
idx = m & (mx == g)
Hh[idx] = (b[idx] - r[idx]) / delta[idx] + 2
idx = m & (mx == b)
Hh[idx] = (r[idx] - g[idx]) / delta[idx] + 4
Hdeg = Hh * 60

FAMILIES = [("red", 345, 15), ("orange", 15, 45), ("yellow", 45, 70),
            ("green", 70, 165), ("cyan", 165, 200), ("blue", 200, 260),
            ("purple", 260, 345)]

def fam_mask(lo, hi):
    if lo < hi:
        return (Hdeg >= lo) & (Hdeg < hi)
    return (Hdeg >= lo) | (Hdeg < hi)

SAT_MIN = 0.22   # 只认定「看得出颜色」的像素，压掉雪面的微弱偏色
VAL_MIN = 0.12
base = (S >= SAT_MIN) & (mx >= VAL_MIN)

total = h * w
shares = {}
for name, lo, hi in FAMILIES:
    mk = base & fam_mask(lo, hi)
    shares[name] = float(mk.sum() / total)

neutral = float((~base).sum() / total)

# 明亮暖色（窗光/路灯池）：高 L + 橙黄系
warm = (L > 55) & fam_mask(20, 65) & (C > 18)
warm_share = float(warm.sum() / total)

# 高饱和小面积亮点（窗、彩墙最艳处）
vivid = base & (S > 0.45) & (C > 30)
vivid_share = float(vivid.sum() / total)

def region(name, y0, y1, x0, x1):
    ys, ye = int(y0 * h), int(y1 * h)
    xs, xe = int(x0 * w), int(x1 * w)
    sub = L[ys:ye, xs:xe]
    subC = C[ys:ye, xs:xe]
    return {
        "region": name,
        "L_med": round(float(np.median(sub)), 1),
        "L_p10": round(float(np.percentile(sub, 10)), 1),
        "L_p90": round(float(np.percentile(sub, 90)), 1),
        "C_med": round(float(np.median(subC)), 1),
        "px": f"{xe - xs}x{ye - ys}",
    }

regions = [
    region("sky_top_left", 0.02, 0.16, 0.02, 0.40),
    region("sky_top_right", 0.02, 0.16, 0.62, 0.98),
    region("sea_horizon_band", 0.14, 0.24, 0.70, 0.99),
    region("snow_foreground_bottom", 0.86, 0.99, 0.05, 0.95),
    region("snow_shadow_mid_left", 0.45, 0.62, 0.02, 0.18),
    region("lamp_pool_center", 0.60, 0.78, 0.42, 0.66),
    region("houses_left_cluster", 0.30, 0.55, 0.04, 0.34),
    region("houses_center", 0.36, 0.60, 0.35, 0.62),
    region("houses_right", 0.45, 0.80, 0.72, 0.99),
]

# 色相族质心（用饱和像素，看各色落在画面哪里）
centroids = {}
for name, lo, hi in FAMILIES:
    mk = (base & fam_mask(lo, hi)) & (S > 0.30)
    if mk.sum() < total * 0.0015:
        continue
    ys, xs = np.nonzero(mk)
    centroids[name] = {
        "share_px": int(mk.sum()),
        "x": round(float(xs.mean() / w), 3),
        "y": round(float(ys.mean() / h), 3),
        "L_med": round(float(np.median(L[mk])), 1),
        "S_med": round(float(np.median(S[mk])), 2),
    }

# 竖向带扫描：每 10% 高度的中位 L（看雪面明暗节奏 / 地平线）
bands = []
for i in range(10):
    y0, y1 = i / 10, (i + 1) / 10
    ys, ye = int(y0 * h), int(y1 * h)
    bands.append({"band": f"{int(y0*100)}-{int(y1*100)}%",
                  "L_med": round(float(np.median(L[ys:ye])), 1)})

# 横向八等分位置参考（曼特 3:5）
def pct(v, total_):
    return round(100 * v / total_, 2)

report = {
    "file": SRC.name,
    "size_px": [W, H],
    "aspect": round(W / H, 4),
    "aspect_hint": "3:2" if abs(W / H - 1.5) < 0.01 else "custom",
    "analysis_resized": [w, h],
    "neutral_share_pct": round(neutral * 100, 2),
    "hue_family_share_pct": {k: round(v * 100, 2) for k, v in shares.items()},
    "warm_lit_share_pct": round(warm_share * 100, 2),
    "vivid_share_pct": round(vivid_share * 100, 3),
    "regions": regions,
    "hue_centroids": centroids,
    "l_bands": bands,
}

print(json.dumps(report, ensure_ascii=False, indent=2))
(OUT / "measure.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

# 可视化辅助：色相族掩膜拼图 + 八等分参考线
dbg = np.asarray(small).copy()
for name, lo, hi in FAMILIES:
    pass
for frac in (0.125, 0.375, 0.5, 0.625):
    x = int(frac * w)
    dbg[:, max(0, x - 1):x + 1] = [255, 0, 0]
Image.fromarray(dbg).save(OUT / "thirds-overlay.jpg", quality=88)
print("saved ->", OUT)

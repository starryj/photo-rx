"""Round 4: locate the painted facades by blob detection (no guessed boxes).

Non-blue hue families (red/orange/yellow/green/purple) are segmented, then
8-connected blobs with area >= 0.02% of the frame are reported with their
median hue / S / L and normalised bbox. Also finds the strongest horizontal
edge in the right third (sea/ice line) and the dark figures inside the lamp pool.
"""
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(r"C:\Users\27669\.dsh\attachments\v1\objects\e2\e2e6fa93d1e2e150e82f9237d3df640c40db19b7f1a231fcf03189df6063701c")
OUT = Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\blue-hour-village")
img = Image.open(SRC).convert("RGB")
W, H = img.size
small = img.resize((1200, 800), Image.LANCZOS)
a = np.asarray(small).astype(np.float32) / 255.0
h, w = a.shape[:2]
total = h * w

mx = a.max(axis=2); mn = a.min(axis=2); delta = mx - mn
S = np.where(mx > 1e-6, delta / np.maximum(mx, 1e-6), 0)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
Hh = np.zeros_like(mx); m = delta > 1e-6
i1 = m & (mx == r); Hh[i1] = ((g[i1] - b[i1]) / delta[i1]) % 6
i2 = m & (mx == g); Hh[i2] = (b[i2] - r[i2]) / delta[i2] + 2
i3 = m & (mx == b); Hh[i3] = (r[i3] - g[i3]) / delta[i3] + 4
Hdeg = Hh * 60

def lab_of(rgb):
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = (lin @ M.T) / np.array([0.95047, 1.0, 1.08883])
    d = 6 / 29
    f = lambda t: np.where(t > d ** 3, np.cbrt(t), t / (3 * d * d) + 4 / 29)
    fx, fy, fz = f(xyz[..., 0]), f(xyz[..., 1]), f(xyz[..., 2])
    return 116 * fy - 16, np.hypot(500 * (fx - fy), 200 * (fy - fz))

NONBLUE = ((Hdeg >= 345) | (Hdeg < 70) | ((Hdeg >= 70) & (Hdeg < 175)) | (Hdeg >= 265))
mask = NONBLUE & (S >= 0.32) & (mx >= 0.10)
lab = np.zeros_like(mask, dtype=bool)
blobs = []
for yy, xx in zip(*np.nonzero(mask)):
    if lab[yy, xx]:
        continue
    q = deque([(yy, xx)]); lab[yy, xx] = True; pts = []
    while q:
        cy, cx = q.popleft(); pts.append((cy, cx))
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = True; q.append((ny, nx))
    if len(pts) < total * 0.0002:
        continue
    ys = np.array([p[0] for p in pts]); xs = np.array([p[1] for p in pts])
    med_rgb = np.median(a[ys, xs], axis=0)
    L, C = lab_of(med_rgb)
    mxv, mnv = med_rgb.max(), med_rgb.min()
    s_med = 0 if mxv == 0 else (mxv - mnv) / mxv
    rr, gg, bb = med_rgb
    if mxv == mnv:
        hue = None
    elif mxv == rr:
        hue = ((gg - bb) / (mxv - mnv)) % 6 * 60
    elif mxv == gg:
        hue = ((bb - rr) / (mxv - mnv) + 2) * 60
    else:
        hue = ((rr - gg) / (mxv - mnv) + 4) * 60
    blobs.append({
        "area_pct": round(100 * len(pts) / total, 3),
        "cx": round(float(xs.mean() / w), 3), "cy": round(float(ys.mean() / h), 3),
        "bbox": [round(float(xs.min() / w), 3), round(float(ys.min() / h), 3),
                 round(float(xs.max() / w), 3), round(float(ys.max() / h), 3)],
        "rgb": [round(float(v * 255)) for v in med_rgb],
        "hue": round(float(hue), 0) if hue is not None else None,
        "S": round(float(s_med), 2), "L": round(float(L), 1), "C": round(float(C), 1),
    })
blobs.sort(key=lambda z: -z["area_pct"])
res = {"nonblue_total_pct": round(100 * float(mask.sum()) / total, 2), "blobs": blobs[:16]}
print(json.dumps(res, ensure_ascii=False, indent=2))

# 水平边：右三分之一逐行平均亮度梯度
band = a[:, int(w * 0.66):int(w * 0.99)]
rowL = band.mean(axis=(1, 2))
grad = np.abs(np.diff(rowL))
top = np.argsort(grad)[-6:][::-1]
res["sea_horizon_candidates"] = [{"y_norm": round(float(y / h), 3),
                                  "dL": round(float(grad[y]), 4)} for y in top[:6]]

# 灯池里的暗块（行人）：灯池区域 L>70 的包围盒内找 L<25 的连通块
pool = (rowL > 0)  # placeholder
ys, xs = np.nonzero((lab_of(a)[0] > 80))
if len(xs):
    x0, x1 = xs.min(), xs.max(); y0, y1 = ys.min(), ys.max()
    sub_dark = (lab_of(a)[0] < 30)
    dark = np.zeros_like(sub_dark)
    dark[y0:y1, x0:x1] = sub_dark[y0:y1, x0:x1]
    labd = np.zeros_like(dark, dtype=bool)
    figures = []
    for yy, xx in zip(*np.nonzero(dark)):
        if labd[yy, xx]:
            continue
        q = deque([(yy, xx)]); labd[yy, xx] = True; pts = []
        while q:
            cy, cx = q.popleft(); pts.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and dark[ny, nx] and not labd[ny, nx]:
                        labd[ny, nx] = True; q.append((ny, nx))
        if 150 <= len(pts) <= total * 0.01:
            yy_ = [p[0] for p in pts]; xx_ = [p[1] for p in pts]
            hgt = (max(yy_) - min(yy_)) / h
            if hgt > 0.02:
                figures.append({"area_pct": round(100 * len(pts) / total, 3),
                                "cx": round(sum(xx_) / len(xx_) / w, 3),
                                "cy": round(sum(yy_) / len(yy_) / h, 3),
                                "height_frac": round(hgt, 3)})
    figures.sort(key=lambda z: -z["area_pct"])
    res["dark_figures_in_pool"] = figures[:6]
print(json.dumps({k: v for k, v in res.items() if k != "blobs"}, ensure_ascii=False, indent=2))
(OUT / "measure4.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

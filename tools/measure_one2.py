"""Round 2: separate the blue-hour cast from the painted facades.

Round 1 counted every blue-ish snow pixel as "blue" (83.9%). That is the light
cast, not the palette. Here we raise thresholds and report per-family shares
inside (a) all saturated pixels, (b) vivid/painted pixels, and locate coloured
facades on a 24x16 grid.
"""
import json
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

def to_linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

lin = to_linear(a)
M = np.array([[0.4124564, 0.3575761, 0.1804375],
              [0.2126729, 0.7151522, 0.0721750],
              [0.0193339, 0.1191920, 0.9503041]])
xyz = lin @ M.T
xyz /= np.array([0.95047, 1.0, 1.08883])
d = 6 / 29
f = lambda t: np.where(t > d ** 3, np.cbrt(t), t / (3 * d * d) + 4 / 29)
fx, fy, fz = f(xyz[..., 0]), f(xyz[..., 1]), f(xyz[..., 2])
L = 116 * fy - 16
A = 500 * (fx - fy)
B = 200 * (fy - fz)
C = np.sqrt(A ** 2 + B ** 2)

mx = a.max(axis=2); mn = a.min(axis=2); delta = mx - mn
S = np.where(mx > 1e-6, delta / np.maximum(mx, 1e-6), 0)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
Hh = np.zeros_like(mx); m = delta > 1e-6
i1 = m & (mx == r); Hh[i1] = ((g[i1] - b[i1]) / delta[i1]) % 6
i2 = m & (mx == g); Hh[i2] = (b[i2] - r[i2]) / delta[i2] + 2
i3 = m & (mx == b); Hh[i3] = (r[i3] - g[i3]) / delta[i3] + 4
Hdeg = Hh * 60

FAM = {"red": (345, 15), "orange": (15, 45), "yellow": (45, 70), "green": (70, 165),
       "cyan": (165, 200), "blue": (200, 260), "purple": (260, 345)}
def fam(lo, hi):
    return (Hdeg >= lo) & (Hdeg < hi) if lo < hi else (Hdeg >= lo) | (Hdeg < hi)

# (a) 蓝调环境光：中低饱和大面积
cast = (S >= 0.22) & (mx >= 0.12)
# (b) 彩绘：更高饱和 + 更高色度
painted = (S >= 0.38) & (C >= 22) & (L >= 12)
# 蓝色要单独提门槛：雪面蓝的色度低于蓝房子
blue_house = fam(200, 260) & (S >= 0.55) & (C >= 30)

res = {"size_px": [W, H], "aspect": round(W / H, 4)}

def shares(mask, label):
    out = {}
    for name, (lo, hi) in FAM.items():
        mk = mask & fam(lo, hi)
        out[name] = round(100 * float(mk.sum()) / total, 2)
    out["_total"] = round(100 * float(mask.sum()) / total, 1)
    res[label] = out

shares(cast, "share_cast_pct")
shares(painted, "share_painted_pct")

# 彩绘族里把蓝色换成「蓝房子」口径
pb = {}
for name, (lo, hi) in FAM.items():
    if name == "blue":
        mk = blue_house
    else:
        mk = painted & fam(lo, hi)
    pb[name] = round(100 * float(mk.sum()) / total, 3)
res["share_painted_blue_house_pct"] = pb

# 彩绘族的面积比（只计家族，不含环境蓝）
painted_only = {k: v for k, v in pb.items() if v > 0.02}
res["painted_area_ratios"] = {
    "red:blue": round(pb["red"] / pb["blue"], 2) if pb["blue"] else None,
    "red:yellow": round(pb["red"] / pb["yellow"], 2) if pb["yellow"] else None,
    "yellow:blue": round(pb["yellow"] / pb["blue"], 2) if pb["blue"] else None,
    "purple:blue": round(pb["purple"] / pb["blue"], 2) if pb["blue"] else None,
}

# 24x16 网格：每格主导彩绘族（>该格 6% 面积）
gw, gh = 24, 16
cells = []
for gy in range(gh):
    for gx in range(gw):
        ys, ye = int(gy / gh * h), int((gy + 1) / gh * h)
        xs, xe = int(gx / gw * w), int((gx + 1) / gw * w)
        cell_area = (ye - ys) * (xe - xs)
        best = None
        for name, (lo, hi) in FAM.items():
            if name == "blue":
                mk = blue_house[ys:ye, xs:xe]
            else:
                mk = (painted & fam(lo, hi))[ys:ye, xs:xe]
            frac = float(mk.sum()) / cell_area
            if frac > 0.06 and (best is None or frac > best[1]):
                best = (name, frac)
        if best:
            cells.append({"cx": round((gx + 0.5) / gw, 3), "cy": round((gy + 0.5) / gh, 3),
                          "fam": best[0], "frac": round(best[1], 2)})
res["painted_cells_n"] = len(cells)
res["painted_cells"] = cells

# 灯池：高亮区（L>80，低饱和，暖而不饱和）
pool = (L > 82) & (S < 0.35)
ys, xs = np.nonzero(pool)
if len(xs):
    res["lamp_pool"] = {"n_px_pct": round(100 * len(xs) / total, 2),
                        "centroid": [round(float(xs.mean() / w), 3), round(float(ys.mean() / h), 3)],
                        "bbox_norm": [round(float(xs.min() / w), 3), round(float(ys.min() / h), 3),
                                      round(float(xs.max() / w), 3), round(float(ys.max() / h), 3)]}

# 窗光点：小面积高亮暖点，数个数（连通块用 8 邻域简易标记）
from collections import deque
warm = (L > 70) & fam(15, 60) & (C > 20)
lab = np.zeros_like(warm, dtype=bool)
blobs = []
for yy, xx in zip(*np.nonzero(warm)):
    if lab[yy, xx]:
        continue
    q = deque([(yy, xx)]); lab[yy, xx] = True; pts = []
    while q:
        cy, cx = q.popleft(); pts.append((cy, cx))
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and warm[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = True; q.append((ny, nx))
    if len(pts) >= 4:
        ys2 = [p[0] for p in pts]; xs2 = [p[1] for p in pts]
        blobs.append({"n": len(pts), "x": round(sum(xs2) / len(xs2) / w, 3),
                      "y": round(sum(ys2) / len(ys2) / h, 3)})
blobs.sort(key=lambda z: -z["n"])
res["warm_points"] = {"count": len(blobs), "top8": blobs[:8]}

print(json.dumps(res, ensure_ascii=False, indent=2))
(OUT / "measure2.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

# 参考图：彩绘掩膜叠加
vis = np.asarray(small).copy()
overlay = np.zeros_like(vis)
for name, (lo, hi) in FAM.items():
    mk = blue_house if name == "blue" else (painted & fam(lo, hi))
    overlay[mk] = [255, 255, 255]
vis = (vis * 0.35 + overlay * 0.65).astype(np.uint8)
Image.fromarray(vis).save(OUT / "painted-mask.jpg", quality=88)

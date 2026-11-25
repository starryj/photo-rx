#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""measure_photo.py — 单张照片的标准量测量（photo-rx 配套，D-04 数值只来自脚本）

一次跑完 12 类标准量，同时输出三张核对图。**引用数值之前必须先看 verify-sheet.jpg**：
上一版把归一化坐标直接套到图上，结果采到了天空和雪——框位错一次，整段结论就废了。

用法:
    python tools/measure_photo.py path/to/photo.jpg
    python tools/measure_photo.py photo.jpg --out out/analysis/mine --max-side 1400

输出（默认 <out> = out/analysis/<图片名>）:
    measure.json     全部量，每项带 note；数值一律来自本脚本，不来自模型
    verify-sheet.jpg 上半=框位叠加图，下半=8 个框的裁图与实测值（目视确认框没落错）
    thirds.jpg       三分线 / 5:8 线叠加图
    grid.jpg         10% 网格参考图

约定:
    * L 为 CIE Lab 明度 0–100，C 为彩度（Lab a/b 的模），hue 为 0–360，S 为 HSV 饱和度 0–1。
    * sRGB 线性化前必须先 /255；不除会得到 L≈3363 这种荒谬值（本脚本已内置修正）。
    * 所有归一化坐标以左上角为原点，x 向右、y 向下。
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageOps

# ---------------------------------------------------------------- 色彩空间


def srgb_to_lab(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """rgb 为 0–1 的 float 数组（H,W,3）→ (L 0–100, C, hue 0–360)。"""
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    m = np.array(
        [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ]
    )
    xyz = (lin @ m.T) / np.array([0.95047, 1.0, 1.08883])
    d = 6.0 / 29.0
    f = np.where(xyz > d**3, np.cbrt(xyz), xyz / (3 * d * d) + 4.0 / 29.0)
    L = 116.0 * f[..., 1] - 16.0
    a = 500.0 * (f[..., 0] - f[..., 1])
    b = 200.0 * (f[..., 1] - f[..., 2])
    C = np.hypot(a, b)
    hue = (np.degrees(np.arctan2(b, a)) + 360.0) % 360.0
    return L, C, hue


def hsv_sat(rgb: np.ndarray) -> np.ndarray:
    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)


def hsv_hue(rgb: np.ndarray) -> np.ndarray:
    """HSV 色相 0–360。

    注意：色相族必须用 HSV 色相，不能用 Lab 色相——同一片蓝调天空，
    HSV 读数约 214，Lab 读数在 270 以上；两套混用会把 84% 的蓝判成 0.6%。
    """
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    df = mx - mn
    safe = np.maximum(df, 1e-6)
    h = np.where(
        mx == r,
        ((g - b) / safe) % 6,
        np.where(mx == g, (b - r) / safe + 2, (r - g) / safe + 4),
    )
    h = h * 60.0
    return np.where(df < 1e-6, 0.0, h % 360.0)


# ---------------------------------------------------------------- 连通块


def label_mask(mask: np.ndarray, min_area: int = 1) -> list[dict]:
    """纯 numpy/python 的四连通标记（本机没有 scipy）。

    返回 [{area, cx, cy, x0, y0, x1, y1}]，坐标为归一化值，按面积降序。
    """
    h, w = mask.shape
    seen = np.zeros((h, w), dtype=bool)
    out: list[dict] = []
    ys, xs = np.nonzero(mask)
    for sy, sx in zip(ys.tolist(), xs.tolist()):
        if seen[sy, sx]:
            continue
        q = deque([(sy, sx)])
        seen[sy, sx] = True
        acc_y = acc_x = n = 0
        y0 = y1 = sy
        x0 = x1 = sx
        while q:
            y, x = q.popleft()
            acc_y += y
            acc_x += x
            n += 1
            if y < y0:
                y0 = y
            elif y > y1:
                y1 = y
            if x < x0:
                x0 = x
            elif x > x1:
                x1 = x
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        if n >= min_area:
            out.append(
                {
                    "area_px": n,
                    "area_frac": round(n / (h * w), 5),
                    "cx": round((acc_x / n) / w, 3),
                    "cy": round((acc_y / n) / h, 3),
                    "x0": round(x0 / w, 3),
                    "y0": round(y0 / h, 3),
                    "x1": round(x1 / w, 3),
                    "y1": round(y1 / h, 3),
                }
            )
    out.sort(key=lambda d: -d["area_px"])
    return out


# ---------------------------------------------------------------- 度量


def bands(values: np.ndarray, axis: int, n: int = 3) -> list[float]:
    """沿指定轴切 n 段，返回各段均值。"""
    size = values.shape[axis]
    edges = [round(i * size / n) for i in range(n + 1)]
    res = []
    for i in range(n):
        sl = [slice(None), slice(None)]
        sl[axis] = slice(edges[i], edges[i + 1])
        res.append(float(values[tuple(sl)].mean()))
    return res


def dark_frac(values: np.ndarray, axis: int, n: int, thr: float) -> list[float]:
    size = values.shape[axis]
    edges = [round(i * size / n) for i in range(n + 1)]
    res = []
    for i in range(n):
        sl = [slice(None), slice(None)]
        sl[axis] = slice(edges[i], edges[i + 1])
        res.append(float((values[tuple(sl)] < thr).mean()))
    return res


def peaks_1d(sig: np.ndarray, k: int = 3, exclude_edges: float = 0.03) -> list[dict]:
    lo = int(len(sig) * exclude_edges)
    hi = len(sig) - lo
    idx = np.argsort(sig[lo:hi])[::-1][: k * 4]
    picked: list[int] = []
    for i in idx:
        i = int(i + lo)
        if all(abs(i - p) > len(sig) * 0.02 for p in picked):
            picked.append(i)
        if len(picked) >= k:
            break
    return [
        {"pos": round(i / len(sig), 3), "strength": round(float(sig[i]), 2)}
        for i in picked
    ]


def crop_tile(
    im: Image.Image, box: tuple[float, float, float, float], size: int = 320, height: int | None = None
) -> Image.Image:
    w, h = im.size
    x0, y0, x1, y1 = box
    px = (max(0, int(x0 * w)), max(0, int(y0 * h)), min(w, int(x1 * w)), min(h, int(y1 * h)))
    if px[2] - px[0] < 4 or px[3] - px[1] < 4:
        px = (0, 0, w, h)
    t = im.crop(px)
    ch = height or size
    t.thumbnail((size, ch), Image.LANCZOS)
    canvas = Image.new("RGB", (size, ch), (28, 28, 32))
    canvas.paste(t, ((size - t.width) // 2, (ch - t.height) // 2))
    return canvas


def pad(box: tuple[float, float, float, float], m: float = 0.02) -> tuple[float, float, float, float]:
    return (max(0.0, box[0] - m), max(0.0, box[1] - m), min(1.0, box[2] + m), min(1.0, box[3] + m))


# ---------------------------------------------------------------- 主流程


def measure(path: str, outdir: str, max_side: int = 1400) -> dict:
    im0 = Image.open(path)
    icc = im0.info.get("icc_profile")
    im0 = ImageOps.exif_transpose(im0)
    if im0.mode in ("RGBA", "LA", "P"):
        im0 = im0.convert("RGBA")
        bg = Image.new("RGBA", im0.size, (255, 255, 255, 255))
        im0 = Image.alpha_composite(bg, im0).convert("RGB")
    else:
        im0 = im0.convert("RGB")
    W0, H0 = im0.size

    scale = 1.0
    if max(H0, W0) > max_side:
        scale = max_side / max(H0, W0)
        im = im0.resize((max(1, int(W0 * scale)), max(1, int(H0 * scale))), Image.LANCZOS)
    else:
        im = im0

    rgb = np.asarray(im).astype(np.float32) / 255.0
    L, C, _lab_hue = srgb_to_lab(rgb)
    S = hsv_sat(rgb)
    hue = hsv_hue(rgb)
    h, w = L.shape
    total = h * w

    res: dict = {
        "image": {
            "path": os.path.abspath(path),
            "px": [W0, H0],
            "ratio": round(W0 / H0, 4),
            "ratio_label": _ratio_label(W0, H0),
            "icc_bytes": len(icc) if icc else 0,
            "work_px": [w, h],
            "note": "比例与 ICC 来自文件；ICC 为空时，色相读数按 sRGB 解释",
        }
    }

    # 1 色相族
    blue = (hue >= 195) & (hue <= 260) & (S >= 0.22)
    neutral = S < 0.22
    warm = (L > 55) & (hue >= 15) & (hue <= 65) & (C > 18)
    res["hue_families"] = {
        "blue": round(float(blue.mean()), 4),
        "neutral": round(float(neutral.mean()), 4),
        "warm": round(float(warm.mean()), 4),
        "other": round(float(1 - blue.mean() - neutral.mean() - warm.mean()), 4),
        "note": "blue=hue195–260&S≥.22；neutral=S<.22；warm=L>55&hue15–65&C>18",
    }

    # 2 三分区明度
    res["thirds"] = {
        "vertical_mean_L": [round(v, 1) for v in bands(L, axis=1)],
        "vertical_dark_frac_Lt30": [round(v, 3) for v in dark_frac(L, axis=1, n=3, thr=30)],
        "horizontal_mean_L": [round(v, 1) for v in bands(L, axis=0)],
        "note": "vertical=左/中/右（沿 x 切）；horizontal=上/中/下（沿 y 切）",
    }

    # 3 明暗跨度
    p5, p50, p99 = (float(np.percentile(L, q)) for q in (5, 50, 99))
    res["tone"] = {
        "L_p5": round(p5, 1),
        "L_median": round(p50, 1),
        "L_p99": round(p99, 1),
        "span_ratio": round((p99 + 1) / (p5 + 1), 2),
        "note": "span_ratio=p99/p5，>3 算硬光或高反差，<1.6 算平",
    }

    # 4 亮池（连通块，避免零星高光把包围盒拉大）
    pool = (L > 85) & (S < 0.35)
    pools = label_mask(pool, min_area=max(16, int(total * 0.00005)))[:3]
    for b in pools:
        y0, y1 = int(b["y0"] * h), max(int(b["y1"] * h) + 1, int(b["y0"] * h) + 1)
        x0, x1 = int(b["x0"] * w), max(int(b["x1"] * w) + 1, int(b["x0"] * w) + 1)
        sl = (slice(y0, y1), slice(x0, x1))
        b["mean_L"] = round(float(L[sl].mean()), 1)
        b["mean_C"] = round(float(C[sl].mean()), 1)
        b["mean_rgb255"] = [int(round(float(v) * 255)) for v in rgb[sl].reshape(-1, 3).mean(axis=0)]
    res["bright_pools"] = {
        "area_frac": round(float(pool.mean()), 4),
        "count": len(pools),
        "top": pools,
        "note": "L>85 且 S<0.35 的连通块，按面积降序；「亮池」就是这里最大的那几块",
    }
    pool_box = (
        (pools[0]["x0"], pools[0]["y0"], pools[0]["x1"], pools[0]["y1"]) if pools else (0.6, 0.6, 0.9, 0.9)
    )

    # 4b 高彩度小面（窗光、灯、招牌这类「色度源头」）
    chroma = (C > 40) & (L > 60)
    peaks = label_mask(chroma, min_area=max(9, int(total * 0.00002)))[:3]
    for b in peaks:
        y0, y1 = int(b["y0"] * h), max(int(b["y1"] * h) + 1, int(b["y0"] * h) + 1)
        x0, x1 = int(b["x0"] * w), max(int(b["x1"] * w) + 1, int(b["x0"] * w) + 1)
        sl = (slice(y0, y1), slice(x0, x1))
        b["mean_L"] = round(float(L[sl].mean()), 1)
        b["mean_C"] = round(float(C[sl].mean()), 1)
        b["mean_hue"] = round(float(hue[sl].mean()), 1)
        b["peak_rgb255"] = [int(round(float(v) * 255)) for v in rgb[sl].reshape(-1, 3).max(axis=0)]
    res["chroma_peaks"] = {
        "area_frac": round(float(chroma.mean()), 5),
        "count": len(peaks),
        "top": peaks,
        "note": "C>40 且 L>60；画面里最高的那点色度往往就藏在这几块里（窗光/灯/彩色墙）",
    }

    # 5 暖点连通块
    warm_blobs = label_mask(warm, min_area=max(16, int(total * 0.00005)))[:5]
    for b in warm_blobs:
        y0, y1 = int(b["y0"] * h), max(int(b["y1"] * h) + 1, int(b["y0"] * h) + 1)
        x0, x1 = int(b["x0"] * w), max(int(b["x1"] * w) + 1, int(b["x0"] * w) + 1)
        patch = rgb[y0:y1, x0:x1]
        pl, pc, ph = L[y0:y1, x0:x1], C[y0:y1, x0:x1], hue[y0:y1, x0:x1]
        b["mean_L"] = round(float(pl.mean()), 1)
        b["mean_C"] = round(float(pc.mean()), 1)
        b["mean_hue"] = round(float(ph.mean()), 1)
        b["mean_rgb255"] = [int(round(float(v) * 255)) for v in patch.reshape(-1, 3).mean(axis=0)]
    res["warm_blobs"] = {
        "count": len(warm_blobs),
        "top": warm_blobs,
        "note": "暖点=hue15–65&C>18&L>55；按面积降序，最多 5 个",
    }

    # 6 暗块
    dark = L < 25
    dark_blobs = label_mask(dark, min_area=max(64, int(total * 0.0002)))[:3]
    res["dark_masses"] = {
        "area_frac": round(float(dark.mean()), 4),
        "top": dark_blobs,
        "note": "L<25 的连通块，用来判断画面重量落在哪一区",
    }

    # 7 中性锚
    anchor = (S < 0.15) & (L > 35) & (L < 75)
    res["neutral_anchor"] = {
        "area_frac": round(float(anchor.mean()), 4),
        "mean_L": round(float(L[anchor].mean()), 1) if anchor.any() else None,
        "note": "S<0.15 且 35<L<75；色彩诊断里的「中性锚」应在这里找",
    }

    # 8 最强水平 / 垂直分割线
    gx = np.abs(np.diff(L, axis=1)).mean(axis=0)
    gy = np.abs(np.diff(L, axis=0)).mean(axis=1)
    res["gradient_peaks"] = {
        "row_peaks": peaks_1d(gy, k=3),
        "col_peaks": peaks_1d(gx, k=3),
        "note": "pos 为归一化 y（行）或 x（列）；峰值=该行/列的平均明度梯度。"
                "这里报的是「最强的横向/纵向分割线」，不等于地平线——地平线要回图里认。",
    }

    # 9 参考线距离
    def near(v: float, refs: dict) -> dict:
        best = min(refs.items(), key=lambda kv: abs(v - kv[1]))
        return {"nearest": best[0], "delta": round(v - best[1], 3)}

    refs = {"1/3": 1 / 3, "5/8": 5 / 8, "2/3": 2 / 3, "center": 0.5}
    if res["gradient_peaks"]["col_peaks"]:
        x = res["gradient_peaks"]["col_peaks"][0]["pos"]
        res["rule_of_thirds_check"] = {
            "main_vertical_x": x,
            **near(x, refs),
            "note": "delta 在 ±0.02 内才谈得上「压线」；两线都近时不得断言用了黄金分割",
        }
    if res["gradient_peaks"]["row_peaks"]:
        y = res["gradient_peaks"]["row_peaks"][0]["pos"]
        res["main_horizontal_line"] = {**near(y, refs), "y": y}

    # 10 边缘吸附
    def edge_energy(band: float) -> dict:
        n = max(2, int(min(h, w) * band))
        parts = {
            "top": gy[:n].mean(),
            "bottom": gy[-n:].mean(),
            "left": gx[:n].mean(),
            "right": gx[-n:].mean(),
        }
        base = float(gx.mean() + gy.mean()) / 2.0 + 1e-6
        return {k: round(float(v) / base, 2) for k, v in parts.items()}

    res["edge_intrusion"] = {
        "ratio_vs_mean_gradient": edge_energy(0.02),
        "note": "与该图平均梯度比；>1.6 说明该边有建筑/主体被切，值得考虑裁掉或补边",
    }

    # 11 主体候选
    cands = []
    for tag, blobs in (("dark", dark_blobs), ("warm", warm_blobs[:3])):
        for b in blobs[:2]:
            cands.append(
                {
                    "tag": tag,
                    "cx": b["cx"],
                    "cy": b["cy"],
                    "area_frac": b["area_frac"],
                    "height_frac": round(b["y1"] - b["y0"], 3),
                    "width_frac": round(b["x1"] - b["x0"], 3),
                }
            )
    res["subject_candidates"] = {
        "list": cands,
        "note": "height_frac<0.08 的块多半是细节而非主体（人、灯、窗）",
    }

    # 12 抽样点
    probes = {
        "sky_top": (0.0, 0.0, 1.0, 0.08),
        "foreground_bottom": (0.0, 0.90, 1.0, 1.0),
        "center": (0.40, 0.40, 0.60, 0.60),
        "left_third": (0.02, 0.30, 0.30, 0.70),
        "right_third": (0.70, 0.30, 0.98, 0.70),
        "upper_right": (0.70, 0.05, 0.98, 0.30),
        "bright_pool": pad(pool_box, 0.03),
    }
    if warm_blobs:
        b = warm_blobs[0]
        probes["warm_top1"] = pad((b["x0"], b["y0"], b["x1"], b["y1"]), 0.01)
    if peaks:
        b = peaks[0]
        probes["chroma_top1"] = pad((b["x0"], b["y0"], b["x1"], b["y1"]), 0.01)
    if dark_blobs:
        b = dark_blobs[0]
        probes["dark_top1"] = pad((b["x0"], b["y0"], b["x1"], b["y1"]), 0.01)
    table = {}
    for name, box in probes.items():
        x0, y0, x1, y1 = box
        xs0, xs1 = int(x0 * w), max(int(x1 * w), int(x0 * w) + 1)
        ys0, ys1 = int(y0 * h), max(int(y1 * h), int(y0 * h) + 1)
        sl = (slice(ys0, ys1), slice(xs0, xs1))
        table[name] = {
            "box": [round(v, 3) for v in box],
            "L": round(float(L[sl].mean()), 1),
            "C": round(float(C[sl].mean()), 1),
            "S": round(float(S[sl].mean()), 3),
            "hue": round(float(hue[sl].mean()), 1),
            "rgb255": [int(round(float(v) * 255)) for v in rgb[sl].reshape(-1, 3).mean(axis=0)],
        }
    res["probes"] = {"regions": table, "note": "区域均值；box 为归一化坐标 (x0,y0,x1,y1)"}

    # ---- 出图 ----
    os.makedirs(outdir, exist_ok=True)

    # verify-sheet：上半是打了编号框的缩略图，下半是每个框的裁图 + 实测值
    sheet_boxes = [
        ("sky-top", "sky_top", probes["sky_top"]),
        ("bottom", "foreground_bottom", probes["foreground_bottom"]),
        ("bright-pool", "bright_pool", probes["bright_pool"]),
        ("chroma-1", "chroma_top1", probes.get("chroma_top1", probes["center"])),
        ("warm-1", "warm_top1", probes.get("warm_top1", probes["center"])),
        ("dark-1", "dark_top1", probes.get("dark_top1", (0.1, 0.1, 0.4, 0.4))),
        ("dark-2", None, pad((dark_blobs[1]["x0"], dark_blobs[1]["y0"], dark_blobs[1]["x1"], dark_blobs[1]["y1"]), 0.01)
         if len(dark_blobs) > 1 else (0.6, 0.6, 0.9, 0.9)),
        ("center", "center", probes["center"]),
    ]
    tile, cap, cols = 300, 34, 4
    rows = math.ceil(len(sheet_boxes) / cols)
    thumb = im.copy()
    thumb.thumbnail((1200, 1200), Image.LANCZOS)
    tw, th = thumb.size
    td = ImageDraw.Draw(thumb)
    for i, (label, _key, box) in enumerate(sheet_boxes):
        x0, y0, x1, y1 = box
        td.rectangle([tw * x0, th * y0, tw * x1, th * y1], outline=(255, 40, 40), width=2)
        td.text((tw * x0 + 4, max(0, th * y0 - 12)), f"#{i + 1}", fill=(255, 255, 0))
    sheet = Image.new(
        "RGB", (max(cols * tile, tw), th + 8 + rows * (tile * 2 // 3 + cap)), (16, 16, 18)
    )
    sheet.paste(thumb, (0, 0))
    draw = ImageDraw.Draw(sheet)
    for i, (label, key, box) in enumerate(sheet_boxes):
        cx = (i % cols) * tile
        cy = th + 8 + (i // cols) * (tile * 2 // 3 + cap)
        draw.rectangle([cx, cy, cx + tile - 4, cy + tile * 2 // 3], fill=(28, 28, 32))
        sheet.paste(crop_tile(im, box, tile, height=tile * 2 // 3), (cx, cy))
        p = table[key] if key in table else {"L": "?", "C": "?", "rgb255": ["?", "?", "?"]}
        draw.text(
            (cx + 6, cy + tile * 2 // 3 + 4),
            f"#{i + 1} {label}  L{p['L']} C{p['C']} rgb{tuple(p['rgb255'])}",
            fill=(225, 225, 225),
        )
    sheet.save(os.path.join(outdir, "verify-sheet.jpg"), quality=88)

    ov = im.copy()
    d2 = ImageDraw.Draw(ov)
    for f in (1 / 3, 2 / 3):
        d2.line([(w * f, 0), (w * f, h)], fill=(255, 90, 90), width=max(2, w // 600))
        d2.line([(0, h * f), (w, h * f)], fill=(255, 90, 90), width=max(2, w // 600))
    d2.line([(w * 5 / 8, 0), (w * 5 / 8, h)], fill=(90, 200, 255), width=max(2, w // 600))
    ov.save(os.path.join(outdir, "thirds.jpg"), quality=88)

    gr = im.copy()
    d3 = ImageDraw.Draw(gr)
    for i in range(1, 10):
        d3.line([(w * i / 10, 0), (w * i / 10, h)], fill=(120, 255, 160), width=1)
        d3.line([(0, h * i / 10), (w, h * i / 10)], fill=(120, 255, 160), width=1)
    gr.save(os.path.join(outdir, "grid.jpg"), quality=88)

    res["artifacts"] = {
        "dir": os.path.abspath(outdir),
        "files": ["measure.json", "verify-sheet.jpg", "thirds.jpg", "grid.jpg"],
        "note": "先看 verify-sheet.jpg 确认框位，再引用 probes 里的数值",
    }
    with open(os.path.join(outdir, "measure.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    res["artifacts"]["dir"] = os.path.abspath(outdir)
    return res


def _ratio_label(w: int, h: int) -> str:
    for name, (rw, rh) in {
        "1:1": (1, 1),
        "4:3": (4, 3),
        "3:2": (3, 2),
        "16:9": (16, 9),
        "2:3": (2, 3),
        "3:4": (3, 4),
        "9:16": (9, 16),
        "5:4": (5, 4),
        "7:5": (7, 5),
    }.items():
        if abs(w / h - rw / rh) < 0.012:
            return name
    return "未归类"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="单张照片标准量测量")
    ap.add_argument("image")
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-side", type=int, default=1400)
    ap.add_argument("--quiet", action="store_true", help="不打印 JSON 摘要")
    args = ap.parse_args(argv)

    if not os.path.exists(args.image):
        print(f"找不到图片: {args.image}", file=sys.stderr)
        return 2
    outdir = args.out or os.path.join(
        "out", "analysis", os.path.splitext(os.path.basename(args.image))[0][:40]
    )
    res = measure(args.image, outdir, args.max_side)

    if not args.quiet:
        brief = {
            "image": res["image"],
            "hue_families": res["hue_families"],
            "thirds": res["thirds"],
            "tone": res["tone"],
            "bright_pools": res["bright_pools"],
            "chroma_peaks": {k: v for k, v in res["chroma_peaks"].items() if k != "top"},
            "warm_blobs": {k: v for k, v in res["warm_blobs"].items() if k != "top"},
            "horizon": res["gradient_peaks"],
            "edge_intrusion": res["edge_intrusion"],
            "artifacts": res["artifacts"],
        }
        print(json.dumps(brief, ensure_ascii=False, indent=2))
    print(f"\n先看 {os.path.join(outdir, 'verify-sheet.jpg')} 再引用数值。", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

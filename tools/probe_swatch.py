"""Locate representative patches for the landscape swatch strip.

Scans the source photo at low resolution, keeps pixels matching each named
hue family, and reports the largest blob's centroid as fractional coordinates
so the report strip samples real paint rather than a guessed box.

    python tools/probe_swatch.py <image>
"""
import sys
from collections import deque
from pathlib import Path

from PIL import Image

W = 320

TARGETS = {
    "灯下暖": lambda h, s, v: 18 <= h < 55 and v >= 0.62 and s >= 0.25,
    "黄屋": lambda h, s, v: 35 <= h < 65 and s >= 0.42 and v >= 0.35,
    "红屋": lambda h, s, v: (h < 15 or h >= 340) and s >= 0.45 and v >= 0.25,
    "雪面": lambda h, s, v: s < 0.16 and v >= 0.72,
}


def classify(img):
    w, h = img.size
    px = img.load()
    out = {name: bytearray(w * h) for name in TARGETS}
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            mx, mn = max(r, g, b), min(r, g, b)
            v = mx / 255.0
            s = 0.0 if mx == 0 else (mx - mn) / mx
            if mx == mn:
                hue = 0.0
            elif mx == r:
                hue = (60 * ((g - b) / (mx - mn))) % 360
            elif mx == g:
                hue = 60 * ((b - r) / (mx - mn)) + 120
            else:
                hue = 60 * ((r - g) / (mx - mn)) + 240
            for name, test in TARGETS.items():
                if test(hue, s, v):
                    out[name][y * w + x] = 1
    return out


def largest_blob(mask, w, h):
    seen = bytearray(w * h)
    best = (0, None)
    for i in range(w * h):
        if not mask[i] or seen[i]:
            continue
        q = deque([i])
        seen[i] = 1
        xs, ys = [], []
        while q:
            j = q.popleft()
            ys.append(j // w)
            xs.append(j % w)
            x, y = j % w, j // w
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h:
                    k = ny * w + nx
                    if mask[k] and not seen[k]:
                        seen[k] = 1
                        q.append(k)
        if len(xs) > best[0]:
            best = (len(xs), (min(xs), min(ys), max(xs), max(ys)))
    return best


def main():
    path = Path(sys.argv[1])
    im = Image.open(path).convert("RGB")
    im.thumbnail((W, W * 4), Image.LANCZOS)
    w, h = im.size
    masks = classify(im)
    print(f"source {path.name}  probe {w}x{h}")
    for name, mask in masks.items():
        n, box = largest_blob(mask, w, h)
        if not box:
            print(f"{name}: no blob")
            continue
        x0, y0, x1, y1 = box
        print(f"{name}: cells={n} box=({x0 / w:.3f},{y0 / h:.3f},{x1 / w:.3f},{y1 / h:.3f})")


if __name__ == "__main__":
    main()

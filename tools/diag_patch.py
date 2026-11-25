"""Diagnostic: is the patch median really blue-grey while the crop looks khaki?"""
import numpy as np
from PIL import Image
from pathlib import Path

SRC = Path(r"C:\Users\27669\.dsh\attachments\v1\objects\e2\e2e6fa93d1e2e150e82f9237d3df640c40db19b7f1a231fcf03189df6063701c")
img = Image.open(SRC).convert("RGB")
print("full size", img.size, "mode", img.mode)
print("icc bytes", len(img.info.get("icc_profile", b"")))

a = np.asarray(img).astype(np.float32)
print("array shape", a.shape)

def box_stats(name, x0, y0, x1, y1, src):
    H, W = src.shape[:2]
    sub = src[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)].reshape(-1, 3)
    print(f"{name}: n={len(sub)} median={np.median(sub, axis=0).round(1)} "
          f"p25={np.percentile(sub,25,axis=0).round(1)} p75={np.percentile(sub,75,axis=0).round(1)}")

box_stats("full-res yellow", 0.060, 0.520, 0.200, 0.600, a)
small = np.asarray(img.resize((1200, 800), Image.LANCZOS)).astype(np.float32)
box_stats("resized yellow", 0.060, 0.520, 0.200, 0.600, small)

# 直接看几个点
for (fx, fy) in [(0.10, 0.55), (0.12, 0.57), (0.08, 0.54), (0.15, 0.58)]:
    px = a[int(fy * a.shape[0]), int(fx * a.shape[1])]
    print(f"pixel at ({fx:.2f},{fy:.2f}) =", px.astype(int))

# 保存该区域全分辨率 PNG，供目视核对
crop = img.crop((int(0.060 * img.size[0]), int(0.520 * img.size[1]),
                 int(0.200 * img.size[0]), int(0.600 * img.size[1])))
crop.save(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\blue-hour-village\yellow-crop.png")
print("crop size", crop.size)

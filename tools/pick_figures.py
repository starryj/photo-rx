# -*- coding: utf-8 -*-
"""从解析结果里挑代表图版，供本地 VLM 定性解读。

规则（可调）：
  1. 按 sha1 去重（MinerU 的图片文件名就是 sha1）
  2. 面积占比过滤：默认保留占页面 10% 以上的图块
  3. 每页最多取 2 张（图版书一页多图时取最大两张）
  4. 全书均匀抽样到 --n 张（默认 60）

产物：photo-vision\\out\\figures\\<slug>\\picked.json + contact.png
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
PARSE = ROOT / "out" / "parse"
DEST = ROOT / "out" / "figures"


def collect(slug: str, min_frac: float, per_page: int) -> list[dict]:
    src = PARSE / slug
    blocks = json.loads((src / "content_list.json").read_text("utf-8"))

    page_wh: dict[int, tuple[float, float]] = {}
    for b in blocks:
        bx = b.get("bbox") or [0, 0, 0, 0]
        p = int(b.get("page_idx") or 0)
        w, h = page_wh.get(p, (0.0, 0.0))
        page_wh[p] = (max(w, float(bx[2])), max(h, float(bx[3])))

    by_page: dict[int, list[dict]] = defaultdict(list)
    seen: set[str] = set()
    for b in blocks:
        if b.get("type") not in ("image", "figure"):
            continue
        ip = (b.get("img_path") or "").strip()
        name = Path(ip).name if ip else ""
        if not name or name in seen:
            continue
        f = src / "images" / name
        if not f.exists():
            continue
        bx = b.get("bbox") or [0, 0, 0, 0]
        p = int(b.get("page_idx") or 0)
        pw, ph = page_wh.get(p, (1.0, 1.0))
        bw, bh = float(bx[2]) - float(bx[0]), float(bx[3]) - float(bx[1])
        frac = (bw * bh) / max(pw * ph, 1.0)
        if frac < min_frac:
            continue
        seen.add(name)
        try:
            with Image.open(f) as im:
                iw, ih = im.size
        except Exception:
            iw = ih = 0
        cap = " ".join((b.get("image_caption") or []) + (b.get("image_footnote") or [])).strip()
        by_page[p].append(
            {
                "page_idx": p,
                "img": name,
                "path": str(f),
                "frac": round(frac, 4),
                "px": [iw, ih],
                "caption": cap,
            }
        )

    picked: list[dict] = []
    for p in sorted(by_page):
        row = sorted(by_page[p], key=lambda x: -x["frac"])[:per_page]
        row.sort(key=lambda x: x["page_idx"])
        picked.extend(row)
    return picked


def thin(picked: list[dict], n: int) -> list[dict]:
    if len(picked) <= n:
        return picked
    step = len(picked) / n
    out, i = [], 0.0
    while len(out) < n and int(i) < len(picked):
        out.append(picked[int(i)])
        i += step
    return out


def contact(items: list[dict], path: Path, cols: int = 10, cell: int = 220) -> None:
    rows = math.ceil(len(items) / cols)
    sheet = Image.new("RGB", (cols * cell, rows * (cell + 18)), (250, 249, 246))
    dr = ImageDraw.Draw(sheet)
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        x, y = c * cell, r * (cell + 18)
        try:
            im = Image.open(it["path"]).convert("RGB")
            im.thumbnail((cell - 8, cell - 8), Image.LANCZOS)
            sheet.paste(im, (x + 4, y + 4))
        except Exception:
            pass
        dr.rectangle([x, y, x + cell - 1, y + cell - 1], outline=(226, 222, 214))
        dr.text((x + 6, y + cell + 3), f"p{it['page_idx'] + 1:03d} {it['frac'] * 100:.0f}%", fill=(60, 58, 52))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, "JPEG", quality=85)
    print(f"  contact sheet -> {path} ({sheet.width}x{sheet.height})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--min-frac", type=float, default=0.10)
    ap.add_argument("--per-page", type=int, default=2)
    a = ap.parse_args()

    allf = collect(a.slug, a.min_frac, a.per_page)
    print(f"[{a.slug}] 候选 {len(allf)} 张（面积 ≥{a.min_frac:.0%}、每页 ≤{a.per_page}）")
    picked = thin(allf, a.n)
    print(f"[{a.slug}] 抽样 {len(picked)} 张")

    outdir = DEST / a.slug
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "picked.json").write_text(
        json.dumps({"slug": a.slug, "n": len(picked), "candidates": len(allf), "items": picked},
                   ensure_ascii=False, indent=2),
        "utf-8",
    )
    contact(picked, outdir / "contact.jpg")
    return 0


if __name__ == "__main__":
    sys.exit(main())

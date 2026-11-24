# -*- coding: utf-8 -*-
"""把 MinerU 的 content_list.json 转成可读的 source\\book.md + page-map.tsv。

用法：
  python tools\\build_book_md.py                 # 处理 out\\parse 下所有 book
  python tools\\build_book_md.py --slug color-bible

产物（photo-vision\\books\\<slug>\\source\\）：
  book.md         按页锚定的全文，图片保留相对引用
  page-map.tsv    全局页号 ↔ 原书页码 ↔ 该页图片数 ↔ 该页字数
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
PARSE = ROOT / "out" / "parse"
BOOKS = ROOT / "books"


def img_size(p: Path) -> tuple[int, int]:
    try:
        with Image.open(p) as im:
            return im.size
    except Exception:
        return (0, 0)


def convert(slug: str) -> dict:
    src = PARSE / slug
    cl_path = src / "content_list.json"
    if not cl_path.exists():
        raise SystemExit(f"缺少 {cl_path}")
    blocks = json.loads(cl_path.read_text("utf-8"))

    by_page: dict[int, list[dict]] = defaultdict(list)
    for b in blocks:
        by_page[int(b.get("page_idx") or 0)].append(b)

    outdir = BOOKS / slug / "source"
    outdir.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    pmap: list[str] = ["md_page\tbook_page\timages\tchars\tnote"]
    total_chars = 0
    total_imgs = 0

    for page_no, pidx in enumerate(sorted(by_page), start=1):
        pblocks = by_page[pidx]
        pblocks.sort(key=lambda b: (b.get("bbox") or [0, 0, 0, 0])[1])
        chars = 0
        nimg = 0
        book_page = ""
        notes: list[str] = []
        body: list[str] = []

        for b in pblocks:
            t = b.get("type")
            if t == "text":
                txt = (b.get("text") or "").strip()
                if txt:
                    body.append(txt)
                    chars += len(txt)
            elif t == "title":
                txt = (b.get("text") or "").strip()
                lv = b.get("text_level") or 1
                if txt:
                    body.append(("#" * (2 + min(int(lv), 3))) + " " + txt)
                    chars += len(txt)
            elif t in ("image", "figure"):
                ip = (b.get("img_path") or "").strip()
                name = Path(ip).name if ip else ""
                local = src / "images" / name
                w, h = img_size(local) if local.exists() else (0, 0)
                nimg += 1
                cap = " ".join((b.get("image_caption") or []) + (b.get("image_footnote") or [])).strip()
                tag = f"p{page_no:03d}-f{nimg}"
                if name:
                    body.append(f"![{tag} {w}x{h}](images/{name})")
                else:
                    body.append(f"[图 {tag} 无文件]")
                if cap:
                    body.append(f"*图注*：{cap}")
                    chars += len(cap)
            elif t == "table":
                html = (b.get("table_body") or "").strip()
                cap = " ".join(b.get("table_caption") or []).strip()
                body.append("[table] " + (cap or "") + "\n" + html[:4000])
                chars += len(cap)
                notes.append("table")
            elif t in ("equation", "interline_equation"):
                body.append("[equation] " + (b.get("text") or "").strip())
                notes.append("equation")
            elif t == "page_number":
                val = (b.get("text") or "").strip()
                if val and not book_page:
                    book_page = val
            else:
                # list / header / footer / aside_text 等
                txt = (b.get("text") or "").strip()
                if txt:
                    body.append(f"[{t}] {txt}")
                    chars += len(txt)
                    notes.append(t)

        lines.append(f"## p{page_no:03d}")
        lines.extend(body)
        lines.append("")
        total_chars += chars
        total_imgs += nimg
        pmap.append(
            f"p{page_no:03d}\t{book_page or ''}\t{nimg}\t{chars}\t{','.join(sorted(set(notes)))}"
        )

    (outdir / "book.md").write_text("\n".join(lines), "utf-8")
    (outdir / "page-map.tsv").write_text("\n".join(pmap) + "\n", "utf-8")

    # 图片目录做一份符号链接副本不划算，改为写清单
    imgs = sorted((src / "images").glob("*")) if (src / "images").exists() else []
    manifest = [f"{p.name}\t{p.stat().st_size}" for p in imgs if p.is_file()]
    (outdir / "images.tsv").write_text("\n".join(manifest) + "\n", "utf-8")

    stats = {
        "slug": slug,
        "pages": len(by_page),
        "blocks": len(blocks),
        "chars": total_chars,
        "images": total_imgs,
        "book_md": str(outdir / "book.md"),
        "book_md_bytes": (outdir / "book.md").stat().st_size,
        "with_book_page": sum(1 for r in pmap[1:] if r.split("\t")[1]),
    }
    print(
        f"[{slug}] {stats['pages']} 页 · {stats['blocks']} 块 · {stats['chars']} 字 · "
        f"{stats['images']} 图 · book.md {stats['book_md_bytes']} B"
        f" · 有原书页码 {stats['with_book_page']} 页"
    )
    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", default="")
    a = ap.parse_args()
    slugs = [a.slug] if a.slug else [p.name for p in PARSE.iterdir() if p.is_dir()]
    out = []
    for s in slugs:
        if (PARSE / s / "content_list.json").exists():
            out.append(convert(s))
    (ROOT / "out" / "book_md_stats.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), "utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

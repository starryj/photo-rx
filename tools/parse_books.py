# -*- coding: utf-8 -*-
"""批一：把三本书整本交 MinerU 解析（串行），完成后复制产物到 photo-vision\\out\\parse\\<slug>\\。

用法：
  python tools\\parse_books.py                # 跑批一三本
  python tools\\parse_books.py --slug color-bible
  python tools\\parse_books.py --force        # 已解析过也重跑
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

import requests

try:  # 控制台按 UTF-8 输出，避免 pwsh 管道按 GBK 解码成乱码
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BOOKDIR = Path(r"E:\03-Book\Photography")
SVC = "http://127.0.0.1:11500"
SVCOUT = Path(r"G:\AI_Workspace\06-VisionService\out\parse")
ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "out" / "parse"

BATCH1 = [
    ("color-bible", "摄影色彩圣经"),
    ("interacting-with-color", "Interacting with Color"),
    ("interaction-of-color", "Interaction of Color"),
]

BATCH4 = [
    ("chinese-aesthetics", "中国美学史大纲"),
    ("meixue-sanbu", "美学散步"),
]
BATCH3 = [
    ("arnheim-art", "艺术与视知觉"),
    ("gombrich-illusion", "艺术与错觉"),
]
BATCH2 = [
    ("freeman-sight", "摄影师的视界"),
    ("freeman-light", "光线与用光"),
]

BATCH6 = [
    ("linquan-gaozhi", "林泉高致"),
]

BATCH7 = [
    ("photo-composition-color", "摄影构图与色彩设计"),
]

BATCH8 = [
    ("sense-of-order", "秩序感"),
    ("ways-of-seeing", "观看之道"),
]


def find_pdf(key: str) -> Path:
    hits = [p for p in BOOKDIR.glob("*.pdf") if key in p.name]
    if len(hits) != 1:
        raise SystemExit(f"匹配到 {len(hits)} 个文件：{key} -> {[h.name for h in hits]}")
    return hits[0]


def wait_job(jid: str, label: str, timeout_s: int = 3600) -> dict:
    t0 = time.time()
    last = ""
    while True:
        r = requests.get(f"{SVC}/v1/jobs/{jid}", timeout=30)
        r.raise_for_status()
        job = r.json()
        state = job.get("state")
        prog = job.get("progress")
        msg = job.get("message") or ""
        line = f"{state} {prog:.0%} {msg}"
        if line != last:
            print(f"  [{label}] {line}", flush=True)
            last = line
        if state in ("done", "failed", "error"):
            if state != "done":
                raise SystemExit(f"{label} 解析失败：{job.get('error') or msg}")
            return job
        if time.time() - t0 > timeout_s:
            raise SystemExit(f"{label} 轮询超时（{timeout_s}s）")
        time.sleep(3)


def run_one(slug: str, key: str, force: bool) -> dict:
    pdf = find_pdf(key)
    target = DEST / slug
    stamp = target / "_meta.json"
    if stamp.exists() and not force:
        meta = json.loads(stamp.read_text("utf-8"))
        print(f"[{slug}] 已解析过，跳过（{meta.get('pages')} 页，{meta.get('md_chars')} 字）")
        return meta

    size_mb = pdf.stat().st_size / 1048576
    print(f"[{slug}] {pdf.name} ({size_mb:.1f} MB) -> 提交 MinerU …", flush=True)
    t0 = time.time()
    r = requests.post(
        f"{SVC}/v1/pdf/parse",
        data={"path": str(pdf)},
        timeout=120,
    )
    r.raise_for_status()
    jid = r.json()["job_id"]
    print(f"  job={jid}", flush=True)
    job = wait_job(jid, slug)
    res = job.get("result") or {}
    saved = res.get("saved") or {}
    secs = round(time.time() - t0, 1)

    src = Path(saved.get("dir") or "")
    if not src.exists():
        raise SystemExit(f"[{slug}] 服务报的产物目录不存在：{src}")

    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    for name in ("index.md", "content_list.json"):
        if (src / name).exists():
            shutil.copy2(src / name, target / name)
    ims = src / "images"
    n_img = 0
    if ims.exists():
        tgt_im = target / "images"
        tgt_im.mkdir(exist_ok=True)
        for f in ims.glob("*"):
            if f.is_file():
                shutil.copy2(f, tgt_im / f.name)
                n_img += 1

    meta = {
        "slug": slug,
        "source_pdf": pdf.name,
        "mineru_service_dir": str(src),
        "backend": res.get("backend") or "pipeline",
        "pages": None,
        "md_chars": saved.get("md_chars"),
        "n_blocks": saved.get("n_blocks"),
        "n_images": n_img,
        "parse_ms": res.get("ms"),
        "wall_s": secs,
        "job_id": jid,
        "parsed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    stamp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), "utf-8")
    print(
        f"[{slug}] 完成 {secs}s · 正文 {meta['md_chars']} 字 · "
        f"{meta['n_blocks']} 块 · {n_img} 张图",
        flush=True,
    )
    return meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--batch", type=int, default=1)
    a = ap.parse_args()

    pool = {1: BATCH1, 2: BATCH2, 3: BATCH3, 4: BATCH4, 6: BATCH6, 7: BATCH7, 8: BATCH8}[a.batch]
    todo = [b for b in pool if not a.slug or b[0] == a.slug]
    if not todo:
        raise SystemExit(f"未知 slug：{a.slug}")

    DEST.mkdir(parents=True, exist_ok=True)
    out = []
    for slug, key in todo:
        out.append(run_one(slug, key, a.force))

    print(f"\n=== 批{a.batch}解析汇总 ===")
    for m in out:
        print(f"{m['slug']:26} {str(m['md_chars']):>8} 字  {m['n_images']:>4} 图  {m['wall_s']:>7}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

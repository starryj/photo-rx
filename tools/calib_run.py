# -*- coding: utf-8 -*-
"""校准批跑：10 张图版过 VLM，3 页过 MinerU OCR，结果落 JSON。

用法：python calib_run.py [--only vlm|ocr]
"""
from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:11500"
ROOT = Path(__file__).resolve().parent.parent
CALIB = ROOT / "out" / "calib"
BOOK_DIR = Path(r"E:\03-Book\Photography")

# (id, 图片, task_id, 问法说明——写进报告)
VLM_ITEMS = [
    ("C01", "interacting_p31.png", "figure_semantics"),
    ("C02", "ioc_p126.png", "figure_semantics"),
    ("C03", "arnheim_p26.png", "page_region"),
    ("C04", "arnheim2_p530.png", "quality_check"),
    ("C05", "gombrich_p56.png", "page_region"),
    ("C06", "zhongguo_p286.png", "page_region"),
    ("C07", "meixue_p111.png", "figure_semantics"),
    ("C08", "shengjing_p96.png", "figure_semantics"),
    ("C09", "shijie_p166.png", "page_region"),
    ("C10", "guangxian_p121.png", "figure_semantics"),
]

OCR_ITEMS = [
    ("O01", "中国美学史大纲 (叶朗) (z-library.sk, 1lib.sk, z-lib.sk).pdf", 286, "中文扫描正文"),
    ("O02", "Interacting with Color A Pr_ (z-library.sk, 1lib.sk, z-lib.sk).pdf", 31, "英文图版说明"),
    ("O03", "艺术与视知觉（35周年纪念版） (鲁道夫·阿恩海姆) (z-library.sk, 1lib.sk, z-lib.sk).pdf", 26, "中文图文混排"),
]


def vlm() -> list[dict]:
    out = []
    with httpx.Client(timeout=300) as c:
        for cid, img, task in VLM_ITEMS:
            t0 = time.time()
            with open(CALIB / img, "rb") as f:
                r = c.post(f"{BASE}/v1/describe",
                           data={"task_id": task, "force": "true"},
                           files={"file": (img, f, "image/png")})
            j = r.json()
            out.append({"id": cid, "img": img, "task": task, "ms": int((time.time() - t0) * 1000),
                        "used": j.get("used"), "model": j.get("model"), "cached": j.get("cached"),
                        "sent": j.get("sent") or j.get("image_size"), "text": j.get("text") or j.get("description") or json.dumps(j, ensure_ascii=False)[:400]})
            print(f"VLM {cid} {out[-1]['ms']}ms chars={len(out[-1]['text'])}", flush=True)
    return out


def ocr() -> list[dict]:
    out = []
    with httpx.Client(timeout=600) as c:
        for oid, fname, pno, note in OCR_ITEMS:
            pdf = BOOK_DIR / fname
            r = c.post(f"{BASE}/v1/pdf/parse",
                       data={"path": str(pdf), "start_page_id": pno - 1, "end_page_id": pno})
            jid = r.json()["job_id"]
            for _ in range(200):
                time.sleep(3)
                j = c.get(f"{BASE}/v1/jobs/{jid}").json()
                if j.get("state") != "running":
                    break
            saved = (j.get("result") or {}).get("saved") or {}
            md = ""
            if saved.get("md_path") and Path(saved["md_path"]).exists():
                md = Path(saved["md_path"]).read_text(encoding="utf-8", errors="replace")
                dest = CALIB / f"{oid}.md"
                dest.write_text(md, encoding="utf-8")
            out.append({"id": oid, "book": fname, "page": pno, "note": note,
                        "state": j.get("state"), "msg": j.get("message"),
                        "md_chars": len(md), "n_blocks": saved.get("n_blocks"),
                        "n_images": saved.get("n_images"), "md": md[:4000]})
            print(f"OCR {oid} state={j.get('state')} chars={len(md)}", flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["vlm", "ocr"])
    a = ap.parse_args()
    res = {}
    if a.only in (None, "vlm"):
        res["vlm"] = vlm()
    if a.only in (None, "ocr"):
        res["ocr"] = ocr()
    dest = CALIB / f"calib_run_{a.only or 'all'}.json"
    dest.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"WROTE {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

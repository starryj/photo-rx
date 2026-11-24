# -*- coding: utf-8 -*-
"""模板修好后复测：C01/C02/C07 走 figure_semantics v2，C04 走 quality_check v2，C05 走 page_region v2。"""
from __future__ import annotations

import json
import time
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:11500"
CALIB = Path(__file__).resolve().parent.parent / "out" / "calib"

ITEMS = [
    ("C01", "interacting_p31.png", "figure_semantics"),
    ("C02", "ioc_p126.png", "figure_semantics"),
    ("C07", "meixue_p111.png", "figure_semantics"),
    ("C04", "arnheim2_p530.png", "quality_check"),
    ("C05", "gombrich_p56.png", "page_region"),
]


def main() -> int:
    out = []
    with httpx.Client(timeout=300) as c:
        for cid, img, task in ITEMS:
            t0 = time.time()
            with open(CALIB / img, "rb") as f:
                r = c.post(f"{BASE}/v1/describe", data={"task_id": task, "force": "true"},
                           files={"file": (img, f, "image/png")})
            j = r.json()
            out.append({"id": cid, "task": task, "ms": int((time.time() - t0) * 1000),
                        "used": j.get("used"), "text": j.get("text") or ""})
            print(f"{cid} {out[-1]['ms']}ms chars={len(out[-1]['text'])}", flush=True)
    dest = CALIB / "calib_run_round2.json"
    dest.write_text(json.dumps({"vlm": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"WROTE {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

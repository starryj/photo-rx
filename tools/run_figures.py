# -*- coding: utf-8 -*-
"""对挑出来的图版逐张跑本地 VLM 定性解读，落 jsonl（可断点续跑）。

用法：
  python tools\\run_figures.py --slug color-bible --task photo_example
  python tools\\run_figures.py --slug interacting-with-color --task figure_semantics
  python tools\\run_figures.py --slug interaction-of-color --task figure_semantics
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
SVC = "http://127.0.0.1:11500"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--task", default="figure_semantics")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-px", type=int, default=1600)
    a = ap.parse_args()

    base = ROOT / "out" / "figures" / a.slug
    picked = json.loads((base / "picked.json").read_text("utf-8"))["items"]
    if a.limit:
        picked = picked[: a.limit]

    out = base / f"desc_{a.task}.jsonl"
    done: set[str] = set()
    if out.exists():
        for line in out.read_text("utf-8").splitlines():
            try:
                done.add(json.loads(line)["img"])
            except Exception:
                pass
    todo = [it for it in picked if it["img"] not in done]
    print(f"[{a.slug}] 共 {len(picked)} 张，已完成 {len(done)}，待跑 {len(todo)} · task={a.task}")

    t_all = time.time()
    fh = out.open("a", encoding="utf-8")
    ok = fail = 0
    for i, it in enumerate(todo, 1):
        t0 = time.time()
        rec: dict = {
            "page_idx": it["page_idx"],
            "img": it["img"],
            "frac": it["frac"],
            "px": it["px"],
            "caption": it.get("caption", ""),
            "task": a.task,
        }
        try:
            r = requests.post(
                f"{SVC}/v1/describe",
                data={"path": it["path"], "task_id": a.task, "force": "1"},
                timeout=300,
            )
            r.raise_for_status()
            d = r.json()
            rec.update(
                {
                    "ok": True,
                    "text": (d.get("text") or "").strip(),
                    "used": d.get("used"),
                    "model": d.get("model"),
                    "sent": d.get("sent"),
                    "ms": d.get("ms"),
                }
            )
            ok += 1
        except Exception as e:  # noqa: BLE001
            rec.update({"ok": False, "error": f"{type(e).__name__}: {e}"})
            fail += 1
        rec["wall_s"] = round(time.time() - t0, 2)
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        fh.flush()
        flag = "ok" if rec["ok"] else "FAIL"
        print(
            f"  [{i}/{len(todo)}] p{it['page_idx'] + 1:03d} {flag} {rec['wall_s']}s "
            f"{(rec.get('text') or rec.get('error') or '')[:70]}",
            flush=True,
        )

    fh.close()
    print(f"\n[{a.slug}] 完成 {ok} 失败 {fail}，总耗时 {round(time.time() - t_all, 1)}s -> {out}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

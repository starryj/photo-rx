# -*- coding: utf-8 -*-
"""丢掉 S07 / S09 / S38 三条旧转写，让 ocr_verify.py run 只补这三张（裁图已因 locate 修复而变）。"""
import json
from pathlib import Path

OUT = Path("out/ocr-sample")
jl = OUT / "transcripts.jsonl"
DROP = {"S07", "S09", "S38"}

kept, dropped = [], []
for line in jl.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    rec = json.loads(line)
    (dropped if rec.get("sample_id") in DROP else kept).append(rec)

jl.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept), encoding="utf-8")
print(f"kept {len(kept)} · dropped {[r['sample_id'] for r in dropped]}")
for r in dropped:
    print("  old:", r["sample_id"], "ok=", r.get("ok"), "len=", len(r.get("text") or ""))

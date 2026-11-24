# -*- coding: utf-8 -*-
"""诊断：为什么个别裁图转写返回空串。打印完整响应 JSON。"""
import json
import sys
from pathlib import Path

import requests

OUT = Path("out/ocr-sample")
SVC = "http://127.0.0.1:11500"
sid = sys.argv[1] if len(sys.argv) > 1 else "S07"
p = OUT / f"{sid}.png"
with p.open("rb") as fh:
    r = requests.post(
        f"{SVC}/v1/describe",
        files={"file": (p.name, fh, "image/png")},
        data={"task_id": "verbatim_transcribe", "force": "1"},
        timeout=900,
    )
print("HTTP", r.status_code)
j = r.json()
j2 = dict(j)
if isinstance(j2.get("text"), str):
    j2["text"] = f"<{len(j2['text'])} chars> {j2['text'][:120]}"
print(json.dumps(j2, ensure_ascii=False, indent=1)[:1500])

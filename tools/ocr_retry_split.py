"""对少数「视觉服务返回空串」的裁图做窄版重试：把裁图缩到更窄，减少一次性要读的字数。"""
import json
import sys
from pathlib import Path

import requests
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\ocr-sample")
SVC = "http://127.0.0.1:11500"

for sid in sys.argv[1:]:
    src = OUT / f"{sid}.png"
    im = Image.open(src).convert("RGB")
    # 上下切两半分别读，再拼起来
    w, h = im.size
    half = h // 2
    texts = []
    for i, box in enumerate([(0, 0, w, half + 20), (0, half - 20, w, h)]):
        part = im.crop(box)
        scale = 760 / part.width
        part = part.resize((760, int(part.height * scale)), Image.LANCZOS)
        canvas = Image.new("RGB", (766, part.height + 6), "white")
        canvas.paste(part, (3, 3))
        tmp = OUT / f"_{sid}_p{i}.png"
        canvas.save(tmp)
        with tmp.open("rb") as fh:
            r = requests.post(
                f"{SVC}/v1/describe",
                files={"file": (tmp.name, fh, "image/png")},
                data={"task_id": "verbatim_transcribe", "force": "1"},
                timeout=600,
            )
        j = r.json()
        t = (j.get("text") or "").strip()
        print(f"{sid} part{i}: {len(t)} 字")
        texts.append(t)
    joined = " ".join(x for x in texts if x)
    rec = {"sample_id": sid, "ok": bool(joined), "text": joined, "split": True}
    with (OUT / "transcripts.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"{sid} → {len(joined)} 字")

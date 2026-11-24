# -*- coding: utf-8 -*-
"""补读返回空串的裁图：整块读不出来，就横切成 strips 逐条读再拼接。

为什么这样修：视觉服务会把长边压到 max_image_px（约 820 px），
一块 1091×705 的裁图压下去，正文字高只剩十来个像素，4B 会直接回空串。
横切后每条 strip 的长边仍在同一上限内，但字在画面里的相对尺寸变大，
模型就能读出来。每轮都改字节（加 1 px 白边）以绕开「空结果被缓存」。
"""
import json
import sys
import time
from pathlib import Path

import requests
from PIL import Image

OUT = Path("out/ocr-sample")
SVC = "http://127.0.0.1:11500"
TASK = "verbatim_transcribe"
JL = OUT / "transcripts.jsonl"


def read(png_bytes: bytes, name: str, force: bool = True) -> str:
    r = requests.post(
        f"{SVC}/v1/describe",
        files={"file": (name, png_bytes, "image/png")},
        data={"task_id": TASK, "force": "1" if force else "0"},
        timeout=900,
    )
    r.raise_for_status()
    return (r.json().get("text") or "").strip()


def to_bytes(im: Image.Image, border: int = 0) -> bytes:
    import io

    if border:
        im = ImageOps_expand(im, border)
    b = io.BytesIO()
    im.save(b, format="PNG")
    return b.getvalue()


def ImageOps_expand(im: Image.Image, border: int) -> Image.Image:
    w, h = im.size
    canvas = Image.new("RGB", (w + 2 * border, h + 2 * border), "white")
    canvas.paste(im, (border, border))
    return canvas


def strips(im: Image.Image, n: int, overlap: float = 0.12):
    w, h = im.size
    step = h / n
    out = []
    for i in range(n):
        y0 = max(0, int(i * step - overlap * step))
        y1 = min(h, int((i + 1) * step + overlap * step))
        out.append(im.crop((0, y0, w, y1)))
    return out


def recover(sid: str) -> dict:
    p = OUT / f"{sid}.png"
    im = Image.open(p).convert("RGB")
    w, h = im.size
    t0 = time.time()

    # 1) 整块先试一次（会让出缓存）；不行再切
    tries = [("whole", im)]
    n = 2 if h < 900 else 3
    for i, s in enumerate(strips(im, n)):
        tries.append((f"strip{i+1}", s))

    parts = []
    log = []
    for tag, sub in tries:
        if tag != "whole" and parts:
            # 已经用 strips 拼出来就不读整块了
            pass
        for border in (0, 1):  # 第二遍改字节绕缓存
            try:
                txt = read(to_bytes(sub, border), f"{sid}_{tag}_{border}.png")
            except Exception as e:  # noqa: BLE001
                txt = ""
                log.append(f"{tag}/b{border} err {str(e)[:80]}")
            if txt:
                log.append(f"{tag}/b{border} ok {len(txt)}")
                if tag == "whole":
                    return {"sample_id": sid, "text": txt, "via": "whole", "log": log,
                            "ms": int((time.time() - t0) * 1000)}
                parts.append(txt)
                break
            log.append(f"{tag}/b{border} empty")
        if tag == "whole":
            continue

    txt = "\n".join(parts) if parts else ""
    return {"sample_id": sid, "text": txt, "via": f"strips{n}", "log": log,
            "ms": int((time.time() - t0) * 1000)}


def main():
    sids = sys.argv[1:] or ["S07", "S09", "S38"]
    recs = []
    for sid in sids:
        r = recover(sid)
        print(f"{sid} via={r['via']} {r['ms']}ms {len(r['text'])}字  {r['log'][-4:]}")
        recs.append(r)

    # 用新结果替换 transcripts.jsonl 里对应 sid 的记录（含空串记录）
    lines = []
    repl = {r["sample_id"]: r for r in recs}
    for line in JL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        sid = rec.get("sample_id")
        if sid in repl:
            new = repl.pop(sid)
            lines.append({"sample_id": sid, "ok": bool(new["text"]), "text": new["text"],
                          "ms": new["ms"], "via": new["via"], "recovered": True})
        else:
            lines.append(rec)
    for sid, new in repl.items():
        lines.append({"sample_id": sid, "ok": bool(new["text"]), "text": new["text"],
                      "ms": new["ms"], "via": new["via"], "recovered": True})
    JL.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in lines), encoding="utf-8")
    print("transcripts.jsonl 现有", len(lines), "条")


if __name__ == "__main__":
    main()

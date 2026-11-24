"""用视觉服务对 40 张 OCR 抽样裁图做「只转写不解释」，再与 claims 里的逐字引文对比。

目的：验证 MinerU 的 OCR 有没有把字抄错，从而污染我们引用的「逐字引文」。
这是独立第二读——同一个模型转写，不是为了证明 OCR 错，而是找出「两个读者不一致」的位置，
再对不一致处人工回看原页。

用法：
  python tools\\ocr_verify.py run      # 逐张调服务，写 out\\ocr-sample\\transcripts.jsonl（断点续跑）
  python tools\\ocr_verify.py diff     # 与 manifest 对齐，输出逐条相似度与差异，写 report.md
"""
import argparse
import difflib
import json
import re
import sys
import time
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision")
OUT = ROOT / "out" / "ocr-sample"
SVC = "http://127.0.0.1:11500"


def levenshtein(a, b):
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        ca = a[i - 1]
        for j in range(1, lb + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != b[j - 1]))
        prev = cur
    return prev[lb]


def norm(s):
    s = re.sub(r"\s+", "", s or "")
    return "".join(ch for ch in s if ch.isalnum())


def run(outdir=None, retry_failed=False):
    out = Path(outdir) if outdir else OUT
    man = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    done = set()
    jl = out / "transcripts.jsonl"
    if jl.exists():
        recs = []
        for line in jl.read_text(encoding="utf-8").splitlines():
            if line.strip():
                recs.append(json.loads(line))
        if retry_failed:
            keep = [r for r in recs if r.get("ok")]
            jl.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in keep),
                          encoding="utf-8")
            recs = keep
        done = {r["sample_id"] for r in recs}
    print(f"已完成 {len(done)} / {len(man)}")
    with jl.open("a", encoding="utf-8") as f:
        for m in man:
            sid = m["sample_id"]
            if sid in done:
                continue
            p = out / f"{sid}.png"
            t0 = time.time()
            try:
                with p.open("rb") as fh:
                    r = requests.post(
                        f"{SVC}/v1/describe",
                        files={"file": (p.name, fh, "image/png")},
                        data={"task_id": "verbatim_transcribe", "force": "1"},
                        timeout=600,
                    )
                r.raise_for_status()
                j = r.json()
                text = j.get("text") or ""
                rec = {"sample_id": sid, "ok": bool(j.get("ok")), "text": text,
                       "ms": int((time.time() - t0) * 1000), "sent": j.get("sent"), "used": j.get("used")}
            except Exception as e:
                rec = {"sample_id": sid, "ok": False, "text": "", "error": str(e)[:300]}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            print(f"  {sid} ok={rec['ok']} {rec.get('ms','-')}ms {len(rec['text'])}字")


def diff(outdir=None):
    out = Path(outdir) if outdir else OUT
    man = {m["sample_id"]: m for m in json.loads((out / "manifest.json").read_text(encoding="utf-8"))}
    tr = {}
    for line in (out / "transcripts.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            tr[r["sample_id"]] = r

    rows = []
    for sid in sorted(man):
        m = man[sid]
        r = tr.get(sid, {})
        got = norm(r.get("text"))
        want = norm(m["quote"])
        detail = ""
        if not got:
            ratio, verdict = 0.0, "空转写"
        else:
            sm = difflib.SequenceMatcher(None, want, got)
            if want and want in got:
                ratio, verdict = 1.0, "引文整句在转写内"
            else:
                # 近似子串匹配：在转写里找编辑距离最小的窗口
                L = len(want)
                lo, hi = max(1, int(L * 0.7)), int(L * 1.4) + 4
                best = (10 ** 9, 0, 0)
                for st in range(0, max(1, len(got) - lo + 1)):
                    for wl in range(lo, min(hi, len(got) - st) + 1):
                        d = levenshtein(want, got[st: st + wl])
                        if d < best[0]:
                            best = (d, st, wl)
                dist, st, wl = best
                win = got[st: st + wl]
                ratio = max(0.0, 1.0 - dist / max(1, L))
                ops = difflib.SequenceMatcher(None, want, win).get_opcodes()
                parts = []
                for tag, i1, i2, j1, j2 in ops:
                    if tag == "equal":
                        if i2 - i1 >= 1:
                            parts.append(want[i1:i2])
                    elif tag == "replace":
                        parts.append(f"【{want[i1:i2]}→{win[j1:j2]}】")
                    elif tag == "delete":
                        parts.append(f"【多{''.join(want[i1:i2])}】")
                    else:
                        parts.append(f"【少{''.join(win[j1:j2])}】")
                detail = "".join(parts)
                verdict = "逐字一致" if ratio > 0.97 else ("个别字不同" if ratio > 0.85 else "不一致")
        rows.append((sid, m, r, got, want, ratio, verdict, detail))

    rows.sort(key=lambda x: x[5])
    lines = [f"# OCR 引文抽样核对（{len(rows)} 条）", "",
             "方法：把 claims 里每条逐字引文回定位到 PDF 原页的文本块，裁出该区域（放大到约 1080 px 宽），",
             "交给视觉服务（qwen3-vl:4b，`verbatim_transcribe` 模板，只转写不解释），再把转写结果与引文做归一化比对。",
             "两个读者不一致处，就是需要回原页人工裁决的位置。", "",
             "| 样本 | 书 | claim | 页 | 相似度 | 判定 |", "|---|---|---|---|---|---|"]
    for sid, m, r, got, want, ratio, verdict, detail in rows:
        lines.append(f"| {sid} | {m['book']} | {m['claim_id']} | p{m['md_anchor']} | {ratio:.2f} | {verdict} |")

    bad = [x for x in rows if x[5] <= 0.85]
    lines += ["", f"## 需要人工回看的位置（相似度 ≤ 0.85）：{len(bad)} 条", ""]
    for sid, m, r, got, want, ratio, verdict, detail in bad:
        lines += [f"### {sid} · {m['book']} · {m['claim_id']}（{ratio:.2f}）",
                  f"- 引文：{m['quote']}",
                  f"- 逐字对照：{detail[:900]}", ""]

    meh = [x for x in rows if 0.85 < x[5] <= 0.97]
    lines += ["", f"## 轻微不一致（0.85 < 相似度 ≤ 0.97）：{len(meh)} 条", ""]
    for sid, m, r, got, want, ratio, verdict, detail in meh:
        lines += [f"- {sid} {m['claim_id']}（{ratio:.2f}）{detail[:300]}"]

    n30 = sum(1 for x in rows if x[5] > 0.97)
    lines += ["", "## 汇总", "",
              f"- {len(rows)} 条里 {n30} 条与独立转写几乎逐字一致（>0.97）；{len(meh)} 条轻微不一致；{len(bad)} 条需回原页裁决。",
              "- 口径边界：第二个读者也是视觉模型（4B），它自己的误读会记成「不一致」，所以「不一致」不等于「OCR 错」，只是「该看一眼」。"]
    (out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"n30={n30} 轻微={len(meh)} 需裁决={len(bad)} → {out / 'report.md'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "diff"])
    ap.add_argument("--out", default=None, help="样本目录，默认 out\\ocr-sample")
    ap.add_argument("--retry-failed", action="store_true", help="删掉失败记录并重跑")
    a = ap.parse_args()
    run(a.out, a.retry_failed) if a.cmd == "run" else diff(a.out)

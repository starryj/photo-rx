"""把 picked.json + desc_photo_example.jsonl 合成 digest.md。

只做排版与统计，不改写模型描述；描述里的题材来自 Qwen3-VL 首句。
用法：python tools/build_figure_digest.py --slug photo-composition-color
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def first_topic(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    m = re.search(r"(?:1\.\s*)?题材[：:]\s*(.+)", text)
    if m:
        line = m.group(1)
    else:
        line = text.splitlines()[0]
        line = re.sub(r"^1\.\s*", "", line)
    line = line.strip()
    line = re.split(r"[。\n]", line)[0]
    return line[:60]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", default="photo-composition-color")
    ap.add_argument("--task", default="photo_example")
    args = ap.parse_args()

    figdir = ROOT / "out" / "figures" / args.slug
    picked = json.loads((figdir / "picked.json").read_text(encoding="utf-8"))
    desc_path = figdir / f"desc_{args.task}.jsonl"
    desc = {}
    for line in desc_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("img"):
            desc[r["img"]] = r

    items = sorted(picked["items"], key=lambda x: x["page_idx"])
    rows = []
    for it in items:
        p = it["page_idx"] + 1
        r = desc.get(it["img"], {})
        text = r.get("text", "")
        rows.append(
            {
                "page": f"p{p:03d}",
                "frac": round(it["frac"] * 100),
                "topic": first_topic(text) or "（无描述）",
                "text": text.replace("\n", " ").strip(),
                "ok": r.get("ok"),
                "ms": r.get("ms"),
            }
        )

    ok = sum(1 for r in rows if r["ok"])
    pages = {r["page"] for r in rows}
    avg = round(sum(r["frac"] for r in rows) / len(rows), 1)

    out = []
    out.append("# 曼特图版摘要：60 张代表图版\n")
    out.append(
        "> 来源 `books/photo-composition-color/source/book.md`（p001–p212）；"
        "任务 `photo_example`，本地 qwen3-vl:4b；"
        f"{ok}/{len(rows)} 张成功。\n"
    )
    out.append("## 怎么读\n")
    out.append(
        "- 抽样规则：sha1 去重、单图占页面面积 ≥10%、每页最多 2 张、按页均匀取 60。\n"
        "- 描述是模型对**画面结构**的读数：题材、色彩关系、光线性质、组织方式、用途猜测；"
        "不是色度测量，也不判断作者意图。\n"
        "- 图版里 p053（画幅比例示意）与 p111（A–F 几何关系示意）是示意图，其余以照片为主。\n"
        f"- 覆盖 {len(pages)} 页，平均单图占页 {avg}%（60 张合计占页面积不是 100%，两页一图时各算各的）。\n"
    )
    out.append("\n## 逐页目录\n")
    out.append("| 页 | 占页 | 题材（首句） |")
    out.append("|---|---:|---|")
    for r in rows:
        out.append(f"| {r['page']} | {r['frac']}% | {r['topic']} |")

    out.append("\n## 逐张描述\n")
    for r in rows:
        out.append(f"### {r['page']} · {r['frac']}%\n")
        out.append(r["text"] + "\n")
        out.append("")

    dst = figdir / "digest.md"
    dst.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {dst} ({len(rows)} rows, {ok} ok)")


if __name__ == "__main__":
    main()

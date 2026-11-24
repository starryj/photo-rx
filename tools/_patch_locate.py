# -*- coding: utf-8 -*-
"""修 ocr_sample.py 的 locate()：
1) min_len 14 → 8：短引文（如 ms06 归一后 12 字）此前被直接判 None，退化成整页裁图。
2) 把 image 块的 image_caption / image_footnote 纳入候选池，bbox 取图片框并向下扩
   18% 高度（图注通常紧贴图下沿），这样引到图注的条目也能按块裁。
只改这两个函数/常量，其余不动。
"""
from pathlib import Path
import re

P = Path(__file__).with_name("ocr_sample.py")
s = P.read_text(encoding="utf-8")

old_locate_head = '''def locate(cl, pidx, quote, min_len=14):'''
new_locate_head = '''def caption_blocks(cl, pidx):
    """图注块：MinerU 把图注放在 image 块的 image_caption / image_footnote 里，
    自身没有独立 bbox。取图片框并向下扩 18% 高度（图注紧贴图下沿）。"""
    out = []
    for b in cl:
        if int(b.get("page_idx") or 0) != pidx:
            continue
        if b.get("type") != "image":
            continue
        caps = []
        for k in ("image_caption", "image_footnote"):
            v = b.get(k)
            if isinstance(v, list):
                caps.extend([x for x in v if isinstance(x, str)])
            elif isinstance(v, str):
                caps.append(v)
        t = " ".join(x.strip() for x in caps if x and x.strip())
        bbox = b.get("bbox")
        if not t or not bbox or len(bbox) != 4:
            continue
        x0, y0, x1, y1 = bbox
        h = max(1.0, y1 - y0)
        out.append(([x0, y0, x1, min(1000.0, y1 + 0.18 * h)], t))
    return out


def locate(cl, pidx, quote, min_len=8):'''
assert old_locate_head in s
s = s.replace(old_locate_head, new_locate_head, 1)

# 在 blocks 收集完之后、if not blocks 之前并入图注块
old_tail = '''    if not blocks:
        return None
'''
new_tail = '''    blocks.extend(caption_blocks(cl, pidx))

    if not blocks:
        return None
'''
assert old_tail in s
s = s.replace(old_tail, new_tail, 1)

P.write_text(s, encoding="utf-8")
print("patched", P)
print("min_len=8:", "def locate(cl, pidx, quote, min_len=8)" in s)
print("caption_blocks:", "def caption_blocks(" in s)

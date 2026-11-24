"""Batch quote finder: given (id, [keywords...]) pairs, print the best verbatim sentence.

Usage:
  python tools/batch_quotes.py fs      # freeman-sight
  python tools/batch_quotes.py fl      # freeman-light
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

BOOKS = {"fs": "freeman-sight", "fl": "freeman-light"}

SPLIT = re.compile(r"(?<=[。！？；])[\s\u3000]*")

WANT = {
    "fs": [
        ("fs01", ["构图", "组织成"]),
        ("fs02", ["3:2", "美学"]),
        ("fs03", ["双眼", "水平"]),
        ("fs04", ["竖直格式", "上"]),
        ("fs05", ["方形", "刻板"]),
        ("fs06", ["全景", "真实"]),
        ("fs07", ["裁剪", "万能"]),
        ("fs08", ["填满", "环境"]),
        ("fs09", ["偏离中心", "理由"]),
        ("fs10", ["静态", "比例"]),
        ("fs11", ["黄金分割", "比例"]),
        ("fs12", ["地平线", "理想"]),
        ("fs13", ["框架", "平面"]),
        ("fs14", ["对比", "平衡", "原则"]),
        ("fs15", ["和谐感", "构图规则"]),
        ("fs16", ["整体", "部分"]),
        ("fs17", ["平衡", "完美", "眼睛"]),
        ("fs18", ["持久"]),
        ("fs19", ["模棱两可"]),
        ("fs20", ["节奏", "引导"]),
        ("fs21", ["纹理", "图案"]),
        ("fs22", ["纹理", "结构", "触觉"]),
        ("fs23", ["透视", "加强"]),
        ("fs24", ["大小", "恒常"]),
        ("fs25", ["选择性", "清晰", "深度"]),
        ("fs26", ["重要性", "加权"]),
        ("fs27", ["眼睛", "注意"]),
        ("fs28", ["中央", "静止"]),
        ("fs29", ["两个", "更弱"]),
        ("fs30", ["斜线", "动态", "角度"]),
        ("fs31", ["三角形", "极易"]),
        ("fs32", ["圆形", "闭合"]),
        ("fs33", ["焦点", "关注点"]),
        ("fs34", ["决定性瞬间"]),
        ("fs35", ["广角", "影响"]),
        ("fs36", ["远摄", "结构"]),
        ("fs37", ["高色调", "彩色", "曝光错误"]),
        ("fs38", ["歌德", "赋值"]),
        ("fs39", ["对比色", "聚焦"]),
        ("fs40", ["柔和", "视觉空间"]),
        ("fs41", ["通道", "混合", "滤镜"]),
        ("fs42", ["目的", "意图"]),
        ("fs43", ["功效", "规则"]),
        ("fs44", ["兴趣点", "场景"]),
        ("fs45", ["模糊", "阅读速度"]),
        ("fs46", ["延迟"]),
        ("fs47", ["并置", "关系"]),
        ("fs48", ["探索", "限制"]),
        ("fs49", ["广角", "视点", "变化"]),
        ("fs50", ["回访", "风险"]),
    ],
    "fl": [
        ("fl01", ["20°", "3500K"]),
        ("fl02", ["金色", "色温"]),
        ("fl03", ["正午", "5200"]),
        ("fl04", ["阴天", "柔光板"]),
        ("fl05", ["积云", "色温"]),
        ("fl06", ["偏光镜", "天空"]),
        ("fl07", ["渐变滤镜", "直方图"]),
        ("fl08", ["眩光", "光圈"]),
        ("fl09", ["逆向", "剪影", "轮廓光"]),
        ("fl10", ["柔光", "方向"]),
        ("fl11", ["包围光", "超现实"]),
        ("fl12", ["硬光", "投影", "方向"]),
        ("fl13", ["明暗对照", "硬光", "柔光"]),
        ("fl14", ["边缘光", "形状"]),
        ("fl15", ["质感", "侧光"]),
        ("fl16", ["动态范围", "挡"]),
        ("fl17", ["位深", "动态范围"]),
        ("fl18", ["RAW", "JPEG"]),
        ("fl19", ["点测光", "2%"]),
        ("fl20", ["矩阵测光", "图像库"]),
        ("fl21", ["白平衡", "灰卡"]),
        ("fl22", ["创意白平衡", "演绎"]),
        ("fl23", ["硬光", "没有", "阻隔"]),
        ("fl24", ["柔光", "察觉"]),
        ("fl25", ["阴天", "扩散"]),
        ("fl26", ["白平衡", "加入", "演绎"]),
        ("fl27", ["逆光", "形状"]),
        ("fl28", ["质感", "侧光", "微观"]),
        ("fl29", ["正午", "投影"]),
        ("fl30", ["包围光", "少见"]),
        ("fl31", ["矩阵", "图像库"]),
        ("fl32", ["创意", "白平衡"]),
    ],
}


def load(slug: str):
    p = BASE / "books" / slug / "source" / "book.md"
    text = p.read_text(encoding="utf-8", errors="replace")
    pages, cur = [], "?"
    buf = []
    for line in text.splitlines():
        m = re.match(r"^## (p\d+)$", line.strip())
        if m:
            if buf:
                pages.append((cur, " ".join(buf)))
            cur, buf = m.group(1), []
            continue
        s = line.strip()
        if not s or s.startswith("!") or s.startswith("[header]") or s.startswith("[footer]"):
            continue
        buf.append(s)
    if buf:
        pages.append((cur, " ".join(buf)))
    return pages


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s)


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else "fs"
    slug = BOOKS[key]
    pages = load(slug)
    sents = []
    for page, body in pages:
        for raw in SPLIT.split(body):
            s = raw.strip()
            n = norm(s)
            if 12 <= len(n) <= 150:
                sents.append((page, s, n))
    for cid, kws in WANT[key]:
        kn = [norm(k) for k in kws]
        hits = [(p, s) for p, s, n in sents if all(k in n for k in kn)]
        if not hits:
            print(f"{cid}\tMISS\t{'|'.join(kws)}")
            continue
        hits.sort(key=lambda x: -len(norm(x[1])))
        page, s = hits[0]
        print(f"{cid}\t{page}\t{s}")


if __name__ == "__main__":
    main()

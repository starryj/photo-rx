"""批三（阿恩海姆 / 贡布里希）引文探针。

用法：python tools\\b3_quotes.py ar      # 阿恩海姆
      python tools\\b3_quotes.py go      # 贡布里希
      python tools\\b3_quotes.py ar ar07  # 只跑某一条

输出每行：id \t pNNN \t 字数 \t 原句
未命中：id \t MISS
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKS = {"ar": "arnheim-art", "go": "gombrich-illusion"}

WANT = {
    "ar": {
        "ar01": [["平衡", "力"]],
        "ar02": [["知觉力"]],
        "ar03": [["重力"]],
        "ar04": [["上方", "下方"]],
        "ar05": [["基底", "重量"]],
        "ar06": [["简化"]],
        "ar07": [["矫平"]],
        "ar08": [["增锐"]],
        "ar09": [["细分"]],
        "ar10": [["结构骨架"]],
        "ar11": [["图与底"]],
        "ar12": [["背景", "形状"]],
        "ar13": [["重叠", "深度"]],
        "ar14": [["梯度", "深度"]],
        "ar15": [["框架", "窗口"]],
        "ar16": [["相对亮度"]],
        "ar17": [["阴影"]],
        "ar18": [["光线", "空间"]],
        "ar19": [["形与色"]],
        "ar20": [["和谐"]],
        "ar21": [["冷", "暖", "色"]],
        "ar22": [["张力"]],
        "ar23": [["倾斜", "动"]],
        "ar24": [["表现性"]],
        "ar25": [["机械复制"]],
        "ar26": [["整体", "部分"]],
        "ar27": [["知觉概念"]],
        "ar28": [["视觉", "思维"]],
        "ar29": [["方向", "平衡"]],
        "ar30": [["中心", "力"]],
    },
    "go": {
        "go01": [["图式"]],
        "go02": [["修正"]],
        "go03": [["观看者", "本分"]],
        "go04": [["心理定向"]],
        "go05": [["错觉", "条件"]],
        "go06": [["符号"]],
        "go07": [["区别性特征"]],
        "go08": [["透视", "程式"]],
        "go09": [["逼真"]],
        "go10": [["投射"]],
        "go11": [["漫画"]],
        "go12": [["制作", "匹配"]],
        "go13": [["假设", "知觉"]],
        "go14": [["风格"]],
        "go15": [["程式", "再现"]],
        "go16": [["相似"]],
        "go17": [["光", "色", "程式"]],
        "go18": [["错觉", "信念"]],
        "go19": [["预期", "知觉"]],
        "go20": [["观看", "学习"]],
    },
}

MAXLEN = 150
MINLEN = 12


def norm(s: str) -> str:
    return re.sub(r"[\s\u3000]+", "", s)


def load_pages(slug: str):
    md = (ROOT / "books" / slug / "source" / "book.md").read_text(encoding="utf-8")
    pages, cur = [], None
    for line in md.splitlines():
        m = re.match(r"^## (p\d+)$", line)
        if m:
            cur = m.group(1)
            pages.append([cur, []])
            continue
        if cur and line.strip():
            pages[-1][1].append(line)
    return [(p, "\n".join(ls)) for p, ls in pages]


def clean(text: str) -> str:
    text = re.sub(r"!\ [[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"^\s*\[[a-z_]+\]\s*", " ", text, flags=re.M)
    text = re.sub(r"^\s*\*图注\*：", " ", text, flags=re.M)
    return text


def sentences(pages):
    out = []
    for page, text in pages:
        for s in re.split(r"(?<=[。！？；])", clean(text)):
            s = norm(s)
            if MINLEN <= len(s) <= MAXLEN:
                out.append((page, s))
    return out


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "ar"
    only = sys.argv[2] if len(sys.argv) > 2 else None
    slug = BOOKS[tag]
    pages = load_pages(slug)
    sents = sentences(pages)
    print(f"=== {slug} · {len(pages)} 页 · {len(sents)} 句 ===")
    for cid, groups in WANT[tag].items():
        if only and cid != only:
            continue
        hits = []
        for page, s in sents:
            for g in groups:
                if all(k in s for k in g):
                    hits.append((page, s))
                    break
            if len(hits) >= 4:
                break
        if not hits:
            print(f"{cid}\tMISS")
            continue
        for page, s in hits:
            print(f"{cid}\t{page}\t{len(s)}\t{s}")


if __name__ == "__main__":
    main()

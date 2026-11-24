"""批五：从 Pixar 画册的 XHTML 抽取正文，写成 book.md（与 PDF 书同一格式）。

只取 div.calibreEbookContent 内部的内容，跳过 calibreMeta / calibreEbNavTop / calibreEbNav
这类 Calibre 导航块（否则每页都重复书名、作者与「previous page next page」）。
"""
from __future__ import annotations

import io
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"E:\03-Book\Photography\The Art of Pixar The Comple\0ck4l-tht6i_files\OEBPS")
DST = ROOT / "books" / "art-of-pixar" / "source"

SKIP_CLASS = ("calibreMeta", "calibreEbNavTop", "calibreEbNav", "calibreNav")
VOID = {"br", "img", "hr", "meta", "link", "input"}


class Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[tuple[str, str]] = []
        self._skip = 0            # 跳过深度
        self._content = 0         # 是否在 calibreEbookContent 内
        self._buf: list[str] = []
        self._tag = ""

    def _cls(self, attrs) -> str:
        for k, v in attrs:
            if k == "class" and v:
                return v
        return ""

    def handle_starttag(self, tag, attrs):
        cls = self._cls(attrs)
        if tag not in VOID:
            if any(s in cls for s in SKIP_CLASS):
                self._skip += 1
            elif "calibreEbookContent" in cls:
                self._content += 1
        if self._skip or not self._content:
            if tag == "img" and not self._skip:
                pass
            return
        if tag == "img":
            self._flush()
            src = dict(attrs).get("src", "")
            self.parts.append(("img", src))
        elif tag in ("h1", "h2", "h3"):
            self._flush()
            self._tag = tag
        elif tag in ("p", "div", "br", "li"):
            self._flush()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        # 先处理 content / skip 退出（用类名无法回溯，简化：按 depth 弹栈）
        if tag == "div":
            if self._skip:
                self._skip -= 1
            elif self._content:
                # calibreEbookContent 结束只会出现一次在页末
                pass
        if self._skip or not self._content:
            return
        if tag in ("h1", "h2", "h3") and self._tag == tag:
            self._flush(as_title=True)
            self._tag = ""
        elif tag in ("p", "div", "li"):
            self._flush()

    def handle_data(self, data):
        if self._content and not self._skip:
            self._buf.append(data)

    def _flush(self, as_title: bool = False) -> None:
        text = " ".join("".join(self._buf).split())
        self._buf = []
        if text:
            self.parts.append(("title" if as_title else "text", text))


def convert(html: str) -> list[tuple[str, str]]:
    p = Collector()
    p.feed(html)
    p._flush()
    return p.parts


def main() -> int:
    if not SRC.exists():
        print(f"未找到源目录: {SRC}")
        return 1
    files = sorted(SRC.joinpath("Text").glob("*.xhtml"))
    print(f"共 {len(files)} 个 xhtml")

    DST.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["# The Art of Pixar: The Complete Color Scripts", ""]
    n_img = n_chars = 0
    for i, f in enumerate(files, start=1):
        parts = convert(f.read_text(encoding="utf-8", errors="replace"))
        if not parts:
            continue
        lines.append(f"## p{i:03d}")
        lines.append("")
        for kind, payload in parts:
            if kind == "img":
                n_img += 1
                lines.append(f"![p{i:03d}-f{n_img}](images/{payload.split('/')[-1]})")
            elif kind == "title":
                n_chars += len(payload)
                lines.append(f"### {payload}")
            else:
                n_chars += len(payload)
                lines.append(payload)
            lines.append("")
    # 去掉重复的目录块（每页都带一份相同的 TOC），只保留第一次
    cleaned: list[str] = []
    seen_toc = False
    dropping = False
    for ln in lines:
        t = ln.strip()
        if t == "### Table of contents":
            if seen_toc:
                dropping = True
                continue
            seen_toc = True
        if dropping:
            if t == "Chronicle Ebooks":
                dropping = False
            continue
        cleaned.append(ln)
    lines = cleaned
    out = DST / "book.md"
    io.open(out, "w", encoding="utf-8").write("\n".join(lines))
    print(f"写出 {out} · {out.stat().st_size} B · {len(lines)} 行 · 正文 {n_chars} 字 · {n_img} 图")
    return 0


if __name__ == "__main__":
    sys.exit(main())

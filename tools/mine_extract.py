# -*- coding: utf-8 -*-
"""Split book.md into chapter-range extracts for claim mining."""
import re
from pathlib import Path

ROOT = Path('.')
OUT = ROOT / 'out' / 'mine'
OUT.mkdir(parents=True, exist_ok=True)


def split_pages(slug):
    text = (ROOT / 'books' / slug / 'source' / 'book.md').read_text(encoding='utf-8')
    parts = re.split(r'(?m)^## (p\d{3})\s*$', text)
    pages = {}
    for i in range(1, len(parts), 2):
        pages[parts[i]] = parts[i + 1]
    return pages


def write_range(slug, name, start, end):
    pages = split_pages(slug)
    lo, hi = int(start[1:]), int(end[1:])
    chunks = []
    for n in range(lo, hi + 1):
        k = f'p{n:03d}'
        if k in pages:
            chunks.append(f'## {k}\n' + pages[k].strip())
    path = OUT / f'{slug}-{name}.md'
    path.write_text('\n\n'.join(chunks) + '\n', encoding='utf-8')
    print(path, len(chunks), 'pages', path.stat().st_size, 'bytes')


# Ways of Seeing: chapters (md pages = PDF pages)
write_range('ways-of-seeing', 'ch1', 'p006', 'p039')
write_range('ways-of-seeing', 'ch3', 'p050', 'p073')
write_range('ways-of-seeing', 'ch4', 'p074', 'p091')
write_range('ways-of-seeing', 'ch5', 'p092', 'p127')
write_range('ways-of-seeing', 'ch6', 'p128', 'p143')
write_range('ways-of-seeing', 'ch7', 'p144', 'p188')

# Sense of Order: relevant chapters by md page
write_range('sense-of-order', 'intro', 'p014', 'p033')
write_range('sense-of-order', 'ch4', 'p122', 'p145')
write_range('sense-of-order', 'ch5', 'p146', 'p179')
write_range('sense-of-order', 'ch6', 'p180', 'p205')
write_range('sense-of-order', 'ch10', 'p294', 'p331')

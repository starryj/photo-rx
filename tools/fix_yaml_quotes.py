"""把 claims.yaml 里含 ASCII 双引号的 quote 改成 YAML 单引号风格（内部再无 ASCII 双引号时安全）。"""
from __future__ import annotations

import re
import sys

for path in sys.argv[1:]:
    lines = open(path, encoding="utf-8").read().splitlines()
    out, fixed = [], 0
    for ln in lines:
        m = re.match(r'^(\s*quote: )"(.*)"$', ln)
        if m and '"' in m.group(2):
            out.append(m.group(1) + "'" + m.group(2) + "'")
            fixed += 1
        else:
            out.append(ln)
    open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"{path}: fixed {fixed}")

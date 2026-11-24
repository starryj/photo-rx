import io, re, sys, yaml

base = r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\mine"
files = {
    "导论": "sense-of-order-intro.md",
    "第四章": "sense-of-order-ch4.md",
    "第五章": "sense-of-order-ch5.md",
    "第六章": "sense-of-order-ch6.md",
    "第十章": "sense-of-order-ch10.md",
}
pages = {}
for ch, fn in files.items():
    text = io.open(base + "\\" + fn, encoding="utf-8").read()
    parts = re.split(r"^## (p\d+)\s*$", text, flags=re.M)
    d = {}
    # parts: [pre, pNNN, body, pNNN, body, ...]
    for i in range(1, len(parts), 2):
        d[parts[i]] = parts[i + 1]
    pages[ch] = d

claims = yaml.safe_load(io.open(base + r"\claims-sense-of-order.yaml", encoding="utf-8"))
TYPES = {"framework", "principle", "mechanism", "case", "counter-example"}
DOMAINS = {"构图与结构","方法论","空间","光与时段","器材与后期","机制","语境与相对性","明度",
           "数量与面积","和谐与协调","饱和度","色相与色环","情绪与象征","对比","冷暖"}
ok = 0
problems = []
for i, c in enumerate(claims, 1):
    ch = c["source_chapter"].split(" ")[0]
    q = c["quote"]
    found = [p for p, body in pages[ch].items() if q in body]
    if not found:
        problems.append(f'{c["id"]}: MISSING in {ch}')
    elif c["page"] not in found:
        problems.append(f'{c["id"]}: page says {c["page"]} but found in {found}')
    else:
        ok += 1
    if i != int(c["id"][2:]):
        problems.append(f'{c["id"]}: id order {i}')
    if c["type"] not in TYPES:
        problems.append(f'{c["id"]}: bad type {c["type"]}')
    if c["domain"] not in DOMAINS:
        problems.append(f'{c["id"]}: bad domain {c["domain"]}')
    L, QL = len(c["claim"]), len(q)
    if not 20 <= L <= 60:
        problems.append(f'{c["id"]}: claim len {L}')
    if not 20 <= QL <= 80:
        problems.append(f'{c["id"]}: quote len {QL}')
    if any(t in q for t in "……"):
        problems.append(f'{c["id"]}: ellipsis in quote')

print("total", len(claims), "hit", ok)
for p in problems:
    print("PROBLEM", p)

import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
exp = json.loads((root / "out" / "blind" / "without-skill-expected.json").read_text(encoding="utf-8"))
got = {x["id"]: x["route"] for x in json.loads((root / "out" / "blind" / "without-skill-judge.json").read_text(encoding="utf-8"))}
ok = 0
miss = []
for k, v in exp.items():
    if got.get(k) == v:
        ok += 1
    else:
        miss.append((k, v, got.get(k)))
print(f"{ok}/{len(exp)} = {ok/len(exp):.1%}")
for m in miss:
    print("MISS", *m)
# Wilson 95%
n = len(exp)
p = ok / n
z = 1.96
den = 1 + z * z / n
centre = (p + z * z / (2 * n)) / den
half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
print(f"Wilson [{centre-half:.1%}, {centre+half:.1%}]")

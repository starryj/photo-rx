import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
cases = json.loads((root / "out" / "gate3" / "cases.json").read_text(encoding="utf-8"))
judge_path = root / "out" / "gate3" / (sys.argv[1] if len(sys.argv) > 1 else "judge2.json")
verdicts = {x["id"]: x["verdict"] for x in json.loads(judge_path.read_text(encoding="utf-8"))}
ok = 0
miss = []
for c in cases:
    got = verdicts.get(c["id"])
    if got == c["expect"]:
        ok += 1
    else:
        miss.append((c["id"], c["skill"], c["expect"], got))
print(f"{ok}/{len(cases)} = {ok/len(cases):.1%}")
for m in miss:
    print("MISS", *m)
by = {}
for c in cases:
    by.setdefault(c["skill"], [0, 0])
    by[c["skill"]][1] += 1
    if verdicts.get(c["id"]) == c["expect"]:
        by[c["skill"]][0] += 1
for k, (a, b) in sorted(by.items()):
    print(f"{k}: {a}/{b}")

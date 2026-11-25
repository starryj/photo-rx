import json
import pathlib

p = pathlib.Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\analysis\dsc-7326\measure.json")
m = json.loads(p.read_text(encoding="utf-8"))
keep = ["hue_families", "tone", "probes", "chroma_peaks", "bright_pools", "dark_masses",
        "thirds", "main_horizontal_line", "rule_of_thirds_check", "edge_intrusion", "warm_blobs",
        "neutral_anchor", "subject_candidates"]
out = {k: m.get(k) for k in keep}
txt = "keys: " + ", ".join(m.keys()) + "\n\n" + json.dumps(out, ensure_ascii=False, indent=1)
pathlib.Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\out\keys.txt").write_text(txt, encoding="utf-8")
print("ok")

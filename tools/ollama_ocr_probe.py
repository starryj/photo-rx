import base64
import json
import sys
from pathlib import Path

import requests

img = Path(sys.argv[1])
prompt = "只逐字转写图片里的文字，不要解释、不要补全、不要翻译、不要加标点。按原换行。看不清的字写 [?]。只输出转写。"
b64 = base64.b64encode(img.read_bytes()).decode()
r = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={"model": "qwen3-vl:4b", "prompt": prompt, "images": [b64], "stream": False,
          "options": {"temperature": 0, "num_predict": 600}},
    timeout=180,
)
print(r.status_code)
d = r.json()
print(d.get("response", "")[:800])
print("done_reason", d.get("done_reason"), "eval_count", d.get("eval_count"))

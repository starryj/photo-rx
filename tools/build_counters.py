"""生成 counters.yaml：双方引文一律按 claim id 从已校验的归一库取，避免手抄出错。

每条的裁决（resolution / rationale / runtime_action）在这里写死，脚本只负责取引文。
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "claims" / "claims.yaml"
OUT = ROOT / "counters" / "counters.yaml"

SPEC = [
    {
        "id": "K1",
        "kind": "contested",
        "statement": "色彩和谐是不是一个客观存在的目标",
        "targets": ["C016", "C014", "C015"],
        "side_a": {"label": "和谐可求且可辨认（规则派）", "claim_ids": ["C016"]},
        "side_b": {"label": "任何色都能搭配，和谐不是唯一可欲（相对派）", "claim_ids": ["C014", "C015"]},
        "resolution": "both-valid-by-intent",
        "resolution_by": "editor",
        "rationale": "两边说的不是一件事：规则派谈的是「多数观者会读成协调的组合」（可用于交付给客户、投稿、做封面），相对派谈的是「和谐不是唯一值得追求的关系」（可用于个人创作、当代摄影、要张力时）。把它裁成一方胜出会丢掉实用性，裁成折中又会失去两边的锋利。故运行时不裁决，按用户意图分岔，并在卡片里写清分岔点。",
        "reverse_writable": "把规则派写成相对派能接受的形式：「存在一类被多数人读作协调的组合，它可被列举、可被复现——但它只是众多关系之一，没有优先权。」相对派能接受。反向把相对派写成规则派能接受的形式：「任何色都能成立，但成立的条件是数量；追求和谐也只是选择了一组数量。」规则派也能接受（它本来就靠数量与搭配给出配方）。两边互写得通，说明这是真分歧而非表述差异。",
        "runtime_action": "branch",
        "branch_condition": "用户要「协调／好看／能交付」→ 走规则派配方（C016 域）；用户要「张力／不要俗／当代感」或明确说「不想按套路」→ 走相对派（C014/C015），并提示数量是唯一硬约束。",
    },
    {
        "id": "K5",
        "kind": "contested",
        "statement": "具体的色彩规则能不能用于指导拍摄与后期",
        "targets": ["C041", "C042", "C045", "C059", "C065", "C069", "C070"],
        "side_a": {"label": "规则可操作、有判词（规则派）", "claim_ids": ["C041", "C042", "C045", "C059"]},
        "side_b": {"label": "教的是问题不是答案，实践先于理论（相对派）", "claim_ids": ["C065", "C069", "C070"]},
        "resolution": "downgrade-side-a",
        "resolution_by": "editor",
        "rationale": "相对派反对的是「把规则当答案」，不是「规则为假」。规则派给的是条件判词（几点、什么光、什么器材），这类经验断言在它自己的适用条件下有效；一旦跨出条件（换成阴天、换成室内混合光、换成无偏振镜）就没有依据。故不否定规则，而是把每条规则降级为「有条件可操作」，并在卡片 E 段强制写判停点。",
        "reverse_writable": "把相对派写成规则派能接受的形式：「规则只在它所由抽出的条件下成立，条件变了要重新判断」——规则派会同意（书里自己也写黄金时段无法预测、白平衡要按主光源定）。反向把规则派写成相对派能接受的形式：「有一批在特定条件下反复验证过的经验判词，它们不是美学的答案，只是提高命中率的先验。」相对派能接受。",
        "runtime_action": "downgrade",
        "branch_condition": "输出任何带时间／光线／器材判词的结论时，必须同时给出它的失效条件；给不出失效条件就不许写进结论。",
    },
    {
        "id": "K6",
        "kind": "contested",
        "statement": "照片该不该承载再现与自我表达",
        "targets": ["C062", "C064", "C066", "C067"],
        "side_a": {"label": "色彩可承载情绪与地域叙事（规则派）", "claim_ids": ["C062", "C064"]},
        "side_b": {"label": "课程禁止再现，再现会分散对色彩的注意（相对派）", "claim_ids": ["C066", "C067"]},
        "resolution": "both-valid-by-stage",
        "resolution_by": "editor",
        "rationale": "阿尔伯斯的禁令是教学装置：要把注意力压到色彩关系上，就必须暂时拿掉内容。这不是对摄影的主张——他几乎不谈摄影。摄影的成片必然承载内容，所以禁令只能约束「分析色彩时」的阶段，不能约束「拍一张照片」的产出。",
        "reverse_writable": "把禁令写成摄影可接受的形式：「分析色彩关系时先假装画面没有内容，把色块当色块看；分析完再把内容放回来。」摄影者能接受（这就是双轨诊断）。反向把摄影立场写成阿尔伯斯能接受的形式：「色彩关系在具体画面里被检验」，他会补一句「但检验时别让内容替色彩辩护」。",
        "runtime_action": "branch",
        "branch_condition": "任务＝诊断/分析色彩 → 暂时屏蔽内容（按纯色块读）；任务＝创作/选片/编排 → 内容必须进判断，色彩只作一条轨。",
    },
    {
        "id": "K7",
        "kind": "contested",
        "statement": "照片本身能不能裁决视觉判断",
        "targets": ["C028", "C047", "C048"],
        "side_a": {"label": "照片不可靠，不能当证据（相对派）", "claim_ids": ["C028"]},
        "side_b": {"label": "直方图/灰卡/包围曝光能给出读数（规则派）", "claim_ids": ["C047", "C048"]},
        "resolution": "split-by-measurable",
        "resolution_by": "editor",
        "rationale": "两边的对象不同：阿尔伯斯说的是「色相与明度的知觉关系」不能被照片代表（照片把亮记得更亮、暗记得更暗，中间灰被压平）；规则派说的是「曝光量与亮度数值」可以被仪器读出（测光表按中灰设计、灰卡三通道 128）。前者是知觉判断，后者是物理测量。故拆开：数值类以仪器为准，色相类以眼睛为准，且二者不可互相替代。",
        "reverse_writable": "把规则派写成相对派能接受的形式：「仪器能告诉你进了多少光，不能告诉你看起来是什么颜色。」相对派会同意。反向把相对派写成规则派能接受的形式：「肉眼对中间灰与色相的分辨优于任何相机的记录，故校色时不要只信屏幕。」规则派会同意（色彩管理章正是这么说的）。",
        "runtime_action": "downgrade",
        "branch_condition": "任何色彩结论必须标明依据：来自脚本测量（L 值、面积占比、直方图）／来自人眼判断／来自模型描述。三者不可混为一谈，模型描述不得冒充测量。",
    },
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    claims = {c["id"]: c for c in yaml.safe_load(CLAIMS.read_text(encoding="utf-8"))}
    out = []
    for spec in SPEC:
        item = dict(spec)
        for side in ("side_a", "side_b"):
            ids = item[side].pop("claim_ids")
            item[side]["quotes"] = [
                {
                    "claim": cid,
                    "book": claims[cid]["sources"][0]["book"],
                    "page": claims[cid]["sources"][0]["page"],
                    "quote": claims[cid]["sources"][0]["quote"],
                }
                for cid in ids
            ]
        out.append(item)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8")
    print(f"写出 {OUT.relative_to(ROOT)} · {len(out)} 条对抗")
    for o in out:
        print(f"  {o['id']} {o['statement']} → {o['resolution']} ({o['runtime_action']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

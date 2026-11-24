import re
from pathlib import Path

p = Path(__file__).resolve().parent / "batch_quotes.py"
s = p.read_text(encoding="utf-8")

extra = '''        ("fl23", ["硬光", "没有", "阻隔"]),
        ("fl24", ["柔光", "察觉"]),
        ("fl25", ["阴天", "扩散"]),
        ("fl26", ["白平衡", "加入", "演绎"]),
        ("fl27", ["逆光", "形状"]),
        ("fl28", ["质感", "侧光", "微观"]),
        ("fl29", ["正午", "投影"]),
        ("fl30", ["包围光", "少见"]),
        ("fl31", ["矩阵", "图像库"]),
        ("fl32", ["创意", "白平衡"]),
'''
anchor = '        ("fl22", ["创意白平衡", "演绎"]),\n'
if anchor in s and '"fl23"' not in s:
    s = s.replace(anchor, anchor + extra)
    p.write_text(s, encoding="utf-8")
    print("added")
else:
    print("skip")

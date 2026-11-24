from pathlib import Path

p = Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\books\freeman-sight\claims\claims.yaml")
s = p.read_text(encoding="utf-8")

pairs = [
    (
        '  quote: "远摄镜头…对图像结构也有着各种影响：压缩图像的平面，减弱深度感"',
        '  quote: "广角镜头往往会增强线性透视，而远摄镜头则将它扁平化。"',
    ),
    (
        '  quote: "德国诗人歌德是第一个给色调赋值的人黄色为9，橙色为8，红色和绿色为6，蓝色为4，紫色为3"',
        '  quote: "是第一个给色调赋值的人黄色为9，橙色为8，红色和绿色为6，蓝色为4，紫色为3"',
    ),
    (
        '  quote: "严重依赖于在一个画幅里放置两个……我们天生就倾向于假设并排的事物之间存在关系"',
        '  quote: "我们天生就倾向于假设并排的事物之间存在有关系"',
    ),
]
n = 0
for a, b in pairs:
    if a in s:
        s = s.replace(a, b)
        n += 1
p.write_text(s, encoding="utf-8")
print(f"fixed {n}")

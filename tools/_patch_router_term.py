# -*- coding: utf-8 -*-
"""给 router 描述补一条「术语释义」触发，幂等。"""
import io
import pathlib

P = pathlib.Path(r"G:\AI_Workspace\04-MadeMySkills\photo-vision\.cangjie\capabilities\verified.yaml")
OLD = "或问某个题材该往哪个方向深挖这类学习路径与方向问题。"
NEW = ("或问某个题材该往哪个方向深挖这类学习路径与方向问题；"
       "也用于用户问某个概念或术语本身是什么意思（如「气韵生动」「三远」「虚实相生」「三大」），"
       "此时按术语表作解释，不必有照片。")

t = io.open(P, encoding="utf-8").read()
assert t.count(OLD) == 1, t.count(OLD)
if NEW in t:
    print("already patched")
else:
    t = t.replace(OLD, NEW)
    io.open(P, "w", encoding="utf-8", newline="\n").write(t)
    print("patched")

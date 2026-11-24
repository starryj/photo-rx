# -*- coding: utf-8 -*-
import sys
import pymupdf as fitz

doc = fitz.open(r'E:\03-Book\Photography\摄影构图与色彩设计 (Pdg2Pic, （德）哈拉尔德_ (Z-Library).pdf')
for sid, pidx in (('S03', 23), ('S07', 64), ('S10', 106), ('S14', 127)):
    page = doc[pidx]
    pix = page.get_pixmap(matrix=fitz.Matrix(200 / 72, 200 / 72))
    pix.save(f'out/ocr-sample-mant/page-{sid}.png')
    print(sid, pix.width, pix.height)

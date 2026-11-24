# -*- coding: utf-8 -*-
import pymupdf as fitz

doc = fitz.open(r'E:\03-Book\Photography\摄影构图与色彩设计 (Pdg2Pic, （德）哈拉尔德_ (Z-Library).pdf')
for sid, pidx in (('S03next', 25), ('S07next', 66), ('S10next', 108), ('S14next', 129)):
    page = doc[pidx]
    pix = page.get_pixmap(matrix=fitz.Matrix(200 / 72, 200 / 72))
    pix.save(f'out/ocr-sample-mant/page-{sid}.png')
    print(sid, pidx, pix.width, pix.height)

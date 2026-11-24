# -*- coding: utf-8 -*-
import json, sys
sys.path.insert(0, 'tools')
import ocr_sample as S
import fitz

cl = json.load(open('out/parse/photo-composition-color/content_list.json', encoding='utf-8'))
man = {x['sample_id']: x for x in json.load(open('out/ocr-sample-mant/manifest.json', encoding='utf-8'))}
doc = fitz.open(r'E:\03-Book\Photography\摄影构图与色彩设计 (Pdg2Pic, （德）哈拉尔德_ (Z-Library).pdf')
for sid in ('S03', 'S07', 'S10', 'S14'):
    it = man[sid]
    pidx = it['pdf_page_idx']
    hit = S.locate(cl, pidx, it['quote'])
    bbox, text = hit
    page = doc[pidx]
    print(sid, 'bbox', bbox, 'rect', page.rect, 'textlen', len(text))
    ext = (page.rect.width, page.rect.height)
    img = S.render_crop(doc, pidx, bbox, ext, target_w=1600, pad=10)
    img.save(f'out/ocr-sample-mant/full-{sid}.png')
print('saved')

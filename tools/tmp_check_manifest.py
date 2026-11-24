# -*- coding: utf-8 -*-
import json

with open('out/ocr-sample-mant/manifest.json', encoding='utf-8') as f:
    m = json.load(f)
for it in m:
    sid = it['sample_id']
    if sid not in ('S03', 'S07', 'S10', 'S14'):
        continue
    q = it['quote'].strip('"')
    bt = it.get('block_text', '')
    print(sid, 'blocklen', len(bt), 'quote_in_block', q[:12] in bt)
    print('keys', sorted(it.keys()))

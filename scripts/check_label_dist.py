import json
from collections import Counter
r=json.load(open('labelstudio_export_synthetic.json'))
c=Counter()
for rec in r:
    ann = rec.get('annotations',[None])[0]
    if not ann: continue
    for rr in ann.get('result',[]):
        if rr.get('type') in ('choices','singlechoice'):
            choice = rr.get('value',{}).get('choices') or rr.get('value')
            c.update([str(choice)])
print(c)

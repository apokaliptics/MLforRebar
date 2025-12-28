import json
from collections import Counter
r=json.load(open('labelstudio_export_synthetic.json'))
labels=[None]*len(r)
for i, rec in enumerate(r):
    ann = rec.get('annotations',[None])[0]
    if not ann: continue
    for rr in ann.get('result',[]):
        if rr.get('type') in ('choices','singlechoice'):
            choice = rr.get('value',{}).get('choices') or rr.get('value')
            if isinstance(choice, (list, tuple)) and len(choice)>0:
                value = str(choice[0]).strip().lower()
            else:
                value = str(choice).strip().lower()
            labels[i] = 1 if value == 'split' else 0
labels=[l for l in labels if l is not None]
print('total', len(labels), Counter(labels))
# now simulate stratified split
total=len(labels)
from sklearn.model_selection import train_test_split
X=list(range(len(labels)))
X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42, stratify=labels)
print('train', len(y_train), Counter(y_train))
print('test', len(y_test), Counter(y_test))

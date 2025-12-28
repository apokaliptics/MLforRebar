"""
Evaluate paragraph split model with document-level split and stress tests.

Outputs saved to `eval/`:
 - document_split_report.json
 - confusion_matrix.png
 - top_false_pos.csv
 - top_false_neg.csv
 - stress_tests_summary.json

Usage:
  python scripts/eval_document_split.py --input labelstudio_export_provenance.json --max-docs 1000

"""
import argparse
import json
import os
import sys
import random
from collections import defaultdict
from pathlib import Path
import csv
# ensure project root on sys.path so we can import training helper classes
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

from scripts.train_production_model import FeatureExtractor


def parse_label(rec):
    ann = rec.get('annotations') or rec.get('predictions') or []
    lab = None
    for a in ann:
        for r in a.get('result', []):
            if r.get('type') in ['choices','singlechoice']:
                v = r.get('value')
                if isinstance(v, dict):
                    choices = v.get('choices') or []
                    if choices:
                        lab = choices[0]
                elif isinstance(v, str):
                    lab = v
                break
    return (1 if str(lab).strip().lower()=='split' else 0) if lab is not None else None


def records_to_Xy(records, fe: FeatureExtractor):
    X=[]; y=[]; meta=[]
    for r in records:
        label = parse_label(r)
        if label is None: continue
        data = r.get('data', {})
        before = data.get('text_before','')
        after = data.get('text_after','')
        full = data.get('full_paragraph','')
        feats = fe.extract_all_features(before, after, full)
        X.append(feats); y.append(label); meta.append(data)
    if not X:
        return np.array([]), np.array([]), []
    return np.vstack(X), np.array(y), meta


def train_and_eval(X_train, y_train, X_test, y_test):
    scaler = StandardScaler()
    Xtr = scaler.fit_transform(X_train)
    Xte = scaler.transform(X_test)
    model = LogisticRegression(class_weight='balanced', max_iter=500, C=10.0)
    model.fit(Xtr, y_train)
    y_pred = model.predict(Xte)
    y_prob = model.predict_proba(Xte)[:,1]
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred).tolist()
    return model, scaler, report, cm, y_pred, y_prob


def save_top_errors(meta_test, y_test, y_pred, y_prob, out_dir, kind='fp', topk=50):
    rows=[]
    for m, true, pred, p in zip(meta_test, y_test, y_pred, y_prob):
        if kind=='fp' and pred==1 and true==0:
            rows.append((p, m, true, pred))
        if kind=='fn' and pred==0 and true==1:
            rows.append((p, m, true, pred))
    if kind=='fp':
        rows.sort(key=lambda x: -x[0])
    else:
        rows.sort(key=lambda x: x[0])
    outf = out_dir / (f'top_{kind}.csv')
    with open(outf, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['prob_split','source_file','text_before','text_after','true','pred'])
        for p,m,true,pred in rows[:topk]:
            w.writerow([p, m.get('source_file',''), m.get('text_before','')[:200], m.get('text_after','')[:200], true, pred])
    return outf


def synthesize_ocr(text):
    # simple OCR-like errors: drop spaces, swap chars, remove vowels randomly
    import random
    s = ''.join(ch if random.random()>0.03 else '' for ch in text)
    s = s.replace('rn','m')
    return s


from scripts.post_filter import apply_post_filter


def stress_test_model(model, scaler, fe, sources, out_dir, apply_filter: bool = True, filter_threshold: float = 0.7):
    results = {}
    for name, docs in sources.items():
        X_list=[]; y_list=[]; meta=[]
        for doc in docs:
            # create pseudo-samples: split paragraphs and adjacent sentence pairs
            paragraphs = [p.strip() for p in doc.split('\n\n') if p.strip()]
            for i in range(len(paragraphs)-1):
                before = paragraphs[i]; after = paragraphs[i+1]; full = before + '\n\n' + after
                feats = fe.extract_all_features(before, after, full)
                X_list.append(feats); y_list.append(None); meta.append({'text_before': before, 'text_after': after, 'full_paragraph': full})
        if not X_list:
            continue
        X = np.vstack(X_list)
        Xs = scaler.transform(X)
        probs = model.predict_proba(Xs)[:,1]
        preds = (probs>=0.5).astype(int)
        # basic stats: fraction predicted split (original)
        frac_orig = float(preds.mean())
        # apply post-filter if requested
        if apply_filter:
            filtered_mask = apply_post_filter(probs, meta, threshold=filter_threshold)
            frac_filtered = float(filtered_mask.mean())
        else:
            frac_filtered = frac_orig
        results[name] = {'n': len(probs), 'frac_orig': frac_orig, 'frac_filtered': frac_filtered, 'avg_prob_split': float(probs.mean())}
    out_file = out_dir / 'stress_tests_summary.json'
    with open(out_file,'w',encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    return out_file, results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='labelstudio_export_provenance.json')
    parser.add_argument('--max-docs', type=int, default=2000)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--out-dir', default='eval')
    args = parser.parse_args()

    random.seed(args.seed)
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.input,'r',encoding='utf-8') as f:
        records = json.load(f)
    # group by source_file
    groups = defaultdict(list)
    for r in records:
        src = r.get('data',{}).get('source_file','unknown')
        groups[src].append(r)
    sources = list(groups.keys())
    random.shuffle(sources)
    if args.max_docs and len(sources)>args.max_docs:
        sources = sources[:args.max_docs]
    # split sources 80/20
    split = int(0.8*len(sources))
    train_srcs = set(sources[:split]); test_srcs = set(sources[split:])
    train_recs = [rec for s in train_srcs for rec in groups[s]]
    test_recs = [rec for s in test_srcs for rec in groups[s]]
    print(f'Sources: total={len(sources)}, train={len(train_srcs)}, test={len(test_srcs)}; samples train={len(train_recs)}, test={len(test_recs)}')

    fe = FeatureExtractor()
    X_train,y_train,meta_train = records_to_Xy(train_recs, fe)
    X_test,y_test,meta_test = records_to_Xy(test_recs, fe)
    if X_train.size==0 or X_test.size==0:
        print('Insufficient data after parsing, aborting')
        return
    model, scaler, report, cm, y_pred, y_prob = train_and_eval(X_train, y_train, X_test, y_test)
    with open(out_dir / 'document_split_report.json','w',encoding='utf-8') as f:
        json.dump({'report':report,'confusion_matrix':cm}, f, indent=2)

    # save top errors
    fp = save_top_errors(meta_test, y_test, y_pred, y_prob, Path(out_dir), kind='fp', topk=50)
    fn = save_top_errors(meta_test, y_test, y_pred, y_prob, Path(out_dir), kind='fn', topk=50)

    # Stress tests: build OOD sources
    sources_ood = {}
    # wiki_md (formal)
    wiki_files = list(Path('datasets/raw_docs/wiki_md').rglob('*.md'))[:200]
    sources_ood['wiki_sample'] = [f.read_text(encoding='utf-8') for f in wiki_files]
    # messy student essays (other_high)
    messy = list(Path('datasets/raw_docs/student/essays/other_high').rglob('*.md'))[:200]
    sources_ood['messy_essays'] = [f.read_text(encoding='utf-8') for f in messy]
    # transcripts synthetically created: take essays and remove punctuation
    transcripts = []
    for f in messy[:200]:
        t = f.read_text(encoding='utf-8')
        transcripts.append(' '.join(ch for ch in t if ch.isalnum() or ch.isspace()))
    sources_ood['transcripts_synth'] = transcripts
    # OCR noise
    ocr = []
    for f in messy[:200]:
        ocr.append(synthesize_ocr(f.read_text(encoding='utf-8')[:2000]))
    sources_ood['ocr_synth'] = ocr

    # use post-filter by default with recommended threshold 0.7
    stress_out, stress_results = stress_test_model(model, scaler, fe, sources_ood, Path(out_dir), apply_filter=True, filter_threshold=0.7)

    print('Done. Outputs in', out_dir)

if __name__=='__main__':
    main()

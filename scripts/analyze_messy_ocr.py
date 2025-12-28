"""
Score and sample 'messy_essays' and 'ocr_synth' stress sources, save CSVs and threshold breakdowns.

Usage:
  python scripts/analyze_messy_ocr.py --input labelstudio_export_provenance_all_v2.json --out-dir eval_full/messy_ocr_analysis
"""
import argparse
import json
import random
from pathlib import Path
import csv
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.eval_document_split import FeatureExtractor, records_to_Xy, train_and_eval, synthesize_ocr
import numpy as np


def write_csv(path, rows, header=['prob','source_file','text_before','text_after']):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path,'w',encoding='utf-8',newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([r.get('prob'), r.get('source_file'), (r.get('text_before') or '')[:400], (r.get('text_after') or '')[:400]])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='labelstudio_export_provenance_all_v2.json')
    parser.add_argument('--out-dir', default='eval_full/messy_ocr_analysis')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.input,'r',encoding='utf-8') as f:
        records = json.load(f)
    # train/test split like eval
    from collections import defaultdict
    groups = defaultdict(list)
    for r in records:
        src = r.get('data',{}).get('source_file','unknown')
        groups[src].append(r)
    sources = list(groups.keys())
    random.shuffle(sources)
    split = int(0.8*len(sources))
    train_srcs = set(sources[:split]); test_srcs = set(sources[split:])
    train_recs = [rec for s in train_srcs for rec in groups[s]]
    test_recs = [rec for s in test_srcs for rec in groups[s]]

    fe = FeatureExtractor()
    X_train,y_train,meta_train = records_to_Xy(train_recs, fe)
    X_test,y_test,meta_test = records_to_Xy(test_recs, fe)
    model, scaler, report, cm, y_pred, y_prob = train_and_eval(X_train, y_train, X_test, y_test)

    # Build messy_essays and ocr_synth sources (matching eval script)
    messy_files = list(Path('datasets/raw_docs/student/essays/other_high').rglob('*.md'))
    messy_texts = [f.read_text(encoding='utf-8') for f in messy_files[:500]]
    messy_docs = [{'source_file': str(messy_files[i]), 'text': messy_texts[i]} for i in range(len(messy_texts))]

    ocr_texts = [synthesize_ocr(t[:2000]) for t in messy_texts[:500]]
    ocr_docs = [{'source_file': f'ocr_synth_{i}', 'text': ocr_texts[i]} for i in range(len(ocr_texts))]

    def make_samples(docs):
        samples=[]
        for d in docs:
            paragraphs = [p.strip() for p in d['text'].split('\n\n') if p.strip()]
            for i in range(len(paragraphs)-1):
                samples.append({'source_file': d['source_file'], 'text_before': paragraphs[i], 'text_after': paragraphs[i+1], 'full_paragraph': paragraphs[i]+"\n\n"+paragraphs[i+1]})
        return samples

    messy_samples = make_samples(messy_docs)
    ocr_samples = make_samples(ocr_docs)

    def score(samples):
        feats=[]; metas=[]
        for s in samples:
            feats.append(fe.extract_all_features(s['text_before'], s['text_after'], s['full_paragraph']))
            metas.append(s)
        if not feats:
            return []
        X = np.vstack(feats)
        Xs = scaler.transform(X)
        probs = model.predict_proba(Xs)[:,1]
        out=[]
        for p,m in zip(probs, metas):
            rec = {'prob': float(p), **m}
            out.append(rec)
        return out

    messy_scored = score(messy_samples)
    ocr_scored = score(ocr_samples)

    # Save analytics
    if messy_scored:
        probs = np.array([r['prob'] for r in messy_scored])
        with open(out_dir / 'messy_stats.txt','w',encoding='utf-8') as f:
            f.write(f'n={len(probs)}\nmean={float(probs.mean())}\nmedian={float(np.median(probs))}\nmin={float(probs.min())}\nmax={float(probs.max())}\n')
        write_csv(out_dir / 'messy_top_high.csv', sorted(messy_scored, key=lambda r:-r['prob'])[:200])
        write_csv(out_dir / 'messy_top_low.csv', sorted(messy_scored, key=lambda r:r['prob'])[:200])
    if ocr_scored:
        probs = np.array([r['prob'] for r in ocr_scored])
        with open(out_dir / 'ocr_stats.txt','w',encoding='utf-8') as f:
            f.write(f'n={len(probs)}\nmean={float(probs.mean())}\nmedian={float(np.median(probs))}\nmin={float(probs.min())}\nmax={float(probs.max())}\n')
        write_csv(out_dir / 'ocr_top_high.csv', sorted(ocr_scored, key=lambda r:-r['prob'])[:200])
        write_csv(out_dir / 'ocr_top_low.csv', sorted(ocr_scored, key=lambda r:r['prob'])[:200])

    # threshold breakdowns
    thresholds = [0.3,0.5,0.6,0.7,0.8,0.9]
    thresh_summary = {'messy':{}, 'ocr':{}}
    for t in thresholds:
        thresh_summary['messy'][str(t)] = {'n': len(messy_scored), 'frac_split': float((np.array([r['prob'] for r in messy_scored])>=t).mean()) if messy_scored else None}
        thresh_summary['ocr'][str(t)] = {'n': len(ocr_scored), 'frac_split': float((np.array([r['prob'] for r in ocr_scored])>=t).mean()) if ocr_scored else None}
    with open(out_dir / 'messy_ocr_threshold_summary.json','w',encoding='utf-8') as f:
        json.dump(thresh_summary, f, indent=2)

    print('Wrote analysis outputs to', out_dir)

if __name__=='__main__':
    main()

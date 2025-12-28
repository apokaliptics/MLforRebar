"""
Inspect EDGAR and Wiki failure modes and sweep decision thresholds.
Saves CSVs of top high, low, and near-threshold examples plus a JSON summary.

Usage:
  python scripts/stress_inspect_thresholds.py --input labelstudio_export_provenance_full.json --out-dir eval_full/stress_more/edgar_wiki_inspect --max-docs 2000
"""
import argparse
import json
import random
from pathlib import Path
import csv
import sys
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.eval_document_split import FeatureExtractor, records_to_Xy, train_and_eval


def load_texts_from_dir(dirpath, max_files=500, max_chars=None):
    p = Path(dirpath)
    if not p.exists():
        return []
    files = sorted(list(p.rglob('*.md')) + list(p.rglob('*.txt')))
    out=[]
    for f in files[:max_files]:
        try:
            t = f.read_text(encoding='utf-8')
            if max_chars:
                t = t[:max_chars]
            out.append({'source_file': str(f), 'text': t})
        except Exception:
            continue
    return out


def make_samples_from_docs(docs):
    samples=[]
    for doc in docs:
        text = doc['text']
        src = doc['source_file']
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        for i in range(len(paragraphs)-1):
            before = paragraphs[i]; after = paragraphs[i+1]; full = before + '\n\n' + after
            samples.append({'source_file': src, 'text_before': before, 'text_after': after, 'full_paragraph': full})
    return samples


def write_csv(path, rows, header=['prob','source_file','text_before','text_after']):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path,'w',encoding='utf-8',newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([r.get('prob'), r.get('source_file'), (r.get('text_before') or '')[:400], (r.get('text_after') or '')[:400]])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='labelstudio_export_provenance_full.json')
    parser.add_argument('--out-dir', default='eval_full/stress_more/edgar_wiki_inspect')
    parser.add_argument('--max-docs', type=int, default=2000)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.input,'r',encoding='utf-8') as f:
        records = json.load(f)
    groups = defaultdict(list)
    for r in records:
        src = r.get('data',{}).get('source_file','unknown')
        groups[src].append(r)
    sources = list(groups.keys())
    random.shuffle(sources)
    if args.max_docs and len(sources)>args.max_docs:
        sources = sources[:args.max_docs]
    split = int(0.8*len(sources))
    train_srcs = set(sources[:split]); test_srcs = set(sources[split:])
    train_recs = [rec for s in train_srcs for rec in groups[s]]
    test_recs = [rec for s in test_srcs for rec in groups[s]]

    fe = FeatureExtractor()
    X_train,y_train,meta_train = records_to_Xy(train_recs, fe)
    X_test,y_test,meta_test = records_to_Xy(test_recs, fe)
    if X_train.size==0 or X_test.size==0:
        print('Insufficient samples after parsing, aborting')
        return
    model, scaler, report, cm, y_pred, y_prob = train_and_eval(X_train, y_train, X_test, y_test)

    # load EDGAR and Wiki samples (try multiple edgar paths if empty)
    edgar_docs = load_texts_from_dir('datasets/edgar_md', max_files=300, max_chars=10000)
    if not edgar_docs:
        edgar_docs = load_texts_from_dir('datasets/edgar_md_test', max_files=300, max_chars=10000)
    if not edgar_docs:
        edgar_docs = load_texts_from_dir('sec-edgar-filings', max_files=300, max_chars=10000)
    wiki_docs = load_texts_from_dir('datasets/wiki_md_full', max_files=300, max_chars=10000)

    edgar_samples = make_samples_from_docs(edgar_docs)
    wiki_samples = make_samples_from_docs(wiki_docs)

    def score_samples(samples):
        feats = []
        metas = []
        for s in samples:
            feats.append(fe.extract_all_features(s['text_before'], s['text_after'], s['full_paragraph']))
            metas.append(s)
        import numpy as np
        X = np.vstack(feats)
        Xs = scaler.transform(X)
        probs = model.predict_proba(Xs)[:,1]
        scored = []
        for p,m in zip(probs, metas):
            rec = {'prob': float(p), **m}
            scored.append(rec)
        return scored

    edg_scored = score_samples(edgar_samples)
    wiki_scored = score_samples(wiki_samples)

    # write top/bottom and near-threshold for thresholds
    thresholds = [0.3,0.5,0.6,0.7,0.8,0.9]
    threshold_summary = {'edgar':{}, 'wiki':{}}

    # overall frac per threshold
    import numpy as np
    edg_probs = np.array([r['prob'] for r in edg_scored]) if edg_scored else np.array([])
    wik_probs = np.array([r['prob'] for r in wiki_scored]) if wiki_scored else np.array([])
    for t in thresholds:
        threshold_summary['edgar'][str(t)] = {'n': int(len(edg_probs)), 'frac_split': float((edg_probs>=t).mean()) if edg_probs.size else None}
        threshold_summary['wiki'][str(t)] = {'n': int(len(wik_probs)), 'frac_split': float((wik_probs>=t).mean()) if wik_probs.size else None}
        # near-threshold (within +/-0.05)
        near_e = [r for r in edg_scored if abs(r['prob']-t)<=0.05]
        near_w = [r for r in wiki_scored if abs(r['prob']-t)<=0.05]
        write_csv(out_dir / f'edgar_near_{int(t*100)}.csv', sorted(near_e, key=lambda r: -r['prob'])[:200])
        write_csv(out_dir / f'wiki_near_{int(t*100)}.csv', sorted(near_w, key=lambda r: -r['prob'])[:200])

    # top high / low
    write_csv(out_dir / 'edgar_top_high.csv', sorted(edg_scored, key=lambda r: -r['prob'])[:200])
    write_csv(out_dir / 'edgar_top_low.csv', sorted(edg_scored, key=lambda r: r['prob'])[:200])
    write_csv(out_dir / 'wiki_top_high.csv', sorted(wiki_scored, key=lambda r: -r['prob'])[:200])
    write_csv(out_dir / 'wiki_top_low.csv', sorted(wiki_scored, key=lambda r: r['prob'])[:200])

    # save summary
    with open(out_dir / 'edgar_wiki_threshold_summary.json','w',encoding='utf-8') as f:
        json.dump(threshold_summary, f, indent=2)

    print('Wrote edgar/wiki inspection outputs to', out_dir)

if __name__=='__main__':
    main()

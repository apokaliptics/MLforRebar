"""
Run stress tests with a post-filter that requires:
 - probability >= threshold AND
 - (before ends with sentence punctuation OR after starts with uppercase)

Outputs summary JSON and suppressed samples CSVs.

Usage:
  python scripts/stress_test_filter.py --model models/paragraph_split_v6.json --out eval_full/messy_ocr_analysis --thresholds 0.5 0.6 0.7 0.8 0.9
"""
import argparse
import json
import random
from pathlib import Path
import csv
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.eval_document_split import FeatureExtractor
import numpy as np


def load_export(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

class SimpleLR:
    def __init__(self, weights, bias, mean, scale):
        self.w = np.array(weights)
        self.b = float(bias)
        self.mean = np.array(mean)
        self.scale = np.array(scale)
    def predict_proba(self, X):
        Xs = (X - self.mean) / self.scale
        logits = Xs.dot(self.w) + self.b
        probs = 1/(1+np.exp(-logits))
        return probs


def load_texts_from_dir(dirpath, max_files=300, max_chars=None):
    p = Path(dirpath)
    if not p.exists():
        return []
    files = list(p.rglob('*.md')) + list(p.rglob('*.txt'))
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


def make_samples(docs):
    samples=[]
    for d in docs:
        paragraphs = [p.strip() for p in d['text'].split('\n\n') if p.strip()]
        for i in range(len(paragraphs)-1):
            samples.append({'source_file': d['source_file'], 'text_before': paragraphs[i], 'text_after': paragraphs[i+1], 'full_paragraph': paragraphs[i]+'\n\n'+paragraphs[i+1]})
    return samples


from scripts.post_filter import boundary_confirmed


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path,'w',encoding='utf-8',newline='') as f:
        w = csv.writer(f)
        w.writerow(['prob','source_file','text_before','text_after','reason'])
        for r in rows:
            w.writerow([r['prob'], r['source_file'], (r['text_before'] or '')[:400], (r['text_after'] or '')[:400], r.get('reason','')])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--out', default='eval_full/messy_ocr_analysis')
    parser.add_argument('--thresholds', nargs='+', type=float, default=[0.5,0.6,0.7,0.8,0.9])
    parser.add_argument('--max-files', type=int, default=300)
    args = parser.parse_args()

    outdir = Path(args.out); outdir.mkdir(parents=True, exist_ok=True)
    model_json = load_export(args.model)
    lr = SimpleLR(model_json['model']['weights'], model_json['model']['bias'], model_json['scaler']['mean'], model_json['scaler']['scale'])
    fe = FeatureExtractor()

    # Load sources
    sources = {}
    sources['messy'] = make_samples(load_texts_from_dir('datasets/raw_docs/student/essays/other_high', max_files=args.max_files))
    sources['ocr'] = []
    messy_files = load_texts_from_dir('datasets/raw_docs/student/essays/other_high', max_files=args.max_files)
    for i,d in enumerate(messy_files):
        s = ''.join(ch if random.random()>0.03 else '' for ch in d['text'][:2000])
        sources['ocr'].append({'source_file': f'ocr_synth_{i}', 'text': s})
    sources['ocr'] = make_samples(sources['ocr'])
    sources['wiki'] = make_samples(load_texts_from_dir('datasets/wiki_md_full', max_files=args.max_files, max_chars=5000))
    sources['arxiv'] = make_samples(load_texts_from_dir('datasets/arxiv_md', max_files=args.max_files, max_chars=5000))
    sources['edgar'] = make_samples(load_texts_from_dir('datasets/edgar_md_test', max_files=args.max_files, max_chars=5000))

    results = {}
    for name, samples in sources.items():
        if not samples:
            results[name] = None
            continue
        feats = np.vstack([fe.extract_all_features(s['text_before'], s['text_after'], s['full_paragraph']) for s in samples])
        probs = lr.predict_proba(feats)
        row_probs = list(probs)
        results[name] = {}
        for t in args.thresholds:
            pred_mask = (probs >= t)
            frac_orig = float(pred_mask.mean())
            # apply filter
            confirmed = [boundary_confirmed(s['text_before'], s['text_after']) for s in samples]
            filtered_mask = pred_mask & np.array(confirmed)
            frac_filtered = float(filtered_mask.mean())
            results[name][str(t)] = {'n': len(probs), 'frac_orig': frac_orig, 'frac_filtered': frac_filtered, 'mean_prob': float(probs.mean())}
            # save suppressed samples where pred=True but filtered=False for a representative subset
            suppressed_idx = [i for i,(p,conf) in enumerate(zip(pred_mask, confirmed)) if p and not conf]
            suppressed_rows = []
            for idx in suppressed_idx[:200]:
                suppressed_rows.append({'prob': float(probs[idx]), **samples[idx], 'reason': 'no_boundary'})
            write_csv(outdir / f'suppressed_{name}_{int(t*100)}.csv', suppressed_rows)
    with open(outdir / 'filter_results.json','w',encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print('Wrote filter results to', outdir)

if __name__=='__main__':
    main()

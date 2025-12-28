"""
Extra stress tests across more out-of-domain corpora (arXiv, EDGAR, wiki_full, 2539 corpus).
Saves a summary JSON to the out-dir.

Usage:
  python scripts/stress_test_more.py --input labelstudio_export_provenance_full.json --out-dir eval_full/stress_more --max-docs 2000
"""
import argparse
import json
import random
from pathlib import Path
from collections import defaultdict
import os
import sys
# ensure project root on sys.path so imports from `scripts` work (same approach as eval_document_split)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# import helpers from eval script
from scripts.eval_document_split import FeatureExtractor, records_to_Xy, train_and_eval, stress_test_model, synthesize_ocr


def load_texts_from_dir(dirpath, max_files=200, max_chars=None):
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
            out.append(t)
        except Exception:
            continue
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='labelstudio_export_provenance_full.json')
    parser.add_argument('--out-dir', default='eval_full/stress_more')
    parser.add_argument('--max-docs', type=int, default=2000)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.input, 'r', encoding='utf-8') as f:
        records = json.load(f)
    # group records by source_file similar to eval
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

    # build OOD sources
    sources_ood = {}
    # arXiv full md
    sources_ood['arxiv_sample'] = load_texts_from_dir('datasets/arxiv_md', max_files=300, max_chars=5000)
    # edgar md
    sources_ood['edgar_md'] = load_texts_from_dir('datasets/edgar_md', max_files=300, max_chars=5000)
    # edgar test
    sources_ood['edgar_md_test'] = load_texts_from_dir('datasets/edgar_md_test', max_files=200, max_chars=5000)
    # wiki full (long articles)
    sources_ood['wiki_full'] = load_texts_from_dir('datasets/wiki_md_full', max_files=300, max_chars=5000)
    # sec corpus we moved (2539)
    sources_ood['corpus_2539'] = load_texts_from_dir('datasets/raw_docs/2539', max_files=200, max_chars=5000)
    # kaggle (student style but different length/format)
    sources_ood['kaggle_high'] = load_texts_from_dir('datasets/raw_docs/student/essays/kaggle_high', max_files=300, max_chars=5000)

    # create transformed variants
    # 1) lowercased (loss of capitalization signal)
    sources_ood['lowercase_kaggle'] = [t.lower() for t in sources_ood.get('kaggle_high',[])[:200]]
    # 2) compressed (no paragraph breaks)
    sources_ood['compressed_wiki'] = [' '.join(t.split()) for t in sources_ood.get('wiki_full',[])[:200]]
    # 3) ocr noisy from edgar
    sources_ood['edgar_ocr'] = [synthesize_ocr(t[:3000]) for t in sources_ood.get('edgar_md',[])[:200]]

    stress_out, stress_results = stress_test_model(model, scaler, fe, sources_ood, out_dir)

    # write readable summary and top fractions
    with open(out_dir / 'stress_more_summary.json','w',encoding='utf-8') as f:
        json.dump(stress_results, f, indent=2)

    print('Wrote stress results to', out_dir)

if __name__=='__main__':
    main()

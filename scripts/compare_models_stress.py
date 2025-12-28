"""
Compare stress-test behavior of two exported models (v4 and v6). Loads model JSONs and runs stress sources.
Usage:
  python scripts/compare_models_stress.py --models models/paragraph_split_v4.json models/paragraph_split_v6.json --out eval_full/model_compare
"""
import argparse
import json
from pathlib import Path
import numpy as np
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.eval_document_split import FeatureExtractor


def load_export(path):
    with open(path,'r',encoding='utf-8') as f:
        return json.load(f)

class SimpleLR:
    def __init__(self, weights, bias, scaler_mean, scaler_scale):
        self.weights = np.array(weights)
        self.bias = float(bias)
        self.mean = np.array(scaler_mean)
        self.scale = np.array(scaler_scale)
    def predict_proba(self, X):
        Xs = (X - self.mean)/self.scale
        logits = Xs.dot(self.weights) + self.bias
        probs = 1/(1+np.exp(-logits))
        return np.vstack([1-probs, probs]).T


def load_model_from_json(path):
    e = load_export(path)
    w = e['model']['weights']
    b = e['model']['bias']
    mean = e['scaler']['mean']
    scale = e['scaler']['scale']
    return SimpleLR(w,b,mean,scale)


def load_texts_from_dir(dirpath, max_files=300, max_chars=5000):
    p = Path(dirpath)
    files = list(p.rglob('*.md')) + list(p.rglob('*.txt'))
    out=[]
    for f in files[:max_files]:
        try:
            t = f.read_text(encoding='utf-8')
            out.append({'source_file': str(f), 'text': t[:max_chars]})
        except Exception:
            continue
    return out


def make_samples(docs):
    samples=[]
    for d in docs:
        paragraphs = [p.strip() for p in d['text'].split('\n\n') if p.strip()]
        for i in range(len(paragraphs)-1):
            samples.append({'source_file': d['source_file'], 'text_before': paragraphs[i], 'text_after': paragraphs[i+1], 'full_paragraph': paragraphs[i]+"\n\n"+paragraphs[i+1]})
    return samples


def score_samples(model, scaler_mean, scaler_scale, fe, samples):
    feats = np.vstack([fe.extract_all_features(s['text_before'], s['text_after'], s['full_paragraph']) for s in samples])
    # using SimpleLR predict_proba
    sr = SimpleLR(model['model']['weights'], model['model']['bias'], model['scaler']['mean'], model['scaler']['scale'])
    probs = sr.predict_proba(feats)[:,1]
    return probs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--models', nargs='+', required=True)
    parser.add_argument('--out', default='eval_full/model_compare')
    args = parser.parse_args()

    fe = FeatureExtractor()
    sources = {
        'messy': make_samples([{'source_file':'other','text': t.read_text(encoding='utf-8')[:10000]} for t in Path('datasets/raw_docs/student/essays/other_high').rglob('*.md')][:300]),
        'ocr': make_samples([{'source_file':f'ocr_{i}','text': ''.join(ch if random.random()>0.03 else '' for ch in t.read_text(encoding='utf-8')[:2000])} for i,t in enumerate(list(Path('datasets/raw_docs/student/essays/other_high').rglob('*.md'))[:300])]),
        'wiki': make_samples([{'source_file':str(f),'text': f.read_text(encoding='utf-8')[:5000]} for f in list(Path('datasets/wiki_md_full').rglob('*.md'))[:300]]),
        'edgar': make_samples([{'source_file':str(f),'text': f.read_text(encoding='utf-8')[:5000]} for f in list(Path('datasets/edgar_md_test').rglob('*.md'))[:300]])
    }

    results = {}
    for mpath in args.models:
        model_json = load_export(mpath)
        # create a SimpleLR from model_json
        lr = SimpleLR(model_json['model']['weights'], model_json['model']['bias'], model_json['scaler']['mean'], model_json['scaler']['scale'])
        results[Path(mpath).name] = {}
        for name, samples in sources.items():
            if not samples:
                results[Path(mpath).name][name] = None
                continue
            feats = np.vstack([fe.extract_all_features(s['text_before'], s['text_after'], s['full_paragraph']) for s in samples])
            Xs = (feats - lr.mean)/lr.scale
            logits = Xs.dot(lr.weights) + lr.bias
            probs = 1/(1+np.exp(-logits))
            frac = float((probs>=0.5).mean())
            results[Path(mpath).name][name] = {'n': len(probs), 'frac_split': frac, 'mean_prob': float(probs.mean())}
    Path(args.out).mkdir(parents=True, exist_ok=True)
    with open(Path(args.out)/'model_compare.json','w',encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print('Wrote model_compare.json')

if __name__=='__main__':
    import random
    main()

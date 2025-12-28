"""
Generate a Label Studio style JSON export from raw markdown/text essays under
`datasets/raw_docs`.

Heuristic labelling:
 - paragraph boundary => 'split'
 - adjacent sentences within the same paragraph => 'no_split'

Usage:
  python scripts/generate_labelstudio_from_raw.py --in-dir datasets/raw_docs --out labelstudio_export_all.json --max-samples 20000

"""
import argparse
import json
import random
import re
from pathlib import Path

try:
    import nltk
    nltk.download('punkt', quiet=True)
    from nltk.tokenize import sent_tokenize
    def _safe_sent_tokenize(text):
        try:
            return sent_tokenize(text)
        except Exception:
            # fallback
            return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    sent_tokenize = _safe_sent_tokenize
except Exception:
    # fallback simple splitter
    sent_tokenize = lambda t: [s.strip() for s in re.split(r'(?<=[.!?])\s+', t) if s.strip()]


def iter_md_files(root: Path):
    for p in root.rglob('*.md'):
        yield p


def split_paragraphs(text: str):
    # split on blank lines
    parts = re.split(r'\n\s*\n+', text.strip())
    parts = [p.strip() for p in parts if p.strip()]
    return parts


def make_record(before: str, after: str, full: str, label: str, source: str):
    return {
        "data": {
            "text_before": before,
            "text_after": after,
            "full_paragraph": full,
            "source_file": source
        },
        "annotations": [
            {"result": [{"type": "singlechoice", "value": {"choices": [label]}}]}
        ]
    }


def generate_samples_from_file(path: Path):
    text = path.read_text(encoding='utf-8')
    paragraphs = split_paragraphs(text)
    records = []
    # split = paragraph boundary pairs
    for i in range(len(paragraphs)-1):
        before = paragraphs[i]
        after = paragraphs[i+1]
        full = before + '\n\n' + after
        records.append((make_record(before, after, full, 'split', source=str(path)), 'split'))
    # no_split = adjacent sentences within same paragraph
    for p in paragraphs:
        sents = sent_tokenize(p)
        for i in range(len(sents)-1):
            before = sents[i].strip()
            after = sents[i+1].strip()
            full = p
            if before and after:
                records.append((make_record(before, after, full, 'no_split', source=str(path)), 'no_split'))
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-dir', default='datasets/raw_docs', help='Root folder with raw md essays')
    parser.add_argument('--out', default='labelstudio_export_all.json', help='Output JSON path')
    parser.add_argument('--max-samples', type=int, default=20000, help='Max total samples to generate (balanced across classes)')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--include-synthetic', default=None, help='Optional path to a synthetic Label Studio JSON to include')
    args = parser.parse_args()

    random.seed(args.seed)
    root = Path(args.in_dir)
    all_records = {'split': [], 'no_split': []}
    files = list(iter_md_files(root))
    print(f'Found {len(files)} files under {root}')
    for i, f in enumerate(files, 1):
        try:
            recs = generate_samples_from_file(f)
            for rec, label in recs:
                # attach provenance
                rec['data']['source_file'] = str(f)
                all_records[label].append(rec)
        except Exception as e:
            print(f'Error processing {f}: {e}')

    # optionally include synthetic export
    if args.include_synthetic:
        synth_path = Path(args.include_synthetic)
        if synth_path.exists():
            try:
                synth = json.load(open(synth_path, 'r', encoding='utf-8'))
                for rec in synth:
                    # infer label if available in annotations
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
                    if lab in ['split','no_split']:
                        all_records[lab].append(rec)
            except Exception as e:
                print(f'Error reading synthetic export {synth_path}: {e}')
    # determine sampling counts
    max_per_class = args.max_samples // 2
    chosen = []
    for label in ['split', 'no_split']:
        pool = all_records[label]
        if not pool:
            continue
        if len(pool) > max_per_class:
            pool = random.sample(pool, max_per_class)
        chosen.extend(pool)
    random.shuffle(chosen)
    print(f'Generated: split={len(all_records["split"])}, no_split={len(all_records["no_split"])}, chosen={len(chosen)}')
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(chosen, f, ensure_ascii=False, indent=2)
    print(f'Wrote {len(chosen)} examples to {args.out}')


if __name__ == '__main__':
    main()

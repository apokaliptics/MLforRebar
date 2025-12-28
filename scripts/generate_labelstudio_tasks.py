"""Generate Label Studio tasks (JSONL) from .md files in workspace root.
Each task corresponds to a candidate split (between two sentences) with fields:
  data.text_before, data.text_after, data.full_paragraph, data.doc, data.paragraph_index, data.boundary_index
"""
from pathlib import Path
import re
import json

try:
    import nltk
    from nltk import tokenize
except Exception:
    raise SystemExit("Please install nltk and run nltk.download('punkt') before using this script")

ROOT = Path(__file__).resolve().parent.parent


def sentence_split(paragraph):
    sents = [s.strip() for s in tokenize.sent_tokenize(paragraph) if s.strip()]
    return sents


def main():
    md_files = list(ROOT.glob('*.md'))
    tasks = []
    for p in md_files:
        text = p.read_text(encoding='utf-8')
        paragraphs = [pb.strip() for pb in re.split(r'\n\s*\n', text) if pb.strip()]
        for pi, para in enumerate(paragraphs):
            sents = sentence_split(para)
            if len(sents) < 2:
                continue
            for bi in range(len(sents)-1):
                before = ' '.join(sents[:bi+1])
                after = ' '.join(sents[bi+1:])
                tasks.append({'data': {'text_before': before, 'text_after': after, 'full_paragraph': para, 'doc': str(p.name), 'paragraph_index': pi, 'boundary_index': bi}})
    out_path = ROOT / 'labelstudio_tasks.jsonl'
    with open(out_path, 'w', encoding='utf-8') as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + '\n')
    print(f'Wrote {len(tasks)} tasks to {out_path}')


if __name__ == '__main__':
    main()
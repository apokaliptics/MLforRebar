"""
Heuristic check for paragraph boundary artifacts: if 'before' doesn't end with sentence punctuation and 'after' starts with lowercase, treat as potential artifact.
Writes summary JSON counts for messy and ocr scored CSVs produced earlier.
"""
import json
from pathlib import Path
import csv


def load_csv(path):
    rows=[]
    with open(path,'r',encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def is_artifact(before, after):
    if not before or not after:
        return False
    end_punct = before.rstrip()[-1] if before.rstrip() else ''
    start_char = after.lstrip()[0] if after.lstrip() else ''
    return (end_punct not in '.!?…') and (start_char.islower())


def analyze(path):
    rows = load_csv(path)
    total = len(rows)
    if total==0:
        return {'n':0,'artifact_count':0,'artifact_frac':None}
    art = sum(1 for r in rows if is_artifact(r['text_before'], r['text_after']))
    return {'n': total, 'artifact_count': art, 'artifact_frac': art/total}


def main():
    out = {}
    messy_high = analyze('eval_full/messy_ocr_analysis/messy_top_high.csv')
    messy_low = analyze('eval_full/messy_ocr_analysis/messy_top_low.csv')
    ocr_high = analyze('eval_full/messy_ocr_analysis/ocr_top_high.csv')
    ocr_low = analyze('eval_full/messy_ocr_analysis/ocr_top_low.csv')
    out['messy_top_high'] = messy_high
    out['messy_top_low'] = messy_low
    out['ocr_top_high'] = ocr_high
    out['ocr_top_low'] = ocr_low
    Path('eval_full/messy_ocr_analysis').mkdir(parents=True, exist_ok=True)
    with open('eval_full/messy_ocr_analysis/artifact_summary.json','w',encoding='utf-8') as f:
        json.dump(out, f, indent=2)
    print('Wrote artifact_summary.json')

if __name__=='__main__':
    main()

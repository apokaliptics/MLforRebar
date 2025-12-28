"""
Scan `datasets/raw_docs` and write `datasets/manifest.csv` with basic metadata.
"""
from pathlib import Path
import csv

ROOT = Path('datasets/raw_docs')
MANIFEST = Path('datasets/manifest.csv')

rows = []
for p in ROOT.rglob('*.md'):
    rel = p.relative_to('.')
    # category: student/essays or inferred from path
    parts = p.parts
    category = '/'.join(parts[2:4]) if len(parts) >= 4 else 'other'
    rows.append({'filename': p.name, 'original_path': str(p), 'new_path': str(p), 'category': category, 'keywords': '', 'snippet': ''})

MANIFEST.parent.mkdir(parents=True, exist_ok=True)
with open(MANIFEST, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['filename','original_path','new_path','category','keywords','snippet'])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f'Wrote {len(rows)} entries to {MANIFEST}')

"""Analyze datasets/wiki_md files for size and content completeness."""
from pathlib import Path
from statistics import mean

ROOT = Path('.').resolve()
DIR = ROOT / 'datasets' / 'wiki_md'

files = sorted(DIR.glob('*.md'))
count = len(files)
lengths = []
short_under_100 = []
short_under_500 = []
empty = []

for f in files:
    txt = f.read_text(encoding='utf-8', errors='ignore')
    # remove YAML frontmatter
    body = txt.split('---\n', 2)
    if len(body) == 3:
        content = body[2]
    else:
        content = txt
    content = content.strip()
    L = len(content)
    lengths.append(L)
    if L == 0:
        empty.append(f.name)
    if L < 100:
        short_under_100.append((f.name, L))
    if L < 500:
        short_under_500.append((f.name, L))

print('Total files:', count)
print('Empty files:', len(empty))
print('Files <100 chars:', len(short_under_100))
print('Files <500 chars:', len(short_under_500))
print('Mean length:', mean(lengths) if lengths else 0)

print('\nExamples of very short files (<100 chars):')
for name, L in short_under_100[:10]:
    print('-', name, L)

print('\nExamples of modest files (100-500 chars):')
for name, L in short_under_500[:10]:
    if L >= 100:
        print('-', name, L)

# Output a small histogram
bins = [0, 50, 100, 200, 500, 1000, 5000]
hist = {b:0 for b in bins}
for L in lengths:
    for b in bins:
        if L <= b:
            hist[b]+=1
            break
print('\nHistogram (<=bins):')
for b in bins:
    print(f' <={b}: {hist[b]}')

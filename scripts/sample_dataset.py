"""Sample MD files from datasets into datasets/sampled for inspection.

Usage:
    python scripts/sample_dataset.py --n 200 --out datasets/sampled
"""
import random
from pathlib import Path
import shutil
import argparse


def main(n=200, root='datasets', out='datasets/sampled'):
    root = Path(root)
    files = list(root.rglob('*.md'))
    files = [f for f in files if 'sampled' not in str(f)]
    if len(files) == 0:
        print('No files found under', root)
        return
    n = min(n, len(files))
    sample = random.sample(files, n)
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)
    for f in sample:
        dest = outdir / f.name
        shutil.copy2(str(f), str(dest))
    print(f'Copied {len(sample)} files to {outdir}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, default=200)
    parser.add_argument('--out', default='datasets/sampled')
    args = parser.parse_args()
    main(n=args.n, out=args.out)

"""Download arXiv sources using the `arxiv` package.

Usage example:
    pip install arxiv
    python scripts/download_arxiv.py --query "cat:cs.AI" --max 200 --out datasets/arxiv

This will download tar.gz source packages for results.
"""
import argparse
from pathlib import Path

try:
    import arxiv
except Exception:
    raise SystemExit('Please install the arxiv package: pip install arxiv')


def main(query='cat:cs.AI', max_results=100, out='datasets/arxiv'):
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)
    search = arxiv.Search(query=query, max_results=max_results)
    count = 0
    for result in search.results():
        try:
            result.download_source(dirpath=str(outdir))
            count += 1
        except Exception as e:
            print(f"Failed to download {result.entry_id}: {e}")
    print(f"Downloaded {count} entries to {outdir}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', default='cat:cs.AI')
    parser.add_argument('--max', type=int, default=100)
    parser.add_argument('--out', default='datasets/arxiv')
    args = parser.parse_args()
    main(query=args.query, max_results=args.max, out=args.out)

"""Download *metadata* and abstracts from arXiv and save as lightweight Markdown files.

Usage:
    pip install arxiv
    python scripts/download_arxiv_md.py --query "cat:cs.AI" --max 3000 --out datasets/arxiv_md

Each paper becomes a small .md:
---
title: "..."
authors: ...
categories: ...
url: ...
---

Abstract, comments, and link to PDF.
"""
import argparse
from pathlib import Path
import arxiv


def save_md(outdir: Path, idx: int, result):
    title = result.title.strip()
    authors = ', '.join([a.name for a in result.authors])
    categories = ', '.join(result.categories or [])
    url = result.entry_id
    pdf = result.pdf_url
    summary = result.summary.strip()
    fname = f"paper_{idx:05d}.md"
    path = outdir / fname
    content = f"---\ntitle: \"{title.replace('\n',' ')}\"\nauthors: \"{authors}\"\ncategories: \"{categories}\"\nsource: \"{url}\"\npdf: \"{pdf}\"\n---\n\n"
    content += f"## Abstract\n\n{summary}\n"
    path.write_text(content, encoding='utf-8')


def main(query='cat:cs.AI', max_results=3000, out='datasets/arxiv_md'):
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate)
    i = 0
    for res in search.results():
        i += 1
        try:
            save_md(outdir, i, res)
            if i % 100 == 0:
                print(f'Saved {i} papers')
        except Exception as e:
            print('Failed to save', res.entry_id, e)
    print(f'Done: saved {i} papers to {outdir}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', default='cat:cs.AI')
    parser.add_argument('--max', type=int, default=3000)
    parser.add_argument('--out', default='datasets/arxiv_md')
    args = parser.parse_args()
    main(query=args.query, max_results=args.max, out=args.out)

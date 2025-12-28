"""Process WikiExtractor output and write up to N lightweight Markdown files.

Usage:
  1) Run the download & WikiExtractor step first with `scripts/download_wikipedia.py`.
  2) Run: python scripts/process_wikipedia_to_md.py --extracted datasets/wiki/extracted --out datasets/wiki_md --max 3000

Each article saved as `article_00001.md` with title and content.
"""
import argparse
from pathlib import Path
import re


def iter_docs(extracted_dir: Path):
    # WikiExtractor outputs multiple files under extracted/**/wiki_* files with <doc ...> ... </doc>
    for f in extracted_dir.rglob('**/*'):
        if not f.is_file():
            continue
        text = f.read_text(encoding='utf-8', errors='ignore')
        parts = re.split(r'<doc[^>]*>', text)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if '</doc>' in part:
                body, _ = part.split('</doc>', 1)
            else:
                body = part
            # try to find Title: usually first line
            lines = [l.strip() for l in body.splitlines() if l.strip()]
            if not lines:
                continue
            title = lines[0][:200]
            content = '\n\n'.join(lines[1:])[:100000]
            yield title, content


def main(extracted='datasets/wiki/extracted', out='datasets/wiki_md', max_docs=3000):
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)
    extracted_dir = Path(extracted)
    written = 0
    for title, content in iter_docs(extracted_dir):
        written += 1
        fname = f'article_{written:05d}.md'
        path = outdir / fname
        md = f'---\ntitle: "{title.replace("\"","\'\")}"\n---\n\n# {title}\n\n{content}\n'
        path.write_text(md, encoding='utf-8')
        if written % 100 == 0:
            print('Wrote', written)
        if written >= max_docs:
            break
    print(f'Wrote {written} wiki articles to {outdir}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--extracted', default='datasets/wiki/extracted')
    parser.add_argument('--out', default='datasets/wiki_md')
    parser.add_argument('--max', type=int, default=3000)
    args = parser.parse_args()
    main(extracted=args.extracted, out=args.out, max_docs=args.max)

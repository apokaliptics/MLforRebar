"""Fetch full Wikipedia page HTML for short articles, strip images, convert to Markdown, and save as full versions.

Usage:
    python scripts/download_wikipedia_full_md.py --src datasets/wiki_md --out datasets/wiki_md_full --min_chars 200

Behavior:
- For each markdown in src, if the body (after frontmatter) is shorter than min_chars, fetch full page using action=parse and prop=text.
- Remove <img>, <figure>, <table> blocks and data URIs before converting.
- Convert HTML -> Markdown with markdownify and save to out with same filename.
- Uses a polite User-Agent and retries.
"""
import argparse
from pathlib import Path
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import re

API = 'https://en.wikipedia.org/w/api.php'

# session with retries
session = requests.Session()
retry = Retry(total=5, backoff_factor=1, status_forcelist=[429,500,502,503,504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
session.headers.update({'User-Agent': 'RebarDatasetBot/0.1 (contact: dev@example.com)', 'From': 'dev@example.com'})

IMG_RE = re.compile(r'data:image/[^)\s]+', re.IGNORECASE)


def get_title_from_md(path: Path):
    txt = path.read_text(encoding='utf-8', errors='ignore')
    # Expect frontmatter between first two '---' lines
    parts = txt.split('---\n', 2)
    if len(parts) >= 3:
        fm = parts[1]
        for line in fm.splitlines():
            if line.lower().startswith('title:'):
                val = line.split(':',1)[1].strip().strip('\"').strip("'")
                return val
    # fallback to filename (replace underscores)
    return path.stem


def get_body_length(path: Path):
    txt = path.read_text(encoding='utf-8', errors='ignore')
    parts = txt.split('---\n', 2)
    if len(parts) == 3:
        content = parts[2]
    else:
        content = txt
    return len(content.strip())


def fetch_full_html(title: str):
    params = {
        'format': 'json',
        'action': 'parse',
        'page': title,
        'prop': 'text',
        'redirects': 1
    }
    r = session.get(API, params=params, timeout=30)
    # handle 404-like
    if r.status_code == 404:
        raise requests.exceptions.HTTPError(f'404 Not Found for {title}')
    r.raise_for_status()
    j = r.json()
    if 'error' in j:
        raise requests.exceptions.HTTPError(str(j['error']))
    html = j.get('parse', {}).get('text', {}).get('*', '')
    return html


def strip_images_and_blocks(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    # remove figures, images, tables
    for tag in soup.find_all(['figure', 'img', 'table']):
        tag.decompose()
    # remove elements with class 'navbox', 'infobox', 'vertical-navbox'
    for tag in soup.find_all(class_=lambda c: c and any(x in c for x in ['navbox','infobox','vertical-navbox','hatnote'])):
        tag.decompose()
    # drop data URI occurrences
    cleaned = IMG_RE.sub('(image removed)', str(soup))
    return cleaned


def html_to_markdown(html: str):
    # markdownify does a reasonable job for headings and lists
    return md(html, heading_style='ATX')


def main(src='datasets/wiki_md', out='datasets/wiki_md_full', min_chars=200, limit=None):
    srcdir = Path(src)
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)
    files = sorted(srcdir.glob('*.md'))
    processed = 0
    skipped = 0
    errors = []

    for p in files:
        if limit and processed >= limit:
            break
        L = get_body_length(p)
        if L >= min_chars:
            skipped += 1
            continue
        title = get_title_from_md(p)
        try:
            html = fetch_full_html(title)
            stripped = strip_images_and_blocks(html)
            markdown = html_to_markdown(stripped)
            # write frontmatter with source
            src_url = ''
            # attempt to keep source if original had it
            txt = p.read_text(encoding='utf-8', errors='ignore')
            if 'source:' in txt.splitlines()[0:10].__str__():
                # naive extraction
                match = re.search(r'source:\s*"([^"]+)"', txt)
                if match:
                    src_url = match.group(1)
            outpath = outdir / p.name
            safe_title = title.replace('"', "'")
            src_field = src_url or ("https://en.wikipedia.org/wiki/" + title.replace(' ', '_'))
            front = f"---\ntitle: \"{safe_title}\"\nsource: \"{src_field}\"\n---\n\n"
            outpath.write_text(front + markdown, encoding='utf-8')
            processed += 1
            if processed % 50 == 0:
                print('Processed', processed)
            # polite pause
            time.sleep(0.5)
        except Exception as e:
            errors.append((p.name, title, str(e)))
            print('Error fetching', title, e)
            time.sleep(2)

    print(f'Done. processed={processed}, skipped={skipped}, errors={len(errors)}')
    if errors:
        print('Errors sample:', errors[:10])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default='datasets/wiki_md')
    parser.add_argument('--out', default='datasets/wiki_md_full')
    parser.add_argument('--min_chars', type=int, default=200)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    main(src=args.src, out=args.out, min_chars=args.min_chars, limit=args.limit)

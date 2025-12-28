"""Download N random Wikipedia articles (lightweight) using the MediaWiki API and save as Markdown.

Usage:
    python scripts/download_wikipedia_random.py --max 3000 --out datasets/wiki_md

Each article saved as article_00001.md with title and extract.
"""
import argparse
from pathlib import Path
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API = 'https://en.wikipedia.org/w/api.php'


# prepare a session with retries and a polite User-Agent; required for Wikimedia API access
session = requests.Session()
retry = Retry(total=5, backoff_factor=1, status_forcelist=[429,500,502,503,504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
# Update with a contact email; change as needed
session.headers.update({'User-Agent': 'RebarDatasetBot/0.1 (contact: dev@example.com)', 'From': 'dev@example.com'})


def fetch_random(n=50):
    # We fetch in batches using generator=random
    params = {
        'format': 'json',
        'action': 'query',
        'prop': 'extracts|info',
        'explaintext': 1,
        'exintro': 0,
        'inprop': 'url',
        'generator': 'random',
        'grnnamespace': 0,
        'grnlimit': min(n, 500)
    }
    r = session.get(API, params=params, timeout=30)
    if r.status_code == 403:
        # raise a clear HTTPError so caller can handle backoff/retry strategy
        raise requests.exceptions.HTTPError(f'403 Client Error: Forbidden for url: {r.url}')
    r.raise_for_status()
    return r.json()


def main(max_docs=3000, out='datasets/wiki_md', batch=100, min_batch=10):
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)
    written = 0
    current_batch = batch
    backoff = 1
    while written < max_docs:
        want = min(current_batch, max_docs - written)
        try:
            data = fetch_random(want)
            # reset backoff on success
            backoff = 1
        except requests.exceptions.HTTPError as e:
            print('Fetch error, sleeping briefly', e)
            if '403' in str(e):
                # Be more conservative: reduce batch and wait longer
                current_batch = max(min_batch, current_batch // 4)
                print('Received 403; reducing batch to', current_batch, 'and sleeping 30s')
                time.sleep(30)
            else:
                time.sleep(backoff)
                backoff = min(60, backoff * 2)
            continue
        except Exception as e:
            print('Fetch error, sleeping briefly', e)
            time.sleep(backoff)
            backoff = min(60, backoff * 2)
            continue

        pages = data.get('query', {}).get('pages', {})
        if not pages:
            print('No pages returned; reducing batch and sleeping briefly')
            current_batch = max(min_batch, current_batch // 2)
            time.sleep(5)
            continue

        for pid, p in pages.items():
            written += 1
            title = p.get('title', 'No title')
            extract = p.get('extract', '')[:100000]
            fullurl = p.get('fullurl', '')
            fname = f'article_{written:05d}.md'
            safe_title = title.replace('"', "'")
            md = f"""---
title: "{safe_title}"
source: "{fullurl}"
---

# {safe_title}

{extract}
"""
            (outdir / fname).write_text(md, encoding='utf-8')
            if written % 100 == 0:
                print('Wrote', written)
        # polite pause between batches
        time.sleep(1)
    print('Done: wrote', written, 'wiki md files to', outdir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--max', type=int, default=3000)
    parser.add_argument('--out', default='datasets/wiki_md')
    args = parser.parse_args()
    main(max_docs=args.max, out=args.out)

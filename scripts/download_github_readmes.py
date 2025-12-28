"""Download README.md from popular GitHub repositories using the GitHub API.

Usage:
  Set GITHUB_TOKEN environment variable (recommended) or pass --token (less safe).
  python scripts/download_github_readmes.py --max 5000 --min-stars 100 --min-length 200 --out datasets/github_readmes

Notes:
- The script uses the Search API to find top repositories by stars and fetches README via the contents API (raw).
- It respects rate limits and retries on 429/403 with backoff.
- Saves sanitized README files with frontmatter including repo metadata.
"""
import os
import time
import argparse
import requests
from pathlib import Path
import hashlib
import re

API_SEARCH = 'https://api.github.com/search/repositories'
API_README = 'https://api.github.com/repos/{owner}/{repo}/readme'


def sanitize_filename(s: str):
    return re.sub(r'[^0-9A-Za-z._-]', '_', s)[:200]


def save_readme(outdir: Path, owner: str, repo: str, stars: int, html_url: str, content: str, idx: int):
    fname = f'{idx:05d}_{sanitize_filename(owner)}_{sanitize_filename(repo)}.md'
    path = outdir / fname
    front = f'---\ntitle: "{owner}/{repo}"\nowner: "{owner}"\nrepo: "{repo}"\nstars: {stars}\nsource: "{html_url}"\n---\n\n'
    path.write_text(front + content, encoding='utf-8')
    return path


def get_headers(token=None):
    h = {'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'RebarDatasetBot/0.1'}
    if token:
        h['Authorization'] = f'token {token}'
    return h


def fetch_readme_raw(owner, repo, headers):
    url = API_README.format(owner=owner, repo=repo)
    r = requests.get(url, headers={**headers, 'Accept': 'application/vnd.github.v3.raw'}, timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.text


def search_repos(q, page, per_page, headers):
    params = {'q': q, 'sort': 'stars', 'order': 'desc', 'per_page': per_page, 'page': page}
    r = requests.get(API_SEARCH, headers=headers, params=params, timeout=30)
    if r.status_code in (403, 429):
        raise requests.exceptions.HTTPError(f'{r.status_code} Error')
    r.raise_for_status()
    return r.json()


def main(max_repos=5000, min_stars=100, min_length=200, out='datasets/github_readmes', token=None):
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)
    headers = get_headers(token)

    collected = 0
    page = 1
    per_page = 100
    seen_hashes = set()
    errors = 0

    q = f'stars:>={min_stars}'

    while collected < max_repos:
        try:
            data = search_repos(q, page, per_page, headers)
        except requests.exceptions.HTTPError as e:
            errors += 1
            print('Search API rate-limited or blocked, sleeping 60s', e)
            time.sleep(60)
            continue
        items = data.get('items', [])
        if not items:
            print('No more items returned; stopping')
            break
        for item in items:
            owner = item['owner']['login']
            repo = item['name']
            stars = item.get('stargazers_count', 0)
            html_url = item.get('html_url')
            try:
                raw = fetch_readme_raw(owner, repo, headers)
                if not raw:
                    continue
                if len(raw) < min_length:
                    continue
                h = hashlib.sha1(raw.encode('utf-8')).hexdigest()
                if h in seen_hashes:
                    continue
                seen_hashes.add(h)
                collected += 1
                save_readme(outdir, owner, repo, stars, html_url, raw, collected)
                if collected % 50 == 0:
                    print('Saved', collected, 'readmes')
                if collected >= max_repos:
                    break
            except requests.exceptions.HTTPError as e:
                errors += 1
                print('Failed to fetch README for', owner + '/' + repo, e)
                if errors > 10:
                    print('Multiple errors, sleeping 30s')
                    time.sleep(30)
            except Exception as e:
                errors += 1
                print('Unexpected error for', owner + '/' + repo, e)
        page += 1
        # be polite
        time.sleep(1)
    print(f'Done: collected {collected} READMEs to {outdir} (errors={errors})')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--max', type=int, default=5000)
    parser.add_argument('--min-stars', type=int, default=100)
    parser.add_argument('--min-length', type=int, default=200)
    parser.add_argument('--out', default='datasets/github_readmes')
    parser.add_argument('--token', help='GitHub token (not recommended on CLI); prefer env var GITHUB_TOKEN')
    args = parser.parse_args()
    token = args.token or os.environ.get('GITHUB_TOKEN')
    main(max_repos=args.max, min_stars=args.min_stars, min_length=args.min_length, out=args.out, token=token)
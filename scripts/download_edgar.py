"""Download EDGAR filings (10-K / 10-Q) and convert to lightweight Markdown.

Usage:
  pip install sec-edgar-downloader beautifulsoup4 pandas markdownify
  python scripts/download_edgar.py --tickers-file tickers.txt --max 200 --out datasets/edgar_md

Notes:
- The script uses sec_edgar_downloader to fetch filings for tickers in a list.
- It converts HTML/text to Markdown using markdownify and extracts HTML tables to CSV sidecars.
- Start with a small --max to validate; scale to 3000 when ready.
"""
import argparse
from pathlib import Path
from sec_edgar_downloader import Downloader
from bs4 import BeautifulSoup
import pandas as pd
from markdownify import markdownify as md
import re

ROOT = Path(__file__).resolve().parent.parent


def extract_text_and_tables(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    # remove images/figures
    for tag in soup.find_all(['img', 'figure', 'svg']):
        tag.decompose()

    # Extract tables
    tables = []
    for i, table in enumerate(soup.find_all('table')):
        try:
            df = pd.read_html(str(table))[0]
            tables.append(df)
            table.decompose()
        except Exception:
            # ignore parse errors
            table.decompose()
            continue

    # Remaining HTML to markdown
    cleaned_html = str(soup)
    text_md = md(cleaned_html, heading_style='ATX')
    return text_md, tables


def sanitize_filename(s: str):
    return re.sub(r'[^0-9A-Za-z._-]', '_', s)[:200]


def main(tickers_file, max_files=200, out='datasets/edgar_md', email=None):
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)

    # Initialize Downloader(company_name, email_address, download_folder)
    dl = Downloader('Rebar', email, str(outdir / 'edgar_downloads'))

    tickers = []
    if tickers_file and Path(tickers_file).exists():
        tickers = [l.strip() for l in open(tickers_file, 'r', encoding='utf-8') if l.strip()]
    else:
        # default small set to bootstrap
        tickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'TSLA', 'BRK-A', 'JPM', 'V', 'NVDA']

    written = 0
    for t in tickers:
        if written >= max_files:
            break
        # get a few recent 10-K and 10-Q filings
        for ftype in ['10-K', '10-Q']:
            amount = 5
            try:
                # correct signature: dl.get(form, ticker_or_cik, limit=...)
                dl.get(ftype, t, limit=amount)
            except Exception as e:
                print('Download failed for', t, ftype, e)
                continue
            # downloaded to outdir/edgar_downloads/**/<t>/<ftype>/* (structure may vary by package version)
            bases = list(outdir.glob(f'edgar_downloads/**/{t}/{ftype}'))
            if not bases:
                # try older path layout
                bases = list(outdir.glob(f'edgar_downloads/{t}/{ftype}'))
            if not bases:
                continue
            for base in bases:
                for filing in sorted(base.glob('**/*')):
                    if filing.is_file() and filing.suffix.lower() in ('.txt', '.html'):
                        html = filing.read_text(encoding='utf-8', errors='ignore')
                        md_text, tables = extract_text_and_tables(html)
                        # create filename
                        fname = sanitize_filename(f"{t}_{ftype}_{filing.stem}") + '.md'
                        fpath = outdir / fname
                        front = f"---\ntitle: \"{t} {ftype}\"\ncompany: \"{t}\"\nfiling: \"{ftype}\"\nsource: \"{filing}\"\n---\n\n"
                        fpath.write_text(front + md_text, encoding='utf-8')
                        # write tables as csv sidecar
                        for i, df in enumerate(tables):
                            csv_name = fpath.with_suffix('')
                            csv_path = csv_name.with_name(csv_name.name + f'_table_{i+1}.csv')
                            try:
                                df.to_csv(csv_path, index=False, encoding='utf-8')
                            except Exception:
                                pass
                        written += 1
                        print('Wrote', fpath)
                        if written >= max_files:
                            break
            if written >= max_files:
                break
    print('Done: wrote', written, 'edgar md files to', outdir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tickers-file', help='path to newline-separated tickers list')
    parser.add_argument('--email', help='your contact email required by sec-edgar-downloader', default='dev@example.com')
    parser.add_argument('--max', type=int, default=200)
    parser.add_argument('--out', default='datasets/edgar_md')
    args = parser.parse_args()
    main(tickers_file=args.tickers_file, max_files=args.max, out=args.out, email=args.email)
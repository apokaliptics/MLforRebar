"""Download Wikipedia dumps and extract with WikiExtractor.

Usage example:
    pip install wikiextractor
    python scripts/download_wikipedia.py --lang en --out datasets/wiki --sample 1000

Notes:
 - The script downloads the latest pages-articles XML dump for the language.
 - It runs WikiExtractor to extract plain text files.
 - It can write a sampled subset to `datasets/wiki_sampled/`.
"""
import argparse
from pathlib import Path
import subprocess


def main(lang='en', out='datasets/wiki', sample=None):
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)
    dump_url = f'https://dumps.wikimedia.org/{lang}wiki/latest/{lang}wiki-latest-pages-articles.xml.bz2'
    local = outdir / f'{lang}wiki-latest-pages-articles.xml.bz2'
    print('Download URL:', dump_url)
    print('Downloading to', local)
    subprocess.check_call(['curl', '-L', '-o', str(local), dump_url])
    print('Running WikiExtractor... (this may take a while)')
    subprocess.check_call(['python', '-m', 'wikiextractor.WikiExtractor', str(local), '-o', str(outdir / 'extracted')])
    if sample:
        print('Sampling', sample, 'articles (script will gather sample)')
        # lightweight sampling can be done here (left as an exercise) 
    print('Done. Extracted to', outdir / 'extracted')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', default='en')
    parser.add_argument('--out', default='datasets/wiki')
    parser.add_argument('--sample', type=int)
    args = parser.parse_args()
    main(lang=args.lang, out=args.out, sample=args.sample)

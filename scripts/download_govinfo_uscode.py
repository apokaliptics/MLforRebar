"""Download a govinfo bulk data example (USCODE) and extract it.

Usage:
    python scripts/download_govinfo_uscode.py --out datasets/legal

This downloads a sample zip and extracts. Adjust URLs/datasets for other gov portals.
"""
import argparse
from pathlib import Path
import subprocess


def main(out='datasets/legal'):
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)
    url = 'https://www.govinfo.gov/bulkdata/USCODE/2023/uscode-2023.xml.zip'
    local_zip = outdir / 'uscode-2023.xml.zip'
    print('Downloading', url, '->', local_zip)
    subprocess.check_call(['curl', '-L', '-o', str(local_zip), url])
    print('Unzipping...')
    subprocess.check_call(['unzip', '-o', str(local_zip), '-d', str(outdir)])
    print('Done. Extracted to', outdir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='datasets/legal')
    args = parser.parse_args()
    main(out=args.out)

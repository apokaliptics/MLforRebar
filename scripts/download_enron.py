"""Download and process the Enron email corpus and save as Markdown files.

Usage:
  python scripts/download_enron.py --max 3000 --out datasets/enron_md

Notes:
- Downloads the CMU Enron dataset tarball, extracts, walks maildir folders and parses individual emails.
- Saves each email as a Markdown file with frontmatter (From, To, Subject, Date, Message-Id, filename)
- Skips attachments; prefers text/plain bodies; falls back to text/html (stripped to text).
"""
import argparse
from pathlib import Path
import tarfile
import requests
import email
from email import policy
import re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent

ENRON_URL = 'https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz'


def text_from_message(msg):
    # prefer plain text
    if msg.is_multipart():
        parts = []
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get_content_disposition())
            if disp == 'attachment':
                continue
            if ctype == 'text/plain':
                try:
                    parts.append(part.get_content().strip())
                except Exception:
                    try:
                        parts.append(part.get_payload(decode=True).decode('utf-8', 'ignore').strip())
                    except Exception:
                        continue
            elif ctype == 'text/html' and not parts:
                try:
                    html = part.get_content()
                    parts.append(BeautifulSoup(html, 'html.parser').get_text())
                except Exception:
                    continue
        return '\n\n'.join([p for p in parts if p])
    else:
        ctype = msg.get_content_type()
        try:
            if ctype == 'text/plain':
                return msg.get_content().strip()
            elif ctype == 'text/html':
                html = msg.get_content()
                return BeautifulSoup(html, 'html.parser').get_text()
        except Exception:
            try:
                return msg.get_payload(decode=True).decode('utf-8', 'ignore').strip()
            except Exception:
                return ''


def sanitize_filename(s: str):
    return re.sub(r'[^0-9A-Za-z._-]', '_', s)[:200]


def main(max_files=3000, out='datasets/enron_md', download_url=ENRON_URL):
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)
    tmp = ROOT / 'downloads'
    tmp.mkdir(parents=True, exist_ok=True)
    tar_path = tmp / 'enron_mail_20150507.tar.gz'

    if not tar_path.exists():
        print('Downloading Enron dataset...')
        r = requests.get(download_url, stream=True, timeout=60)
        r.raise_for_status()
        with open(tar_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print('Downloaded to', tar_path)
    else:
        print('Using existing file', tar_path)

    print('Extracting...')
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(path=tmp)
    print('Extraction complete')

    # The extracted folder is 'maildir' under the tar root
    mailroot = tmp / 'maildir'
    if not mailroot.exists():
        # try alternate path
        mailroot = tmp

    written = 0
    for p in mailroot.rglob('*'):
        if written >= max_files:
            break
        if p.is_file():
            try:
                raw = p.read_text(encoding='utf-8', errors='ignore')
                msg = email.message_from_string(raw, policy=policy.default)
                body = text_from_message(msg)
                if not body or len(body.strip()) < 50:
                    continue
                subj = (msg.get('subject') or '').strip()
                frm = (msg.get('from') or '').strip()
                to = (msg.get('to') or '').strip()
                date = (msg.get('date') or '').strip()
                mid = (msg.get('message-id') or '').strip()
                fname = sanitize_filename(p.name + '_' + (mid or subj or 'msg')) + '.md'
                front = f"---\ntitle: \"{subj}\"\nfrom: \"{frm}\"\nto: \"{to}\"\ndate: \"{date}\"\nmessage_id: \"{mid}\"\nsource: \"{p}\"\n---\n\n"
                content = front + body
                (outdir / fname).write_text(content, encoding='utf-8')
                written += 1
                if written % 200 == 0:
                    print('Wrote', written)
            except Exception as e:
                # skip parse errors
                continue
    print('Done. Wrote', written, 'Enron emails to', outdir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--max', type=int, default=3000)
    parser.add_argument('--out', default='datasets/enron_md')
    parser.add_argument('--url', default=ENRON_URL)
    args = parser.parse_args()
    main(max_files=args.max, out=args.out, download_url=args.url)
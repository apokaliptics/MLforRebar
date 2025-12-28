"""Cleanup image content from Markdown files in student and education datasets.

- Scans `datasets/raw_docs/education` and `datasets/raw_docs/student` recursively
- Makes a backup copy of each edited file under `datasets/backup_preimage_cleanup/` preserving directory structure
- Removes/normalizes image references and common HTML figure/inline image blocks
- Replaces images with a short placeholder that preserves alt text when available
- Writes a report to stdout and `datasets/image_cleanup_report.csv`
"""
from pathlib import Path
import re
import shutil
import csv

ROOT = Path(__file__).resolve().parent.parent
TARGET_DIRS = [ROOT / 'datasets' / 'raw_docs' / 'education', ROOT / 'datasets' / 'raw_docs' / 'student']
BACKUP_ROOT = ROOT / 'datasets' / 'backup_preimage_cleanup'
REPORT_CSV = ROOT / 'datasets' / 'image_cleanup_report.csv'

MD_IMAGE_RE = re.compile(r'!\[(.*?)\]\((.*?)\)')
HTML_IMG_ALT_RE = re.compile(r'<img[^>]*alt=["\']([^"\']*)["\'][^>]*>', re.IGNORECASE)
HTML_IMG_RE = re.compile(r'<img[^>]*>', re.IGNORECASE)
FIGURE_RE = re.compile(r'<figure[^>]*>.*?</figure>', re.IGNORECASE | re.DOTALL)
WPICT_RE = re.compile(r'<w:pict[^>]*>.*?</w:pict>', re.IGNORECASE | re.DOTALL)
DATA_URI_RE = re.compile(r'data:image/[^)\s]+', re.IGNORECASE)


def backup_file(p: Path):
    rel = p.relative_to(ROOT)
    dest = BACKUP_ROOT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(p), str(dest))
    return dest


def process_text(text: str):
    changes = 0

    # Remove figure blocks entirely, replace with placeholder
    def repl_figure(m):
        nonlocal changes
        changes += 1
        return '\n*(image removed)*\n'
    text, n = FIGURE_RE.subn(repl_figure, text)

    # Remove Word pict blocks
    text, n2 = WPICT_RE.subn(lambda m: '\n*(image removed)*\n', text)
    changes += n2

    # Replace markdown images with placeholder keeping alt text
    def repl_md_img(m):
        nonlocal changes
        alt = m.group(1).strip()
        changes += 1
        if alt:
            return f'*(image removed: {alt})*'
        return '*(image removed)*'
    text, n3 = MD_IMAGE_RE.subn(repl_md_img, text)
    changes += 0  # n3 counted in repl_md_img

    # Replace HTML imgs with alt-preserving placeholder
    def repl_html_img(m):
        nonlocal changes
        changes += 1
        # try alt
        alt = m.group(1) if m.groups() else ''
        if alt:
            return f'*(image removed: {alt})*'
        return '*(image removed)*'
    text, n4 = HTML_IMG_ALT_RE.subn(repl_html_img, text)
    changes += 0

    # Remove any remaining <img ...>
    text, n5 = HTML_IMG_RE.subn('*(image removed)*', text)
    changes += n5

    # Remove data URIs inline
    text, n6 = DATA_URI_RE.subn('(image removed)', text)
    changes += n6

    return text, changes


def main():
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    report_rows = []
    total_changed_files = 0
    total_changes = 0

    for d in TARGET_DIRS:
        if not d.exists():
            print('Skipping missing dir', d)
            continue
        for p in d.rglob('*.md'):
            try:
                text = p.read_text(encoding='utf-8')
            except Exception as e:
                print('Failed to read', p, e)
                continue
            new_text, changes = process_text(text)
            if changes > 0:
                backup_file(p)
                p.write_text(new_text, encoding='utf-8')
                report_rows.append({'file': str(p.relative_to(ROOT)), 'changes': changes})
                total_changed_files += 1
                total_changes += changes
                print(f'Cleaned {p} ({changes} image blocks)')
    # write CSV report
    with open(REPORT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'changes'])
        writer.writeheader()
        for r in report_rows:
            writer.writerow(r)

    print('\nDone. Files changed:', total_changed_files, 'Total image blocks removed/replaced:', total_changes)
    print('Backup copies stored under', BACKUP_ROOT)
    print('Report written to', REPORT_CSV)


if __name__ == '__main__':
    main()

"""Organize and classify Markdown documents into `datasets/raw_docs/<category>`.

Usage:
    python scripts/organize_and_classify_docs.py [--move | --copy]

By default, the script moves files. It writes a manifest at `datasets/manifest.csv`.
"""
from pathlib import Path
import re
import shutil
import csv
import argparse

ROOT = Path(__file__).resolve().parent.parent
DATASETS = ROOT / 'datasets'
RAW = DATASETS / 'raw_docs'
EXCLUDE = set([
    'DOCX_TO_MD_INDEX.md',
    'README_LABEL_STUDIO.md',
    'DOCX_TO_MD_INDEX.md',
])

CATEGORY_RULES = {
    'education/lesson_plans': [r'lesson', r'plan', r'teaching', r'lesson plan'],
    'student/essays': [r'essay', r'writing', r'homework', r'writing', r'LNY', r'homework', r'my essay'],
    'tests/mock': [r'mock test', r'test', r'exam', r'kỳ thi', r'ky thi', r'MOCK TEST', r'KT', r'KTDT'],
    'exams/proposals': [r'DE HSGQG', r'ĐỀ', r'DE', r'de xuat', r'de xuat', r'DE', r'DHBB'],
    'academic/technology': [r'technology', r'technical', r'AI', r'computer', r'technology', r'khoa', r'technology gap'],
    'misc/notes': [r'outline', r'notes', r'outline for my speech', r'nostalgic', r'copy for myself'],
}

DEFAULT_CATEGORY = 'uncategorized'


def classify_text(text: str, filename: str):
    text_lower = text.lower()
    file_lower = filename.lower()
    matches = []
    for cat, patterns in CATEGORY_RULES.items():
        for pat in patterns:
            if re.search(pat.lower(), text_lower) or re.search(pat.lower(), file_lower):
                matches.append((cat, pat))
    if matches:
        # pick first matching category (priority by order in CATEGORY_RULES)
        return matches[0][0], [m[1] for m in matches]
    # fallback heuristics
    if 'lesson' in text_lower or 'lesson' in file_lower:
        return 'education/lesson_plans', []
    if 'essay' in text_lower or 'essay' in file_lower:
        return 'student/essays', []
    if 'test' in text_lower or 'mock' in text_lower or 'kỳ thi' in text_lower or 'exam' in text_lower:
        return 'tests/mock', []
    return DEFAULT_CATEGORY, []


def snippet(text, n=200):
    return text.replace('\n', ' ')[:n]


def main(move_files=True):
    DATASETS.mkdir(exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)

    md_files = [p for p in ROOT.glob('*.md') if p.name not in EXCLUDE]
    manifest = []

    for p in md_files:
        try:
            txt = p.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Skipping {p} (read error: {e})")
            continue
        cat, keywords = classify_text(txt, p.name)
        dest_dir = RAW / cat
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / p.name
        if move_files:
            shutil.move(str(p), str(dest_path))
            action = 'moved'
        else:
            shutil.copy2(str(p), str(dest_path))
            action = 'copied'
        manifest.append({'filename': p.name, 'original_path': str(p), 'new_path': str(dest_path), 'category': cat, 'keywords': ';'.join(keywords), 'snippet': snippet(txt)})
        print(f"{action}: {p.name} -> {dest_path} (category={cat})")

    manifest_path = DATASETS / 'manifest.csv'
    with open(manifest_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'original_path', 'new_path', 'category', 'keywords', 'snippet'])
        writer.writeheader()
        for row in manifest:
            writer.writerow(row)

    print(f"\nDone. {len(manifest)} files processed. Manifest written to {manifest_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--copy', action='store_true', help='Copy files instead of moving')
    args = parser.parse_args()
    main(move_files=not args.copy)

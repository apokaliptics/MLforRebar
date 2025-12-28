"""
Ingest BAWE dataset if provided locally.

Usage:
  - Place BAWE dataset files (text files or CSVs) into `data/bawe/`.
  - Run: python scripts/ingest_bawe.py --in data/bawe --out datasets/raw_docs/student/essays/bawe_high --min-level "1" 

Note: BAWE licensing may restrict redistribution. This script only processes local files you already have.
"""

import argparse
import os
from pathlib import Path


def find_text_files(folder: Path):
    # include plain text, markdown, csv and TEI/XML files
    files = list(folder.rglob("*.txt")) + list(folder.rglob("*.md")) + list(folder.rglob("*.csv"))
    files += list(folder.rglob("*.xml"))
    return files


def simple_filter_text(txt: str):
    # heuristics: remove very short files
    return len(txt.strip()) > 200


def extract_text_from_xml(path: Path) -> str:
    # Lightweight TEI/XML extractor: collect text from <p> and <text> elements
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(str(path))
        root = tree.getroot()
        texts = []
        # collect paragraph-like tags
        for el in root.iter():
            if el.tag.lower().endswith('p') or el.tag.lower().endswith('text') or el.tag.lower().endswith('body'):
                if el.text:
                    texts.append(el.text.strip())
        return '\n\n'.join(t for t in texts if t and len(t) > 50)
    except Exception:
        return ''


def process_txt_files(files, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in files:
        try:
            if f.suffix.lower() == '.xml':
                txt = extract_text_from_xml(f)
            else:
                txt = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if not simple_filter_text(txt):
            continue
        name = f.stem
        # make filename unique by prefixing with 'bawe_' if not already
        if not name.lower().startswith('bawe'):
            name = f"bawe_{name}"
        out_path = out_dir / f"{name}.md"
        with open(out_path, "w", encoding="utf-8") as o:
            o.write("---\n")
            o.write("source: bawe\n")
            o.write("---\n\n")
            o.write(txt)
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_dir", required=True)
    parser.add_argument("--out", default="datasets/raw_docs/student/essays/bawe_high")
    args = parser.parse_args()

    in_dir = Path(args.in_dir)
    if not in_dir.exists():
        print(f"Input folder {in_dir} does not exist. Place BAWE files there.")
        return
    files = find_text_files(in_dir)
    out_dir = Path(args.out)
    count = process_txt_files(files, out_dir)
    print(f"Saved {count} BAWE files to {out_dir}")

if __name__ == "__main__":
    main()

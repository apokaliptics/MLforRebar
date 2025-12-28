"""
Download and filter Kaggle IELTS writing datasets to extract high-scoring essays.

Usage:
  - Install Kaggle CLI and python dependencies:
      pip install kaggle pandas tqdm
  - Place your Kaggle credentials in environment variables or in ~/.kaggle/kaggle.json
    (the script expects either KAGGLE_USERNAME/KAGGLE_KEY or a local kaggle.json file)
  - Run:
      python scripts/download_kaggle_ielts.py --dataset <kaggle-dataset-slug> --min-score 8 --out datasets/raw_docs/student/essays/kaggle_high

Notes:
  - The script supports basic schemas with columns like 'score', 'band', 'band_score', 'score_band', or 'score_essay'.
  - If the dataset is a zip or csv file with a different schema, pass --score-column to specify the field.
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

import pandas as pd

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    KAGGLE_AVAILABLE = True
except Exception:
    KAGGLE_AVAILABLE = False


def download_kaggle_file(dataset, target_dir):
    api = KaggleApi()
    api.authenticate()
    # download dataset files to a temp dir
    tmp_dir = Path(".kaggle_tmp")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir()
    api.dataset_download_files(dataset, path=str(tmp_dir), unzip=True)
    return tmp_dir


def find_csv_files(folder: Path):
    return list(folder.rglob("*.csv"))


def find_text_files(folder: Path):
    return list(folder.rglob("*.txt")) + list(folder.rglob("*.md"))


def canonical_score_column(df: pd.DataFrame):
    candidates = [c for c in df.columns if "score" in c.lower() or "band" in c.lower()]
    return candidates[0] if candidates else None


def filter_high_scoring_csv(csv_path: Path, min_score: float, score_column: str = None):
    df = pd.read_csv(csv_path)
    if score_column is None:
        score_column = canonical_score_column(df)
    if score_column is None:
        print(f"No score column detected in {csv_path.name}; skipping")
        return []
    try:
        df[score_column] = pd.to_numeric(df[score_column], errors="coerce")
    except Exception:
        print(f"Unable to coerce scores in {csv_path}")
        return []
    selected = df[df[score_column] >= min_score]
    essays = []
    # heuristics for text column
    text_col = None
    for c in df.columns:
        if c.lower() in ["essay", "text", "writing", "response", "content"]:
            text_col = c
            break
    if text_col is None:
        # fallback: look for long text columns
        for c in df.columns:
            if df[c].astype(str).map(len).median() > 100:
                text_col = c
                break
    if text_col is None:
        print(f"No text column detected in {csv_path.name}; skipping")
        return []
    for i, row in selected.iterrows():
        txt = str(row[text_col])
        if not txt.strip():
            continue
        essays.append({"id": f"{csv_path.stem}_{i}", "text": txt})
    return essays


def save_essays(essays, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    for e in essays:
        fname = out_dir / f"{e['id']}.md"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(f"source: kaggle\n")
            f.write("---\n\n")
            f.write(e['text'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Kaggle dataset in owner/dataset format, e.g., 'username/dataset' or dataset-slug'")
    parser.add_argument("--min-score", type=float, default=8.0, help="Minimum score/band to keep")
    parser.add_argument("--out", default="datasets/raw_docs/student/essays/kaggle_high", help="Output directory for high scoring essays")
    parser.add_argument("--score-column", default=None, help="Optional: specify score column name in CSV")
    args = parser.parse_args()

    if not KAGGLE_AVAILABLE:
        print("Kaggle API not available. Install with `pip install kaggle` and ensure credentials are configured.")
        sys.exit(1)

    out_dir = Path(args.out)
    tmp = download_kaggle_file(args.dataset, out_dir)
    csvs = find_csv_files(tmp)
    total_saved = 0
    for csv in csvs:
        essays = filter_high_scoring_csv(csv, args.min_score, args.score_column)
        save_essays(essays, out_dir)
        total_saved += len(essays)
    # also check text files
    txts = find_text_files(tmp)
    for t in txts:
        # if filename indicates score, attempt to parse
        # skip for now
        pass

    print(f"Saved {total_saved} high-scoring essays to {out_dir}")


if __name__ == "__main__":
    main()

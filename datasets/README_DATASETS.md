# External datasets (BAWE, Kaggle IELTS)

This folder documents how to add external datasets for student essays (high-quality subsets).

Kaggle (IELTS datasets)
- We provide `scripts/download_kaggle_ielts.py` to download and extract high-scoring essays from a Kaggle dataset.
- Requirements:
  - `pip install kaggle pandas tqdm`
  - Configure Kaggle credentials (either set `KAGGLE_USERNAME` and `KAGGLE_KEY` environment variables or place `kaggle.json` in `~/.kaggle/`).
- Example run:
```
python scripts/download_kaggle_ielts.py --dataset username/dataset-slug --min-score 8 --out datasets/raw_docs/student/essays/kaggle_high
```

BAWE (British Academic Written English)
- BAWE may have licensing restrictions. Place the BAWE corpus files in `data/bawe/` on your machine.
- Use `scripts/ingest_bawe.py --in data/bawe --out datasets/raw_docs/student/essays/bawe_high` to copy filtered samples into the repo structure.

Notes
- These scripts only process local or Kaggle-hosted data you have access to; they do not attempt to redistribute copyrighted data.
- After populating high-quality samples, you may want to add a small curated subset to the repo (or to a separate data release) and keep large archives out of git (use Git LFS if needed).

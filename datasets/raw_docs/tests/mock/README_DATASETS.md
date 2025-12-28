# Datasets: automated download, conversion, sampling, and cleanup

This folder contains scripts and guidance to: gather legal/academic/wiki data, convert to Markdown, sample, and keep only what you need.

Scripts
- `scripts/download_arxiv.py` — download arXiv source tarballs by query.
- `scripts/download_wikipedia.py` — download a Wikipedia dump and run WikiExtractor.
- `scripts/download_govinfo_uscode.py` — download a US Code bulk XML example.
- `scripts/sample_dataset.py` — randomly sample Markdown files into `datasets/sampled/`.
- `scripts/organize_and_classify_docs.py` — move and classify local `.md` files into `datasets/raw_docs/<category>` and write `datasets/manifest.csv`.

Quick usage
1. Move and classify the current `.md` docs (default: move):
   ```bash
   python scripts/organize_and_classify_docs.py
   ```
   To copy instead of move:
   ```bash
   python scripts/organize_and_classify_docs.py --copy
   ```

2. Sample dataset for inspection:
   ```bash
   python scripts/sample_dataset.py --n 100
   ```

3. Download arXiv examples (safe, API based):
   ```bash
   pip install arxiv
   python scripts/download_arxiv.py --query "cat:cs.AI" --max 50
   ```

4. Download and extract a Wikipedia dump (large, use --sample to extract a subset):
   ```bash
   pip install wikiextractor
   python scripts/download_wikipedia.py --lang en
   ```

5. Download a US Code example (public domain):
   ```bash
   python scripts/download_govinfo_uscode.py
   ```

Conversion & cleanup
- Convert source files (LaTeX, HTML, XML) with Pandoc to Markdown.
- Keep only Markdown + small manifests + model artifacts. Delete raw dumps after conversion.

Security & ethics
- Use official APIs / dumps only and respect robots / terms where applicable.
- Sample aggressively; do not keep multi-GB dumps in the repo.

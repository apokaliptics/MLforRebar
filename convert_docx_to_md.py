#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import mammoth
from markdownify import markdownify as md

WORKSPACE = Path(__file__).resolve().parent


def convert_file(docx_path: Path, md_path: Path):
    """Convert a single DOCX file to Markdown and write to md_path."""
    # Ignore temporary Office files
    if docx_path.name.startswith("~$"):
        return "skipped-temp"
    with open(docx_path, "rb") as f:
        result = mammoth.convert_to_html(f)
        html = result.value
        messages = [str(m) for m in result.messages]

    markdown = md(html, heading_style="ATX")

    frontmatter = (
        "---\n"
        f"title: \"{md_path.stem}\"\n"
        f"source: \"{docx_path.as_posix()}\"\n"
        "---\n\n"
    )

    md_path.parent.mkdir(parents=True, exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as out:
        out.write(frontmatter)
        out.write(markdown)

    return messages


def main(root_dir: Path = WORKSPACE):
    converted = []
    errors = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if not filename.lower().endswith(".docx"):
                continue
            docx_path = Path(dirpath) / filename
            # Skip temp files
            if filename.startswith("~$"):
                continue
            md_path = docx_path.with_suffix(".md")
            try:
                msgs = convert_file(docx_path, md_path)
                converted.append((docx_path, md_path, msgs))
                print(f"Converted: {docx_path} -> {md_path}")
            except Exception as e:
                errors.append((docx_path, str(e)))
                print(f"Error converting {docx_path}: {e}", file=sys.stderr)

    # Create index file
    index_path = root_dir / "DOCX_TO_MD_INDEX.md"
    with open(index_path, "w", encoding="utf-8") as idx:
        idx.write("# DOCX to Markdown conversion index\n\n")
        idx.write(f"Converted {len(converted)} files.\n\n")
        for docx, mdfile, msgs in converted:
            rel = mdfile.relative_to(root_dir)
            idx.write(f"- [{rel.as_posix()}]({rel.as_posix()}) — originally `{docx.name}`\n")
            if msgs:
                idx.write("  - messages: " + "; ".join(msgs) + "\n")

        if errors:
            idx.write("\n## Errors\n")
            for docx, err in errors:
                idx.write(f"- `{docx}`: {err}\n")

    print(f"\nConversion complete. Index written to: {index_path}")


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else WORKSPACE
    main(target)

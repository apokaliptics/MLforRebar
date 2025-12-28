"""Delete all .docx files in the workspace root and subfolders. Use with caution."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

count = 0
for p in ROOT.rglob('*.docx'):
    try:
        p.unlink()
        count += 1
        print('Deleted', p)
    except Exception as e:
        print('Failed to delete', p, e)

print(f'Deleted {count} .docx files')

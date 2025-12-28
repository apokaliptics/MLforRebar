"""Simple test runner for pre-commit-free environments.
Run with: python scripts/run_unit_tests.py
"""
import traceback
import sys
from pathlib import Path
# ensure repo root is on sys.path so we can import tests and project modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

tests = [
    'tests.test_post_filter',
    'tests.test_eval_filter_stats'
]

failed = []
for t in tests:
    try:
        mod = __import__(t, fromlist=['*'])
        # execute functions starting with 'test_'
        for name in dir(mod):
            if name.startswith('test_'):
                fn = getattr(mod, name)
                print(f'Running {t}.{name}...')
                fn()
    except Exception as e:
        print(f'FAILED {t}:', e)
        traceback.print_exc()
        failed.append(t)

if not failed:
    print('All tests passed')
else:
    print('Failed tests:', failed)
    raise SystemExit(1)

"""
Post-filter utilities for paragraph-split inference.
The default rule is: predict split only if
 - prob >= threshold AND
 - (before ends with sentence punctuation OR after starts with uppercase)

Functions:
 - boundary_confirmed(before, after) -> bool
 - apply_post_filter(probs, metas, threshold=0.7) -> np.ndarray (bool mask)
"""
from typing import Sequence
import numpy as np

SENTENCE_ENDERS = set('.!?…')


def boundary_confirmed(before: str, after: str) -> bool:
    if not before or not after:
        return False
    try:
        last = before.rstrip()[-1]
    except Exception:
        return False
    if last in SENTENCE_ENDERS:
        return True
    first = after.lstrip()[0] if after.lstrip() else ''
    if first and first.isupper():
        return True
    return False


def apply_post_filter(probs: np.ndarray, metas: Sequence[dict], threshold: float = 0.7) -> np.ndarray:
    """Return boolean mask of kept (True) predictions after applying post-filter.

    probs: 1-d numpy array of split probabilities
    metas: sequence of meta dicts with keys 'text_before' and 'text_after'
    threshold: probability threshold
    """
    if len(probs) != len(metas):
        raise ValueError('probs and metas must be same length')
    pred_mask = probs >= threshold
    confirmed = [boundary_confirmed(m.get('text_before',''), m.get('text_after','')) for m in metas]
    filtered_mask = pred_mask & np.array(confirmed, dtype=bool)
    return filtered_mask

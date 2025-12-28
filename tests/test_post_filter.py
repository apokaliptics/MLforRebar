import numpy as np
from scripts.post_filter import boundary_confirmed, apply_post_filter


def test_boundary_confirmed_punctuation():
    assert boundary_confirmed('This is a sentence.', 'Next begins')
    assert not boundary_confirmed('This ends mid', 'next begins lower')


def test_boundary_confirmed_capital():
    assert boundary_confirmed('ends mid', 'Next begins')


def test_apply_post_filter():
    probs = np.array([0.95, 0.8, 0.6, 0.99])
    metas = [
        {'text_before': 'One.', 'text_after': 'Begins with Caps'},  # confirmed
        {'text_before': 'mid', 'text_after': 'Begins with Caps'},  # confirmed
        {'text_before': 'One.', 'text_after': 'lower case start'}, # not confirmed
        {'text_before': 'no end', 'text_after': 'lower start'}     # not confirmed
    ]
    mask = apply_post_filter(probs, metas, threshold=0.7)
    # only indices 0 and 1 should be kept
    assert mask.tolist() == [True, True, False, False]

import numpy as np
from scripts.eval_document_split import stress_test_model


class DummyScaler:
    def transform(self, X):
        return X


class DummyModel:
    def __init__(self, p):
        self.p = p
    def predict_proba(self, X):
        n = X.shape[0]
        probs = np.full(n, self.p, dtype=float)
        # return shape (n,2)
        return np.column_stack([1-probs, probs])


import tempfile


def test_stress_test_model_reports_filtered_and_orig():
    scaler = DummyScaler()
    # model returns high probability for split
    model = DummyModel(0.95)
    from scripts.train_production_model import FeatureExtractor
    fe = FeatureExtractor()
    # sources: one doc with clear boundary, one without
    sources = {
        'confirmed': ['First paragraph.\n\nSecond paragraph.'],
        'not_confirmed': ['first para\n\nsecond para']
    }
    with tempfile.TemporaryDirectory() as td:
        out_path = __import__('pathlib').Path(td)
        out_file, results = stress_test_model(model, scaler, fe, sources, out_path, apply_filter=True, filter_threshold=0.9)
    assert 'confirmed' in results and 'not_confirmed' in results
    for name, stats in results.items():
        assert 'frac_orig' in stats and 'frac_filtered' in stats
        # filtered fraction should be <= original
        assert stats['frac_filtered'] <= stats['frac_orig']

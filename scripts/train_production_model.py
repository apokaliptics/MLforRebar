"""
Train production paragraph split model (adapted from provided implementation).
"""
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

# Core ML
from sklearn.model_selection import cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

# NLP helpers
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk import pos_tag, word_tokenize
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    STOPWORDS = set(stopwords.words('english'))
except Exception:
    print('Warning: NLTK not fully available, some features disabled')
    STOPWORDS = set()


@dataclass
class ModelMetadata:
    version: str
    created_at: str
    model_type: str
    feature_count: int
    training_samples: int
    cross_val_f1: float
    test_accuracy: float
    test_f1: float
    test_precision: float
    test_recall: float
    hyperparameters: dict
    feature_names: list
    class_balance: dict


class FeatureExtractor:
    def __init__(self):
        self.continuation_markers = {'however', 'moreover', 'furthermore', 'additionally', 'also'}
        self.topic_shift_markers = {'now', 'next', 'turning to', 'regarding', 'concerning'}
        self.conclusion_markers = {'conclusion', 'summary', 'finally', 'lastly'}

    def extract_all_features(self, before, after, full):
        feats = []
        feats.extend(self._basic_features(full))
        feats.extend(self._boundary_features(before, after))
        feats.extend(self._discourse_features(before, after))
        feats.extend(self._structural_features(before, after, full))
        feats.extend(self._lexical_features(before, after))
        return np.array(feats, dtype=np.float32)

    def _basic_features(self, text):
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        words = text.split()
        return [len(sentences), len(words)/max(1, len(sentences)), text.count(','), len(words)]

    def _boundary_features(self, before, after):
        before_words = before.split(); after_words = after.split()
        last_word = before_words[-1].lower().strip('.,;:!?') if before_words else ''
        first_word = after_words[0].lower().strip('.,;:!?') if after_words else ''
        before_sents = [s.strip() for s in before.split('.') if s.strip()]
        after_sents = [s.strip() for s in after.split('.') if s.strip()]
        last_sent = before_sents[-1] if before_sents else ''
        first_sent = after_sents[0] if after_sents else ''
        return [len(before_words), len(after_words), len(last_sent.split()), len(first_sent.split()), len(last_sent.split())/max(1, len(first_sent.split())), int(first_word in self.continuation_markers), int(first_word in self.topic_shift_markers), int(last_word in {'and','or','but'})]

    def _discourse_features(self, before, after):
        after_lower = after.lower(); before_lower = before.lower()
        pronouns = {'he','she','it','they','this','that','these','those','his','her','their'}
        first_words = after.split()[:3]
        starts_with_pronoun = any(w.lower() in pronouns for w in first_words)
        before_words = set(w.lower() for w in before.split() if w.lower() not in STOPWORDS)
        after_words = set(w.lower() for w in after.split() if w.lower() not in STOPWORDS)
        overlap = len(before_words & after_words) / len(before_words | after_words) if (before_words and after_words) else 0.0
        return [int(starts_with_pronoun), overlap, sum(1 for m in self.continuation_markers if m in after_lower), sum(1 for m in self.topic_shift_markers if m in after_lower), sum(1 for m in self.conclusion_markers if m in before_lower), int(after[0].isupper() if after else False), int(after.strip().split()[0].rstrip('.').isdigit() if after else False)]

    def _structural_features(self, before, after, full):
        before_question = before.count('?'); after_question = after.count('?'); before_exclaim = before.count('!')
        before_caps = sum(1 for c in before if c.isupper()); after_caps = sum(1 for c in after if c.isupper())
        before_quotes = before.count('"') + before.count("'"); after_quotes = after.count('"') + after.count("'")
        return [before_question, after_question, before_exclaim, before_caps/max(1, len(before)), after_caps/max(1, len(after)), int((before_quotes % 2) == 1), len(before)/max(1,len(full))]

    def _lexical_features(self, before, after):
        before_words = before.split(); after_words = after.split()
        before_ttr = len(set(w.lower() for w in before_words))/len(before_words) if before_words else 0
        after_ttr = len(set(w.lower() for w in after_words))/len(after_words) if after_words else 0
        before_avg_len = sum(len(w) for w in before_words)/len(before_words) if before_words else 0
        after_avg_len = sum(len(w) for w in after_words)/len(after_words) if after_words else 0
        return [before_ttr, after_ttr, before_avg_len, after_avg_len]

    def get_feature_names(self):
        return ['sentence_count','avg_sentence_length','comma_count','total_words','words_before_split','words_after_split','last_sentence_length','first_sentence_length','length_ratio','starts_with_continuation','starts_with_topic_shift','ends_with_conjunction','starts_with_pronoun','lexical_overlap','continuation_marker_count','topic_shift_marker_count','conclusion_marker_before','starts_with_capital','starts_with_number','questions_before','questions_after','exclamations_before','capitalization_ratio_before','capitalization_ratio_after','unclosed_quotes_before','position_in_paragraph','lexical_diversity_before','lexical_diversity_after','avg_word_length_before','avg_word_length_after']


class ParagraphSplitModel:
    def __init__(self, model_type='logistic', version='2.0.0'):
        self.version = version
        self.model_type = model_type
        self.feature_extractor = FeatureExtractor()
        self.scaler = StandardScaler()
        self.model = None
        self.feature_names = self.feature_extractor.get_feature_names()

    def load_data_from_export(self, export_path):
        with open(export_path, 'r', encoding='utf-8') as f:
            records = json.load(f)
        X_list=[]; y_list=[]
        for r in records:
            data = r.get('data', {})
            ann = None
            for a in r.get('annotations', []) + r.get('predictions', []):
                ann = a; break
            if not ann: continue
            results = ann.get('result', [])
            choice=None
            for res in results:
                if res.get('type') in ['choices','singlechoice']:
                    choice = res.get('value', {}).get('choices') or res.get('value')
                    break
            if not choice: continue
            # normalize choice value
            if isinstance(choice, (list, tuple)) and len(choice) > 0:
                choice_val = str(choice[0]).strip().lower()
            else:
                choice_val = str(choice).strip().lower()
            label = 1 if choice_val == 'split' else 0
            before = data.get('text_before','')
            after = data.get('text_after','')
            full = data.get('full_paragraph', before + ' ' + after)
            features = self.feature_extractor.extract_all_features(before, after, full)
            X_list.append(features); y_list.append(label)
        X = np.array(X_list); y = np.array(y_list)
        return X, y

    def train(self, X, y, test_size=0.2):
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        class_counts = np.bincount(y_train)
        class_weight = {0: len(y_train)/(2*class_counts[0]), 1: len(y_train)/(2*class_counts[1])} if len(class_counts)==2 else None
        print('Training Logistic Regression...')
        param_grid = {'C':[0.01,0.1,1.0,10.0], 'penalty':['l2'], 'max_iter':[500]}
        base_model = LogisticRegression(class_weight=class_weight, random_state=42)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        grid_search = GridSearchCV(base_model, param_grid, cv=cv, scoring='f1', n_jobs=-1, verbose=0, error_score=np.nan)
        try:
            grid_search.fit(X_train_scaled, y_train)
            if hasattr(grid_search, 'best_estimator_') and grid_search.best_estimator_ is not None:
                self.model = grid_search.best_estimator_
                print(f"\nBest parameters: {grid_search.best_params_}")
                print(f"Best cross-val F1: {grid_search.best_score_:.4f}")
            else:
                print("Grid search completed but no valid fit found; falling back to default estimator")
                base_model.fit(X_train_scaled, y_train)
                self.model = base_model
        except Exception as e:
            print("Grid search failed with error:", e)
            print("Falling back to default estimator fit")
            base_model.fit(X_train_scaled, y_train)
            self.model = base_model

        y_pred = self.model.predict(X_test_scaled)
        print(classification_report(y_test, y_pred, digits=4))
        # metadata
        counts = np.bincount(y)
        best_score = getattr(grid_search, 'best_score_', None)
        best_params = getattr(grid_search, 'best_params_', None)
        self.metadata = ModelMetadata(version=self.version, created_at=datetime.now().isoformat(), model_type=self.model_type, feature_count=X.shape[1], training_samples=len(y), cross_val_f1=best_score if best_score is not None else 0.0, test_accuracy=accuracy_score(y_test, y_pred), test_f1=f1_score(y_test, y_pred), test_precision=precision_score(y_test, y_pred), test_recall=recall_score(y_test, y_pred), hyperparameters=best_params if best_params is not None else {}, feature_names=self.feature_names, class_balance={'no_split': int(counts[0]), 'split': int(counts[1])})
        return self.model

    def export(self, output_path):
        if self.model is None: raise ValueError('Model not trained yet')
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(self.model, LogisticRegression):
            export_data = {
                'metadata': asdict(self.metadata),
                'model': {
                    'type':'logistic_regression',
                    'weights':self.model.coef_[0].tolist(),
                    'bias':float(self.model.intercept_[0])
                },
                'scaler': {'mean':self.scaler.mean_.tolist(),'scale':self.scaler.scale_.tolist()},
                'feature_names':self.feature_names,
                # recommended runtime post-filter settings
                'post_filter': {
                    'enabled': True,
                    'threshold': 0.7,
                    'rule': 'prob >= threshold AND (before ends with .!?… OR after starts uppercase)'
                }
            }
        else:
            export_data = {'metadata': asdict(self.metadata), 'model': {'type':self.model_type, 'note':'Tree models require ONNX or API deployment'}, 'feature_names': self.feature_names}
        with open(out, 'w', encoding='utf-8') as f: json.dump(export_data, f, indent=2)
        print(f'Exported model to {out}')


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='labelstudio_export_synthetic.json')
    parser.add_argument('--output', default='models/paragraph_split_v2.json')
    parser.add_argument('--model', default='logistic', choices=['logistic','xgboost','gradient_boost','random_forest'])
    parser.add_argument('--version', default='2.0.0')
    args = parser.parse_args()
    model = ParagraphSplitModel(model_type=args.model, version=args.version)
    X, y = model.load_data_from_export(args.input)
    if len(y) < 50:
        print('Warning: Less than 50 samples; model may be unreliable')
    model.train(X, y)
    model.export(args.output)

if __name__ == '__main__':
    main()

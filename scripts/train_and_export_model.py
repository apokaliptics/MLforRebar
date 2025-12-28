"""Train logistic regression on training_data.csv and export a JSON model for Rebar."""
import csv
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import json


def train(csv_path='training_data.csv', model_out='paragraph_split_model.json'):
    X = []
    y = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            feats = [float(row['sentence_count']), float(row['avg_sentence_length']), float(row['comma_count'])]
            X.append(feats)
            y.append(int(row['label']))
    X = np.array(X)
    y = np.array(y)
    if len(y) < 10:
        print('Warning: fewer than 10 labeled examples; model will be unstable')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    print('Accuracy:', accuracy_score(y_test, preds))
    print(classification_report(y_test, preds))
    model_data = {'weights': model.coef_[0].tolist(), 'bias': float(model.intercept_[0])}
    with open(model_out, 'w', encoding='utf-8') as f:
        json.dump(model_data, f)
    print('Exported model to', model_out)

if __name__ == '__main__':
    train()
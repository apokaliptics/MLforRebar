"""Convert Label Studio export (JSON) into a training CSV with features and labels."""
import json, csv, re

def extract_features(text):
    sentences = re.split(r'[.!?]', text)
    sentence_count = len([s for s in sentences if s.strip()])
    avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(1, sentence_count)
    comma_count = text.count(',')
    return [sentence_count, avg_sentence_length, comma_count]


def convert(export_path='labelstudio_export.json', out_csv='training_data.csv'):
    with open(export_path, 'r', encoding='utf-8') as f:
        records = json.load(f)
    rows = []
    for r in records:
        data = r.get('data', {})
        ann = None
        for a in r.get('annotations', []) + r.get('predictions', []):
            ann = a
            break
        if not ann:
            continue
        results = ann.get('result', [])
        choice = None
        for res in results:
            if res.get('type') == 'choices' or res.get('type') == 'singlechoice':
                choice = res.get('value', {}).get('choices') or res.get('value')
                break
        if not choice:
            continue
        label = 1 if 'split' in choice else 0
        full = data.get('full_paragraph') or (data.get('text_before','') + ' ' + data.get('text_after',''))
        feats = extract_features(full)
        rows.append({'label': label, 'features': feats, 'doc': data.get('doc'), 'paragraph_index': data.get('paragraph_index'), 'boundary_index': data.get('boundary_index')})
    with open(out_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['label', 'sentence_count', 'avg_sentence_length', 'comma_count', 'doc', 'paragraph_index', 'boundary_index'])
        for r in rows:
            writer.writerow([r['label']] + r['features'] + [r['doc'], r['paragraph_index'], r['boundary_index']])
    print('Wrote training CSV with', len(rows), 'rows to', out_csv)

if __name__ == '__main__':
    convert()
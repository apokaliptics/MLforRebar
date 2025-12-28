"""
Generate a synthetic Label Studio JSON export for paragraph split task.
Each record will contain `data`: text_before, text_after, full_paragraph and an annotation with choice 'split' or 'no_split'.
"""
import json
import random
from pathlib import Path

CONTINUATION_MARKERS = {'however','moreover','furthermore','additionally','also','likewise','similarly','consequently'}
TOPIC_SHIFT_MARKERS = {'now','next','turning to','regarding','concerning','on the other hand','conversely'}
PRONOUNS = {'he','she','it','they','this','that','these','those','his','her','their'}

SENTENCES = [
    "Technology has changed the way people communicate.",
    "Students often struggle with adapting to online learning.",
    "Public policy must consider long-term consequences.",
    "There are clear benefits and drawbacks to this approach.",
    "The evidence points to a gradual but definite change.",
    "This trend has implications for both practice and research.",
    "However, further work is required to confirm these findings.",
    "Consequently, stakeholders should evaluate the options carefully.",
    "Many experts suggest that an interdisciplinary approach is needed.",
]


def make_paragraph(paragraph_length=4):
    return ' '.join(random.choices(SENTENCES, k=paragraph_length))


def decide_split(after):
    # heuristics: if after starts with pronoun or continuation marker => no split
    first_word = after.split()[0].strip('.,').lower() if after else ''
    if first_word in PRONOUNS:
        return 'no_split'
    if any(after.lower().startswith(m) for m in CONTINUATION_MARKERS):
        return 'no_split'
    # random but biased
    return 'split' if random.random() < 0.4 else 'no_split'


def generate(n=5000, out='labelstudio_export_synthetic.json'):
    records = []
    for i in range(n):
        para_len = random.randint(3,6)
        full = make_paragraph(para_len)
        # choose a boundary within paragraph: split into before/after sentences
        split_point = random.randint(1, para_len-1)
        sentences = full.split('. ')
        before = '. '.join(sentences[:split_point]).strip()
        after = '. '.join(sentences[split_point:]).strip()
        if not before.endswith('.'):
            before = before + '.'
        if not after.endswith('.'):
            after = after + '.'
        label = decide_split(after)
        rec = {
            'data': {
                'text_before': before,
                'text_after': after,
                'full_paragraph': before + ' ' + after
            },
            'annotations': [
                {
                    'result': [
                        { 'type': 'singlechoice', 'value': {'choices':[label]} }
                    ]
                }
            ]
        }
        records.append(rec)
    Path(out).write_text(json.dumps(records, indent=2), encoding='utf-8')
    print(f'Wrote {n} records to {out}')

if __name__ == '__main__':
    generate()

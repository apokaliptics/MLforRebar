"""
Generate synthetic 'high-quality' essays for testing and bootstrapping datasets.

Usage:
  python scripts/generate_synthetic_essays.py --out datasets/raw_docs/student/essays/kaggle_high --count 3000 --source kaggle

The script writes Markdown files with a simple YAML header containing `source: <source>` and a plausible essay body.
These are synthetic placeholders and should be replaced with real data when available.
"""

import argparse
import random
from pathlib import Path

SENTENCE_TEMPLATES = [
    "{start} {clause}, which demonstrates {point}.",
    "{start} {clause}.",
    "{start} {clause}; therefore, {consequence}.",
    "{start} {clause}, and this suggests {implication}.",
]

STARTS = [
    "In recent years", "Traditionally", "Interestingly", "Notably", "Consequently",
    "Furthermore", "On the other hand", "For example", "Generally", "Specifically"
]

CLAUSES = [
    "technology has advanced rapidly", "students increasingly rely on digital platforms",
    "societal norms have shifted", "globalization affects local economies",
    "educational outcomes vary across regions", "public policy influences innovation",
]

POINTS = [
    "a shift in priorities", "a growing need for regulation", "a challenge for policymakers",
    "a new opportunity for educators", "an important trade-off"
]

CONSEQUENCES = [
    "stakeholders must respond", "we must reassess our strategies", "further research is needed",
    "policy adjustments may help", "stakeholders should collaborate"
]

IMPLICATIONS = [
    "long-term changes in behavior", "an improvement in outcomes", "greater inequality",
    "a reconsideration of values", "a need for better measurement"
]

PARAGRAPH_TEMPLATES = [
    "{sent1} {sent2} {sent3}",
    "{sent1} {sent2} {sent3} {sent4}",
]


def make_sentence():
    start = random.choice(STARTS)
    clause = random.choice(CLAUSES)
    point = random.choice(POINTS)
    consequence = random.choice(CONSEQUENCES)
    implication = random.choice(IMPLICATIONS)
    template = random.choice(SENTENCE_TEMPLATES)
    return template.format(start=start, clause=clause, point=point, consequence=consequence, implication=implication)


def make_paragraph(sent_count=4):
    sents = [make_sentence() for _ in range(sent_count)]
    return ' '.join(sents)


def make_essay(num_paragraphs=4):
    paras = [make_paragraph(sent_count=random.randint(3,6)) for _ in range(num_paragraphs)]
    return '\n\n'.join(paras)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--count', type=int, default=3000)
    parser.add_argument('--source', default='synthetic')
    parser.add_argument('--min_paras', type=int, default=3)
    parser.add_argument('--max_paras', type=int, default=6)
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    for i in range(args.count):
        paras = random.randint(args.min_paras, args.max_paras)
        essay = make_essay(num_paragraphs=paras)
        fname = out / f"{args.source}_{i:05d}.md"
        with open(fname, 'w', encoding='utf-8') as f:
            f.write('---\n')
            f.write(f"source: {args.source}\n")
            f.write('synthetic: true\n')
            f.write('---\n\n')
            f.write(essay)

    print(f"Generated {args.count} synthetic essays in {out}")

if __name__ == '__main__':
    main()

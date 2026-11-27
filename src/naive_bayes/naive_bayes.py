"""
CampusAsk-NLP | Naive Bayes + lowercasing experiment
Put this file in: src/naive_bayes/naive_bayes.py

Usage (from the repo root):
    python src/naive_bayes/naive_bayes.py            # development: cross-validation on TRAIN only
    python src/naive_bayes/naive_bayes.py --final    # final run: trains on all 80, predicts the 20 test rows ONCE

Uses only the Python standard library.
Assumed CSV columns: question_id, question, intent, style, split
"""

import argparse
import csv
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
OUT_DIR = Path(__file__).resolve().parent
SEED = 42


# ----------------------------------------------------------------- data
def load_data(data_dir):
    """Read every CSV in data/, dedupe by question_id, split using the `split` column."""
    rows = {}
    for path in sorted(data_dir.glob("*.csv")):
        with open(path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                rows[r["question_id"]] = r
    train = [r for r in rows.values() if r["split"].strip().lower().startswith("train")]
    test = [r for r in rows.values() if r["split"].strip().lower().startswith("test")]
    if not train or not test:
        raise SystemExit("Could not find train/test rows. Check the `split` column values in data/*.csv")
    return train, test


# ------------------------------------------------------------ the model
def tokenize(text, lowercase, ngram_max):
    if lowercase:
        text = text.lower()
    words = re.findall(r"[A-Za-z0-9']+", text)
    tokens = list(words)
    if ngram_max >= 2:
        tokens += [a + "_" + b for a, b in zip(words, words[1:])]
    return tokens


class NaiveBayes:
    """Multinomial Naive Bayes with Laplace (add-alpha) smoothing."""

    def __init__(self, alpha=1.0, lowercase=True, ngram_max=1):
        self.alpha = alpha
        self.lowercase = lowercase
        self.ngram_max = ngram_max

    def fit(self, questions, labels):
        self.classes = sorted(set(labels))
        self.class_counts = Counter(labels)
        self.word_counts = defaultdict(Counter)
        vocab = set()
        for q, y in zip(questions, labels):
            toks = tokenize(q, self.lowercase, self.ngram_max)
            self.word_counts[y].update(toks)
            vocab.update(toks)
        self.vocab = vocab
        self.total_words = {c: sum(self.word_counts[c].values()) for c in self.classes}
        self.n = len(labels)
        return self

    def log_scores(self, question):
        toks = tokenize(question, self.lowercase, self.ngram_max)
        V = len(self.vocab)
        scores = {}
        for c in self.classes:
            s = math.log(self.class_counts[c] / self.n)
            denom = self.total_words[c] + self.alpha * V
            for t in toks:
                if t in self.vocab:  # ignore words never seen in training
                    s += math.log((self.word_counts[c][t] + self.alpha) / denom)
            scores[c] = s
        return scores

    def predict_one(self, question):
        scores = self.log_scores(question)
        return max(self.classes, key=lambda c: scores[c])

    def predict(self, questions):
        return [self.predict_one(q) for q in questions]


# ------------------------------------------------------ cross-validation
def stratified_folds(rows, k, seed):
    by_class = defaultdict(list)
    for r in rows:
        by_class[r["intent"]].append(r)
    rng = random.Random(seed)
    folds = [[] for _ in range(k)]
    for c in sorted(by_class):
        items = by_class[c][:]
        rng.shuffle(items)
        for i, r in enumerate(items):
            folds[i % k].append(r)
    return folds


def cross_val_accuracy(train, k, **cfg):
    folds = stratified_folds(train, k, SEED)
    correct = total = 0
    for i in range(k):
        val = folds[i]
        fit = [r for j, f in enumerate(folds) if j != i for r in f]
        model = NaiveBayes(**cfg).fit([r["question"] for r in fit], [r["intent"] for r in fit])
        preds = model.predict([r["question"] for r in val])
        correct += sum(p == r["intent"] for p, r in zip(preds, val))
        total += len(val)
    return correct / total


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true",
                    help="train on all training rows and predict the test set (run this once)")
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--alpha", type=float, default=1.0)
    args = ap.parse_args()

    train, test = load_data(DATA_DIR)
    print(f"Train: {len(train)} rows | Test: {len(test)} rows (test is untouched until --final)\n")

    # Experiment: lowercasing on/off (unigrams), plus unigram+bigram as an extra row.
    # All numbers come from cross-validation on TRAIN ONLY.
    configs = [
        ("no lowercasing, unigrams", dict(lowercase=False, ngram_max=1)),
        ("lowercasing,    unigrams", dict(lowercase=True, ngram_max=1)),
        ("no lowercasing, uni+bi", dict(lowercase=False, ngram_max=2)),
        ("lowercasing,    uni+bi", dict(lowercase=True, ngram_max=2)),
    ]
    results = []
    print(f"{args.folds}-fold stratified CV accuracy on training data (alpha={args.alpha}):")
    for name, cfg in configs:
        acc = cross_val_accuracy(train, args.folds, alpha=args.alpha, **cfg)
        results.append((acc, name, cfg))
        print(f"  {name:28s} {acc:.3f}")

    # Tie-break: prefer lowercasing and the simpler (unigram) model.
    best = max(results, key=lambda t: (t[0], t[2]["lowercase"], -t[2]["ngram_max"]))
    print(f"\nChosen setting: {best[1].strip()} (CV accuracy {best[0]:.3f})")

    if not args.final:
        print("\nDevelopment mode: test set not used. Run with --final when the setting is decided.")
        return

    model = NaiveBayes(alpha=args.alpha, **best[2]).fit(
        [r["question"] for r in train], [r["intent"] for r in train])
    preds = model.predict([r["question"] for r in test])

    out_path = OUT_DIR / "predictions_naive_bayes.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["question_id", "predicted_intent"])
        for r, p in zip(test, preds):
            w.writerow([r["question_id"], p])
    print(f"\nPredictions saved to {out_path}")
    acc = sum(p == r["intent"] for p, r in zip(preds, test)) / len(test)
    print(f"Test accuracy: {acc:.3f} (report this once; do not tune further)")


if __name__ == "__main__":
    main()

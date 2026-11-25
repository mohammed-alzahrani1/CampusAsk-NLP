"""
CampusAsk-NLP | Step 4: Majority Baseline + Keyword Rules
Run from repo root:  python src/baseline_rules/baseline_rules.py
"""
import os
import re
import sys
from collections import Counter

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report

TEXT_COL = "question"
LABEL_COL = "intent"
TRAIN_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "CampusAsk_Train_80.csv"
)

# Keyword rules: intent -> keywords (intents match the real data:
# Contact, Fees, Hours, Location, Registration)
KEYWORD_RULES = {
    "Hours": ["hours", "open", "close", "closing", "opening", "what time", "when does", "schedule"],
    "Fees": ["fee", "fees", "tuition", "cost", "pay", "payment", "price", "charge", "refund", "scholarship"],
    "Registration": ["register", "registration", "enroll", "enrol", "drop", "withdraw", "add a course", "sign up", "waitlist", "deadline"],
    "Location": ["where", "located", "location", "find", "building", "room", "floor", "directions", "campus map", "which building"],
    "Contact": ["contact", "email", "phone", "call", "reach", "number", "talk to", "speak to", "office hours"],
}


def keyword_predict(text, majority_label, valid_labels):
    text = str(text).lower()
    scores = {}
    for label, kws in KEYWORD_RULES.items():
        if label not in valid_labels:
            continue
        scores[label] = sum(
            1 for kw in kws if re.search(r"\b" + re.escape(kw.lower()), text)
        )
    if not scores:
        return majority_label
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else majority_label


def report(name, y_true, y_pred):
    print(f"\n===== {name} =====")
    print(f"Accuracy : {accuracy_score(y_true, y_pred):.4f}")
    print(f"Macro-F1 : {f1_score(y_true, y_pred, average='macro', zero_division=0):.4f}")
    print(classification_report(y_true, y_pred, zero_division=0))


def main():
    if not os.path.exists(TRAIN_PATH):
        sys.exit(f"File not found: {TRAIN_PATH}")
    df = pd.read_csv(TRAIN_PATH)
    for col in (TEXT_COL, LABEL_COL):
        if col not in df.columns:
            sys.exit(f"Column '{col}' missing. Available: {list(df.columns)}")
    df = df.dropna(subset=[TEXT_COL, LABEL_COL])

    labels = set(df[LABEL_COL].unique())
    print(f"Loaded {len(df)} rows from CampusAsk_Train_80.csv")
    print("Intent distribution:\n", df[LABEL_COL].value_counts())
    missing = [k for k in KEYWORD_RULES if k not in labels]
    if missing:
        print(f"\n[!] Rule keys not matching any intent (ignored): {missing}")
        print(f"[!] Real intents are: {sorted(labels)}")

    majority_label = Counter(df[LABEL_COL]).most_common(1)[0][0]
    print(f"\nMajority class: {majority_label}")
    report("Majority Baseline", df[LABEL_COL], [majority_label] * len(df))

    preds = df[TEXT_COL].apply(lambda t: keyword_predict(t, majority_label, labels))
    report("Keyword Rules", df[LABEL_COL], preds)


if __name__ == "__main__":
    main()
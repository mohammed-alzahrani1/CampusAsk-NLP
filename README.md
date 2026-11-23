# CampusAsk-NLP

University Student Question Intent Classification | CS1763

Al-Baha University, Natural Language Processing (CS1763).

The project classifies an English student question as `Hours`, `Fees`, `Location`,
`Registration`, or `Contact`. This repository currently contains the supplied
dataset, data checks, and collaboration instructions. Models, evaluation results,
the course report, and presentation have not been implemented.

## Dataset

| Intent | All | Train | Test |
| --- | ---: | ---: | ---: |
| Hours | 20 | 16 | 4 |
| Fees | 20 | 16 | 4 |
| Location | 20 | 16 | 4 |
| Registration | 20 | 16 | 4 |
| Contact | 20 | 16 | 4 |
| Total | 100 | 80 | 20 |

Each CSV has `question_id`, `question`, `intent`, `style`, and `split` columns.
The master CSV contains the same records as the union of the training and test
CSVs. Use the 80 training records for development. Reserve the 20 test records for
final evaluation; do not use them to choose rules, preprocessing, or models.

All five supplied data and review files are preserved byte for byte. Their
SHA-256 hashes are recorded in `docs/dataset_manifest.json`.
Structural checks pass for the supplied version. Human approval of wording,
labels, university context, and possible semantic overlap remains pending in
[`docs/data_review.md`](docs/data_review.md).

The fixed split matches Python `random.Random(42 + category_index).sample(...)`,
with four test records sampled from each category's ascending question IDs.
Category order is Hours, Fees, Location, Registration, Contact. The base seed is
42 and the category seeds are 42 through 46. The original generation script was
not supplied, so this demonstrates a compatible reproduction of the saved split.
The validator never creates a new split.

## Repository layout

```text
CampusAsk-NLP/
  data/                       # Original master, training, and test CSVs
  docs/                       # Original workbook/guide, provenance, validation, review
  scripts/validate_dataset.py
  src/baseline_rules/          # Reserved for the majority baseline and keyword rules
  src/naive_bayes/             # Reserved for Naive Bayes and the lowercasing experiment
  evaluation/                 # Reserved for evaluation and error analysis
  report/                     # Reserved for the course report
  presentation/               # Reserved for the final presentation
  .github/                    # Pull request template and dataset validation workflow
  AGENTS.md
  CONTRIBUTING.md
  README.md
  .gitignore
  .gitattributes
```

## Run the dataset checks

Use Python 3.10 or later; verification was performed with Python 3.13.11.
The validator uses only the Python standard library. No dependency installation
or model training is required.

```shell
python scripts/validate_dataset.py
```

The command works from any directory when the script is given by its path. It
checks schema, counts, class balance, empty values, IDs, exact and normalized
duplicates, split tags, train/test overlap, full-row CSV consistency, fixed seed
reproduction, source-file hashes, and workbook-to-CSV agreement. A failed check
returns exit code 1. Similarity warnings require review and are separate from
structural failures. Passing validation does not approve semantic quality.

To save a new validation record intentionally:

```shell
python scripts/validate_dataset.py --json-output docs/dataset_validation.json
```

## Assigned responsibilities

These are work assignments, not claims that each member has completed the work.

| Member | Assigned work | Suggested branch |
| --- | --- | --- |
| Mohammed Alzahrani | Question collection, labeling, cleaning, fixed train/test split | `data/review` |
| Omar Alsharqi | Majority baseline and keyword rules | `feature/baseline-rules` |
| Amro Hilal | Naive Bayes and lowercasing experiment | `feature/naive-bayes` |
| Ayman Alghamdi | Evaluation, error analysis, report and presentation compilation | `analysis/evaluation` |
| Ayman Omar | Code organization, README, GitHub setup, final packaging | `chore/repository-setup` |

All members contribute to the final report and presentation. GitHub account names
for the other members have not been provided; the owner must invite and verify
each member's access.

## Collaborate and resume work

Repository: <https://github.com/mohammed-alzahrani1/CampusAsk-NLP>.
Follow [`CONTRIBUTING.md`](CONTRIBUTING.md) for clone, pull, branch, commit, push,
and pull request commands. Work on task branches and obtain another member's
review before merging into `main`. GitHub Actions checks the dataset on pull
requests and pushes to `main`; enforcement also depends on repository settings.

Open the existing `CampusAsk-NLP` directory in Codex for later local work. Check
`git status`, `git remote -v`, and `gh auth status`, then fetch and pull when the
working tree is ready. Do not extract another copy, clone again, or reinitialize
Git in this folder.

Local GitHub CLI authentication does not establish a tested Codex Cloud
connection. Cloud use requires a separately available environment and repository
access; verify those before relying on cloud fetch or push.

Academic source and tool provenance is recorded in `docs/data_review.md`. The
final course report must contain the required sources and AI-use disclosure,
following the actual course guide when it is available.

# Dataset review record

Status: structural validation passed; human semantic approval pending.

## Scope and provenance

The supplied source is `CampusAsk_GitHub_Starter.zip`. The original three CSVs,
review workbook, and data guide are preserved byte for byte. SHA-256 hashes are
in `dataset_manifest.json`. No questions, labels, IDs, styles, or split tags were
edited during repository setup. `dataset_validation.json` records an actual
validator run, not model performance.

The source guide describes the questions as hypothetical and AI-assisted. Its
references to instructor approval, a feedback screenshot, and a Student Guide
were not independently verified: those materials were not supplied. Verify the
actual course requirements before the final submission. No deadline, approval,
or attribution of completed work is inferred from the starter documentation.

The final course report should record AI assistance in the supplied draft and in
repository documentation/validation work, together with human review and the
actual tools and sources used. The final academic report is not written here.

## Mechanical checks

The master has 100 rows across five intents, with 20 rows per intent. Training
has 80 rows and test has 20, with 16 and 4 rows per intent. The CSVs agree on every
field. There are no empty fields, repeated IDs, exact duplicate questions, or
duplicates after Unicode normalization, case folding, whitespace normalization,
and punctuation removal. No IDs or exact/normalized questions overlap across
train and test. All three workbook data sheets match the corresponding CSVs,
and workbook summary counts agree.

The fixed assignments match sampling four ascending IDs per category using
`random.Random(42 + category_index)`. Category order is Hours, Fees, Location,
Registration, Contact. The original generation script was not supplied; its
historical execution cannot be proved. No split was regenerated or written.

## Semantic review

All 100 supplied questions were inspected during setup. The following items
need human decisions. They are review candidates, not confirmed labeling errors.
No automatic corrections were made.

| IDs | Current label(s) | Review question | Split |
| --- | --- | --- | --- |
| HOU-013 | Hours | Does using a lab outside class hours express service availability clearly enough, rather than permission/access policy? | Train |
| LOC-002 | Location | Is the elliptical question "Computer science building?" sufficiently clear without a location word? | Train |
| REG-017 | Registration | Confirm that maximum credit hours belongs to registration policy; the word "hours" does not mean opening times. | Train |
| FEE-011, CON-014 | Fees, Contact | "Where" asks for financial account information or contact details, rather than a physical location; retain the intended boundary if approved. | Train |
| REG-001, REG-008, REG-013 | Registration | Admission, withdrawal, and enrollment deadlines are registration questions, distinct from service opening hours. | Train |
| FEE-001, FEE-019 | Fees | Both ask whether an application costs money. Decide whether the shared intent is acceptable paraphrase coverage. | Train / Train |
| FEE-014, FEE-016 | Fees | Related certificate-charge questions, with an initial certificate versus an additional copy. Confirm the distinction is adequate. | Train / Train |
| REG-004, REG-014 | Registration | Both concern full courses; joining a waiting list is more specific. Assess potential semantic overlap across the fixed split before approving the dataset. | Train / Test |
| HOU-001, HOU-012 | Hours | Library opening questions differ by weekday/Friday. Assess the related wording across splits without changing the saved split. | Test / Train |
| HOU-003, LOC-001, CON-001 | Hours, Location, Contact | Same admissions-office entity but different requested information. These are lexical similarity candidates, not exact duplicates. | Train |

The automatic similarity scan uses token Jaccard similarity at threshold 0.50
after removing a documented stop-word set in the validator. It identifies
HOU-003/LOC-001 and LOC-001/CON-001, both within training. This heuristic does not
detect all paraphrases, approve labels, or prove the absence of semantic leakage.
The two cross-split groups above therefore remain open for human review.

Confirm the university relevance of hypothetical services such as dormitories,
shuttles, gym access, international tuition, and certificate charges. The questions
do not establish that those services or fees exist at Al-Baha University.

## Approval record

No human approval has been recorded. A reviewer should record their name, date,
IDs reviewed, decision and rationale, and any explicitly approved changes in a
pull request. Preserve the original version and fixed split. Obtain owner approval
before modifying any original data. Begin model development after the team has
resolved the review items according to course requirements.

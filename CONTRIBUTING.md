# Contributing

## Access and ownership

The repository owner invites each member through **Settings > Collaborators >
Add people**, using a confirmed GitHub username. Members must accept their
invitations before private repository access works. Use contribution access
without giving administrative access unless the team has agreed otherwise.
Member names and work assignments appear in the README. Do not infer GitHub
usernames from those names. Access for other members is pending until verified.

## Clone once

Install Git, Python 3.10 or later, and GitHub CLI. Authenticate using the official
browser flow. Do not put passwords or access tokens in this repository or chat.

```shell
gh auth login --hostname github.com --git-protocol https --web
gh auth status
git clone https://github.com/mohammed-alzahrani1/CampusAsk-NLP.git
cd CampusAsk-NLP
git remote -v
python scripts/validate_dataset.py
```

Clone only when you do not already have a local checkout. For an existing
checkout, open that same directory and continue below.

## Start a task

Save or commit local work before switching branches. Do not discard another
member's work to make a command succeed.

```shell
git status
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c feature/your-task
```

Use `git switch <existing-branch>` instead of `git switch -c` when a task branch
already exists. To use an existing remote branch for the first time, run
`git switch --track origin/<branch>`. Suggested task branch names are in the
README; create additional branches for separate tasks when needed.

Keep implementation in the assigned folders. Coordinate shared-file changes.
Do not overwrite, rename, or remove a teammate's files without agreement.

## Commit and push

```shell
python scripts/validate_dataset.py
git diff --check
git diff
git add <specific-files>
git diff --cached
git commit -m "feat: add keyword rules"
git push -u origin HEAD
gh pr create --base main --fill
```

The commit message is an example. Describe the actual change using `feat:`,
`fix:`, `docs:`, `data:`, or `chore:` followed by a concise action. Keep unrelated
changes in separate commits. Stage specific files and review them for secrets.
Never force push or commit credentials, local environments, private student
records, generated caches, or claimed results from experiments not run.

## Review and merge

Open a pull request into `main` and request a different member's review. Include
the purpose, changed files, commands actually run, and any limitations. Dataset
validation must pass. Owners of later model code add and run the relevant
checks for their changes. Resolve comments before merging and keep `main` usable.

The owner should enforce pull requests, one approving review, and the
`Validate dataset` check on `main`, with force pushes and deletions disabled.
Server enforcement depends on the repository's GitHub plan and permissions.
If enforcement is unavailable, review remains a required team procedure, with
the technical limitation recorded in the setup report. Do not bypass protection.

To bring updated `main` into an active task branch without rewriting history:

```shell
git fetch origin
git merge origin/main
python scripts/validate_dataset.py
git push
```

If a merge conflicts, inspect each affected file and coordinate with its owner.
Do not resolve conflicts by replacing the whole file with your copy.

## Data changes

The supplied split is fixed at base seed 42, with per-category seeds 42 through
46. Do not regenerate it or tune against the held-out test questions. The master
CSV is the canonical record; train and test are its saved subsets. Never combine
all three as separate training examples or maintain personal alternative copies.

Open an issue or pull request describing any proposed wording or label correction
before editing. Record stable question IDs, the reason, affected records, and the
approval. Update all affected CSV and workbook records together only after owner
approval. Preserve IDs and split assignments, and update the reviewed provenance
manifest and validation record in the same change. Never update hashes merely
to silence a failed check. Keep semantic decisions in `docs/data_review.md`.

## Resume in Codex

Open the same project folder. Read `AGENTS.md`, inspect `git status`, verify
`git remote -v` and `gh auth status`, and run `git fetch origin`. Pull only when
local changes have been handled. Do not run `git init` or clone into this folder.
Cloud repository access is a separate setup and must be tested in that environment.

Keep sources, actual experiment settings, tool versions, and AI assistance records
for the final course report. Each member remains responsible for understanding,
reviewing, and accurately describing their own work.

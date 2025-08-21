# Contributing Guide

Thanks for contributing to AI Narrative Nexus! This guide explains our workflow and how to submit changes confidently.

## TL;DR
- Create a feature branch from `main`.
- Keep changes focused; include tests/docs when relevant.
- Run the notebook or unit tests for your area before pushing.
- Open a Pull Request (PR) with a clear description and checklist.

## Collaborator onboarding: from invite to first PR

1) Accept the GitHub invite (email or repo Settings > Collaborators) and ensure you can access the repo: `https://github.com/dipeshkumar123/ai-narrative-nexus`.

2) Clone the repo and configure your identity (one-time):

```powershell
git clone https://github.com/dipeshkumar123/ai-narrative-nexus.git
cd ai-narrative-nexus
git config user.name "Your Name"
git config user.email "you@example.com"
```

3) Create a feature branch off `main` for your work:

```powershell
git checkout -b feat/<your-part>
```

4) Set up your environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\ml\requirements.txt
```

5) Run locally (pick what you need):

- Notebook: open `ml/nlp_tasks.ipynb` and Run All relevant cells.
- API: `python .\ml\app.py` or `.\.venv\Scripts\python.exe -m uvicorn ml.app:app --host 127.0.0.1 --port 8001`.

6) Commit and push your branch, then open a PR:

```powershell
git add -A
git commit -m "feat: add <short description>"
git push -u origin feat/<your-part>
# then open a PR in GitHub: compare feat/<your-part> -> main
```

7) Keep your branch up-to-date with main (pull before you push):

```powershell
git fetch origin
git switch main
git pull --rebase origin main
git switch feat/<your-part>
git rebase origin/main
# resolve conflicts, then:
git add <files>
git rebase --continue
git push --force-with-lease
```

### If you already have local code you want to bring in

Option A (recommended): copy your files into this cloned repo folder, then commit and push on a new branch.

Option B (if your folder isn’t a git repo yet):

```powershell
# inside your existing local code folder
git init
git remote add origin https://github.com/dipeshkumar123/ai-narrative-nexus.git
git fetch origin
git checkout -b feat/<your-part> origin/main
# move/keep your code here, then:
git add -A
git commit -m "feat: import initial <your-part>"
git push -u origin feat/<your-part>
```

Option C (advanced): if your code is in a separate git repo, you can add it as a remote, fetch, and cherry-pick commits. Ask a maintainer if you’d like help with this path.

## Prerequisites
- Python 3.10+
- Node/other stacks as required by `frontend/` or `backend/` (if applicable)
- Git installed and a GitHub account with access to the repo

## Setup
```powershell
# From repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\ml\requirements.txt
```

If you work on the API, make sure the saved artifacts exist (run `ml/nlp_tasks.ipynb` once). See `ml/README.md`.

## Branching strategy
- `main` is protected. Create branches off `main`:
  - `feat/<short-title>` (new feature)
  - `fix/<short-title>` (bug fix)
  - `docs/<short-title>` (docs only)
  - `chore/<short-title>` (tooling, config, etc.)

Example:
```powershell
git checkout -b feat/summarization-batch
```

## Commit messages
- Use conventional, short, imperative messages:
  - `feat: add batching for summarization`
  - `fix: guard against empty input in sentiment endpoint`
  - `docs: expand README with troubleshooting`

## Code style & quality
- Python: follow PEP8 where practical. Prefer type hints.
- Keep notebooks deterministic; clear stale cells and re-execute before commit.
- Avoid committing large/binary files. Use `.gitignore`. Consider Git LFS for very large artifacts.

## Running and testing
- Notebook: `ml/nlp_tasks.ipynb` — run all sections related to your change, ensure no errors.
- API:
```powershell
python .\ml\app.py
# or
.\.venv\Scripts\python.exe -m uvicorn ml.app:app --host 127.0.0.1 --port 8001 --log-level info
```
- Smoke-tests (PowerShell):
```powershell
$body = @{ text = 'I loved this movie!' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://localhost:8001/sentiment' -ContentType 'application/json' -Body $body
```

## Typical daily workflow

```powershell
# Morning sync
git fetch origin
git switch main
git pull --rebase origin main
git switch feat/<your-part>
git rebase origin/main

# Do work, validate locally
git add -A
git commit -m "feat: <incremental change>"
git push --force-with-lease

# Open/refresh PR and request reviews
```

## Pull Requests
- Keep PRs small and focused; include:
  - What changed and why
  - Screenshots/outputs for notebook cells or API responses (when helpful)
  - Any migration or setup steps
- Link related issue(s) and add reviewers.
- CI (if configured) must pass before merge.

## Review checklist (author)
- [ ] Branch is up-to-date with `main`
- [ ] Notebook cells re-run cleanly; outputs relevant and concise
- [ ] No secrets or large data checked in
- [ ] Docs updated (`README.md`, `ml/README.md`, comments)
- [ ] Endpoint contracts unchanged or documented

## Review checklist (reviewer)
- [ ] Meets acceptance criteria / solves the problem
- [ ] Code is readable and modular
- [ ] Tests / outputs demonstrate correctness
- [ ] No unnecessary files or debug code
- [ ] Performance and error handling are acceptable

## Merging
- Use “Squash and merge” for cleaner history unless otherwise agreed.
- Delete branches after merging.

## Release & tags (optional)
- Use semantic versioning tags (e.g., `v0.1.0`) for milestones.

## Troubleshooting
- PowerShell JSON errors: build a hashtable and pipe to `ConvertTo-Json`.
- Missing models: run the notebook to (re)generate artifacts.
- spaCy model missing: `python -m spacy download en_core_web_sm`.
 - Large datasets: don’t commit big files to git; keep them in `data/` locally and add to `.gitignore` or use Git LFS.
 - Conflicts during rebase: resolve files, `git add`, then `git rebase --continue`. If stuck: `git rebase --abort` and try again or ask for help.

## Questions
Open a GitHub Discussion or Issue, or tag a maintainer in your PR.

# Contributing to AI Narrative Nexus

Thanks for your interest in contributing! This guide explains setup, workflow, and PR expectations.

## Project structure
- `ml/nlp_tasks.ipynb` — trains/evaluates models (sentiment, summarization, topic modeling)
- `ml/app.py` — FastAPI service exposing endpoints
- `data/` — CSV datasets used by the notebook

## Setup
```powershell
# from repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\ml\requirements.txt
# optional, one-time
python -m spacy download en_core_web_sm
```

Run API locally:
```powershell
python .\ml\app.py
# or
.\.venv\Scripts\python.exe -m uvicorn ml.app:app --host 127.0.0.1 --port 8001 --log-level info
```

Quick smoke tests:
```powershell
Invoke-RestMethod -Method Get -Uri 'http://localhost:8001/health' | ConvertTo-Json -Depth 5

$s_body = @{ text = 'this was amazing!' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://localhost:8001/sentiment' -ContentType 'application/json' -Body $s_body | ConvertTo-Json -Depth 5
```

To regenerate artifacts, open `ml/nlp_tasks.ipynb` and Run All. Expected outputs in `ml/`:
- `sentiment_analysis_model.pkl`
- `sentiment_analysis_vectorizer.pkl`
- `t5_summarization_model/`
- `topic_modeling_model.model`
- `topic_modeling_dictionary.dict`

## Branching and commits
- Branch from `main`: `feat/<topic>`, `fix/<topic>`, or `chore/<topic>`
- Use Conventional Commits where practical (e.g., `feat: add ROUGE-Lsum metric`)

## PR checklist
- [ ] Code runs locally without errors
- [ ] Notebook cells execute cleanly end-to-end (if modified)
- [ ] API endpoints smoke-tested
- [ ] Docs updated (README/usage)
- [ ] No large binaries committed (prefer samples or Git LFS)

## Reporting issues
Please include repro steps, expected vs. actual, logs/errors, and scope/acceptance criteria for features.

## Security
Do not commit secrets. Use environment variables or secret storage.

---
Thanks for contributing!

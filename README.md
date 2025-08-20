# AI Narrative Nexus

This repository contains a full-stack setup for NLP tasks: Sentiment Analysis, Text Summarization, and Topic Modeling.

- `ml/nlp_tasks.ipynb`: End-to-end notebook that trains/evaluates models and saves artifacts.
- `ml/app.py`: FastAPI service to serve predictions using the saved models.
- `ml/README.md`: Service setup, endpoints, and troubleshooting.
- `data/`: CSV datasets used by the notebook.
- `backend/`, `frontend/`: App scaffolds (if applicable).

## Getting started

1) Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\ml\requirements.txt
```

2) Run the API

```powershell
python .\ml\app.py
# or
.\.venv\Scripts\python.exe -m uvicorn ml.app:app --host 127.0.0.1 --port 8001 --log-level info
```

3) Open the notebook

- Open `ml/nlp_tasks.ipynb` in VS Code and Run All to reproduce training and artifacts.

## Collaboration

We recommend creating a private GitHub repository and pushing this folder structure. See the instructions below to initialize git and push.

### Initialize git locally

```powershell
# from repo root
cd "c:\Users\panji\OneDrive\Desktop\Sem 7\Placement Training\Infosys\new"
git init
git add .
git commit -m "chore: initial commit for AI Narrative Nexus"
```

### Create GitHub repo and push (two options)

Option A: GitHub CLI (gh)

```powershell
# Create a private repository; change name if you prefer
$repoName = "ai-narrative-nexus"
.\.venv\Scripts\python.exe -c "print('skip')" # no-op to keep powershell block valid
# If you have gh installed and authenticated:
gh repo create $repoName --private --source . --remote origin --push
```

Option B: Manual via HTTPS

```powershell
# Create an empty repo on GitHub named ai-narrative-nexus
# Then set remote and push
git remote add origin https://github.com/<your-username>/ai-narrative-nexus.git
git branch -M main
git push -u origin main
```

Add collaborators under the GitHub repo Settings > Collaborators and teams.

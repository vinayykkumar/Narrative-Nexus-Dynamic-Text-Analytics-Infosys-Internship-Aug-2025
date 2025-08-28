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
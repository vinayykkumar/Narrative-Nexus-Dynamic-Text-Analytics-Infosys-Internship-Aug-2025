# AI Narrative Nexus

This repository contains a full-stack setup for NLP tasks: Sentiment Analysis, Text Summarization, and Topic Modeling.


## Getting started

### Backend (FastAPI + NLP services)

```powershell
# create & activate virtual env
python -m venv .venv
./.venv/Scripts/Activate.ps1

# install dependencies
pip install -r backend/requirements.txt

# prepare data/models (downloads datasets & trains topic models)
python pipeline.py

# start API
cd backend
uvicorn app:app --reload
```

The API exposes:

- `POST /summarize` – returns extractive/abstractive summaries
- `POST /sentiment` – combined transformer + VADER + TextBlob sentiment bundle
- `POST /topics` – NMF topic ids + keywords
- `POST /analyze` – full insight pack (summaries, sentiment, topics, keyword cloud, suggestions)
- `POST /analyze-file` – upload `.txt/.csv/.docx/.pdf` and receive same insight payload

### Frontend (Vite + React)

```powershell
cd FrontEnd
npm install
npm run dev
```

By default the frontend expects the API at `http://127.0.0.1:8000`.

### Running automated tests

```powershell
cd backend
python -m pytest tests
```

Tests run the FastAPI app with lightweight stubs (no large model downloads required) to verify summarization, sentiment, and insight endpoints.

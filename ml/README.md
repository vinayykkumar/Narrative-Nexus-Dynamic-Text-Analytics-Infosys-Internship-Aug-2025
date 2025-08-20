# NLP Model Service (`ml/app.py`)

FastAPI service exposing endpoints for Sentiment Analysis, Text Summarization, and Topic Modeling using artifacts saved by `ml/nlp_tasks.ipynb`.

## Prerequisites

- Python 3.10+ recommended
- Model artifacts saved by the notebook (see Expected Artifacts)

## Install

Windows PowerShell:

```powershell
# 1) Create & activate a virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Install dependencies
pip install -r .\ml\requirements.txt

# 3) Optional: download spaCy English model once
python -m spacy download en_core_web_sm
```

## Run the API

Choose one of the following:

```powershell
# Option A: run via Python (uses the __main__ block in app.py)
python .\ml\app.py

# Option B: run via uvicorn directly
.\.venv\Scripts\python.exe -m uvicorn ml.app:app --host 127.0.0.1 --port 8001 --log-level info
```

## Quick smoke tests (PowerShell)

PowerShell inline JSON can be tricky. Prefer building a hashtable then ConvertTo-Json.

```powershell
# Health
Invoke-RestMethod -Method Get -Uri 'http://localhost:8001/health' | ConvertTo-Json -Depth 5

# Sentiment
$s_body = @{ text = 'this was amazing!' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://localhost:8001/sentiment' -ContentType 'application/json' -Body $s_body | ConvertTo-Json -Depth 5

# Summarize
$sum_body = @{ text = 'Long article text goes here...' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://localhost:8001/summarize' -ContentType 'application/json' -Body $sum_body | ConvertTo-Json -Depth 5

# Topics
$t_body = @{ text = 'The central bank raised interest rates...' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://localhost:8001/topics' -ContentType 'application/json' -Body $t_body | ConvertTo-Json -Depth 5
```

## Endpoints

All endpoints accept/return JSON.

- GET `/health`
	- Response: `{ status: string, models: { sentiment: boolean, summarizer: boolean, topics: boolean } }`

- POST `/sentiment`
	- Request: `{ "text": string }`
	- Response: `{ "label": string, "probabilities"?: { [class]: number } }`

- POST `/summarize`
	- Request: `{ "text": string, "max_length"?: number, "min_length"?: number, "num_beams"?: number, "length_penalty"?: number }`
	- Response: `{ "summary": string }`

- POST `/topics`
	- Request: `{ "text": string, "top_k"?: number, "topn_terms"?: number }`
	- Response: `{ "topics": [ { "topic_id": number, "probability": number, "top_terms": [ { "term": string, "weight": number } ] } ] }`

## Expected Model Artifacts

Produced by `ml/nlp_tasks.ipynb` and loaded by the service:

- `ml/sentiment_analysis_model.pkl`
- `ml/sentiment_analysis_vectorizer.pkl`
- `ml/t5_summarization_model/` (directory with tokenizer/model files). If missing, service falls back to `t5-small`.
- `ml/topic_modeling_model.model`
- `ml/topic_modeling_dictionary.dict`

If any are missing, open `ml/nlp_tasks.ipynb` and Run All to train & save.

## Troubleshooting

- JSON decode error in PowerShell when posting bodies:
	- Use a hashtable piped to `ConvertTo-Json` (see smoke tests). Avoid raw inline JSON with quotes/escapes.
- 500 “model not available”:
	- Ensure Expected Model Artifacts exist in `ml/` (see above). Re-run notebook cells to generate them.
- Slow first request for summarization:
	- On first run, `t5-small` may download; subsequent calls are faster. Consider warming up at boot.
- spaCy model missing error:
	- Run `python -m spacy download en_core_web_sm` once (or re-run the notebook’s first cell that auto-installs it).
- Port already in use:
	- Change `--port` or stop the existing process bound to that port.

## Integration notes

- Timeouts: summarization on CPU can take a few seconds on long input; set backend HTTP timeouts accordingly (e.g., 20–60s).
- Input length: requests truncate to 512 tokens for summarization; adjust in code if needed.
- CORS is enabled for `*` by default; tighten in production if necessary.

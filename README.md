# AI Narrative Nexus

This repository contains a full-stack setup for NLP tasks: Sentiment Analysis, Text Summarization, and Topic Modeling.

## Project Structure

narrative_nexus/
├── data/
│   ├── bbc-text.csv
│   ├── imdb-dataset.csv
│   └── cnn_dailymail.csv
├── frontend/                # frontend ui code
├── models/
│   ├── lda_model.pkl
│   ├── nmf_model.pkl
│   ├── tfidf_vectorizer.pkl
│   └── sentiment_model/      # HF cached or saved
├── src/
│   ├── preprocessing.py
│   ├── topic_modeling.py
│   ├── sentiment.py
│   ├── summarization.py
│   ├── insights.py
│   └── utils.py
├── backend/
│   ├── app.py                # FastAPI app
│   └── api_schema.py
├── pipeline.py
├── requirements.txt
└── README.md


## Getting started

1) Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

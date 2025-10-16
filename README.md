# 🧠 AI Narrative Nexus — NLP Based Text Analysis 

## 📘 Project Overview
**AI Narrative Nexus** is a modular NLP pipeline designed to transform unstructured text into interpretable insights.  
The project integrates **preprocessing, topic modeling, sentiment analysis, summarization, and executive dashboards** to extract patterns, emotional tone, and concise representations from text datasets.

This document covers **Weeks 1–6**, focusing on:
- Data ingestion and preprocessing
- Topic modeling (NMF & LDA)
- Sentiment analysis (VADER & Transformer-based)
- Summarization (extractive, abstractive, hybrid, topic-level)
- Interactive dashboard with insights and reporting

##  Project UI
![alt text](<Screenshot 2025-10-14 224234.png>)
---

## 🗂️ Week 1 — Data Input & Preprocessing

### 🔹 Objective
Prepare raw text (TXT, DOCX, CSV) into clean, structured data for downstream NLP tasks.

### 🔹 Techniques Used
- **File ingestion:** Supports `.txt`, `.csv`, `.docx`
- **Cleaning operations:**
  - URL, email, punctuation, and control character removal
  - Lowercasing and whitespace normalization
  - Token filtering (remove tokens ≤ 2 characters)
- **Linguistic preprocessing (spaCy):**
  - Lemmatization
  - Stopword removal

### 📘 Data Input UI
**CSV / PDF / DOCX / Paste The TEXT
![alt text](<Screenshot 2025-10-14 224410.png>) 

### 🔹 Key Implementation
```python
from src.preprocessing import clean_text, summarize_text_stats
cleaned = clean_text(raw_text)
stats = summarize_text_stats(cleaned)
```

### 🔹 Outputs
- Cleaned corpus ready for modeling  
- Text statistics summary:  
  - Total words, unique words  
  - Average word length  
  - Top 10 frequent terms  

---

## 🗂️ Week 2 — Topic Modeling

### 🔹 Objective
Discover latent topics/themes within the corpus.

### 🔹 Techniques Used
**Vectorization:**
- TfidfVectorizer (for NMF)
- CountVectorizer (for LDA)

**Models:**
- NMF (Non-negative Matrix Factorization): interpretable, distinct topics
- LDA (Latent Dirichlet Allocation): probabilistic, soft assignment of topics

### 🔹 Diagnostics & Metrics
| Metric | Description | Implementation |
|--------|-------------|----------------|
| Coherence Score | Semantic consistency of top words | gensim.CoherenceModel |
| Perplexity | Likelihood of unseen data | LDA intrinsic metric |
| Topic Diversity | Unique fraction of top-n words | Custom function |
| Silhouette Score | Topic separation via embeddings | sentence-transformers + sklearn |

### 🔹 Key Implementation
```python
from src.topic_modeling import vectorize_tfidf, fit_nmf, top_terms_per_topic, compute_coherence_score

V = vectorize_tfidf(docs)
nmf = fit_nmf(V.X, n_topics=8)
topics = top_terms_per_topic(nmf, V.feature_names)
coh = compute_coherence_score(nmf, docs, V.feature_names)
```

### 🔹 Outputs
- Trained topic model (.joblib)  
- Topic-word distributions  
- Document-topic responsibilities (theta matrix)  
- Evaluation metrics (coherence, perplexity, diversity)  

---

## 🗂️ Week 3 — Topic Visualization & Labeling

### 🔹 Objective
Make the topics discovered via NMF & LDA (from Week 2) interpretable and human-readable by visualizing them and assigning meaningful labels.

### 🔹 Techniques Used
**Model outputs used**
- NMF (Non-negative Matrix Factorization) topics

- LDA (Latent Dirichlet Allocation) topics

**Visualization tools**
- pyLDAvis for LDA (interactive topic-term visualization)

- Word clouds for top terms per topic

- Bar charts for topic weights across documents

**Keyword extraction**
- Top-n words per topic (from model output)

**Topic labeling approaches**

- Heuristic labeling: Based on most frequent/semantically strong keywords

- Zero-shot classification (optional): Hugging Face models for label suggestion

### 📘 Topic Modeling UI
![alt text](<Screenshot 2025-10-14 224627.png>) 

### 🔹 Implementation
```python
# Example: Visualize LDA topics using pyLDAvis
import pyLDAvis.sklearn
pyLDAvis.enable_notebook()
vis = pyLDAvis.sklearn.prepare(lda_model, dtm, vectorizer)
pyLDAvis.display(vis)

# Example: Label topics heuristically
from src.labeling import keyword_labeler
topic_label = keyword_labeler(top_terms)

```

### 🔹 Outputs
- Interactive pyLDAvis visualization (topic-term relevance, inter-topic distance)

- Word clouds & bar charts for topic keywords

- Human-friendly topic labels (e.g., “Technology”, “Healthcare”)

- Labels persisted in st.session_state for use in Summarization (Week 5) and Dashboard (Week 6)

---

## 🗂️ Week 4 — Sentiment Analysis

### 🔹 Objective
Assess emotional tone across documents and topics.

### 🔹 Techniques Used
**Option A: VADER**
- Fast, lexicon-based analyzer  
- Works well for informal text  

**Option B: Hugging Face Transformer**
- Model: `cardiffnlp/twitter-roberta-base-sentiment-latest`  
- Context-aware, robust, returns NEG/NEU/POS distribution  

### 📘 Sentiment Analysis UI

![alt text](<Screenshot 2025-10-14 224824.png>)

**Overall sentiment distribution**
![alt text](<Screenshot 2025-10-14 224847.png>)

**Sentiments by Topics**
![alt text](<Screenshot 2025-10-14 224911.png>) 

### 🔹 Implementation
```python
from src.sentiment import analyze_vader, analyze_hf

results_vader = analyze_vader(docs)
results_hf = analyze_hf(docs, batch_size=16)
```

### 🔹 Aggregations
**Overall sentiment distribution**
```python
from src.sentiment import overall_distribution_pct
overall_distribution_pct(labels)
```

**Sentiment by Topic**
- Dominant Topic (argmax)  
- Weighted by topic probability  

```python
from src.sentiment import sentiment_by_topic_argmax, sentiment_by_topic_weighted
df_argmax = sentiment_by_topic_argmax(labels, theta)
df_weighted = sentiment_by_topic_weighted(labels, theta)
```

### 🔹 Visualizations
- Pie chart & bar chart (overall)  
- Stacked bars (sentiment per topic)  

---

## 🗂️ Week 5 — Summarization

### 🔹 Objective
Generate concise summaries at document-level and topic-level.

### 🔹 Techniques Used
- **Extractive Summarization**  
  TF-IDF + Maximal Marginal Relevance (MMR)  
- **Abstractive Summarization**  
  Transformer models: BART / DistilBART  
- **Hybrid Summarization**  
  Extractive backbone + abstractive rephrasing  
- **Topic-Level Summarization**  
  Summarizes docs grouped by topic assignment (Dominant/Weighted modes) 

### 📘 Summarization UI 
![alt text](<Screenshot 2025-10-14 225002.png>) 

### 🔹 Implementation
```python
from src.summarization import summarize_document, summarize_by_topics

summary = summarize_document(
    cleaned_text,
    mode="hybrid",
    num_sentences=10,
    min_words=150,
    max_words=300,
    model_name="distilbart"
)

topic_summaries = summarize_by_topics(docs, topic_assignments, n_topics, sentences_per_topic=5)
```

### 🔹 Outputs
- Executive summary for entire corpus  
- Topic-level summaries with labels + keywords  
- Downloadable CSV of topic summaries  

---

## 🗂️ Week 6 — Dashboard & Insights

### 🔹 Objective
Provide an interactive executive dashboard for exploring, diagnosing, and exporting results.

### 🔹 Components
- **KPIs**  
  - #Documents, #Topics  
  - Dominant topic & keywords  
  - Sentiment % (positive/negative)  

- **Word Cloud**  
  - Per-topic or global keywords  

- **Topic Distribution**  
  - Pie/bar charts of mean topic weights  

- **Sentiment Overview**  
  - Pie chart of overall sentiment  
  - Sentiment per topic (dominant-topic aggregation)  

- **Topic-Level Summaries**  
  - Human-labeled summaries with keywords  
  - Editable labels inline  

- **Insights & Recommendations**  
  - Auto-generated rules:  
    - Topics with ≥40% NEGATIVE flagged ⚠️  
    - High POSITIVE topics → amplify wins  

### 📘 Dashboard UI
![alt text](<Screenshot 2025-10-14 224029.png>)

**Word Cloud**
![alt text](<Screenshot 2025-10-14 223958.png>)

Example:  
⚠️ Health shows 80% negative sentiment — prioritize investigation.  
🧭 Use topic summaries to pre-fill your executive brief.  

- **Executive Report Export**  
  - Styled HTML report with KPIs, distributions, word cloud, summaries, insights  

### 🔹 Implementation
```python
from src.dashboard import page_dashboard
page_dashboard()  # Called from app.py
```

### 🔹 Example Insights
- ⚠️ Health shows 80% negative sentiment → escalate investigation  
- ⚠️ Support Tickets shows 55% negative sentiment → monitor closely  
- 🧭 Use topic summaries to pre-fill your executive brief  

---

## 📊 End-to-End Pipeline (Weeks 1–6)

| Step | Module | Description |
|------|--------|-------------|
| Data Input | inputHandler_fn.py | Upload/paste text input |
| Preprocessing | preprocessing.py | Clean, tokenize, normalize |
| Topic Modeling | topic_modeling.py | Discover latent topics |
| Labeling | labeling.py | Assign interpretable labels |
| Sentiment | sentiment.py | Polarity detection |
| Summarization | summarization.py | Executive & topic-level summaries |
| Dashboard | dashboard.py | Interactive KPIs, insights, reports |
| Frontend | app.py | Streamlit orchestration |

---

## 🧠 Example Final Outputs

**Executive Summary**  
“Artificial intelligence is rapidly transforming industries through automation, improved diagnosis in medicine, and efficiency in manufacturing. Risks include cyberattacks and ethical misuse.”  

**Topic Summaries**  
- Technology: ai, model, machine → AI models improve accuracy in predictions.  
- Health: patient, diagnosis, treatment → AI accelerates diagnosis and enhances planning.  

**Dashboard Insights**  
- ⚠️ Health — 80% negative sentiment  
- 🧭 Topic summaries recommended for executive briefing  


## - By RAUNAK 

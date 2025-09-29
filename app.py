# app.py (patched, drop-in replacement)
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import uuid
import re
import time
import json
import datetime

# Keep only imports that are safe at module import time.
from src.inputHandler_fn import read_file
from src.preprocessing import clean_text, summarize_text_stats

st.set_page_config(page_title="AI Text Analysis", layout="wide")

# Minimal safe CSS
st.markdown("""
<style>
.stButton>button {
  background:#4CAF50; color:white; border:none; border-radius:8px;
  padding:10px 18px; font-weight:700; cursor:pointer;
}
.stButton>button:hover { filter: brightness(1.05); }
</style>
""", unsafe_allow_html=True)

# ---------- MODERN MINIMAL NAVBAR  ----------

# pages (labels only)
PAGES = ["Home", "Data Input", "Preprocessing", "Topic Modeling", "Sentiment", "Summarization", "Dashboard", "About"]
PAGE_INDEX = {n: i for i, n in enumerate(PAGES)}

# state
st.session_state.setdefault("page", "Home")
st.session_state.setdefault("_nav_instance", 0)  # bump to recreate widget after programmatic nav

def _rerun_now():
    try: st.rerun()
    except Exception:
        try: st.experimental_rerun()
        except Exception: st.stop()

def nav_to(target: str):
    """Programmatic nav from buttons: rebuild navbar so default tab is honored."""
    st.session_state["page"] = target
    st.session_state["_nav_instance"] += 1
    _rerun_now()

# recreate the widget when we programmatically navigate
NAV_WIDGET_KEY = f"navbar_tabs_{st.session_state['_nav_instance']}"
default_idx = PAGE_INDEX.get(st.session_state["page"], 0)

st.markdown("""
<style>
.navbar-wrap { position: sticky; top: 0; z-index: 1000; background: #0E1117; }
.navbar { padding: 10px 8px 0 8px; border-bottom: 1px solid rgba(255,255,255,0.10); }
.brand { display:flex; align-items:center; gap:10px; font-weight:800; color:#e6edf3; letter-spacing:.2px; }
.brand-name {font-size: 20px; font-weight: 800; color: #e6edf3; letter-spacing: .3px; padding-left: 6px;}
div[role="radiogroup"] { display:flex; gap:6px; flex-wrap:wrap; border:none!important; box-shadow:none!important; justify-content:flex-end; }
div[role="radiogroup"] input[type="radio"] { display:none!important; }
div[role="radiogroup"] > label > div:first-child { display:none!important; } /* hide radio dot */
div[role="radiogroup"] > label {
  border:none; border-radius:0; padding:10px 14px; margin:0; 
  color:#e6edf3; font-weight:600; font-size:15px; cursor:pointer; opacity:.85; background:transparent;
  transition:opacity .15s ease;
}
div[role="radiogroup"] > label:hover { opacity:1; }
div[role="radiogroup"] > label[data-checked="true"] { opacity:1; color:#d8f3dc; position:relative; }
div[role="radiogroup"] > label[data-checked="true"]::after {
  content:""; position:absolute; left:0; right:0; bottom:-1px; height:3px; background:#4CAF50; border-radius:2px;
}
@media (prefers-color-scheme: light){
  .navbar-wrap{background:#fff;} .navbar{border-bottom-color:rgba(0,0,0,.08);}
  .brand-name { color: #fffff; }
  div[role="radiogroup"] > label[data-checked="true"]{color:#2e7d32;}
  div[role="radiogroup"] > label[data-checked="true"]::after{background:#2e7d32;}
}
</style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='navbar-wrap'><div class='navbar'>", unsafe_allow_html=True)
    left, right = st.columns([1, 4], gap="small")
    with left:
        st.markdown("<div class='brand-name'>AI Text Analysis</div>", unsafe_allow_html=True)
    with right:
        selected = st.radio(
            "Navigation",
            options=PAGES,                    # your list: ["Home", "Data Input", ...]
            index=PAGE_INDEX.get(st.session_state["page"], 0),
            horizontal=True,
            key=NAV_WIDGET_KEY,               # you already compute this with _nav_instance
            label_visibility="collapsed",
        )
    st.markdown("</div></div>", unsafe_allow_html=True)

# sync click -> page
if selected != st.session_state.get("page"):
    st.session_state["page"] = selected

# expose for your pages
NAV_TO = nav_to
# ---------- END NAVBAR ----------



# Debug snapshot
with st.expander("DEBUG session_state snapshot (temporary)", expanded=False):
    snapshot_keys = ["page", "page_requested", "topic_summaries", "topic_labels"]
    snapshot = {k: st.session_state.get(k) for k in snapshot_keys}
    st.write(f"tick: {datetime.datetime.now().isoformat()}")
    st.json(snapshot)

# ---------- Page implementations (lazy imports inside pages) ----------

# --- Home Page ---
def page_home():
    st.markdown("<div style='padding-top:40px; padding-bottom:10px;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#4CAF50; font-size:44px; margin:0;'>Turn Raw Text into Insights</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#b0bec5; font-size:18px; max-width:820px; margin:12px auto 0; line-height:1.5;'>Upload TXT / DOCX / CSV or paste text. Clean automatically, then extract key topics & themes.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 Get Started", key="btn_home_start", use_container_width=True):
            nav_to("Data Input")
    cols = st.columns(4)
    labels = [
        ("📄 Data Input", "Upload TXT / DOCX / CSV, or paste your own text."),
        ("🧹 Preprocessing", "Stopwords, lemmatization, normalization — fast."),
        ("📊 Topic Modeling", "Uncover hidden themes with NMF / LDA."),
        ("💬 Insights", "Summaries & sentiment (coming soon).")
    ]
    for col, (title, desc) in zip(cols, labels):
        with col:
            st.markdown(f"### {title}")
            st.write(desc)


# --- Data Input (CSV, DOCX or TXT) ---
def page_data_input():
    st.title("📄 Step 1: Data Input")
    st.caption("Upload a file or paste text. We’ll validate and show an instant preview before preprocessing.")
    col_main, col_side = st.columns([1.8, 1])
    with col_main:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>Choose your input <span class='pill'>TXT / CSV / DOCX / Paste</span></h3>", unsafe_allow_html=True)
        tabs = st.tabs(["📤 Upload file", "📝 Paste text"])
        uploaded = None
        pasted_text = ""
        with tabs[0]:
            uploaded = st.file_uploader(" ", type=["txt", "csv", "docx"], key="file_up", label_visibility="collapsed")
        with tabs[1]:
            pasted_text = st.text_area("Paste your text here", height=200, key="paste_text")
        st.markdown("</div>", unsafe_allow_html=True)
        preview_text = ""
        df_preview = None
        source_type = None
        if pasted_text and pasted_text.strip():
            preview_text = pasted_text.strip()
            source_type = "pasted"
        elif uploaded is not None:
            try:
                with st.spinner("Reading file…"):
                    data = read_file(uploaded)
                preview_text = data["text"] or ""
                df_preview = data.get("df_preview")
                source_type = data["meta"]["source_type"]
            except Exception as e:
                st.error(f"Failed to read file: {e}")
        if preview_text or df_preview is not None:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3>Quick Preview</h3>", unsafe_allow_html=True)
            if df_preview is not None:
                with st.expander("🔎 CSV rows (sample)"):
                    st.dataframe(df_preview, use_container_width=True)
            if preview_text:
                st.markdown("<div class='preview'>", unsafe_allow_html=True)
                st.text(preview_text[:800] + ("..." if len(preview_text) > 800 else ""))
                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='btn-primary' style='max-width:320px; margin:18px auto 0;'>", unsafe_allow_html=True)
        if st.button("🚀 Go Ahead", key="btn_data_goahead", use_container_width=True):
            if preview_text:
                st.session_state["raw_text"] = preview_text
                st.session_state["df_preview"] = df_preview
                st.session_state["source_type"] = source_type or "pasted"
                nav_to("Preprocessing")
            else:
                st.warning("Please upload a file or paste some text first.")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_side:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>Tips & Requirements</h3>", unsafe_allow_html=True)
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <ul class='muted'>
              <li>CSV: include at least one text-like column (e.g., <i>text, content, body</i>).</li>
              <li>Large CSVs: we preview ~800 rows to keep things fast.</li>
              <li>DOCX support requires <code>python-docx</code> (already in requirements).</li>
            </ul>
            """,
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)


# --- Preprocessing ---
def page_preprocessing():
    st.title("🧹 Step 2: Preprocessing")
    if "raw_text" not in st.session_state or not st.session_state["raw_text"]:
        st.warning("⚠️ Please upload/paste text first in Data Input.")
        return
    raw_text = st.session_state["raw_text"]
    df_preview = st.session_state.get("df_preview")
    if df_preview is not None:
        with st.expander("🔎 CSV Preview (first rows)"):
            st.dataframe(df_preview, use_container_width=True)
    st.subheader("📌 Original Text Preview")
    st.text_area("Original", raw_text[:1000] + ("..." if len(raw_text) > 1000 else ""), height=220)
    MAX_CHARS = 120_000
    text_for_cleaning = raw_text[:MAX_CHARS]
    if len(raw_text) > MAX_CHARS:
        st.info(f"Processing only the first {MAX_CHARS:,} characters for preview.")
    with st.spinner("Cleaning text..."):
        cleaned_text = clean_text(text_for_cleaning)
    st.subheader("🧽 Cleaned Text Preview")
    st.text_area("Cleaned", cleaned_text[:1000] + ("..." if len(cleaned_text) > 1000 else ""), height=220)
    stats = summarize_text_stats(cleaned_text)
    st.subheader("📊 Summary")
    st.dataframe(pd.DataFrame([stats]), use_container_width=True)
    st.session_state["cleaned_text"] = cleaned_text
    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        if st.button("➡️ Next: Topic Modeling", key="btn_next_topic_modeling", use_container_width=True):
            nav_to("Topic Modeling")

def page_topics():
    # lazy imports used by this page
    try:
        from src.topic_modeling import (
            make_docs_from_text, vectorize_tfidf, vectorize_count,
            fit_nmf, fit_lda, top_terms_per_topic, doc_topic_distribution, save_artifacts,
            compute_coherence_score, compute_model_perplexity, topic_diversity, topic_silhouette_score
        )
    except Exception as e:
        st.error(f"Topic-modeling helpers unavailable: {e}")
        return

    st.title("📊 Step 3: Topic Modeling")
    if "raw_text" not in st.session_state or not st.session_state["raw_text"]:
        st.warning("Please go to **Data Input** and add some text first.")
        return
    cleaned_text = st.session_state.get("cleaned_text", None)
    if not cleaned_text:
        with st.spinner("Cleaning text (quick pass)…"):
            cleaned_text = clean_text(st.session_state["raw_text"][:200_000])
    with st.expander("⚙️ Modeling Settings", expanded=True):
        algo = st.selectbox("Algorithm", ["NMF (TF-IDF)", "LDA (Count)"])
        n_topics = st.slider("Number of topics", min_value=3, max_value=20, value=8, step=1)
        max_features = st.slider("Max vocabulary size", min_value=1000, max_value=20000, value=5000, step=500)
        col_ng1, col_ng2 = st.columns(2)
        with col_ng1:
            min_n = st.slider("Min n-gram", 1, 3, 1, step=1)
        with col_ng2:
            max_n = st.slider("Max n-gram", 1, 3, 2, step=1)
        if max_n < min_n:
            st.error("Max n-gram must be ≥ Min n-gram.")
            return
        ngram_range = (min_n, max_n)
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            min_df = st.number_input("min_df (min docs containing term)", min_value=1, max_value=100, value=2, step=1)
        with col_f2:
            max_df = st.slider("max_df (ignore if in >X% docs)", 0.50, 1.00, 0.95, step=0.01)
        cta1, cta2 = st.columns(2)
        with cta1:
            train_btn = st.button("🚀 Train model", key="btn_train_model", use_container_width=True)
        with cta2:
            save_btn = st.button("💾 Save artifacts", key="btn_save_artifacts", use_container_width=True, disabled=("tm_model" not in st.session_state))
    words_per_doc = 200
    try:
        docs = make_docs_from_text(cleaned_text, words_per_doc=words_per_doc)
    except Exception:
        docs = []
    def _chunk_by_words(text: str, chunk_size: int = 200, overlap: int = 20):
        words = text.split()
        if not words:
            return []
        out = []
        step = chunk_size - overlap if (chunk_size - overlap) > 0 else chunk_size
        for i in range(0, len(words), step):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                out.append(chunk)
            if i + chunk_size >= len(words):
                break
        return out
    if len(docs) <= 1:
        docs_fallback = _chunk_by_words(cleaned_text, chunk_size=words_per_doc, overlap=20)
        if len(docs_fallback) > 1:
            docs = docs_fallback
    if len(docs) < 5:
        st.error("Not enough text to form multiple documents. Add more text or use a larger CSV.")
        return
    if train_btn:
        with st.spinner("Vectorizing & training…"):
            if algo.startswith("NMF"):
                V = vectorize_tfidf(docs, max_features=max_features, ngram_range=ngram_range, min_df=min_df, max_df=max_df)
                model = fit_nmf(V.X, n_topics=n_topics)
                algo_name = "NMF"
            else:
                V = vectorize_count(docs, max_features=max_features, ngram_range=ngram_range, min_df=min_df, max_df=max_df)
                model = fit_lda(V.X, n_topics=n_topics)
                algo_name = "LDA"
            st.session_state["tm_algo"] = algo_name
            st.session_state["tm_vectorizer"] = V.vectorizer
            st.session_state["tm_model"] = model
            st.session_state["tm_feature_names"] = V.feature_names
            st.session_state["tm_docs"] = docs
            st.session_state["tm_X"] = V.X
        st.success(f"Trained {algo_name} with {n_topics} topics ✔")
        
    # --- Diagnostics (Coherence, Perplexity) ---
    if "tm_model" in st.session_state:
        model = st.session_state["tm_model"]
        feat_names = st.session_state.get("tm_feature_names")
        X_vec = st.session_state.get("tm_X")
        docs_for_eval = st.session_state.get("tm_docs", [])
    
        with st.expander("🛠️ Model diagnostics (coherence, perplexity, diversity, silhouette)", expanded=False):
            if "tm_model" not in st.session_state:
                st.info("Train a model first to enable diagnostics.")
            else:
                model_saved = st.session_state["tm_model"]
                feat_names = st.session_state.get("tm_feature_names")
                docs_for_eval = st.session_state.get("tm_docs", [])
                X_vec = st.session_state.get("tm_X")

                if not docs_for_eval or not feat_names:
                    st.warning("Docs or feature names missing.")
                else:
                    total_docs = len(docs_for_eval)
                    SAMPLE_DOCS = st.slider("Docs to sample", 50, min(1000, total_docs), min(200, total_docs), 50, key="diag_sample_docs")
                    TOPN = st.slider("Top N words per topic (for coherence)", 5, 20, 10, key="diag_topn")
                    compute_sil = st.checkbox("Compute silhouette (slower)", value=False, key="diag_sil")

                    sampled_docs = docs_for_eval[:SAMPLE_DOCS]

                    @st.cache_data(show_spinner=False, ttl=3600)
                    def coherence_cv_cached(sd, topn, feat_key):
                        from src.topic_modeling import compute_coherence_score
                        return compute_coherence_score(model_saved, sd, feat_names, topn=topn, coherence="c_v")

                    # ---- Run c_v (gensim) ----
                    try:
                        coh_cv = coherence_cv_cached(sampled_docs, TOPN, "|".join(feat_names[:500]))
                    except Exception as e:
                        coh_cv = None
                        st.warning(f"c_v coherence failed: {e}")

                    # ---- Optional: u_mass for comparison ----
                    umass = None
                    if st.button("Compute u_mass (compare)"):
                        try:
                            from src.topic_modeling import compute_coherence_score
                            umass = compute_coherence_score(model_saved, sampled_docs, feat_names, topn=TOPN, coherence="u_mass")
                        except Exception as e:
                            st.warning(f"u_mass failed: {e}")

                    # ---- Perplexity, Diversity, Silhouette ----
                    try:
                        from src.topic_modeling import compute_model_perplexity, topic_diversity
                        perp = compute_model_perplexity(model_saved, X_vec)
                        div  = topic_diversity(model_saved, feat_names, topn=TOPN)
                    except Exception:
                        perp, div = None, None

                    sil = None
                    if compute_sil:
                        try:
                            from src.topic_modeling import topic_silhouette_score
                            SIL_DOCS = min(300, SAMPLE_DOCS)
                            sil = topic_silhouette_score(sampled_docs[:SIL_DOCS], model_saved, X_vec[:SIL_DOCS] if hasattr(X_vec,'__getitem__') else X_vec, feat_names, topn_docs=SIL_DOCS)
                        except Exception as e:
                            st.warning(f"Silhouette failed: {e}")

                    # KPIs
                    k1, k2, k3, k4 = st.columns(4)
                    with k1: st.metric("Coherence (c_v, 0–1 ↑)", f"{coh_cv:.4f}" if coh_cv is not None else "—")
                    with k2: st.metric("Perplexity (↓)", f"{perp:.2f}" if perp is not None else "—")
                    with k3: st.metric("Topic diversity (↑)", f"{div:.3f}" if div is not None else "—")
                    with k4: st.metric("Silhouette (↑)", f"{sil:.4f}" if sil not in (None, float('nan')) else "—")

                    if umass is not None:
                        st.info(f"u_mass (more negative is better): **{umass:.3f}**")

                    # Persist to session for Dashboard/Report
                    if coh_cv is not None:
                        st.session_state["_diag_coherence"] = float(coh_cv)
                    if div is not None:
                        st.session_state["_diag_diversity"] = float(div)

                    # Optional: clear cache button
                    if st.button("🧹 Clear cached coherence"):
                        try:
                            st.cache_data.clear()
                            st.success("Cache cleared. Re-run diagnostics.")
                        except Exception:
                            pass


    # Diagnostics and show results (same logic as before)
    if "tm_model" in st.session_state:
        model = st.session_state["tm_model"]
        feature_names = st.session_state.get("tm_feature_names")
        X = st.session_state.get("tm_X")
        st.subheader("🧩 Discovered Topics")
        topics = top_terms_per_topic(model, feature_names, topn=10)
        for k, terms in enumerate(topics, start=1):
            st.markdown(f"**Topic {k}:** " + ", ".join(terms))
        st.subheader("📈 Topic distribution (first 6 docs)")
        theta = doc_topic_distribution(model, X)
        n_show = min(6, theta.shape[0])
        df_theta = pd.DataFrame(theta[:n_show], columns=[f"Topic {i+1}" for i in range(theta.shape[1])])
        st.dataframe(df_theta.style.format("{:.2f}"), use_container_width=True)
        with st.expander("💾 Save (model + vectorizer)"):
            prefix = st.text_input("Path prefix", value="models/topic_model")
            if st.button("Save", use_container_width=True, key="btn_save_model"):
                try:
                    save_artifacts(prefix, model, st.session_state["tm_vectorizer"])
                    st.success(f"Saved: {prefix}_model.joblib and {prefix}_vectorizer.joblib")
                except Exception as e:
                    st.error(f"Failed to save: {e}")
    else:
        st.info("Adjust settings and click **Train model** to see topics.")
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        if st.button("➡️ Next: Sentiment Analysis", key="btn_next_sentiment", use_container_width=True):
            nav_to("Sentiment")


# --- Sentiments ---
def page_sentiment():
    # lazy imports
    try:
        from src.topic_modeling import make_docs_from_text, doc_topic_distribution
        from src.sentiment import analyze_vader, analyze_hf, distribution, overall_distribution_pct
    except Exception as e:
        st.error(f"Required sentiment/topic helpers missing: {e}")
        return

    st.title("💬 Sentiment Analysis")
    if "raw_text" not in st.session_state or not st.session_state["raw_text"]:
        st.warning("Please add text in **Data Input** first.")
        return
    cleaned_text = st.session_state.get("cleaned_text")
    if not cleaned_text:
        with st.spinner("Cleaning text (quick pass)…"):
            cleaned_text = clean_text(st.session_state["raw_text"][:200_000])
    use_csv_rows_for_sent = False
    if "df_preview" in st.session_state and st.session_state["df_preview"] is not None:
        use_csv_rows_for_sent = st.checkbox("Use uploaded CSV rows as documents for sentiment (recommended for news datasets)", value=False, key="chk_use_csv_rows_sent")
    if use_csv_rows_for_sent:
        df = st.session_state["df_preview"]
        text_col = st.selectbox("Select text column for sentiment", df.columns.tolist(), index=0, key="sel_sent_text_col")
        docs = [str(x) for x in df[text_col].dropna().astype(str).tolist()]
    else:
        try:
            docs = make_docs_from_text(cleaned_text, words_per_doc=200)
        except Exception:
            docs = []
        if len(docs) <= 1:
            def _chunk_by_words(text: str, chunk_size: int = 200, overlap: int = 40):
                words = text.split()
                if not words:
                    return []
                out = []
                step = chunk_size - overlap if (chunk_size - overlap) > 0 else chunk_size
                for i in range(0, len(words), step):
                    chunk = " ".join(words[i:i + chunk_size])
                    if chunk.strip():
                        out.append(chunk)
                    if i + chunk_size >= len(words):
                        break
                return out
            docs_fallback = _chunk_by_words(cleaned_text, chunk_size=200, overlap=40)
            if len(docs_fallback) > 1:
                docs = docs_fallback
    st.caption(f"Documents used for sentiment: {len(docs)}")
    if len(docs) < 3:
        st.error("Not enough text after cleaning/chunking. Please provide more data, or upload a CSV and enable 'Use CSV rows as documents'.")
        return
    with st.expander("⚙️ Sentiment Settings", expanded=True):
        analyzer = st.selectbox(
            "Choose sentiment analyzer",
            ["VADER (fast)", "Hugging Face (accurate)"],
            key="sentiment_analyzer"
        )
        batch_size = st.slider("Batch size (HF only)", 4, 32, 16, 4, key="sli_sent_batch")
        aggregation = st.selectbox(
            "Topic aggregation (when topic model present)",
            ["Dominant topic (argmax)", "Weighted by topic prob"],
            index=0,
            key="sel_sent_agg"
        )
        show_pct_only = st.checkbox("Show percentages in charts (recommended)", value=True, key="chk_sent_pct")
        run_btn = st.button("🔎 Run Sentiment", key="btn_run_sentiment", use_container_width=True)
    if run_btn:
        with st.spinner("Analyzing sentiment…"):
            if analyzer.startswith("VADER"):
                results = analyze_vader(docs)
            else:
                results = analyze_hf(docs, batch_size=batch_size)
        st.session_state["sentiment_results"] = results
        labels = [r["label"] for r in results]
        counts = distribution(labels)
        pct = overall_distribution_pct(labels)
        st.subheader("📊 Overall Sentiment Distribution (dataset level)")
        overall_df = pd.DataFrame([
            {"label": "NEGATIVE", "count": counts.get("NEGATIVE", 0), "pct": pct.get("NEGATIVE", 0.0)},
            {"label": "NEUTRAL",  "count": counts.get("NEUTRAL",  0), "pct": pct.get("NEUTRAL",  0.0)},
            {"label": "POSITIVE", "count": counts.get("POSITIVE", 0), "pct": pct.get("POSITIVE", 0.0)}
        ])
        overall_df["pct_display"] = overall_df["pct"].apply(lambda v: f"{v:.1f}%")
        st.dataframe(overall_df[["label", "count", "pct_display"]].rename(columns={"pct_display":"pct"}), use_container_width=True)
        try:
            import plotly.express as px
            fig_pie = px.pie(overall_df, names="label", values="pct", hole=0.35, title="Overall sentiment (%)")
            st.plotly_chart(fig_pie, use_container_width=True)
        except Exception:
            st.bar_chart(pd.Series({r["label"]: r["pct"] for _, r in overall_df.iterrows()}))
        if "tm_model" in st.session_state and "tm_X" in st.session_state:
            st.subheader("🧩 Sentiment by Topic")
            try:
                theta = doc_topic_distribution(st.session_state["tm_model"], st.session_state["tm_X"])
            except Exception as e:
                st.error(f"Failed to compute doc-topic distribution: {e}")
                return
            n_theta_rows = theta.shape[0]
            n_labels = len(labels)
            n_common = min(n_theta_rows, n_labels)
            if n_common == 0:
                st.error("No overlapping documents between topic model and the sentiment inputs.")
                return
            theta_aligned = theta[:n_common, :]
            labels_aligned = labels[:n_common]
            n_topics = theta_aligned.shape[1]
            if aggregation.startswith("Dominant"):
                dom = np.argmax(theta_aligned, axis=1)
                rows = []
                for t in range(n_topics):
                    idxs = np.where(dom == t)[0]
                    topic_labels = [labels_aligned[i] for i in idxs]
                    neg = topic_labels.count("NEGATIVE")
                    neu = topic_labels.count("NEUTRAL")
                    pos = topic_labels.count("POSITIVE")
                    total_docs = len(idxs)
                    neg_pct = (neg * 100.0 / total_docs) if total_docs > 0 else 0.0
                    neu_pct = (neu * 100.0 / total_docs) if total_docs > 0 else 0.0
                    pos_pct = (pos * 100.0 / total_docs) if total_docs > 0 else 0.0
                    rows.append({
                        "topic": t,
                        "NEGATIVE": neg,
                        "NEUTRAL": neu,
                        "POSITIVE": pos,
                        "neg_pct": neg_pct,
                        "neu_pct": neu_pct,
                        "pos_pct": pos_pct,
                        "total_docs": total_docs
                    })
                s_df = pd.DataFrame(rows)
                s_df_display = s_df.copy()
                s_df_display[["neg_pct", "neu_pct", "pos_pct"]] = s_df_display[["neg_pct","neu_pct","pos_pct"]].round(1)
                st.dataframe(s_df_display.rename(columns={
                    "topic": "Topic",
                    "NEGATIVE": "Negative (count)",
                    "NEUTRAL": "Neutral (count)",
                    "POSITIVE": "Positive (count)",
                    "neg_pct": "Negative (%)",
                    "neu_pct": "Neutral (%)",
                    "pos_pct": "Positive (%)",
                    "total_docs": "Total docs"
                }), use_container_width=True)
                plot_df = s_df[["topic", "pos_pct", "neu_pct", "neg_pct"]].melt(id_vars=["topic"], value_vars=["pos_pct","neu_pct","neg_pct"], var_name="sentiment", value_name="pct")
                plot_df["sentiment"] = plot_df["sentiment"].map({"pos_pct":"Positive","neu_pct":"Neutral","neg_pct":"Negative"})
                plot_df["pct"] = plot_df["pct"].astype(float)
                try:
                    fig = px.bar(plot_df, x="topic", y="pct", color="sentiment", barmode="group", title="Sentiment % by Topic (argmax)", text="pct")
                    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                    fig.update_layout(xaxis_title="Topic (0-indexed)", yaxis_title="Percent (%)")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    st.bar_chart(plot_df.pivot(index="topic", columns="sentiment", values="pct").fillna(0))
            else:
                
                pass
        else:
            st.info("No trained topic model found in session. Train a topic model (Topic Modeling page) to see sentiment-by-topic breakdown.")
        st.success("Sentiment analysis complete ✅")

    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        if st.button("➡️ Next: Summarization", key="btn_next_summarization", use_container_width=True):
            nav_to("Summarization")


# --- Summarization ---
def page_summarization():
    # lazy imports
    try:
        from src.summarization import (
            summarize_with_mmr, summarize_with_embeddings_mmr,
            summarize_abstractive_polish, summarize
        )
        from src.topic_modeling import doc_topic_distribution, top_terms_per_topic
    except Exception as e:
        st.error(f"Summarization helpers unavailable: {e}")
        return

    st.title("🧾 Summarization")
    has_csv = "df_preview" in st.session_state and st.session_state["df_preview"] is not None
    has_text = bool(st.session_state.get("cleaned_text") or st.session_state.get("raw_text"))
    if not has_csv and not has_text:
        st.warning("Please upload/paste text on the Data Input page first.")
        return

    col_a, col_b, col_c = st.columns([1.4, 1, 1])
    with col_a:
        mode = st.selectbox(
            "Choose summarization mode",
            ["Abstractive", "Extractive"],
            key="summarization_mode"
        )
    with col_b:
        use_embeddings = st.checkbox("Use embedding-MMR (optional)", value=False, key="chk_summ_emb")
    with col_c:
        max_sentences = st.number_input("Extractive: max sentences", min_value=1, max_value=12, value=4, step=1, key="num_summ_max_sents")

    if mode.startswith("Abstractive"):
        ui_max_words = st.slider("Abstractive: max words", 50, 400, 120, 10, key="sli_abs_max")
        ui_min_words = st.slider("Abstractive: min words", 20, 200, 40, 5, key="sli_abs_min")
    else:
        ui_max_words, ui_min_words = 120, 40

    if has_csv:
        df = st.session_state["df_preview"]
        st.info(f"CSV detected — {len(df)} rows")
        text_col = st.selectbox("Select text column to summarize", df.columns.tolist(), index=0, key="sel_summ_textcol")
        n_rows = int(min(len(df), st.number_input("Rows to process (first N)", min_value=1, max_value=len(df), value=min(200, len(df)), step=1, key="num_summ_rows")))
        run_csv = st.button("Run summarization (CSV rows)", key="btn_run_summ_csv")
        if run_csv:
            progress = st.progress(0)
            results = []
            failed = 0
            for i in range(n_rows):
                raw = str(df[text_col].iloc[i] or "")
                try:
                    if mode.startswith("Abstractive"):
                        try:
                            s = summarize_abstractive_polish(raw, max_words=ui_max_words, min_words=ui_min_words)
                        except Exception:
                            s = summarize_with_mmr(raw, k=max_sentences)
                    else:
                        if use_embeddings:
                            try:
                                s = summarize_with_embeddings_mmr(raw, k=max_sentences)
                            except Exception:
                                s = summarize_with_mmr(raw, k=max_sentences)
                        else:
                            s = summarize_with_mmr(raw, k=max_sentences)
                    results.append(s)
                except Exception as e:
                    results.append(f"[Error summarizing row {i}: {e}]")
                    failed += 1
                if i % 5 == 0 or i == n_rows - 1:
                    progress.progress(min(100, int(((i + 1) / n_rows) * 100)))
            out_df = df.head(n_rows).copy()
            out_df["summary"] = results
            st.subheader("Preview summaries (first rows)")
            st.dataframe(out_df[[text_col, "summary"]].head(10), use_container_width=True)
            csv_bytes = out_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download summarized CSV", csv_bytes, file_name=f"summaries_{uuid.uuid4().hex[:8]}.csv", mime="text/csv")
            st.success(f"Done — processed {n_rows} rows ({failed} failures).")
    else:
        text = st.session_state.get("cleaned_text") or st.session_state.get("raw_text") or ""
        st.caption(f"Document length ≈ {len(text.split()):,} words")
        run_doc = st.button("Run summarization (document)", key="btn_run_summ_doc")
        if run_doc:
            with st.spinner("Generating summary..."):
                try:
                    if mode.startswith("Abstractive"):
                        summary = summarize_abstractive_polish(text, max_words=ui_max_words, min_words=ui_min_words)
                    else:
                        if use_embeddings:
                            try:
                                summary = summarize_with_embeddings_mmr(text, k=max_sentences)
                            except Exception:
                                summary = summarize_with_mmr(text, k=max_sentences)
                        else:
                            summary = summarize_with_mmr(text, k=max_sentences)
                except Exception as e:
                    st.error(f"Summarization failed: {e}")
                    summary = ""
            if summary:
                st.subheader("✅ Summary")
                st.write(summary)
                st.caption(f"Source words: {len(text.split()):,} → summary words: {len(summary.split()):,}")
            else:
                st.warning("No summary produced.")
    st.markdown("---")
    st.header("🧠 Topic-level summarization (group documents by topic)")
    if "tm_model" not in st.session_state or "tm_X" not in st.session_state or "tm_docs" not in st.session_state:
        st.info("Train a topic model on the Topic Modeling page to enable topic-level summaries.")
        return
    c1, c2, c3 = st.columns([0.6, 1, 1])
    with c1:
        top_k_docs = st.number_input("Top docs per topic", min_value=5, max_value=500, value=50, step=5, key="num_topk_docs")
    with c2:
        per_topic_sent = st.slider("Per-topic max sentences", 1, 6, 3, key="sli_topic_max_sents")
    with c3:
        agg = st.selectbox("Aggregation", ["Weighted (top-K by prob)", "Dominant topic (argmax)"], index=0, key="sel_topic_agg")
    run_topics = st.button("Run topic-level summaries", key="btn_run_topic_summaries")
    if run_topics:
        with st.spinner("Generating topic-level summaries..."):
            docs = st.session_state.get("tm_docs", [])
            try:
                theta = doc_topic_distribution(st.session_state["tm_model"], st.session_state["tm_X"])
            except Exception as e:
                st.error(f"doc-topic distribution failed: {e}")
                return
            n_theta = theta.shape[0]
            n_docs = len(docs)
            n_common = min(n_theta, n_docs)
            if n_common == 0:
                st.error("No overlapping documents between topic model and stored docs.")
                return
            if n_common != n_docs or n_common != n_theta:
                docs = docs[:n_common]
                theta = theta[:n_common, :]
            n_topics = theta.shape[1]
            feat = st.session_state.get("tm_feature_names", None)
            try:
                kws_all = top_terms_per_topic(st.session_state["tm_model"], feat, topn=8) if feat is not None else [[""]] * n_topics
            except Exception:
                kws_all = [[""]] * n_topics
            rows = []
            seen_norm = set()
            for t in range(n_topics):
                if agg.startswith("Dominant"):
                    dom = np.argmax(theta, axis=1)
                    idxs = np.where(dom == t)[0].tolist()
                else:
                    idxs = np.argsort(theta[:, t])[::-1][:int(top_k_docs)].tolist()
                rep_docs = []
                seen_local = set()
                for i in idxs:
                    if i < len(docs):
                        d = docs[i]
                        if not isinstance(d, str) or not d.strip():
                            continue
                        key = d.strip()[:300]
                        if key in seen_local:
                            continue
                        seen_local.add(key)
                        rep_docs.append(d)
                    if len(rep_docs) >= top_k_docs:
                        break
                combined = " ".join(rep_docs)
                if not combined.strip():
                    summary = ""
                else:
                    try:
                        if mode.startswith("Abstractive"):
                            summary = summarize_abstractive_polish(combined, max_words=ui_max_words, min_words=ui_min_words)
                        else:
                            if use_embeddings:
                                try:
                                    summary = summarize_with_embeddings_mmr(combined, k=per_topic_sent)
                                except Exception:
                                    summary = summarize_with_mmr(combined, k=per_topic_sent)
                            else:
                                summary = summarize_with_mmr(combined, k=per_topic_sent)
                    except Exception:
                        try:
                            summary = summarize_with_mmr(combined, k=per_topic_sent)
                        except Exception:
                            summary = ""
                norm = re.sub(r'[^a-z0-9 ]', '', (summary or "").lower())[:200].strip()
                if norm and norm in seen_norm:
                    continue
                if norm:
                    seen_norm.add(norm)
                kws = kws_all[t] if t < len(kws_all) else []
                suggested = "Other"
                try:
                    import src.labeling as labeling_mod
                    try:
                        suggested = labeling_mod.keyword_labeler(kws)
                    except Exception:
                        suggested = "Other"
                except Exception:
                    suggested = "Other"
                rows.append({
                    "topic_idx": int(t),
                    "topic_display": f"Topic {t+1}",
                    "label_suggested": suggested,
                    "label": suggested,
                    "keywords": ", ".join(kws),
                    "n_docs_used": len(rep_docs),
                    "summary": summary or ""
                })
            if not rows:
                st.warning("No topic summaries produced. Try different top-K or aggregation.")
            else:
                st.session_state["topic_summaries"] = rows
                st.session_state.setdefault("topic_labels", {})
                st.success(f"Produced {len(rows)} topic summaries.")
                label_choices = ["Technology", "Business", "Politics", "Health", "Sports", "Entertainment", "Crime", "Other"]
                for r in rows:
                    tidx = r["topic_idx"]
                    disp = r["topic_display"]
                    current_label = st.session_state["topic_labels"].get(tidx, r["label_suggested"])
                    with st.expander(f"{disp} — {current_label} (docs used: {r['n_docs_used']})", expanded=False):
                        st.markdown(f"**Keywords:** {r['keywords']}")
                        st.markdown("**Summary (preview):**")
                        st.write((r["summary"] or "")[:420] + ("..." if (r["summary"] or "") and len(r["summary"])>420 else ""))
                        st.markdown("**Full summary:**")
                        st.write(r["summary"] or "_No summary produced_")
                        choices = [current_label] + [c for c in label_choices if c != current_label]
                        new_label = st.selectbox(f"Label for {disp}", choices, index=0, key=f"label_sel_{tidx}")
                        if st.button(f"Save label for {disp}", key=f"save_label_{tidx}"):
                            st.session_state["topic_labels"][tidx] = new_label
                            st.success(f"Saved label '{new_label}' for {disp}")
                df_out = pd.DataFrame(rows)
                df_out["label_final"] = df_out["topic_idx"].apply(lambda x: st.session_state["topic_labels"].get(int(x), next((r2["label_suggested"] for r2 in rows if r2["topic_idx"]==int(x)), "Other")))
                df_show = df_out[["topic_idx", "topic_display", "label_final", "keywords", "n_docs_used"]].rename(columns={"topic_idx":"topic", "topic_display":"topic_name", "label_final":"label"})
                st.subheader("Topic overview table")
                st.dataframe(df_show.sort_values("topic"), use_container_width=True)
                csv_bytes = df_out[["topic_idx","topic_display","label_final","keywords","n_docs_used","summary"]].to_csv(index=False).encode("utf-8")
                st.download_button("Download topic summaries (CSV)", csv_bytes, file_name=f"topic_summaries_{uuid.uuid4().hex[:8]}.csv", mime="text/csv")
                st.success("Topic summarization complete ✅")
                
    # Always show a Dashboard CTA if we already have topic summaries
    if st.session_state.get("topic_summaries"):
        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,1,1])
        with c2:
            if st.button("➡️ Open Dashboard", key="btn_open_dashboard_persistent", use_container_width=True):
                nav_to("Dashboard")

                        

def page_dashboard_local_fallback():
    # local fallback dashboard (kept simple)
    st.title("📊 Dashboard (local fallback)")
    st.write("This is the local dashboard fallback. Use Summarization -> Open Dashboard to produce topic summaries first.")
    topic_summaries = st.session_state.get("topic_summaries")
    if topic_summaries:
        for r in topic_summaries:
            st.markdown(f"**{r.get('topic_display','Topic')}**")
            st.write((r.get("summary") or "")[:400] + ("..." if r.get("summary") and len(r.get("summary"))>400 else ""))

def page_dashboard_router():
    # lazy import the modular dashboard page if available
    try:
        from src.dashboard import page_dashboard as modular_dashboard
        modular_dashboard()
    except Exception:
        page_dashboard_local_fallback()


# --- About Us ---
def page_about():
    st.title("ℹ️ About")
    st.write("""
    **AI Text Analysis** helps you convert raw text and CSVs into actionable insights.
    Built with Streamlit, pandas, spaCy and scikit-learn.
    """)


# ---------- Router ----------
current = st.session_state.get("page", "Home")
if current == "Home":
    page_home()
elif current == "Data Input":
    page_data_input()
elif current == "Preprocessing":
    page_preprocessing()
elif current == "Topic Modeling":
    page_topics()
elif current == "Sentiment":
    page_sentiment()
elif current == "Summarization":
    page_summarization()
elif current == "Dashboard":
    page_dashboard_router()
elif current == "About":
    page_about()


# ---------- Footer ----------
st.markdown('<hr style="opacity:.08;"><p style="text-align:center; color:#9fb1bd;">© 2025 • AI Text Analysis</p>', unsafe_allow_html=True)

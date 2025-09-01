import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

from src.inputHandler_fn import read_file
from src.preprocessing import clean_text, summarize_text_stats

from src.topic_modeling import (
    make_docs_from_text, vectorize_tfidf, vectorize_count,
    fit_nmf, fit_lda, top_terms_per_topic, doc_topic_distribution, save_artifacts
)

# ---------- Page Config ----------
st.set_page_config(page_title="AI Text Analysis", layout="wide")

# ---------- Theme / UI polish ----------
st.markdown("""
<style>
  html, body, [class*="css"] { font-family: "Segoe UI", -apple-system, Roboto, sans-serif; }
  .hero h1 { color:#4CAF50; font-size:44px; margin:0; text-align:center; }
  .hero p { color:#b0bec5; font-size:18px; text-align:center; max-width:820px; margin:12px auto 0; line-height:1.5; }
  .cards { max-width:1100px; margin:22px auto 0; display:grid; grid-template-columns: repeat(4, 1fr); gap:14px; }
  .card { background:#161A22; border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:16px; }
  .card h3 { margin:0 0 6px; font-size:17px; }
  .card p { margin:0; color:#b0bec5; font-size:14px; }
  @media (max-width:980px){ .cards { grid-template-columns: repeat(2, 1fr);} }
  @media (max-width:600px){ .cards { grid-template-columns: 1fr;} }

  .stButton>button {
    background:#4CAF50; color:white; border:none; border-radius:8px;
    padding:10px 18px; font-weight:700; cursor:pointer;
  }
  .stButton>button:hover { filter: brightness(1.05); }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
  /* SaaS cards */
  .card {
    background:#0F1420; border:1px solid rgba(255,255,255,0.07);
    border-radius:16px; padding:18px;
    box-shadow: 0 8px 28px rgba(0,0,0,.28);
  }
  .card h3 { margin: 0 0 6px; font-size: 18px; }
  .muted { color:#9fb1bd; }
  .pill {
    display:inline-block; padding:4px 10px; border-radius:999px;
    background:rgba(76,175,80,0.12); color:#4CAF50; font-weight:600; font-size:12px;
  }
  .divider { height:1px; background:rgba(255,255,255,0.06); margin:10px 0 16px 0; }
  .hint { font-size:13px; color:#b0bec5; }
  .preview {
    background:#0B0F17; border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:12px;
  }
  .btn-primary .stButton>button {
    width:100%; background:#4CAF50; color:white; border:none;
    border-radius:10px; padding:12px 16px; font-weight:700;
  }
  .btn-primary .stButton>button:hover { filter:brightness(1.05); }
</style>
""", unsafe_allow_html=True)


# ---------- Pages list & helpers ----------
PAGES = ["Home", "Data Input", "Preprocessing", "Topic Modeling", "About"]
PAGE_INDEX = {name: i for i, name in enumerate(PAGES)}

def goto(page_name: str):
    """Centralized navigation helper."""
    st.session_state.page = page_name
    st.rerun()

# ---------- Init session state ----------
if "page" not in st.session_state:
    st.session_state.page = "Home"

# ---------- Navbar ----------
default_idx = PAGE_INDEX.get(st.session_state.page, 0)
with st.container():
    selected = option_menu(
        menu_title=" AI Text Analysis",
        options=PAGES,
        icons=["house", "upload", "magic", "bar-chart", "info-circle"],
        menu_icon="lightning-charge-fill",
        default_index=default_idx,               # <-- binds navbar to session state
        orientation="horizontal",
        styles={
            "container": {
                "padding": "6px 12px",
                "background-color": "#0E1117",
                "border-bottom": "1px solid rgba(255,255,255,0.08)",
                "position": "sticky",
                "top": "0",
                "z-index": "1000",
            },
            "menu-title": {"color": "#FFFFFF", "font-weight": "700"},
            "icon": {"color": "#4CAF50", "font-size": "16px"},
            "nav-link": {
                "font-size": "15px", "color": "#EAEFF2",
                "margin": "0 8px", "padding": "6px 10px", "border-radius": "6px",
            },
            "nav-link-hover": {"color": "#4CAF50", "background-color": "rgba(76,175,80,0.12)"},
            "nav-link-selected": {
                "background-color": "transparent",
                "color": "#4CAF50",
                "border-bottom": "2px solid #4CAF50",
                "font-weight": "700",
            },
        },
    )

# If the user clicked a tab, update state to that tab
if selected != st.session_state.page:
    st.session_state.page = selected

# ---------- Pages ----------
def page_home():
    st.markdown("<div class='hero' style='padding-top:40px; padding-bottom:10px;'>"
                "<h1>Turn Raw Text into Insights</h1>"
                "<p>Upload TXT / DOCX / CSV or paste text.<br>"
                "Clean automatically, then extract key topics & themes.</p></div>",
                unsafe_allow_html=True)

    # Centered CTA
    st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        if st.button("🚀 Get Started", key="home_start", use_container_width=True):
            goto("Data Input")

    # Feature cards
    st.markdown("""
    <div class="cards">
      <div class="card"><h3>📄 Data Input</h3><p>Upload TXT / DOCX / CSV, or paste your own text.</p></div>
      <div class="card"><h3>🧹 Preprocessing</h3><p>Stopwords, lemmatization, normalization — fast.</p></div>
      <div class="card"><h3>📊 Topic Modeling</h3><p>Uncover hidden themes with NMF / LDA.</p></div>
      <div class="card"><h3>💬 Insights</h3><p>Summaries & sentiment (coming soon).</p></div>
    </div>
    """, unsafe_allow_html=True)


def page_data_input():
    st.title("📄 Step 1: Data Input")
    st.caption("Upload a file or paste text. We’ll validate and show an instant preview before preprocessing.")

    col_main, col_side = st.columns([1.8, 1])

    # ========== LEFT: INPUT CARD ==========
    with col_main:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>Choose your input <span class='pill'>TXT / CSV / DOCX / Paste</span></h3>", unsafe_allow_html=True)
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        tabs = st.tabs(["📤 Upload file", "📝 Paste text"])

        uploaded = None
        pasted_text = ""

        # ---- Upload tab ----
        with tabs[0]:
            st.write("Drag & drop or browse a file.")
            uploaded = st.file_uploader(" ", type=["txt", "csv", "docx"], key="file_up", label_visibility="collapsed")
            st.markdown("<div class='hint'>Max recommended CSV preview: ~800 rows for speed.</div>", unsafe_allow_html=True)

        # ---- Paste tab ----
        with tabs[1]:
            pasted_text = st.text_area("Paste your text here", height=200, key="paste_text")
            st.markdown("<div class='hint'>We’ll automatically clean and preview before the next step.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # end card

        # ========== AUTO PREVIEW (if any input present) ==========
        preview_text = ""
        df_preview = None
        source_type = None

        if pasted_text and pasted_text.strip():
            preview_text = pasted_text.strip()
            source_type = "pasted"

        elif uploaded is not None:
            try:
                with st.spinner("Reading file…"):
                    data = read_file(uploaded)  # -> {text, df_preview, meta:{source_type}}
                preview_text = data["text"] or ""
                df_preview = data.get("df_preview")
                source_type = data["meta"]["source_type"]
                st.toast(f"Loaded {source_type.upper()} ✔", icon="✅")
            except Exception as e:
                st.error(f"Failed to read file: {e}")

        # ========== PREVIEW CARD ==========
        if preview_text or df_preview is not None:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3>Quick Preview</h3>", unsafe_allow_html=True)
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

            if df_preview is not None:
                with st.expander("🔎 CSV rows (sample)"):
                    st.dataframe(df_preview, use_container_width=True)

            if preview_text:
                st.markdown("<div class='preview'>", unsafe_allow_html=True)
                st.text(preview_text[:800] + ("..." if len(preview_text) > 800 else ""))
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # ========== PRIMARY CTA ==========
        st.markdown("<div class='btn-primary' style='max-width:320px; margin:18px auto 0;'>", unsafe_allow_html=True)
        if st.button("🚀 Go Ahead", key="go_ahead"):
            if preview_text:
                st.session_state["raw_text"] = preview_text
                st.session_state["df_preview"] = df_preview
                st.session_state["source_type"] = source_type or "pasted"
                # transition
                goto("Preprocessing")
            else:
                st.warning("Please upload a file or paste some text first.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ========== RIGHT: SIDEBAR CARD (guidance) ==========
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
              <li>Very large text is capped for preview; full runs come in later steps.</li>
            </ul>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("**What happens next?**", unsafe_allow_html=True)
        st.markdown(
            "<p class='hint'>We’ll clean the text (lowercase, remove noise, lemmatize, stopwords) and show a summary before topic modeling.</p>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)



def page_preprocessing():
    st.title("🧹 Step 2: Preprocessing")

    if "raw_text" not in st.session_state or not st.session_state["raw_text"]:
        st.warning("⚠️ Please upload/paste text first in Data Input.")
        return

    raw_text = st.session_state["raw_text"]
    df_preview = st.session_state.get("df_preview")

    # CSV preview
    if df_preview is not None:
        with st.expander("🔎 CSV Preview (first rows)"):
            st.dataframe(df_preview, use_container_width=True)

    # Original text (snippet)
    st.subheader("📌 Original Text Preview")
    st.text_area("Original", raw_text[:1000] + ("..." if len(raw_text) > 1000 else ""), height=220)

    # Clean (preview only to keep UI fast)
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

    # Next step (placeholder for Week 3)
    # Store cleaned text for Week 3 and enable Next
    st.session_state["cleaned_text"] = cleaned_text

    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        if st.button("➡️ Next: Topic Modeling", use_container_width=True):
            goto("Topic Modeling")



def page_topics():
    st.title("📊 Step 3: Topic Modeling")

    # Need source text
    if "raw_text" not in st.session_state or not st.session_state["raw_text"]:
        st.warning("Please go to **Data Input** and add some text first.")
        return

    # Prefer previously computed cleaned_text, else quick clean here
    cleaned_text = st.session_state.get("cleaned_text", None)
    if not cleaned_text:
        from src.preprocessing import clean_text
        with st.spinner("Cleaning text (quick pass)…"):
            cleaned_text = clean_text(st.session_state["raw_text"][:200_000])

    with st.expander("⚙️ Modeling Settings", expanded=True):
        algo = st.selectbox("Algorithm", ["NMF (TF-IDF)", "LDA (Count)"])
        n_topics = st.slider("Number of topics", min_value=3, max_value=20, value=8, step=1)
        max_features = st.slider("Max vocabulary size", min_value=1000, max_value=20000, value=5000, step=500)

        # ✅ Replace tuple select with two simple sliders to avoid the error
        col_ng1, col_ng2 = st.columns(2)
        with col_ng1:
            min_n = st.slider("Min n-gram", 1, 3, 1, step=1)
        with col_ng2:
            max_n = st.slider("Max n-gram", 1, 3, 2, step=1)
        if max_n < min_n:
            st.error("Max n-gram must be ≥ Min n-gram.")
            return
        ngram_range = (min_n, max_n)

        # ✅ Keep min_df as INT; keep max_df as proportion in (0,1]
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            min_df = st.number_input("min_df (min docs containing term)", min_value=1, max_value=100, value=2, step=1)
        with col_f2:
            max_df = st.slider("max_df (ignore if in >X% docs)", 0.50, 1.00, 0.95, step=0.01)

        cta1, cta2 = st.columns(2)
        with cta1:
            train_btn = st.button("🚀 Train model", use_container_width=True)
        with cta2:
            save_btn = st.button("💾 Save artifacts", use_container_width=True, disabled=("tm_model" not in st.session_state))

    # Build pseudo-docs from the cleaned text so model has multiple docs
    docs = make_docs_from_text(cleaned_text, words_per_doc=200)
    if len(docs) < 5:
        st.error("Not enough text to form multiple documents. Add more text or use a larger CSV.")
        return

    # Train
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

    # Show results
    if "tm_model" in st.session_state:
        model = st.session_state["tm_model"]
        feature_names = st.session_state["tm_feature_names"]
        X = st.session_state["tm_X"]

        # Top terms per topic
        st.subheader("🧩 Discovered Topics")
        topics = top_terms_per_topic(model, feature_names, topn=10)
        for k, terms in enumerate(topics, start=1):
            st.markdown(f"**Topic {k}:** " + ", ".join(terms))

        # Document-topic distribution
        st.subheader("📈 Topic distribution (first 6 docs)")
        theta = doc_topic_distribution(model, X)
        import pandas as pd
        n_show = min(6, theta.shape[0])
        df_theta = pd.DataFrame(theta[:n_show], columns=[f"Topic {i+1}" for i in range(theta.shape[1])])
        st.dataframe(df_theta.style.format("{:.2f}"), use_container_width=True)

        # Save artifacts
        with st.expander("💾 Save (model + vectorizer)"):
            prefix = st.text_input("Path prefix", value="models/topic_model")
            if st.button("Save", use_container_width=True):
                try:
                    save_artifacts(prefix, model, st.session_state["tm_vectorizer"])
                    st.success(f"Saved: {prefix}_model.joblib and {prefix}_vectorizer.joblib")
                except Exception as e:
                    st.error(f"Failed to save: {e}")
    else:
        st.info("Adjust settings and click **Train model** to see topics.")
        

def page_about():
    st.title("ℹ️ About")
    st.write("""
    **AI Text Analysis** helps you convert raw text and CSVs into actionable insights.
    Built with Streamlit, pandas, spaCy and scikit-learn.
    """)


# ---------- Router ----------
current = st.session_state.page
if current == "Home":
    page_home()
elif current == "Data Input":
    page_data_input()
elif current == "Preprocessing":
    page_preprocessing()
elif current == "Topic Modeling":
    page_topics()
elif current == "About":
    page_about()

# ---------- Footer ----------
st.markdown('<hr style="opacity:.08;"><p style="text-align:center; color:#9fb1bd;">© 2025 • AI Text Analysis</p>', unsafe_allow_html=True)

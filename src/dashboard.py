# src/dashboard.py 


def page_dashboard():
    """
    Safe modular dashboard page: lazily imports everything when page is rendered
    so importing this module does not execute Streamlit UI code or heavy imports.
    """
    # lazy imports (only executed when page_dashboard() is called)
    import streamlit as st
    import pandas as pd
    import numpy as np
    try:
        import plotly.express as px
    except Exception:
        px = None
    import io, base64
    
    
    

    try:
        from src.topic_modeling import doc_topic_distribution, top_terms_per_topic
    except Exception:
        doc_topic_distribution = None
        top_terms_per_topic = None

    try:
        from src.summarization import summarize_all_topics_argmax, summarize_all_topics_weighted
    except Exception:
        summarize_all_topics_argmax = None
        summarize_all_topics_weighted = None

    try:
        from src.sentiment import analyze_vader, overall_distribution_pct, sentiment_by_topic_argmax, sentiment_by_topic_weighted
    except Exception:
        analyze_vader = None
        overall_distribution_pct = None
        sentiment_by_topic_argmax = None
        sentiment_by_topic_weighted = None

    # ---------- Dashboard UI ----------
    st.title("📊 Dashboard & Insights ")

    def get_theta():
        if "tm_theta" in st.session_state:
            return st.session_state["tm_theta"]
        try:
            model = st.session_state.get("tm_model")
            X = st.session_state.get("tm_X")
            if model is None or X is None:
                return None
            theta = doc_topic_distribution(model, X) if doc_topic_distribution is not None else None
            st.session_state["tm_theta"] = theta
            return theta
        except Exception:
            return None

    has_tm = all(k in st.session_state for k in ["tm_model", "tm_X", "tm_docs"])
    has_sent = "sentiment_results" in st.session_state
    topic_rows = st.session_state.get("topic_summaries", None)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if has_tm:
            theta = get_theta()
            if theta is not None:
                try:
                    dom = np.argmax(theta, axis=1)
                    dominant_topic = int(np.bincount(dom).argmax())
                    feat = st.session_state.get("tm_feature_names", None)
                    kws = top_terms_per_topic(st.session_state["tm_model"], feat, topn=6) if (feat is not None and top_terms_per_topic is not None) else [[""]] * theta.shape[1]
                    st.metric("Dominant topic", f"Topic {dominant_topic+1}")
                    st.caption(", ".join(kws[dominant_topic][:6]))
                except Exception:
                    st.write("Dominant topic: —")
            else:
                st.write("Dominant topic: —")
        else:
            st.write("Train topic model to see KPIs.")
    with c2:
        if has_sent and overall_distribution_pct is not None:
            labels = [r.get("label") for r in st.session_state["sentiment_results"]]
            pct = overall_distribution_pct(labels)
            st.metric("Positives (%)", f"{pct.get('POSITIVE',0.0):.1f}%")
        else:
            st.write("Sentiment: —")
    with c3:
        n_docs = len(st.session_state.get("tm_docs", [])) if has_tm else (len(st.session_state.get("df_preview", [])) if st.session_state.get("df_preview") is not None else 0)
        st.metric("Documents", f"{n_docs}")
    with c4:
        if has_tm:
            theta = get_theta()
            n_topics = theta.shape[1] if (theta is not None) else (getattr(st.session_state.get("tm_model", None), "n_components", "n/a"))
            st.metric("Topics", f"{n_topics}")
        else:
            st.write("Topics: —")

    st.markdown("---")
    
    # Word Cloud
    st.header("🖼️ Word Cloud")

    cleaned_text = st.session_state.get("cleaned_text", "") or st.session_state.get("raw_text", "")
    tm_model = st.session_state.get("tm_model")
    tm_feat  = st.session_state.get("tm_feature_names")
    tm_docs  = st.session_state.get("tm_docs", [])
    topic_summaries = st.session_state.get("topic_summaries")

    wc_source = None

    # Prefer topic keywords if available
    if topic_summaries and isinstance(topic_summaries, list):
        try:
            kws_joined = " ".join([r.get("keywords","") for r in topic_summaries])
            wc_source = kws_joined if kws_joined.strip() else None
        except Exception:
            wc_source = None

    # Else use top terms per topic
    if wc_source is None and tm_model is not None and tm_feat is not None:
        try:
            kws = top_terms_per_topic(tm_model, tm_feat, topn=8)
            wc_source = " ".join([w for topic in kws for w in topic]) if kws else None
        except Exception:
            wc_source = None

    # Fallback to full text
    if wc_source is None:
        wc_source = cleaned_text or " ".join(tm_docs)

    if wc_source and wc_source.strip():
        try:
            from wordcloud import WordCloud
            wc = WordCloud(width=1000, height=380, background_color="white", collocations=False).generate(wc_source)
            st.image(wc.to_image(), use_column_width=True)
        except Exception as e:
            st.info("⚠️ WordCloud not available. Run `pip install wordcloud` to enable this panel.")
    else:
        st.info("No text available to generate word cloud.")

    st.markdown("---")


    # Topic distribution
    st.header("Topic distribution")
    if has_tm:
        theta = get_theta()
        if theta is None:
            st.warning("Could not compute doc-topic distribution.")
        else:
            topic_weights = np.mean(theta, axis=0)
            n_topics = len(topic_weights)
            feat = st.session_state.get("tm_feature_names", None)
            kws = top_terms_per_topic(st.session_state["tm_model"], feat, topn=8) if (feat is not None and top_terms_per_topic is not None) else [[""]] * n_topics
            df_topics = pd.DataFrame({
                "topic_idx": list(range(n_topics)),
                "weight": topic_weights,
                "keywords": [", ".join(k) for k in kws],
                "label": [st.session_state.get("topic_labels", {}).get(i, f"Topic {i+1}") for i in range(n_topics)]
            })
            try:
                if px:
                    fig = px.pie(df_topics, names="label", values="weight", title="Topic distribution (mean probability)", hole=0.35)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(df_topics, use_container_width=True)
            except Exception:
                st.dataframe(df_topics, use_container_width=True)
            st.dataframe(df_topics.rename(columns={"topic_idx":"Topic index","label":"Label","keywords":"Top keywords","weight":"Avg weight"}), use_container_width=True)
    else:
        st.info("Train a topic model to populate topic distribution.")

    # Sentiment overview
    st.markdown("---")
    st.header("Sentiment overview")
    if has_sent:
        labels = [r.get("label") for r in st.session_state["sentiment_results"]]
        df = pd.DataFrame([{"label":"POSITIVE","count":labels.count("POSITIVE")},{"label":"NEUTRAL","count":labels.count("NEUTRAL")},{"label":"NEGATIVE","count":labels.count("NEGATIVE")}])
        try:
            if px:
                fig = px.pie(df, names="label", values="count", title="Overall sentiment (counts)", hole=0.35)
                st.plotly_chart(fig, use_container_width=True)
                st.session_state["_dashboard_sentiment_fig"] = fig
            else:
                st.dataframe(df)
                st.session_state["_dashboard_sentiment_fig"] = None
        except Exception:
            st.dataframe(df)
            st.session_state["_dashboard_sentiment_fig"] = None
    else:
        st.info("No sentiment computed yet. Use Sentiment page or run VADER quickly from the Dashboard.")

    # Topic-level summaries display
    st.markdown("---")
    st.header("Topic-level summaries")
    
    if topic_rows:
        for r in topic_rows:
            tidx = int(r["topic_idx"])
            custom_lbl = st.session_state.get("topic_labels", {}).get(tidx, None)
    
            # Build title
            if custom_lbl:
                title = f"Topic {tidx+1} — {custom_lbl} (docs used: {r.get('n_docs_used',0)})"
            else:
                title = f"Topic {tidx+1} (docs used: {r.get('n_docs_used',0)})"
    
            with st.expander(title, expanded=False):
                st.write(r.get("summary") or "_No summary_")
    
                # Quick label editor
                new_label = st.text_input(
                    f"Custom label for Topic {tidx+1}",
                    value=custom_lbl or "",
                    key=f"topic_label_{tidx}"
                )
                if new_label.strip():
                    st.session_state["topic_labels"][tidx] = new_label.strip()
    else:
        st.info("No topic summaries available. Run topic-level summaries on the Summarization page.")


    # ==== UTILITIES: sentiment & topic helpers (paste near top of reporting section) ====

    def _overall_sent_counts():
        res = st.session_state.get("sentiment_results") or []
        labels = [r.get("label") for r in res]
        if not labels:
            return {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
        from collections import Counter
        c = Counter(labels)
        return {k: int(c.get(k, 0)) for k in ["POSITIVE", "NEUTRAL", "NEGATIVE"]}

    def _pct_split(counts):
        total = max(1, sum(counts.values()))
        return {k: (v * 100.0 / total) for k, v in counts.items()}

    def _topic_distribution_df():
        tm_model = st.session_state.get("tm_model")
        X = st.session_state.get("tm_X")
        feat = st.session_state.get("tm_feature_names")
        if tm_model is None or X is None:
            return None, pd.DataFrame()
        theta = doc_topic_distribution(tm_model, X)
        weights = np.mean(theta, axis=0)
        n_topics = len(weights)
        try:
            kws = top_terms_per_topic(tm_model, feat, topn=8) if feat is not None else [[] for _ in range(n_topics)]
        except Exception:
            kws = [[] for _ in range(n_topics)]
        labels = [st.session_state.get("topic_labels", {}).get(i, f"Topic {i+1}") for i in range(n_topics)]
        df = pd.DataFrame({
            "topic_idx": list(range(n_topics)),
            "Topic": [f"Topic {i+1}" for i in range(n_topics)],
            "Label": labels,
            "Avg weight": weights,
            "Keywords": [", ".join(x) for x in kws],
        })
        return theta, df

    def _sentiment_by_topic_argmax(theta, labels):
        """
        Simple, fast: assign each document to its dominant topic and tally sentiment.
        Returns a dataframe with NEG/NEU/POS counts and percentages per topic.
        """
        if theta is None or len(labels) == 0:
            return pd.DataFrame()
        n_docs, n_topics = theta.shape
        n = min(n_docs, len(labels))
        dom = np.argmax(theta[:n, :], axis=1)
        labs = labels[:n]
        rows = []
        for t in range(n_topics):
            idxs = np.where(dom == t)[0]
            if len(idxs) == 0:
                rows.append({"topic_idx": t, "NEG": 0, "NEU": 0, "POS": 0, "Total": 0,
                             "neg_pct": 0.0, "pos_pct": 0.0})
                continue
            sub = [labs[i] for i in idxs]
            NEG = sub.count("NEGATIVE"); NEU = sub.count("NEUTRAL"); POS = sub.count("POSITIVE")
            tot = max(1, len(sub))
            rows.append({
                "topic_idx": t, "NEG": NEG, "NEU": NEU, "POS": POS, "Total": tot,
                "neg_pct": (NEG * 100.0 / tot), "pos_pct": (POS * 100.0 / tot)
            })
        return pd.DataFrame(rows)

    # --- Reporting Part ---

    st.header("📄 Reporting")
    st.caption("Generate a self-contained HTML report with KPIs, word cloud, sentiment & topic charts, topic summaries, and recommendations.")

    def _safe_fig_to_png_b64(fig):
        """Return base64 PNG for a plotly fig if kaleido is available, else None."""
        try:
            import plotly.io as pio
            png_bytes = pio.to_image(fig, format="png", scale=2)  # needs kaleido
            import base64
            return base64.b64encode(png_bytes).decode("ascii")
        except Exception:
            return None

    def _make_wordcloud_b64():
        """Build a word cloud based on topic keywords > top terms > text fallback."""
        wc_source = None
        tm_model = st.session_state.get("tm_model")
        tm_feat  = st.session_state.get("tm_feature_names")
        tm_docs  = st.session_state.get("tm_docs", [])
        topic_summaries = st.session_state.get("topic_summaries")
        cleaned_text = st.session_state.get("cleaned_text", "") or st.session_state.get("raw_text", "")

        # prefer topic keywords if exist
        if topic_summaries and isinstance(topic_summaries, list):
            try:
                s = " ".join([r.get("keywords","") for r in topic_summaries])
                if s.strip(): wc_source = s
            except Exception:
                pass
        # else top terms per topic
        if wc_source is None and tm_model is not None and tm_feat is not None:
            try:
                from src.topic_modeling import top_terms_per_topic
                kws = top_terms_per_topic(tm_model, tm_feat, topn=8)
                if kws: wc_source = " ".join([w for topic in kws for w in topic])
            except Exception:
                pass
        # else full text
        if wc_source is None:
            wc_source = cleaned_text or " ".join(tm_docs)

        if not wc_source or not wc_source.strip():
            return None

        try:
            from wordcloud import WordCloud
            wc = WordCloud(width=1100, height=420, background_color="white",
                           collocations=False).generate(wc_source)
            img = wc.to_image()
            import io, base64
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode("ascii")
        except Exception:
            return None

    def _build_sentiment_fig_and_stats():
        """Return (fig or None, stats_dict) using st.session_state['sentiment_results']."""
        res = st.session_state.get("sentiment_results")
        if not res: 
            return None, {"POSITIVE":0, "NEUTRAL":0, "NEGATIVE":0}
        labels = [r.get("label") for r in res]
        df = pd.DataFrame(labels, columns=["label"])
        counts = df.value_counts().reset_index(name="count").rename(columns={"label":"label"})
        stats = {row["label"]: int(row["count"]) for _, row in counts.iterrows()}
        try:
            import plotly.express as px
            fig = px.bar(counts, x="label", y="count", title="Sentiment distribution (counts)")
            return fig, stats
        except Exception:
            return None, stats

    def _build_topic_distribution_fig_and_df():
        """Return (fig or None, df_topics) using doc-topic mean, labels & keywords."""
        tm_model = st.session_state.get("tm_model")
        X = st.session_state.get("tm_X")
        feat = st.session_state.get("tm_feature_names")
        if tm_model is None or X is None:
            return None, pd.DataFrame()
        from src.topic_modeling import doc_topic_distribution, top_terms_per_topic
        theta = doc_topic_distribution(tm_model, X)
        topic_weights = np.mean(theta, axis=0)
        n_topics = len(topic_weights)
        kws = []
        if feat is not None:
            try:
                kws = top_terms_per_topic(tm_model, feat, topn=8)
            except Exception:
                kws = [[] for _ in range(n_topics)]
        labels = [st.session_state.get("topic_labels", {}).get(i, f"Topic {i+1}") for i in range(n_topics)]
        df_topics = pd.DataFrame({
            "Topic": [f"Topic {i+1}" for i in range(n_topics)],
            "Label": labels,
            "Avg weight": topic_weights,
            "Keywords": [", ".join(k) for k in (kws or [[] for _ in range(n_topics)])],
        })
        try:
            import plotly.express as px
            fig = px.bar(df_topics, x="Label", y="Avg weight", title="Topic distribution (mean probability)")
            return fig, df_topics
        except Exception:
            return None, df_topics

    def _recommendations(stats_sent, df_topics, theta=None, feat=None, top_k=2, coh=None, div=None):
        """
        Build actionable, priority-scored recommendations using:
          - overall sentiment balance
          - topic prevalence (Avg weight)
          - topic-level negative share (argmax)
          - keywords per topic
          - optional quality metrics (coherence/diversity)
        Returns list of dicts: {"priority": int, "title": str, "detail": str}
        """
        # Overall sentiment
        pos = stats_sent.get("POSITIVE", 0)
        neg = stats_sent.get("NEGATIVE", 0)
        neu = stats_sent.get("NEUTRAL", 0)
        total = max(1, pos + neg + neu)
        pos_pct = pos * 100.0 / total
        neg_pct = neg * 100.0 / total

        # Topic-level negatives
        labels_seq = [r.get("label") for r in (st.session_state.get("sentiment_results") or [])]
        by_topic = _sentiment_by_topic_argmax(theta, labels_seq) if theta is not None and labels_seq else pd.DataFrame()

        # Merge with topic weights & labels
        if not df_topics.empty and not by_topic.empty:
            merged = pd.merge(df_topics, by_topic, on="topic_idx", how="left").fillna(0)
            # score = prevalence * negative_share
            merged["neg_share"] = merged["neg_pct"] / 100.0
            merged["priority_score"] = merged["Avg weight"] * merged["neg_share"]
            merged = merged.sort_values("priority_score", ascending=False)
            top_neg = merged.head(top_k)
        else:
            top_neg = pd.DataFrame()

        recs = []

        # R1: Immediate risk / remediation
        if not top_neg.empty and (neg_pct > 30 or neg > pos):
            lbls = ", ".join(top_neg["Label"].tolist())
            kws_list = top_neg["Keywords"].tolist()
            kws_focus = "; ".join([", ".join(k.split(", ")[:4]) for k in kws_list])
            recs.append({
                "priority": 1,
                "title": "Prioritize remediation on high-risk topics",
                "detail": f"High NEGATIVE sentiment. Focus first on: {lbls}. Signals include: {kws_focus}."
            })

        # R2: Quick wins / amplification
        if pos_pct >= 45:
            recs.append({
                "priority": 2,
                "title": "Amplify what works",
                "detail": "POSITIVE sentiment is strong. Identify messaging & features driving POSITIVE topics and replicate across channels."
            })

        # R3: Deep-dive investigation
        if not top_neg.empty:
            first = top_neg.iloc[0]
            recs.append({
                "priority": 3,
                "title": f"Investigate root causes in '{first['Label']}'",
                "detail": f"Highest priority topic by risk score. Sample documents with dominant topic = '{first['Label']}' "
                          f"and tags like: {', '.join(first['Keywords'].split(', ')[:6])}."
            })

        # R4: Modeling quality improvements
        if coh is not None and coh < 0.35:
            recs.append({
                "priority": 4,
                "title": "Improve topic coherence",
                "detail": "Try tighter vocabulary (lower max_df), adjust n-grams, or increase documents to raise coherence."
            })
        if div is not None and div < 0.75:
            recs.append({
                "priority": 5,
                "title": "Reduce topic overlap",
                "detail": "Consider increasing number of topics or vocabulary size to improve diversity."
            })

        # Fallback recommendation if very little signal
        if not recs:
            recs.append({
                "priority": 3,
                "title": "Gather more data / refine preprocessing",
                "detail": "Signal is weak. Add more documents, ensure language consistency, and revisit stopwords/lemmatization."
            })

        # Sort by priority ascending
        recs = sorted(recs, key=lambda x: x["priority"])
        return recs


    # --- Live Recommendations panel (before Reporting) ---
    st.markdown("---")
    st.header("✅ Actionable Recommendations")
    stats_sent = _overall_sent_counts()
    theta, df_topics = _topic_distribution_df()
    coh = st.session_state.get("_diag_coherence")
    div = st.session_state.get("_diag_diversity")
    live_recs = _recommendations(stats_sent, df_topics, theta=theta, coh=coh, div=div)

    for r in live_recs:
        st.markdown(
            f"**{r['title']}**  \n"
            f"<span style='color:#94a3b8;'>Priority {r['priority']}</span><br>{r['detail']}",
            unsafe_allow_html=True
        )

    
    
    def build_html_report():
        """Return HTML bytes for a self-contained report with Executive Summary + Recommendations."""
        ts = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")

        # Core stats
        tm_docs = st.session_state.get("tm_docs", []) or []
        n_docs = len(tm_docs)
        tm_model = st.session_state.get("tm_model")
        n_topics = getattr(tm_model, "n_components", None)

        # Topic distribution + theta
        theta, df_topics = _topic_distribution_df()

        # Sentiment overall
        stats_sent = _overall_sent_counts()
        pct_sent = _pct_split(stats_sent)

        # Executive Summary bullets
        top_topics_text = "n/a"
        top_risk = "n/a"
        top_opportunity = "n/a"

        if not df_topics.empty:
            head = df_topics.sort_values("Avg weight", ascending=False).head(3)
            top_topics_text = "; ".join([f"{r.Label} ({r['Avg weight']:.2f})" for _, r in head.iterrows()])

            # Top Risk: highest negative share
            if theta is not None:
                labels_seq = [r.get("label") for r in (st.session_state.get("sentiment_results") or [])]
                by_topic = _sentiment_by_topic_argmax(theta, labels_seq)
                if not by_topic.empty:
                    by_topic = pd.merge(df_topics, by_topic, on="topic_idx", how="left").fillna(0)
                    if "neg_pct" in by_topic:
                        risk_row = by_topic.sort_values("neg_pct", ascending=False).head(1).iloc[0]
                        top_risk = f"{risk_row['Label']} ({risk_row['neg_pct']:.1f}% negative)"

            # Top Opportunity: highest positive share
            if theta is not None and not by_topic.empty:
                if "pos_pct" in by_topic:
                    opp_row = by_topic.sort_values("pos_pct", ascending=False).head(1).iloc[0]
                    top_opportunity = f"{opp_row['Label']} ({opp_row['pos_pct']:.1f}% positive)"

        exec_summary = [
            f"Processed <b>{n_docs}</b> documents; discovered <b>{n_topics if n_topics is not None else '—'}</b> topics.",
            f"Sentiment split: <b>Positive {pct_sent.get('POSITIVE',0):.1f}%</b>, "
            f"<b>Neutral {pct_sent.get('NEUTRAL',0):.1f}%</b>, <b>Negative {pct_sent.get('NEGATIVE',0):.1f}%</b>.",
            f"Most prevalent themes: {top_topics_text}.",
            f"⚠️ Top Risk: {top_risk}.",
            f"⭐ Top Opportunity: {top_opportunity}."
        ]


        # Figures (PNG base64 if kaleido present)
        fig_sent, _ = _build_sentiment_fig_and_stats()
        img_sent_b64 = _safe_fig_to_png_b64(fig_sent) if fig_sent else None

        from plotly import express as px
        fig_topics = None
        if not df_topics.empty:
            try:
                fig_topics = px.bar(df_topics, x="Label", y="Avg weight", title="Topic distribution (mean probability)")
            except Exception:
                fig_topics = None
        img_topics_b64 = _safe_fig_to_png_b64(fig_topics) if fig_topics else None

        img_wc_b64 = _make_wordcloud_b64()

        # Optional quality metrics if you cached them during diagnostics
        coh = st.session_state.get("_diag_coherence")
        div = st.session_state.get("_diag_diversity")

        # Recommendations
        recs = _recommendations(stats_sent, df_topics, theta=theta, coh=coh, div=div)

        # Topic Summaries
        rows = st.session_state.get("topic_summaries")

        # HTML assemble
        parts = []
        parts.append(f"""<!doctype html>
<html><head><meta charset="utf-8"><title>NarrativeNexus — Executive Report</title>
<style>
body {{ font-family:-apple-system, Segoe UI, Roboto, sans-serif; color:#0f172a; }}
h1 {{ margin: 0 0 6px; }} h2 {{ margin: 22px 0 8px; }} h3 {{ margin: 14px 0 6px; }}
.card {{ border:1px solid #e5e7eb; border-radius:10px; padding:14px; margin:12px 0; }}
.kpis {{ display:flex; gap:16px; flex-wrap:wrap; }}
.kpi {{ background:#f8fafc; border:1px solid #e5e7eb; border-radius:12px; padding:12px 14px; min-width:160px; }}
small.muted {{ color:#64748b; }}
table {{ border-collapse:collapse; width:100%; }}
table th, table td {{ border:1px solid #e5e7eb; padding:8px; text-align:left; }}
.badge {{ display:inline-block; padding:2px 8px; background:#eef2ff; border-radius:999px; border:1px solid #c7d2fe; color:#3730a3; font-size:12px; }}
hr {{ border:0; border-top:1px solid #e5e7eb; margin:16px 0; }}
ol.prioritized > li {{ margin: 6px 0; }}
</style></head><body>
<h1>NarrativeNexus — Executive Report</h1>
<small class="muted">Generated: {ts}</small>

<h2>Executive Summary</h2>
<div class="card">
  <ul>
    <li>{exec_summary[0]}</li>
    <li>{exec_summary[1]}</li>
    <li>{exec_summary[2]}</li>
  </ul>
</div>
""")

    # KPIs
        parts.append(f"""
<div class="kpis">
  <div class="kpi"><b>Documents</b><div>{n_docs}</div></div>
  <div class="kpi"><b>Topics</b><div>{n_topics if n_topics is not None else "—"}</div></div>
  <div class="kpi"><b>Positive %</b><div>{pct_sent.get('POSITIVE',0):.1f}%</div></div>
  <div class="kpi"><b>Negative %</b><div>{pct_sent.get('NEGATIVE',0):.1f}%</div></div>
</div>
""")

    # Word Cloud
        parts.append("<h2>Word Cloud</h2>")
        if img_wc_b64:
            parts.append(f'<div class="card"><img alt="Word Cloud" style="max-width:100%;" src="data:image/png;base64,{img_wc_b64}"/></div>')
        else:
            parts.append('<div class="card"><small class="muted">Word Cloud unavailable (install `wordcloud` or add more text).</small></div>')
    
        # Sentiment
        parts.append("<h2>Sentiment Distribution</h2>")
        if img_sent_b64:
            parts.append(f'<div class="card"><img alt="Sentiment Chart" style="max-width:100%;" src="data:image/png;base64,{img_sent_b64}"/></div>')
        else:
            counts = stats_sent
            parts.append('<div class="card"><table><thead><tr><th>label</th><th>count</th></tr></thead><tbody>')
            for k in ["POSITIVE","NEUTRAL","NEGATIVE"]:
                parts.append(f"<tr><td>{k}</td><td>{counts.get(k,0)}</td></tr>")
            parts.append('</tbody></table><small class="muted">Install `kaleido` to embed charts.</small></div>')
    
        # Topics
        parts.append("<h2>Topic Distribution</h2>")
        if img_topics_b64:
            parts.append(f'<div class="card"><img alt="Topic Chart" style="max-width:100%;" src="data:image/png;base64,{img_topics_b64}"/></div>')
        if not df_topics.empty:
            parts.append('<div class="card"><table><thead><tr><th>Topic</th><th>Label</th><th>Avg weight</th><th>Keywords</th></tr></thead><tbody>')
            for _, r in df_topics.iterrows():
                parts.append(f"<tr><td>{r['Topic']}</td><td>{r['Label']}</td><td>{r['Avg weight']:.3f}</td><td>{r['Keywords']}</td></tr>")
            parts.append("</tbody></table></div>")
        else:
            parts.append('<div class="card"><small class="muted">No trained topic model.</small></div>')
    
        # Recommendations (priority list)
        parts.append("<h2>Actionable Recommendations</h2>")
        parts.append("<div class='card'><ol class='prioritized'>")
        for r in recs:
            parts.append(f"<li><b>{r['title']}</b><br><small class='muted'>Priority {r['priority']}</small><br>{r['detail']}</li>")
        parts.append("</ol></div>")
    
        # Topic summaries
        parts.append("<h2>Topic Summaries</h2>")
        if rows:
            for r in rows:
                title = r.get("topic_display", f"Topic {r.get('topic_idx','')}")
                label = r.get("label_final", r.get("label","Other"))
                keys  = r.get("keywords","")
                text  = (r.get("summary") or "").replace("\n","<br>")
                parts.append(f'<div class="card"><h3>{title} <span class="badge">{label}</span></h3>')
                parts.append(f'<div><b>Keywords:</b> {keys}</div><hr><div>{text}</div></div>')
        else:
            parts.append('<div class="card"><small class="muted">No topic summaries yet.</small></div>')
    
        parts.append("</body></html>")
        return "\n".join(parts).encode("utf-8")


    # Build + download
    if st.button("Generate HTML report", key="btn_dashboard_build_report", use_container_width=True):
        with st.spinner("Building report..."):
            try:
                report_bytes = build_html_report()
                st.success("Report ready.")
                st.download_button(
                    "⬇️ Download Report (HTML)",
                    report_bytes,
                    file_name="ai_text_analysis_report.html",
                    mime="text/html",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Report build failed: {e}")

    
    st.caption("Dashboard (modular) — use the top menu to return to other pages.")

# ==========================
# Imports
# ==========================

import os
import re
import random
import json
import warnings
import sys
from typing import List, Optional

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web server
import matplotlib.pyplot as plt
import seaborn as sns
import nltk

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

from wordcloud import WordCloud, STOPWORDS
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

from flask import Flask, jsonify, request, render_template
import numpy as np
# Gemini (imported lazily inside functions to avoid hard dependency at startup)

# ==========================
# Configs
# ==========================
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Configure matplotlib for web server
import matplotlib
matplotlib.use('Agg')
plt.ioff()  # Turn off interactive mode

PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)
GEMINI_API_KEY = "AIzaSyAbFTcNf6-Xq64tma7ZV7V2EE59ZIQTm9Q"

# ==========================
# NLTK Setup
# ==========================
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

from nltk.sentiment.vader import SentimentIntensityAnalyzer


# ==========================
# Helper Functions
# ==========================
def load_dataset(path: str, sep: str = ",") -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    safe_print(f"[FILE] Loading dataset: {path}")
    
    try:
        # Try to detect file type and load accordingly
        if path.lower().endswith('.pdf'):
            # Handle PDF files
            try:
                import pdfplumber
                text_content = []
                with pdfplumber.open(path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                
                if text_content:
                    # Create a DataFrame with the extracted text
                    combined_text = '\n'.join(text_content)
                    # Split into chunks for analysis
                    chunks = [chunk.strip() for chunk in combined_text.split('\n') if chunk.strip()]
                    return pd.DataFrame({'text_content': chunks[:1000]})  # Limit to 1000 chunks
                else:
                    raise Exception("No text extracted from PDF")
            except ImportError:
                raise Exception("pdfplumber not installed. Cannot process PDF files.")
        
        elif path.lower().endswith(('.xlsx', '.xls')):
            # Handle Excel files
            return pd.read_excel(path)
        
        elif path.lower().endswith('.tsv'):
            # Handle TSV files
            return pd.read_csv(path, sep='\t', encoding='utf-8', on_bad_lines='skip')
        
        else:
            # Handle CSV and other text files
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    return pd.read_csv(path, sep=sep, encoding=encoding, on_bad_lines='skip')
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, try with error handling
            return pd.read_csv(path, sep=sep, encoding='utf-8', errors='replace', on_bad_lines='skip')
            
    except Exception as e:
        safe_print(f"[ERROR] Failed to load {path}: {e}")
        raise


def save_fig(fig, fname: str):
    path = os.path.join(PLOTS_DIR, fname)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    try:
        print(f"[SAVED] {path}")
    except OSError:
        try:
            sys.stdout.write(f"[SAVED] {path}\n")
        except Exception:
            pass


def safe_print(message: str):
    try:
        print(message)
    except OSError:
        try:
            sys.stdout.write(message + "\n")
        except Exception:
            pass


def detect_text_column(df: pd.DataFrame) -> Optional[str]:
    candidates = ["text", "feedback", "description", "comments", "review",
                  "opportunity_text", "title", "message", "content", "StudentComments", "text_content"]
    for c in candidates:
        if c in df.columns:
            return c
    object_cols = [col for col in df.columns if df[col].dtype == object]
    for col in object_cols:
        lens = df[col].dropna().astype(str).map(len)
        if len(lens) > 10 and lens.mean() > 20:
            return col
    return None


def print_top_words(vectorizer, components, n_top_words=10):
    feature_names = vectorizer.get_feature_names_out()
    for topic_idx, topic in enumerate(components):
        top_indices = topic.argsort()[::-1][:n_top_words]
        top_words = [feature_names[i] for i in top_indices]
        try:
            safe_print(f"Topic #{topic_idx + 1}: {', '.join(top_words)}")
        except Exception:
            pass


# ==========================
# Topic Modeling
# ==========================
def run_lda(texts: List[str], n_topics=5, max_features=800, n_top_words=12):
    safe_print("\n[STEP] Running LDA topic modeling...")
    cv = CountVectorizer(max_df=0.95, min_df=2, max_features=max_features, stop_words="english")
    X = cv.fit_transform(texts)
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, learning_method="batch", n_jobs=-1)
    lda.fit(X)
    print_top_words(cv, lda.components_, n_top_words=n_top_words)
    return lda, cv


def run_nmf(texts: List[str], n_topics=5, max_features=1200, n_top_words=12):
    safe_print("\n[STEP] Running NMF topic modeling...")
    tfidf = TfidfVectorizer(max_df=0.95, min_df=2, max_features=max_features, stop_words="english")
    X = tfidf.fit_transform(texts)
    nmf = NMF(n_components=n_topics, random_state=42, init="nndsvd", max_iter=200)
    nmf.fit(X)
    print_top_words(tfidf, nmf.components_, n_top_words=n_top_words)
    return nmf, tfidf


# ==========================
# Sentiment Analysis
# ==========================
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Sentiment analysis now uses only 5 main categories: Very Positive, Positive, Neutral, Negative, Very Negative

def run_sentiment(df: pd.DataFrame, text_col: str):
    sia = SentimentIntensityAnalyzer()
    df_sent = df.copy()
    df_sent["compound"] = df_sent[text_col].fillna("").astype(str).map(lambda x: sia.polarity_scores(x)["compound"])

    # Simplified 5-category sentiment classification
    def categorize_sentiment_simple(compound):
        if compound >= 0.5:
            return "Very Positive"
        elif compound >= 0.1:
            return "Positive"
        elif compound > -0.1:
            return "Neutral"
        elif compound > -0.5:
            return "Negative"
        else:
            return "Very Negative"

    df_sent["sentiment_label"] = df_sent["compound"].apply(categorize_sentiment_simple)

    # Use only the simplified sentiment labels (no emotion detection)
    df_sent["final_label"] = df_sent["sentiment_label"]

    # Plot with only 5 categories
    import matplotlib.pyplot as plt
    import seaborn as sns
    fig, ax = plt.subplots(figsize=(10, 6))
    order = ["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"]
    
    # Create the plot with better styling
    colors = ['#2E8B57', '#90EE90', '#FFD700', '#FF6347', '#DC143C']  # Green to red gradient
    
    counts = df_sent["final_label"].value_counts().reindex(order, fill_value=0)
    bars = ax.bar(order, counts.values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        if height > 0:  # Only show label if there's data
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    ax.set_title("Sentiment Distribution (5 Categories)", fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel("Sentiment Category", fontsize=12, fontweight='bold')
    ax.set_ylabel("Count", fontsize=12, fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    fig_path = os.path.join(PLOTS_DIR, "sentiment_distribution.png")
    fig.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    # Return updated DataFrame and counts (only the 5 main categories)
    sentiment_counts = counts.to_dict()
    return df_sent, sentiment_counts, fig_path



# ==========================
# Classification
# ==========================
def classify_isSame(df: pd.DataFrame, text_col: str, label_col="isSame"):
    if label_col not in df.columns:
        safe_print(f"[SKIP] Label column '{label_col}' not found.")
        return None
    df_subset_all = df[df[label_col].isin(['true', 'fake'])]
    sample_size = min(len(df_subset_all), 5000)
    df_subset = df_subset_all.sample(sample_size, random_state=42) if sample_size > 0 else df_subset_all
    X_text = df_subset[text_col].fillna("").astype(str)
    y = df_subset[label_col].map({"true": 1, "fake": 0}).astype(int)
    if len(y.unique()) < 2:
        safe_print("[SKIP] Not enough samples for both classes. Skipping classification.")
        return None

    tfidf = TfidfVectorizer(max_df=0.95, min_df=2, stop_words="english", max_features=5000)
    X = tfidf.fit_transform(X_text)
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

    clf = LogisticRegression(max_iter=1000, solver="liblinear")
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = metrics.accuracy_score(y_test, y_pred)
    prec = metrics.precision_score(y_test, y_pred)
    rec = metrics.recall_score(y_test, y_pred)
    f1 = metrics.f1_score(y_test, y_pred)

    cm = metrics.confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix")
    save_fig(fig, "confusion_matrix.png")

    return {"model": clf, "vectorizer": tfidf,
            "metrics": {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1}}


# ==========================
# Word Cloud
# ==========================
def generate_wordcloud(texts: List[str], filename="wordcloud.png", category="all"):
    safe_print(f"\n[STEP] Generating word cloud for: {category} ...")
    if not texts or all(t.strip() == "" for t in texts):
        safe_print(f"[WARN] No text found for word cloud: {category}")
        return None
    text = " ".join(texts)
    wc = WordCloud(
        width=800, height=400,
        background_color="white",
        stopwords=STOPWORDS,
        colormap="viridis"
    ).generate(text)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    save_fig(fig, filename)



# ==========================
# Hybrid Summarization
# ==========================
def generate_summary_gemini(text: str) -> str:
    try:
        from google import genai
        from google.genai import types
    except Exception:
        # Fallback if SDK not available
        return text[:800]

    client = genai.Client(api_key=GEMINI_API_KEY)
    model = "gemini-2.5-flash-lite"

    contents = [types.Content(role="user", parts=[types.Part(text)])]
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        response_mime_type="text/plain"
    )
    result = client.models.generate_content(model=model, contents=contents, config=config)
    return result.text


def clean_repetitions(text: str) -> str:
    """Remove excessive repetitions like 'good good good' → 'good'."""
    # Collapse repeated words (case-insensitive)
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text, flags=re.IGNORECASE)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def generate_fallback_summary(combined_text: str) -> str:
    """Generate an intelligent fallback summary when Gemini is not available."""
    safe_print("[SUMMARY] Generating intelligent fallback summary...")
    
    # If text is too short or repetitive, create a structured analysis
    if len(combined_text) < 100 or len(set(combined_text.split())) < 20:
        return generate_structured_analysis(combined_text)
    
    try:
        # Try LexRank first
        text_for_summary = combined_text if combined_text else "No feedback available"
        parser = PlaintextParser.from_string(text_for_summary, Tokenizer("english"))
        summarizer = LexRankSummarizer()
        # Generate more sentences for better summary
        summary_sentences = summarizer(parser.document, sentences_count=15)
        summary_text = " ".join(str(s) for s in summary_sentences)
        cleaned_summary = clean_repetitions(summary_text)
        
        # If the summary is still too repetitive, use structured analysis
        if len(set(cleaned_summary.split())) < 30:
            return generate_structured_analysis(combined_text)
            
        return cleaned_summary
        
    except Exception as e:
        safe_print(f"[SUMMARY] LexRank failed: {e}, using structured analysis")
        return generate_structured_analysis(combined_text)


def generate_structured_analysis(combined_text: str) -> str:
    """Generate a context-aware structured analysis based on the actual content."""
    safe_print("[SUMMARY] Creating structured analysis...")
    
    # Analyze text patterns
    words = combined_text.lower().split()
    word_freq = {}
    
    # Filter out common words and focus on meaningful terms
    stop_words = {'is', 'are', 'was', 'were', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'he', 'she', 'it', 'they', 'his', 'her', 'their', 'this', 'that', 'these', 'those', 'line'}
    
    for word in words:
        word = word.strip('.,!?"\'')
        if len(word) > 2 and word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get most frequent meaningful terms
    common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:25]
    
    # Detect content type based on key terms
    teaching_terms = [w for w, c in common_words if w in ['teacher', 'teaching', 'faculty', 'instructor', 'sir', 'mam', 'professor', 'student', 'class', 'course', 'lecture']]
    research_terms = [w for w, c in common_words if w in ['research', 'study', 'analysis', 'data', 'method', 'model', 'results', 'paper', 'experiment']]
    technical_terms = [w for w, c in common_words if w in ['sensor', 'air', 'quality', 'monitoring', 'system', 'technology', 'algorithm', 'machine', 'learning']]
    
    # Determine content context
    is_academic_feedback = len(teaching_terms) > 2
    is_research_paper = len(research_terms) > 3
    is_technical_document = len(technical_terms) > 3
    
    total_words = len(words)
    
    # Generate context-appropriate analysis
    analysis_parts = []
    
    # Opening statement - context aware
    if is_academic_feedback:
        analysis_parts.append(f"Based on comprehensive analysis of {total_words} words of academic feedback, several key themes emerge regarding educational quality and effectiveness.")
    elif is_research_paper:
        analysis_parts.append(f"This document presents a comprehensive analysis of {total_words} words from a research publication, highlighting key methodological approaches and findings.")
    elif is_technical_document:
        analysis_parts.append(f"Analysis of {total_words} words reveals a technical document focused on specialized systems and methodologies.")
    else:
        analysis_parts.append(f"Content analysis of {total_words} words identifies key themes and patterns within the document.")
    
    # Main content assessment
    top_terms = [w for w, c in common_words[:10] if len(w) > 3]
    if top_terms:
        if is_technical_document:
            analysis_parts.append(f"The content focuses on technical domains including: {', '.join(top_terms[:8])}, indicating specialized knowledge in engineering or technological applications.")
        elif is_research_paper:
            analysis_parts.append(f"Research methodology and findings center around: {', '.join(top_terms[:8])}, demonstrating systematic investigation and analysis.")
        elif is_academic_feedback:
            analysis_parts.append(f"Key areas addressed in the feedback include: {', '.join(top_terms[:8])}, indicating these aspects are central to the educational experience.")
        else:
            analysis_parts.append(f"Primary topics identified include: {', '.join(top_terms[:8])}, representing the core focus areas of the content.")
    
    # Context-specific insights
    if is_technical_document:
        analysis_parts.append("The document demonstrates focus on practical applications, system implementation, and performance optimization within specialized technical domains.")
    elif is_research_paper:
        analysis_parts.append("The research exhibits systematic methodology, data-driven analysis, and evidence-based conclusions typical of academic investigation.")
    elif is_academic_feedback:
        analysis_parts.append("The feedback reflects student perspectives on educational delivery, instructional effectiveness, and learning environment quality.")
    else:
        analysis_parts.append("The content provides insights into the subject matter through detailed examination and structured presentation.")
    
    # Summary conclusion
    if is_technical_document:
        analysis_parts.append("This technical analysis offers valuable insights for system development, implementation strategies, and performance enhancement in the relevant domain.")
    elif is_research_paper:
        analysis_parts.append("The research contributes to academic knowledge and provides a foundation for future investigation and practical application.")
    elif is_academic_feedback:
        analysis_parts.append("This analysis provides valuable insights for educational improvement and institutional development.")
    else:
        analysis_parts.append("The document analysis reveals structured insights that contribute to understanding of the subject matter.")
    
    return " ".join(analysis_parts)


def generate_insights(texts, analysis_results, use_gemini: bool = False):
    """Generate key insights from the analysis results."""
    safe_print("[INSIGHTS] Generating insights...")
    
    # Extract key information from analysis results
    sentiment_counts = analysis_results.get("sentiment_counts", {})
    lda_topics = analysis_results.get("lda_top_words", [])
    nmf_topics = analysis_results.get("nmf_top_words", [])
    
    # Analyze text patterns for context detection
    combined_text = " ".join(texts[:1000])  # Limit for analysis
    text_lower = combined_text.lower()
    
    # Detect content type
    is_technical = any(term in text_lower for term in ['sensor', 'air', 'quality', 'monitoring', 'system', 'algorithm', 'machine', 'learning', 'data', 'model'])
    is_research = any(term in text_lower for term in ['research', 'study', 'paper', 'method', 'experiment', 'results', 'analysis'])
    is_academic = any(term in text_lower for term in ['student', 'teacher', 'faculty', 'course', 'class', 'education', 'feedback'])
    is_business = any(term in text_lower for term in ['project', 'management', 'team', 'planning', 'budget', 'schedule', 'resources'])
    
    # Build insights based on actual content
    insights_parts = []
    
    # Opening insight
    total_items = len(texts)
    if is_technical:
        insights_parts.append(f"Analysis of {total_items} technical entries reveals focused expertise in specialized engineering domains.")
    elif is_research:
        insights_parts.append(f"Examination of {total_items} research elements indicates systematic academic investigation with methodological rigor.")
    elif is_business:
        insights_parts.append(f"Review of {total_items} project management elements demonstrates comprehensive organizational planning and execution strategies.")
    elif is_academic:
        insights_parts.append(f"Assessment of {total_items} educational entries shows diverse perspectives on teaching and learning effectiveness.")
    else:
        insights_parts.append(f"Analysis of {total_items} content items provides structured insights into the subject matter.")
    
    # Topic-based insights
    if lda_topics:
        top_topics = lda_topics[:3]  # Top 3 topics
        if is_technical:
            insights_parts.append(f"Key technical areas include: {', '.join([', '.join(topic[:4]) for topic in top_topics])}, indicating focus on system optimization and performance enhancement.")
        elif is_research:
            insights_parts.append(f"Primary research themes encompass: {', '.join([', '.join(topic[:4]) for topic in top_topics])}, demonstrating comprehensive investigative scope.")
        elif is_business:
            insights_parts.append(f"Core management areas involve: {', '.join([', '.join(topic[:4]) for topic in top_topics])}, showing systematic approach to project delivery.")
        elif is_academic:
            insights_parts.append(f"Educational focus areas cover: {', '.join([', '.join(topic[:4]) for topic in top_topics])}, reflecting diverse learning and teaching aspects.")
        else:
            insights_parts.append(f"Main thematic areas include: {', '.join([', '.join(topic[:4]) for topic in top_topics])}, representing core content focus.")
    
    # Sentiment insights if meaningful
    if sentiment_counts and sum(sentiment_counts.values()) > 0:
        total_sentiment = sum(sentiment_counts.values())
        positive_ratio = (sentiment_counts.get('positive', 0) + sentiment_counts.get('very positive', 0)) / total_sentiment
        negative_ratio = (sentiment_counts.get('negative', 0) + sentiment_counts.get('very negative', 0)) / total_sentiment
        
        if positive_ratio > 0.6:
            insights_parts.append(f"Sentiment analysis indicates predominantly positive tone ({positive_ratio:.1%}), suggesting favorable content characteristics.")
        elif negative_ratio > 0.4:
            insights_parts.append(f"Sentiment patterns show notable concerns ({negative_ratio:.1%} negative), highlighting areas requiring attention.")
        else:
            insights_parts.append(f"Sentiment distribution shows balanced perspectives with {positive_ratio:.1%} positive and {negative_ratio:.1%} negative indicators.")
    
    # Context-specific actionable insights
    if is_technical:
        insights_parts.append("Technical implementation focus suggests opportunities for system integration, performance optimization, and scalability enhancement.")
    elif is_research:
        insights_parts.append("Research methodology emphasis indicates potential for expanded investigation, cross-validation studies, and practical application development.")
    elif is_business:
        insights_parts.append("Project management concentration reveals opportunities for process improvement, resource optimization, and stakeholder engagement enhancement.")
    elif is_academic:
        insights_parts.append("Educational assessment patterns suggest opportunities for pedagogical improvement, curriculum enhancement, and learning outcome optimization.")
    else:
        insights_parts.append("Content analysis patterns suggest opportunities for systematic improvement and strategic development initiatives.")
    
    base_insights = " ".join(insights_parts)
    
    # Optionally enhance with Gemini if requested
    if use_gemini:
        try:
            import google.generativeai as genai
            safe_print("[INSIGHTS] Attempting Gemini enhancement...")
            
            genai.configure(api_key=GEMINI_API_KEY)
            models_to_try = ['models/gemini-2.5-flash-preview-05-20', 'models/gemini-2.5-flash']
            
            # Determine context for prompting
            if is_technical:
                context_type = "technical systems and engineering applications"
                insight_focus = "system performance, optimization strategies, and technical implementation approaches"
            elif is_research:
                context_type = "research methodology and academic investigation"
                insight_focus = "research findings, methodological insights, and academic contributions"
            elif is_business:
                context_type = "project management and organizational planning"
                insight_focus = "project efficiency, resource management, and strategic planning opportunities"
            elif is_academic:
                context_type = "educational assessment and learning outcomes"
                insight_focus = "teaching effectiveness, learning patterns, and educational improvement opportunities"
            else:
                context_type = "structured content analysis"
                insight_focus = "key patterns, trends, and improvement opportunities"
            
            for model_name in models_to_try:
                try:
                    safe_print(f"[INSIGHTS] Trying model: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    
                    prompt = f"""
                    You are an expert analyst specializing in {context_type}. Based on the following preliminary insights, generate enhanced, actionable insights that focus on {insight_focus}.
                    
                    PRELIMINARY INSIGHTS:
                    {base_insights}
                    
                    TASK: Create enhanced insights that are:
                    1. Specific and actionable
                    2. Based on the actual content patterns identified
                    3. Focused on practical implications and opportunities
                    4. Written in clear, professional language
                    5. Structured as coherent paragraphs (no bullet points)
                    
                    Provide insights that would be valuable for decision-making and strategic planning in this domain. Focus on what the analysis reveals about opportunities, trends, and recommendations for improvement or optimization.
                    """
                    
                    response = model.generate_content(prompt)
                    enhanced_insights = response.text.strip()
                    safe_print(f"[INSIGHTS] Gemini enhancement success with {model_name}")
                    return clean_repetitions(enhanced_insights)
                    
                except Exception as model_error:
                    safe_print(f"[INSIGHTS] Failed with {model_name}: {model_error}")
                    continue
            
            safe_print("[INSIGHTS] All Gemini models failed, using base insights")
            return base_insights
            
        except Exception as e:
            safe_print(f"[INSIGHTS] Gemini enhancement failed: {e}")
            return base_insights
    else:
        safe_print("[INSIGHTS] Using base insights without Gemini enhancement")
        return base_insights

def generate_sentiment_interpretation(sentiment_counts, texts, use_gemini: bool = False):
    """Generate AI interpretation of sentiment analysis results."""
    safe_print("[SENTIMENT] Generating sentiment interpretation...")
    
    if not sentiment_counts or sum(sentiment_counts.values()) == 0:
        return "No sentiment data available for interpretation."
    
    # Calculate sentiment distribution
    total_items = sum(sentiment_counts.values())
    positive_count = sentiment_counts.get('positive', 0) + sentiment_counts.get('very positive', 0)
    negative_count = sentiment_counts.get('negative', 0) + sentiment_counts.get('very negative', 0)
    neutral_count = sentiment_counts.get('neutral', 0)
    
    positive_ratio = positive_count / total_items if total_items > 0 else 0
    negative_ratio = negative_count / total_items if total_items > 0 else 0
    neutral_ratio = neutral_count / total_items if total_items > 0 else 0
    
    # Analyze content context
    combined_text = " ".join(texts[:500]).lower()  # Sample for context
    is_technical = any(term in combined_text for term in ['sensor', 'air', 'quality', 'monitoring', 'system', 'algorithm', 'machine', 'learning', 'data', 'model'])
    is_research = any(term in combined_text for term in ['research', 'study', 'paper', 'method', 'experiment', 'results', 'analysis'])
    is_academic = any(term in combined_text for term in ['student', 'teacher', 'faculty', 'course', 'class', 'education', 'feedback'])
    is_business = any(term in combined_text for term in ['project', 'management', 'team', 'planning', 'budget', 'schedule', 'resources'])
    
    # Build base interpretation
    interpretation_parts = []
    
    # Opening statement with context
    if is_technical:
        interpretation_parts.append(f"Sentiment analysis of {total_items} technical content items reveals emotional patterns within specialized engineering discourse.")
    elif is_research:
        interpretation_parts.append(f"Sentiment evaluation of {total_items} research elements indicates academic tone and investigative perspective patterns.")
    elif is_business:
        interpretation_parts.append(f"Sentiment assessment of {total_items} business content items shows organizational communication patterns and project-related attitudes.")
    elif is_academic:
        interpretation_parts.append(f"Sentiment analysis of {total_items} educational items reflects diverse perspectives on teaching and learning experiences.")
    else:
        interpretation_parts.append(f"Sentiment analysis of {total_items} content items provides insights into overall emotional tone and perspective patterns.")
    
    # Sentiment distribution analysis
    if positive_ratio > 0.6:
        interpretation_parts.append(f"The sentiment distribution shows a predominantly positive orientation ({positive_ratio:.1%}), indicating favorable attitudes and constructive perspectives throughout the content.")
    elif negative_ratio > 0.5:
        interpretation_parts.append(f"Results indicate a notably negative sentiment bias ({negative_ratio:.1%}), suggesting critical perspectives or areas of concern within the analyzed content.")
    elif neutral_ratio > 0.5:
        interpretation_parts.append(f"The analysis reveals a predominantly neutral tone ({neutral_ratio:.1%}), indicating objective, factual communication with minimal emotional coloring.")
    else:
        interpretation_parts.append(f"Sentiment distribution shows balanced perspectives with {positive_ratio:.1%} positive, {negative_ratio:.1%} negative, and {neutral_ratio:.1%} neutral indicators, reflecting diverse viewpoints.")
    
    # Additional emotional categories if present
    emotion_insights = []
    if sentiment_counts.get('happy', 0) > 0:
        emotion_insights.append(f"{sentiment_counts['happy']} instances of happiness indicators")
    if sentiment_counts.get('trust', 0) > 0:
        emotion_insights.append(f"{sentiment_counts['trust']} expressions of trust and confidence")
    if sentiment_counts.get('angry', 0) > 0:
        emotion_insights.append(f"{sentiment_counts['angry']} signs of frustration or anger")
    if sentiment_counts.get('sad', 0) > 0:
        emotion_insights.append(f"{sentiment_counts['sad']} expressions of disappointment or sadness")
    
    if emotion_insights:
        interpretation_parts.append(f"Detailed emotional analysis identifies {', '.join(emotion_insights)}, providing nuanced understanding of underlying sentiment patterns.")
    
    # Context-specific implications
    if is_technical:
        if positive_ratio > 0.5:
            interpretation_parts.append("Positive sentiment in technical content suggests effective system performance, successful implementation, or satisfactory technical outcomes.")
        elif negative_ratio > 0.4:
            interpretation_parts.append("Negative sentiment patterns may indicate technical challenges, system limitations, or areas requiring optimization and improvement.")
    elif is_research:
        if neutral_ratio > 0.4:
            interpretation_parts.append("High neutral sentiment is typical in research contexts, reflecting objective scientific communication and evidence-based analysis.")
        if positive_ratio > 0.3:
            interpretation_parts.append("Positive sentiment in research content may indicate successful findings, validated hypotheses, or promising research directions.")
    elif is_business:
        if positive_ratio > 0.5:
            interpretation_parts.append("Positive sentiment in business content suggests successful project outcomes, effective team collaboration, or satisfied stakeholders.")
        elif negative_ratio > 0.4:
            interpretation_parts.append("Negative sentiment may reflect project challenges, resource constraints, or areas requiring management attention and intervention.")
    elif is_academic:
        if positive_ratio > 0.5:
            interpretation_parts.append("Positive sentiment in educational content suggests effective teaching, student satisfaction, or successful learning outcomes.")
        elif negative_ratio > 0.4:
            interpretation_parts.append("Negative sentiment may indicate pedagogical challenges, student concerns, or opportunities for educational improvement.")
    
    base_interpretation = " ".join(interpretation_parts)
    
    # Enhance with Gemini if requested
    if use_gemini and total_items > 10:  # Only use Gemini for substantial datasets
        try:
            import google.generativeai as genai
            safe_print("[SENTIMENT] Attempting Gemini enhancement...")
            
            genai.configure(api_key=GEMINI_API_KEY)
            models_to_try = ['models/gemini-2.5-flash-preview-05-20', 'models/gemini-2.5-flash']
            
            # Determine context for prompting
            if is_technical:
                context_desc = "technical systems and engineering documentation"
                focus_areas = "system performance indicators, user satisfaction with technical solutions, and operational effectiveness"
            elif is_research:
                context_desc = "academic research and scholarly investigation"
                focus_areas = "research confidence levels, methodological satisfaction, and investigative perspectives"
            elif is_business:
                context_desc = "business and project management content"
                focus_areas = "stakeholder satisfaction, project success indicators, and organizational effectiveness"
            elif is_academic:
                context_desc = "educational feedback and learning assessment"
                focus_areas = "student satisfaction, teaching effectiveness, and learning experience quality"
            else:
                context_desc = "general content analysis"
                focus_areas = "overall user perspectives, content effectiveness, and audience reception"
            
            for model_name in models_to_try:
                try:
                    safe_print(f"[SENTIMENT] Trying model: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    
                    prompt = f"""
                    You are an expert sentiment analysis interpreter specializing in {context_desc}. Based on the following sentiment analysis results, provide enhanced interpretation focusing on {focus_areas}.
                    
                    SENTIMENT DATA:
                    Total Items: {total_items}
                    Positive: {positive_count} ({positive_ratio:.1%})
                    Negative: {negative_count} ({negative_ratio:.1%})
                    Neutral: {neutral_count} ({neutral_ratio:.1%})
                    Additional emotions: {dict(sentiment_counts)}
                    
                    PRELIMINARY INTERPRETATION:
                    {base_interpretation}
                    
                    TASK: Create an enhanced sentiment interpretation that:
                    1. Explains what these sentiment patterns mean in this specific context
                    2. Identifies key implications and insights
                    3. Suggests what the sentiment reveals about quality, effectiveness, or satisfaction
                    4. Provides actionable insights based on the sentiment distribution
                    5. Uses clear, professional language without bullet points
                    
                    Focus on practical implications that would be valuable for decision-making and improvement strategies.
                    """
                    
                    response = model.generate_content(prompt)
                    enhanced_interpretation = response.text.strip()
                    safe_print(f"[SENTIMENT] Gemini enhancement success with {model_name}")
                    return clean_repetitions(enhanced_interpretation)
                    
                except Exception as model_error:
                    safe_print(f"[SENTIMENT] Failed with {model_name}: {model_error}")
                    continue
            
            safe_print("[SENTIMENT] All Gemini models failed, using base interpretation")
            return base_interpretation
            
        except Exception as e:
            safe_print(f"[SENTIMENT] Gemini enhancement failed: {e}")
            return base_interpretation
    else:
        safe_print("[SENTIMENT] Using base interpretation")
        return base_interpretation

def hybrid_summary(feedback_texts, num_sentences: int = 50, use_gemini: bool = False):
    # Pre-clean raw feedback to remove heavy repetitions
    combined_text = clean_repetitions(" ".join(feedback_texts))
    
    safe_print(f"[SUMMARY] Using Gemini: {use_gemini}")
    safe_print(f"[SUMMARY] Sample text: {combined_text[:200]}...")

    # Always generate a structured analysis first
    structured_summary = generate_structured_analysis(combined_text)
    
    if use_gemini:
        try:
            import google.generativeai as genai
            safe_print("[SUMMARY] Attempting Gemini refinement of structured summary...")
            
            genai.configure(api_key=GEMINI_API_KEY)
            
            models_to_try = ['models/gemini-2.5-flash-preview-05-20', 'models/gemini-2.5-flash', 'models/gemini-flash-latest', 'models/gemini-pro-latest']
            
            for model_name in models_to_try:
                try:
                    safe_print(f"[SUMMARY] Trying model: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    
                    # Detect content type for appropriate prompting
                    text_lower = combined_text.lower()
                    is_technical = any(term in text_lower for term in ['sensor', 'air', 'quality', 'monitoring', 'system', 'algorithm', 'machine', 'learning', 'data', 'model'])
                    is_research = any(term in text_lower for term in ['research', 'study', 'paper', 'method', 'experiment', 'results', 'analysis'])
                    is_academic = any(term in text_lower for term in ['student', 'teacher', 'faculty', 'course', 'class', 'education', 'feedback'])
                    
                    if is_technical:
                        context_desc = "technical document focused on systems, technology, and engineering applications"
                        report_title = "Technical Analysis Report"
                        sections = """
                        **Executive Summary**
                        Key findings and technical insights in 2-3 sentences.
                        
                        **Technical Overview** 
                        Analysis of systems, methodologies, and technical approaches.
                        
                        **Key Technologies and Methods**
                        Most important technical components and methodologies identified.
                        
                        **Implementation Insights**
                        Practical applications and system implementation considerations.
                        
                        **Performance and Effectiveness**
                        Analysis of system performance, efficiency, and effectiveness patterns.
                        
                        **Recommendations**
                        Specific, actionable suggestions for system optimization and development.
                        """
                        language_style = "technical and professional language suitable for engineering and technology professionals"
                    elif is_research:
                        context_desc = "research document containing academic investigation and findings"
                        report_title = "Research Analysis Report"
                        sections = """
                        **Executive Summary**
                        Key research findings and contributions in 2-3 sentences.
                        
                        **Research Methodology**
                        Analysis of research approaches and methodological frameworks.
                        
                        **Key Findings**
                        Most significant discoveries and research outcomes.
                        
                        **Data and Analysis**
                        Examination of data patterns, analytical approaches, and evidence.
                        
                        **Research Implications**
                        Broader implications and significance of the research findings.
                        
                        **Future Directions**
                        Specific suggestions for continued research and development.
                        """
                        language_style = "academic and scholarly language suitable for research publications"
                    elif is_academic:
                        context_desc = "educational feedback data from academic institutions"
                        report_title = "Educational Analysis Report"
                        sections = """
                        **Executive Summary**
                        Key findings about educational quality and effectiveness in 2-3 sentences.
                        
                        **Educational Assessment**
                        Analysis of teaching effectiveness and educational delivery patterns.
                        
                        **Strengths Identified**
                        Most commonly praised aspects and positive characteristics.
                        
                        **Areas for Development**
                        Constructive themes and improvement opportunities.
                        
                        **Learning Environment**
                        Insights into classroom dynamics and engagement patterns.
                        
                        **Recommendations**
                        Specific, actionable suggestions for educational improvement.
                        """
                        language_style = "professional academic language suitable for educational administration"
                    else:
                        context_desc = "document containing structured information and analysis"
                        report_title = "Content Analysis Report"
                        sections = """
                        **Executive Summary**
                        Key insights and main findings in 2-3 sentences.
                        
                        **Content Overview**
                        Analysis of main themes and subject matter.
                        
                        **Key Components**
                        Most important elements and topics identified.
                        
                        **Insights and Patterns**
                        Notable patterns, trends, and analytical observations.
                        
                        **Significance**
                        Importance and relevance of the content and findings.
                        
                        **Recommendations**
                        Specific, actionable suggestions based on the analysis.
                        """
                        language_style = "clear professional language suitable for business and analytical contexts"
                    
                    prompt = f"""
                    You are an expert data analyst. I have analyzed a document and created a preliminary summary. Please refine this analysis into a comprehensive, meaningful, and professional report.
                    
                    CONTEXT: This is a {context_desc}.
                    
                    PRELIMINARY ANALYSIS:
                    {structured_summary}
                    
                    TASK: Create a refined, comprehensive summary with the following structure. Use **double asterisks** around section headings for proper formatting:
                    
                    **{report_title}**
                    {sections}
                    FORMATTING: Use **double asterisks** around each section heading. Write in {language_style}. Make it meaningful, insightful, and actionable. Avoid generic statements and focus on specific insights derived from the actual content.
                    """
                    
                    response = model.generate_content(prompt)
                    gemini_summary = response.text.strip()
                    safe_print(f"[SUMMARY] Gemini refinement success with {model_name}: {gemini_summary[:200]}...")
                    return clean_repetitions(gemini_summary)
                    
                except Exception as model_error:
                    safe_print(f"[SUMMARY] Failed with {model_name}: {model_error}")
                    continue
            
            # If all models failed, return the structured analysis
            safe_print("[SUMMARY] All Gemini models failed, using structured analysis")
            return structured_summary
            
        except Exception as e:
            safe_print(f"[SUMMARY] Gemini import/setup failed: {e}")
            return structured_summary

    else:
        safe_print("[SUMMARY] Using fallback summary method")
        # Use LexRank to produce a concise, readable summary without repetitions
        try:
            text_for_summary = combined_text if combined_text else " ".join(feedback_texts)
            parser = PlaintextParser.from_string(text_for_summary, Tokenizer("english"))
            summarizer = LexRankSummarizer()
            # Keep it short and readable
            max_sentences = min(max(3, num_sentences // 3), 8)
            summary_sentences = summarizer(parser.document, sentences_count=max_sentences)
            summary_text = " ".join(str(s) for s in summary_sentences)
            return clean_repetitions(summary_text)
        except Exception:
            # Robust fallback: unique sentences from original texts
            seen = set()
            unique_bits = []
            for t in feedback_texts:
                s = t.strip()
                if not s:
                    continue
                key = s.lower()
                if key in seen:
                    continue
                seen.add(key)
                unique_bits.append(s)
                if len(unique_bits) >= 8:
                    break
            return clean_repetitions(" ".join(unique_bits))


# ==========================
# Main Pipeline
# ==========================
# ==========================#
# Main Pipeline with Multiple Word Clouds
# ==========================#
def main(feedback_file=None, opportunity_file=None, use_gemini: bool = False, return_data: bool = True, quick_mode: bool = False):
    results = {"plots": {}, "summary_tab": {}, "other_data": {}}

    # Only process uploaded files, no fallback to workspace files
    if not feedback_file and not opportunity_file:
        # If no files provided, check for default files as last resort
        if os.path.exists("merged_student_feedback.csv"):
            feedback_df = load_dataset("merged_student_feedback.csv")
            opportunity_df = feedback_df.copy()  # Use same data for both
            safe_print("[INFO] Using default workspace files as no upload provided")
        else:
            safe_print("[ERROR] No files provided and no default files found")
            results["summary_tab"]["summary_text"] = "**No Data Available**\n\nNo data file was provided for analysis. Please upload a CSV, TSV, Excel, or PDF file containing the data to analyze."
            return results
    else:
        # Process only uploaded files
        try:
            if feedback_file:
                safe_print(f"[UPLOAD] Processing feedback file: {feedback_file}")
                feedback_df = load_dataset(feedback_file)
                opportunity_df = feedback_df.copy()  # Use same data for both
            elif opportunity_file:
                safe_print(f"[UPLOAD] Processing opportunity file: {opportunity_file}")
                opportunity_df = load_dataset(opportunity_file)
                feedback_df = opportunity_df.copy()  # Use same data for both
        except Exception as e:
            safe_print(f"[ERROR] Failed to process uploaded file: {e}")
            results["summary_tab"]["summary_text"] = f"**File Processing Error**\n\nFailed to process the uploaded file: {str(e)}\n\nPlease ensure the file is a valid CSV, TSV, Excel, or PDF file with readable text content."
            return results

    safe_print(f"[COLUMNS] {list(opportunity_df.columns)}")
    feedback_df = feedback_df.drop_duplicates()
    opportunity_df = opportunity_df.drop_duplicates()

    # Detect text column
    text_col = detect_text_column(opportunity_df) or detect_text_column(feedback_df)
    if not text_col:
        safe_print("[WARN] No text column found. Skipping NLP tasks.")
        return results
    safe_print(f"[INFO] Using text column: '{text_col}'")

    # Sample texts
    texts = opportunity_df[text_col].dropna().astype(str).tolist()
    if quick_mode:
        if len(texts) > 3000:
            texts = random.sample(texts, 3000)
    else:
        if len(texts) > 20000:
            texts = random.sample(texts, 20000)

    # ==========================
    # Topic modeling (skip in quick mode)
    # ==========================
    if not quick_mode:
        lda_model, lda_vectorizer = run_lda(texts, n_topics=5, max_features=800)
        nmf_model, nmf_vectorizer = run_nmf(texts, n_topics=5, max_features=1200)
        results["lda_top_words"] = [
            [lda_vectorizer.get_feature_names_out()[i] for i in topic.argsort()[::-1][:12]]
            for topic in lda_model.components_
        ]
        results["nmf_top_words"] = [
            [nmf_vectorizer.get_feature_names_out()[i] for i in topic.argsort()[::-1][:12]]
            for topic in nmf_model.components_
        ]

    # ==========================
    # Sentiment
    # ==========================
    # ==========================
    # Sentiment
    # ==========================
    df_sent, sentiment_counts, fig_path = run_sentiment(opportunity_df, text_col)
    results["sentiment_counts"] = sentiment_counts
    results["plots"]["sentiment_distribution"] = fig_path

    # ==========================
    # Classification (skip in quick mode)
    # ==========================
    if not quick_mode:
        clf_res = classify_isSame(opportunity_df, text_col)
        if clf_res:
            results["classification_metrics"] = clf_res["metrics"]
            results["plots"]["confusion_matrix"] = os.path.join(PLOTS_DIR, "confusion_matrix.png")

    # ==========================
    # Word Clouds
    # ==========================
    # Overall
    generate_wordcloud(texts, filename="wordcloud_overall.png", category="All")
    results["plots"]["wordcloud_overall"] = os.path.join(PLOTS_DIR, "wordcloud_overall.png")

    # By sentiment
    for sentiment in ["positive", "neutral", "negative"]:
        subset = df_sent[df_sent["sentiment_label"] == sentiment][text_col].dropna().astype(str).tolist()
        if subset:
            generate_wordcloud(subset, filename=f"wordcloud_{sentiment}.png", category=f"Sentiment: {sentiment}")
            results["plots"][f"wordcloud_{sentiment}"] = os.path.join(PLOTS_DIR, f"wordcloud_{sentiment}.png")

    # By LDA topic (skip in quick mode)
    if not quick_mode:
        for idx, topic in enumerate(lda_model.components_):
            top_words = [lda_vectorizer.get_feature_names_out()[i] for i in topic.argsort()[::-1][:50]]
            if top_words:
                generate_wordcloud(top_words, filename=f"wordcloud_topic_{idx + 1}.png", category=f"LDA Topic {idx + 1}")
                results["plots"][f"wordcloud_topic_{idx + 1}"] = os.path.join(PLOTS_DIR, f"wordcloud_topic_{idx + 1}.png")

    # ==========================
    # Summary (new tab)
    # ==========================
    results["summary_tab"]["summary_text"] = hybrid_summary(texts, num_sentences=15, use_gemini=use_gemini)
    
    # ==========================
    # Generate Insights and Sentiment Interpretation
    # ==========================
    results["insights"] = generate_insights(texts, results, use_gemini=use_gemini)
    results["sentiment_text"] = generate_sentiment_interpretation(results.get("sentiment_counts", {}), texts, use_gemini=use_gemini)

    # ==========================
    # Additional Insights (real data if available)
    # ==========================
    # Difficulty Distribution
    # Difficulty Distribution
    diff_counts = {}
    # Prefer feedback_df columns if present, else opportunity_df
    if "Difficulty" in feedback_df.columns:
        diff_counts = feedback_df["Difficulty"].dropna().value_counts().to_dict()
    elif "difficulty" in feedback_df.columns:
        diff_counts = feedback_df["difficulty"].dropna().value_counts().to_dict()
    elif "Difficulty" in opportunity_df.columns:
        diff_counts = opportunity_df["Difficulty"].dropna().value_counts().to_dict()
    elif "difficulty" in opportunity_df.columns:
        diff_counts = opportunity_df["difficulty"].dropna().value_counts().to_dict()

    if diff_counts and any(v > 0 for v in diff_counts.values()):
        results["difficulty_counts"] = diff_counts
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=list(diff_counts.keys()), y=list(diff_counts.values()), ax=ax)
        ax.set_title("Difficulty Distribution")
        save_fig(fig, "difficulty_distribution.png")
        results["plots"]["difficulty_distribution"] = os.path.join(PLOTS_DIR, "difficulty_distribution.png")

    # Attendance Distribution
    att_counts = {}
    # Prefer feedback_df columns if present, else opportunity_df
    if "Attendance" in feedback_df.columns:
        att_counts = feedback_df["Attendance"].dropna().value_counts().to_dict()
    elif "attendance" in feedback_df.columns:
        att_counts = feedback_df["attendance"].dropna().value_counts().to_dict()
    elif "Attendance" in opportunity_df.columns:
        att_counts = opportunity_df["Attendance"].dropna().value_counts().to_dict()
    elif "attendance" in opportunity_df.columns:
        att_counts = opportunity_df["attendance"].dropna().value_counts().to_dict()
    elif "attendance_rate" in opportunity_df.columns:
        df_temp = opportunity_df.copy()
        df_temp = df_temp.dropna(subset=["attendance_rate"])
        if not df_temp.empty:
            df_temp["attendance_category"] = pd.cut(
                df_temp["attendance_rate"], bins=[0, 50, 80, 100], labels=["Low", "Medium", "High"]
            )
            att_counts = df_temp["attendance_category"].value_counts().to_dict()

    if att_counts and any(v > 0 for v in att_counts.values()):
        results["attendance_counts"] = att_counts
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=list(att_counts.keys()), y=list(att_counts.values()), ax=ax)
        ax.set_title("Attendance Distribution")
        save_fig(fig, "attendance_distribution.png")
        results["plots"]["attendance_distribution"] = os.path.join(PLOTS_DIR, "attendance_distribution.png")

    # Feature Correlation (numeric)
    numeric_df = opportunity_df.select_dtypes(include=[np.number]).dropna(how="all")
    if not numeric_df.empty:
        corr_matrix = numeric_df.corr().round(2)
        if corr_matrix.size > 0 and not corr_matrix.isnull().all().all():
            results["correlation_data"] = {"features": list(corr_matrix.columns), "matrix": corr_matrix.values.tolist()}
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(pd.DataFrame(corr_matrix.values, index=corr_matrix.index, columns=corr_matrix.columns),
                        annot=True, cmap="coolwarm", ax=ax)
            ax.set_title("Feature Correlation Heatmap")
            save_fig(fig, "feature_correlation.png")
            results["plots"]["feature_correlation"] = os.path.join(PLOTS_DIR, "feature_correlation.png")

    safe_print("\n[DONE] All steps finished. Check 'plots/' folder.")
    if return_data:
        return results



# ==========================
# CLI Mode
# ==========================
if __name__ == "__main__":
    output_results = main(use_gemini=True)
    print("\n[FRONT-END DATA]")
    print(json.dumps(output_results, indent=2))
    
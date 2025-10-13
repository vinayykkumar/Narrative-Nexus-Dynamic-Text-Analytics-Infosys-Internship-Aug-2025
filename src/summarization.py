"""
Hybrid summarizer: extractive (always) + abstractive (optional).
CPU-optimized with smart fallbacks.
"""
import re
import numpy as np
from typing import List, Dict, Optional
from functools import lru_cache


# ============ Extractive Summarization (MMR) ============

def _safe_import_sklearn():
    """Import scikit-learn components."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        return TfidfVectorizer, cosine_similarity
    except ImportError:
        raise ImportError("Install scikit-learn: pip install scikit-learn")


@lru_cache(maxsize=1)
def _get_sentence_model():
    """Load sentence-transformers model (cached)."""
    try:
        from sentence_transformers import SentenceTransformer
        # Use smallest model (90MB)
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception:
        return None


def extractive_summary_tfidf(
    sentences: List[str],
    k: int = 8,
    lambda_param: float = 0.7
) -> List[str]:
    """
    MMR-based extractive summarization using TF-IDF.
    Fast, no external models needed.
    """
    if not sentences or k <= 0:
        return []
    
    TfidfVectorizer, cosine_similarity = _safe_import_sklearn()
    
    # Vectorize sentences
    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),
        max_features=5000
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(sentences)
    except ValueError:  # Not enough sentences
        return sentences[:k]
    
    # Convert to dense array
    if hasattr(tfidf_matrix, 'toarray'):
        tfidf_matrix = tfidf_matrix.toarray()
    
    # Document centroid
    doc_vector = tfidf_matrix.mean(axis=0, keepdims=True)
    
    # Relevance scores
    relevance = cosine_similarity(tfidf_matrix, doc_vector).flatten()
    
    # MMR selection
    selected_indices = []
    available = list(range(len(sentences)))
    
    for _ in range(min(k, len(sentences))):
        if not available:
            break
        
        if not selected_indices:
            # First sentence: most relevant
            idx = int(np.argmax(relevance))
            selected_indices.append(idx)
            available.remove(idx)
        else:
            # Balance relevance and diversity
            selected_vectors = tfidf_matrix[selected_indices]
            candidate_vectors = tfidf_matrix[available]
            
            # Similarity to already selected
            similarity_to_selected = cosine_similarity(
                candidate_vectors,
                selected_vectors
            ).max(axis=1)
            
            # MMR score
            mmr_scores = (
                lambda_param * relevance[available] -
                (1 - lambda_param) * similarity_to_selected
            )
            
            # Pick best
            best_idx = int(np.argmax(mmr_scores))
            selected_indices.append(available[best_idx])
            available.remove(available[best_idx])
    
    # Return in original order
    selected_indices.sort()
    return [sentences[i] for i in selected_indices]


def extractive_summary_embeddings(
    sentences: List[str],
    k: int = 8,
    lambda_param: float = 0.7
) -> List[str]:
    """
    MMR using sentence embeddings (better quality, slower).
    Falls back to TF-IDF if model unavailable.
    """
    model = _get_sentence_model()
    if model is None:
        # Fallback to TF-IDF
        return extractive_summary_tfidf(sentences, k, lambda_param)
    
    if not sentences or k <= 0:
        return []
    
    _, cosine_similarity = _safe_import_sklearn()
    
    # Encode sentences
    try:
        embeddings = model.encode(sentences, show_progress_bar=False)
    except Exception:
        return extractive_summary_tfidf(sentences, k, lambda_param)
    
    # Document centroid
    doc_vector = embeddings.mean(axis=0, keepdims=True)
    
    # Relevance scores
    relevance = cosine_similarity(embeddings, doc_vector).flatten()
    
    # MMR selection (same as TF-IDF version)
    selected_indices = []
    available = list(range(len(sentences)))
    
    for _ in range(min(k, len(sentences))):
        if not available:
            break
        
        if not selected_indices:
            idx = int(np.argmax(relevance))
            selected_indices.append(idx)
            available.remove(idx)
        else:
            selected_vectors = embeddings[selected_indices]
            candidate_vectors = embeddings[available]
            
            similarity_to_selected = cosine_similarity(
                candidate_vectors,
                selected_vectors
            ).max(axis=1)
            
            mmr_scores = (
                lambda_param * relevance[available] -
                (1 - lambda_param) * similarity_to_selected
            )
            
            best_idx = int(np.argmax(mmr_scores))
            selected_indices.append(available[best_idx])
            available.remove(available[best_idx])
    
    selected_indices.sort()
    return [sentences[i] for i in selected_indices]


# ============ Abstractive Summarization ============

@lru_cache(maxsize=2)
def _get_abstractive_model(model_name: str = "distilbart"):
    """Load abstractive model (cached, CPU-friendly)."""
    try:
        from transformers import pipeline
        
        model_map = {
            "distilbart": "sshleifer/distilbart-cnn-12-6",  # 500MB, fastest
            "bart": "facebook/bart-large-cnn",               # 1.6GB, better quality
        }
        
        if model_name not in model_map:
            model_name = "distilbart"
        
        # Force CPU
        return pipeline(
            "summarization",
            model=model_map[model_name],
            device=-1  # CPU
        )
    except Exception as e:
        print(f"Could not load abstractive model: {e}")
        return None


def abstractive_summary(
    text: str,
    min_length: int = 100,
    max_length: int = 250,
    model_name: str = "distilbart"
) -> Optional[str]:
    """
    Abstractive summarization using transformers.
    Returns None if model unavailable (graceful degradation).
    """
    pipe = _get_abstractive_model(model_name)
    if pipe is None:
        return None
    
    if not text or len(text.split()) < 50:
        return None
    
    try:
        # Truncate if too long (model limit: ~1024 tokens)
        words = text.split()
        if len(words) > 800:
            text = " ".join(words[:800])
        
        result = pipe(
            text,
            min_length=min_length,
            max_length=max_length,
            do_sample=False,
            truncation=True
        )
        
        if result and isinstance(result, list) and len(result) > 0:
            summary = result[0].get('summary_text', '')
            return summary.strip()
    except Exception as e:
        print(f"Abstractive summarization failed: {e}")
    
    return None


# ============ Main Summarization Pipeline ============

def summarize_document(
    text: str,
    *,
    mode: str = "hybrid",  # "extractive", "abstractive", "hybrid"
    num_sentences: int = 10,
    min_words: int = 150,
    max_words: int = 300,
    use_embeddings: bool = True,
    model_name: str = "distilbart"
) -> Dict[str, any]:
    """
    Main summarization function.
    
    Args:
        text: Cleaned text to summarize
        mode: "extractive" (fast), "abstractive" (quality), "hybrid" (best)
        num_sentences: Number of sentences for extractive stage
        min_words: Minimum summary length (words)
        max_words: Maximum summary length (words)
        use_embeddings: Use sentence embeddings (better quality, slower)
    
    Returns:
        {
            "summary": final summary text,
            "extractive_summary": extractive stage output,
            "mode_used": actual mode used (may fallback),
            "word_count": summary word count,
        }
    """
    from .cleaners import split_sentences
    
    # Split into sentences
    sentences = split_sentences(text)
    
    if not sentences:
        return {
            "summary": "",
            "extractive_summary": "",
            "mode_used": "none",
            "word_count": 0,
        }
    
    # If text is already short, return it
    if len(sentences) <= num_sentences:
        summary = " ".join(sentences)
        return {
            "summary": summary,
            "extractive_summary": summary,
            "mode_used": "passthrough",
            "word_count": len(summary.split()),
        }
    
    # Extractive stage
    if use_embeddings:
        extractive_sents = extractive_summary_embeddings(sentences, k=num_sentences)
    else:
        extractive_sents = extractive_summary_tfidf(sentences, k=num_sentences)
    
    extractive_text = " ".join(extractive_sents)
    
    # Early return for extractive-only mode
    if mode == "extractive":
        return {
            "summary": extractive_text,
            "extractive_summary": extractive_text,
            "mode_used": "extractive",
            "word_count": len(extractive_text.split()),
        }
    
    # Abstractive stage (if requested)
    if mode in ["abstractive", "hybrid"]:
        abstractive_text = abstractive_summary(
            extractive_text,
            min_length=min_words,
            max_length=max_words,
            model_name=model_name
        )
        
        if abstractive_text:
            return {
                "summary": abstractive_text,
                "extractive_summary": extractive_text,
                "mode_used": "hybrid" if mode == "hybrid" else "abstractive",
                "word_count": len(abstractive_text.split()),
            }
    
    # Fallback to extractive if abstractive failed
    return {
        "summary": extractive_text,
        "extractive_summary": extractive_text,
        "mode_used": "extractive_fallback",
        "word_count": len(extractive_text.split()),
    }


# ============ Topic-wise Summarization ============

def summarize_by_topics(
    documents: List[str],
    topic_assignments: List[int],
    num_topics: int,
    sentences_per_topic: int = 5
) -> Dict[int, str]:
    """
    Generate summaries for each topic.
    
    Args:
        documents: List of document texts
        topic_assignments: Topic ID for each document (from argmax)
        num_topics: Total number of topics
        sentences_per_topic: Sentences to extract per topic
    
    Returns:
        Dictionary mapping topic_id -> summary
    """
    from .cleaners import split_sentences
    
    topic_summaries = {}
    
    for topic_id in range(num_topics):
        # Get documents for this topic
        topic_docs = [
            documents[i] for i, t in enumerate(topic_assignments)
            if t == topic_id
        ]
        
        if not topic_docs:
            topic_summaries[topic_id] = ""
            continue
        
        # Combine and split into sentences
        combined_text = " ".join(topic_docs)
        sentences = split_sentences(combined_text)
        
        # Extract key sentences
        if len(sentences) <= sentences_per_topic:
            summary_sentences = sentences
        else:
            summary_sentences = extractive_summary_tfidf(
                sentences,
                k=sentences_per_topic,
                lambda_param=0.7
            )
        
        topic_summaries[topic_id] = " ".join(summary_sentences)
    
    return topic_summaries
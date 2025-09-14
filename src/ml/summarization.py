# --- Extractive Summarization (Sumy) ---
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

def extractive_summary(text: str, sentence_count: int = 3) -> str:
    """Extractive summarization using Sumy LSA"""
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, sentence_count)
        return " ".join(str(sentence) for sentence in summary)
    except Exception:
        return " ".join(text.split(".")[:3])

# --- Abstractive Summarization (Transformers) ---
from transformers import pipeline

def abstractive_summary(text: str, model_name='sshleifer/distilbart-cnn-12-6') -> str:
    """Abstractive summarization using BART"""
    summarizer = pipeline("summarization", model=model_name)
    out = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return out[0]['summary_text']

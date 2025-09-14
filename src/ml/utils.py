import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK data (only once)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

STOPWORDS = set(stopwords.words('english'))
LEMMATIZER = WordNetLemmatizer()

def clean_text(text: str) -> str:
    """Lowercase, remove URLs, punctuation, etc."""
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", '', text)
    text = re.sub(r"[^a-z0-9\s]", ' ', text)
    text = re.sub(r"\s+", ' ', text).strip()
    return text

def preprocess_text(text: str, remove_stopwords: bool = True, lemmatize: bool = True) -> str:
    """Clean + tokenize + (optional) stopword removal + lemmatization"""
    text = clean_text(text)
    tokens = nltk.word_tokenize(text)
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS]
    if lemmatize:
        tokens = [LEMMATIZER.lemmatize(t) for t in tokens]
    return ' '.join(tokens)

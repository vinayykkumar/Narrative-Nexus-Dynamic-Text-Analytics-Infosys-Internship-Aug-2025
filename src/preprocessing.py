# src/preprocessing.py
"""
Preprocessing pipeline (simple + lemmatization).

Steps:
- Lowercasing
- Remove URLs
- Remove HTML tags
- Remove punctuation
- Tokenize (split on whitespace)
- Remove stopwords
- Lemmatization (batched with spaCy)
- Save results: one document per line, plus vocab.json
"""

import re, html, json, argparse, logging
from pathlib import Path
from typing import List, Iterable
from collections import Counter

import nltk
from nltk.corpus import stopwords
from nltk import download as nltk_download

# load spaCy
try:
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
except Exception:
    nlp = None

# ensure nltk stopwords
nltk_download('stopwords', quiet=True)

STOPWORDS = set(stopwords.words('english'))
logger = logging.getLogger("preproc")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# regex
URL_RE = re.compile(r'https?://\S+|www\.\S+')
HTML_RE = re.compile(r'<.*?>')
PUNCT_RE = re.compile(r'[^\w\s]')

def clean_text(text: str) -> str:
    if text is None:
        return ""
    t = str(text).lower()
    t = URL_RE.sub(" ", t)
    t = HTML_RE.sub(" ", html.unescape(t))
    t = PUNCT_RE.sub(" ", t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def tokenize(text: str) -> List[str]:
    return [tok for tok in text.split() if tok]

def remove_stop(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]

def lemmatize_batch(token_lists: List[List[str]], batch_size=64, n_process=1) -> List[List[str]]:
    if nlp is None:
        logger.warning("spaCy not available -> skipping lemmatization")
        return token_lists
    texts = [" ".join(toks) for toks in token_lists]
    lemmatized = []
    for doc in nlp.pipe(texts, batch_size=batch_size, n_process=n_process):
        lem = [token.lemma_ for token in doc if not token.is_space]
        lemmatized.append(lem)
    return lemmatized

def preprocess_docs(docs: Iterable[str], batch_size=64, n_process=1) -> List[List[str]]:
    docs = list(docs)
    logger.info("Cleaning + tokenizing %d docs", len(docs))
    token_lists = []
    for d in docs:
        cleaned = clean_text(d)
        toks = tokenize(cleaned)
        toks = remove_stop(toks)
        token_lists.append(toks)
    if nlp is not None:
        logger.info("Lemmatizing %d docs (batch=%d, n_process=%d)", len(token_lists), batch_size, n_process)
        token_lists = lemmatize_batch(token_lists, batch_size=batch_size, n_process=n_process)
    return token_lists

def save_lines(token_lists: List[List[str]], out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf8") as fw:
        for toks in token_lists:
            fw.write(" ".join(toks) + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="input file (csv/json/txt)")
    parser.add_argument("--text-col", default=None, help="column with text (csv/json only)")
    parser.add_argument("--out", required=True, help="output file (.txt)")
    parser.add_argument("--sample", type=int, default=0, help="process only first N docs")
    parser.add_argument("--batch-size", type=int, default=64, help="spaCy batch size")
    parser.add_argument("--n-process", type=int, default=1, help="spaCy n_process")
    args = parser.parse_args()

    inp = Path(args.input)
    docs = []
    if inp.suffix.lower() == ".csv":
        import pandas as pd
        df = pd.read_csv(inp)
        col = args.text_col or [c for c in df.columns if "text" in c.lower() or "description" in c.lower() or "objective" in c.lower()][0]
        docs = df[col].astype(str).fillna("").tolist()
    elif inp.suffix.lower() == ".json":
        import pandas as pd
        try:
            df = pd.read_json(inp, lines=True)
        except Exception:
            df = pd.read_json(inp)
        col = args.text_col or [c for c in df.columns if "text" in c.lower() or "description" in c.lower() or "objective" in c.lower()][0]
        docs = df[col].astype(str).fillna("").tolist()
    elif inp.suffix.lower() == ".txt":
        docs = [l.strip() for l in open(inp, encoding="utf8") if l.strip()]
    else:
        raise ValueError("Unsupported file type")

    if args.sample > 0:
        docs = docs[: args.sample]

    token_lists = preprocess_docs(docs, batch_size=args.batch_size, n_process=args.n_process)
    save_lines(token_lists, Path(args.out))

    counter = Counter()
    for toks in token_lists:
        counter.update(toks)
    vocab_path = Path(args.out).with_suffix(".vocab.json")
    with open(vocab_path, "w", encoding="utf8") as vf:
        json.dump(counter.most_common(), vf, ensure_ascii=False, indent=2)

    logger.info("Saved %d docs -> %s (vocab=%s)", len(token_lists), args.out, vocab_path)

if __name__ == "__main__":
    main()


"""
AI Narrative Nexus - Data Preprocessing Pipeline
Python implementation for text cleaning, normalization, and tokenization
"""

import pandas as pd
import numpy as np
import re
import string
from typing import List, Dict, Tuple, Optional
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import pickle
import json
from pathlib import Path
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextPreprocessor:
    """
    Comprehensive text preprocessing pipeline for AI Narrative Nexus
    """
    
    def __init__(self, 
                 remove_stopwords: bool = True,
                 use_stemming: bool = True,
                 use_lemmatization: bool = False,
                 min_token_length: int = 2,
                 max_token_length: int = 50):
        """
        Initialize the text preprocessor
        
        Args:
            remove_stopwords: Whether to remove English stopwords
            use_stemming: Whether to apply Porter stemming
            use_lemmatization: Whether to apply lemmatization
            min_token_length: Minimum token length to keep
            max_token_length: Maximum token length to keep
        """
        self.remove_stopwords = remove_stopwords
        self.use_stemming = use_stemming
        self.use_lemmatization = use_lemmatization
        self.min_token_length = min_token_length
        self.max_token_length = max_token_length
        
        # Initialize NLTK components
        self.stop_words = set(stopwords.words('english')) if remove_stopwords else set()
        self.stemmer = PorterStemmer() if use_stemming else None
        self.lemmatizer = WordNetLemmatizer() if use_lemmatization else None
        
        # Additional stopwords for better cleaning
        self.stop_words.update(['would', 'could', 'should', 'might', 'must', 'shall'])
        
        logger.info("TextPreprocessor initialized")
        logger.info(f"Stopwords: {remove_stopwords}, Stemming: {use_stemming}, Lemmatization: {use_lemmatization}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing URLs, emails, special characters, etc.
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text string
        """
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs (comprehensive patterns)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'ftp://[^\s]+', '', text)
        
        # Remove email addresses (comprehensive pattern)
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove social media mentions and hashtags
        text = re.sub(r'@\w+', '', text)  # Remove @mentions
        text = re.sub(r'#\w+', '', text)  # Remove #hashtags
        
        # Remove numbers (all numeric patterns)
        text = re.sub(r'\d+\.?\d*', '', text)  # Numbers including decimals
        text = re.sub(r'\b\d+\b', '', text)    # Standalone numbers
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove all punctuation and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by expanding contractions and handling punctuation
        
        Args:
            text: Cleaned text string
            
        Returns:
            Normalized text string
        """
        if not isinstance(text, str):
            return ""
        
        # Expand common contractions
        contractions = {
            "won't": "will not",
            "can't": "cannot",
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would",
            "'m": " am",
            "it's": "it is",
            "that's": "that is",
            "there's": "there is",
            "here's": "here is",
            "what's": "what is",
            "where's": "where is",
            "how's": "how is",
            "let's": "let us"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        # Remove punctuation except for word-internal apostrophes
        text = re.sub(r"[^\w\s]", " ", text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into individual words and apply stemming/lemmatization
        
        Args:
            text: Normalized text string
            
        Returns:
            List of processed tokens
        """
        if not isinstance(text, str):
            return []
        
        # Tokenize using NLTK
        tokens = word_tokenize(text)
        
        # Filter tokens by length
        tokens = [token for token in tokens if 
                 self.min_token_length <= len(token) <= self.max_token_length]
        
        # Remove stopwords
        if self.remove_stopwords:
            tokens = [token for token in tokens if token.lower() not in self.stop_words]
        
        # Remove tokens that are just numbers
        tokens = [token for token in tokens if not token.isdigit()]
        
        # Apply stemming or lemmatization
        if self.use_stemming and self.stemmer:
            tokens = [self.stemmer.stem(token) for token in tokens]
        elif self.use_lemmatization and self.lemmatizer:
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        return tokens
    
    def preprocess_text(self, text: str) -> Tuple[str, str, List[str]]:
        """
        Complete preprocessing pipeline for a single text
        
        Args:
            text: Raw text string
            
        Returns:
            Tuple of (cleaned_text, normalized_text, tokens)
        """
        cleaned = self.clean_text(text)
        normalized = self.normalize_text(cleaned)
        tokens = self.tokenize_text(normalized)
        
        return cleaned, normalized, tokens
    
    def preprocess_dataframe(self, df: pd.DataFrame, text_column: str, 
                           label_column: Optional[str] = None) -> pd.DataFrame:
        """
        Preprocess an entire dataframe
        
        Args:
            df: Input dataframe
            text_column: Name of column containing text
            label_column: Name of column containing labels (optional)
            
        Returns:
            Processed dataframe with additional columns
        """
        logger.info(f"Preprocessing dataframe with {len(df)} rows")
        
        # Create copy to avoid modifying original
        processed_df = df.copy()
        
        # Apply preprocessing to each text
        results = processed_df[text_column].apply(self.preprocess_text)
        
        # Extract results into separate columns
        processed_df['cleaned_text'] = results.apply(lambda x: x[0])
        processed_df['normalized_text'] = results.apply(lambda x: x[1])
        processed_df['tokens'] = results.apply(lambda x: x[2])
        processed_df['token_count'] = processed_df['tokens'].apply(len)
        processed_df['processed_text'] = processed_df['tokens'].apply(lambda x: ' '.join(x))
        
        # Remove rows with no tokens
        processed_df = processed_df[processed_df['token_count'] > 0]
        
        logger.info(f"Preprocessing complete. {len(processed_df)} rows remaining after filtering")
        
        return processed_df

class DatasetLoader:
    """
    Load and prepare datasets for preprocessing
    """
    
    @staticmethod
    def load_amazon_alexa(file_path: str) -> pd.DataFrame:
        """Load Amazon Alexa reviews dataset"""
        logger.info(f"Loading Amazon Alexa dataset from {file_path}")
        
        df = pd.read_csv(file_path, sep='\t')
        
        # Rename columns for consistency
        df = df.rename(columns={
            'verified_reviews': 'text',
            'feedback': 'label'
        })
        
        # Convert feedback to binary (1 for positive, 0 for negative)
        df['label'] = df['label'].astype(int)
        
        # Remove rows with missing text
        df = df.dropna(subset=['text'])
        
        logger.info(f"Loaded {len(df)} Amazon Alexa reviews")
        return df
    
    @staticmethod
    def load_twitter_sentiment(file_path: str, sample_size: Optional[int] = None) -> pd.DataFrame:
        """Load Twitter sentiment dataset"""
        logger.info(f"Loading Twitter sentiment dataset from {file_path}")
        
        df = pd.read_csv(file_path)
        
        # Sample if requested (useful for large datasets)
        if sample_size and len(df) > sample_size:
            df = df.sample(n=sample_size, random_state=42)
            logger.info(f"Sampled {sample_size} tweets from dataset")
        
        # Remove rows with missing text
        df = df.dropna(subset=['text'])
        
        # Ensure labels are binary
        df['sentiment'] = df['sentiment'].astype(int)
        df = df.rename(columns={'sentiment': 'label'})
        
        logger.info(f"Loaded {len(df)} tweets")
        return df
    
    @staticmethod
    def load_amazon_reviews(file_path: str, sample_size: Optional[int] = None) -> pd.DataFrame:
        """Load Amazon product reviews dataset"""
        logger.info(f"Loading Amazon reviews dataset from {file_path}")
        
        # This dataset has no header, columns are: rating, title, review
        df = pd.read_csv(file_path, header=None, names=['rating', 'title', 'review'])
        
        # Sample if requested
        if sample_size and len(df) > sample_size:
            df = df.sample(n=sample_size, random_state=42)
            logger.info(f"Sampled {sample_size} reviews from dataset")
        
        # Use review text as main text
        df['text'] = df['review']
        
        # Convert ratings to binary sentiment (1-2 negative, 4-5 positive, ignore 3)
        df['label'] = df['rating'].apply(lambda x: 0 if x in [1, 2] else (1 if x in [4, 5] else -1))
        df = df[df['label'] != -1]  # Remove neutral ratings
        
        # Remove rows with missing text
        df = df.dropna(subset=['text'])
        
        logger.info(f"Loaded {len(df)} Amazon reviews")
        return df

class FeatureExtractor:
    """
    Extract features from preprocessed text for machine learning
    """
    
    def __init__(self, max_features: int = 10000, ngram_range: Tuple[int, int] = (1, 2)):
        """
        Initialize feature extractor
        
        Args:
            max_features: Maximum number of features to extract
            ngram_range: Range of n-grams to consider
        """
        self.max_features = max_features
        self.ngram_range = ngram_range
        
        # Initialize vectorizers
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words='english'
        )
        
        self.count_vectorizer = CountVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words='english'
        )
        
        logger.info(f"FeatureExtractor initialized with max_features={max_features}, ngram_range={ngram_range}")
    
    def fit_transform_tfidf(self, texts: List[str]) -> np.ndarray:
        """
        Fit TF-IDF vectorizer and transform texts
        
        Args:
            texts: List of preprocessed text strings
            
        Returns:
            TF-IDF feature matrix
        """
        logger.info("Fitting TF-IDF vectorizer")
        features = self.tfidf_vectorizer.fit_transform(texts)
        logger.info(f"TF-IDF features shape: {features.shape}")
        return features.toarray()
    
    def fit_transform_count(self, texts: List[str]) -> np.ndarray:
        """
        Fit Count vectorizer and transform texts
        
        Args:
            texts: List of preprocessed text strings
            
        Returns:
            Count feature matrix
        """
        logger.info("Fitting Count vectorizer")
        features = self.count_vectorizer.fit_transform(texts)
        logger.info(f"Count features shape: {features.shape}")
        return features.toarray()
    
    def get_feature_names(self, vectorizer_type: str = 'tfidf') -> List[str]:
        """
        Get feature names from fitted vectorizer
        
        Args:
            vectorizer_type: 'tfidf' or 'count'
            
        Returns:
            List of feature names
        """
        if vectorizer_type == 'tfidf':
            return self.tfidf_vectorizer.get_feature_names_out().tolist()
        else:
            return self.count_vectorizer.get_feature_names_out().tolist()
    
    def save_vectorizers(self, output_dir: str):
        """Save fitted vectorizers for later use"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save TF-IDF vectorizer
        with open(output_path / 'tfidf_vectorizer.pkl', 'wb') as f:
            pickle.dump(self.tfidf_vectorizer, f)
        
        # Save Count vectorizer
        with open(output_path / 'count_vectorizer.pkl', 'wb') as f:
            pickle.dump(self.count_vectorizer, f)
        
        logger.info(f"Vectorizers saved to {output_dir}")

def save_preprocessed_data(df: pd.DataFrame, output_path: str, format: str = 'csv'):
    """
    Save preprocessed data to file
    
    Args:
        df: Preprocessed dataframe
        output_path: Output file path
        format: Output format ('csv' or 'json')
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(exist_ok=True)
    
    if format == 'csv':
        # Convert tokens list to string for CSV
        df_save = df.copy()
        df_save['tokens'] = df_save['tokens'].apply(lambda x: ' '.join(x) if isinstance(x, list) else x)
        df_save.to_csv(output_file, index=False)
    elif format == 'json':
        df.to_json(output_file, orient='records', indent=2)
    
    logger.info(f"Preprocessed data saved to {output_path}")

def generate_preprocessing_report(df: pd.DataFrame, output_path: str):
    """
    Generate a comprehensive preprocessing report
    
    Args:
        df: Preprocessed dataframe
        output_path: Output file path for report
    """
    report = []
    report.append("# AI Narrative Nexus - Preprocessing Report")
    report.append(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Basic statistics
    report.append("## Dataset Statistics")
    report.append(f"- Total records: {len(df):,}")
    report.append(f"- Average text length: {df['normalized_text'].str.len().mean():.2f} characters")
    report.append(f"- Average token count: {df['token_count'].mean():.2f} tokens")
    report.append("")
    
    # Token statistics
    all_tokens = [token for tokens in df['tokens'] for token in tokens]
    unique_tokens = set(all_tokens)
    
    report.append("## Token Statistics")
    report.append(f"- Total tokens: {len(all_tokens):,}")
    report.append(f"- Unique tokens: {len(unique_tokens):,}")
    report.append(f"- Vocabulary diversity: {len(unique_tokens)/len(all_tokens)*100:.2f}%")
    report.append("")
    
    # Most common tokens
    from collections import Counter
    token_counts = Counter(all_tokens)
    most_common = token_counts.most_common(20)
    
    report.append("## Most Common Tokens")
    for i, (token, count) in enumerate(most_common, 1):
        report.append(f"{i:2d}. {token}: {count:,} occurrences")
    report.append("")
    
    # Label distribution if available
    if 'label' in df.columns:
        label_dist = df['label'].value_counts().sort_index()
        report.append("## Label Distribution")
        for label, count in label_dist.items():
            report.append(f"- Label {label}: {count:,} samples ({count/len(df)*100:.1f}%)")
        report.append("")
    
    # Token length distribution
    token_lengths = [len(token) for tokens in df['tokens'] for token in tokens]
    length_counter = Counter(token_lengths)
    
    report.append("## Token Length Distribution")
    for length in sorted(length_counter.keys())[:10]:  # Show first 10 lengths
        count = length_counter[length]
        report.append(f"- {length} characters: {count:,} tokens")
    report.append("")
    
    # Save report
    with open(output_path, 'w') as f:
        f.write('\n'.join(report))
    
    logger.info(f"Preprocessing report saved to {output_path}")

if __name__ == "__main__":
    # This will be used when running the script directly
    logger.info("TextPreprocessor module loaded successfully")

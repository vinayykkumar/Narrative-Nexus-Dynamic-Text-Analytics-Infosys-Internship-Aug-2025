#!/usr/bin/env python
# coding: utf-8

# ## NarrativeNexus Project: Text Cleaning Implementation
# 
# **Objectives:**
# - Remove special characters, punctuation, and stop words
# - Apply preprocessing to BBC, CNN/DailyMail, and IMDB datasets
# - Save cleaned datasets

# In[1]:


# Import required libraries
import pandas as pd
import numpy as np
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

# Initialize tools
stop_words = set(stopwords.words('english'))
print(f"✅ Setup complete. Loaded {len(stop_words)} stop words.")


# In[2]:


# Define text cleaning functions
def clean_special_characters(text):
    """Remove special characters, keep only letters, numbers, and spaces"""
    if pd.isna(text):
        return ""
    text = str(text)
    # Remove special characters
    cleaned = re.sub(r'[^\w\s]', ' ', text)
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def remove_stop_words(text, keep_negations=True):
    """Remove stop words while preserving negations"""
    if pd.isna(text):
        return ""
    text = str(text)
    
    # Keep important negation words
    stop_words_filtered = stop_words.copy()
    if keep_negations:
        important_words = {'not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing'}
        stop_words_filtered = stop_words_filtered - important_words
    
    # Tokenize and filter
    tokens = word_tokenize(text.lower())
    filtered_tokens = [word for word in tokens if word not in stop_words_filtered]
    return ' '.join(filtered_tokens)

def clean_text_pipeline(text):
    """Complete text cleaning pipeline"""
    if pd.isna(text):
        return ""
    
    # Step 1: Convert to lowercase
    cleaned = str(text).lower()
    
    # Step 2: Remove special characters
    cleaned = clean_special_characters(cleaned)
    
    # Step 3: Remove stop words
    cleaned = remove_stop_words(cleaned, keep_negations=True)
    
    return cleaned

print("✅ Text cleaning functions defined.")


# In[3]:


# Load datasets
data_dir = "../data"
datasets = {}

# Load BBC News Dataset
try:
    bbc_df = pd.read_csv(f"{data_dir}/bbc-text.csv")
    datasets['BBC'] = bbc_df
    print(f"✅ BBC Dataset: {len(bbc_df)} articles loaded")
except Exception as e:
    print(f"❌ Error loading BBC dataset: {e}")

# Load CNN/DailyMail Dataset
try:
    cnn_df = pd.read_csv(f"{data_dir}/cnn_dailymail.csv")
    datasets['CNN'] = cnn_df
    print(f"✅ CNN Dataset: {len(cnn_df)} articles loaded")
except Exception as e:
    print(f"❌ Error loading CNN dataset: {e}")

# Load IMDB Dataset (subset for demo)
try:
    imdb_df = pd.read_csv(f"{data_dir}/imdb-dataset.csv", nrows=1000)
    datasets['IMDB'] = imdb_df
    print(f"✅ IMDB Dataset: {len(imdb_df)} reviews loaded")
except Exception as e:
    print(f"❌ Error loading IMDB dataset: {e}")

print(f"\n📊 Total datasets loaded: {len(datasets)}")


# In[4]:


# Clean BBC News Dataset
if 'BBC' in datasets:
    print("🧹 Cleaning BBC News Dataset...")
    bbc_df = datasets['BBC'].copy()
    
    # Apply cleaning
    tqdm.pandas(desc="Processing BBC")
    bbc_df['text_cleaned'] = bbc_df['text'].progress_apply(clean_text_pipeline)
    
    # Calculate metrics
    original_avg = bbc_df['text'].str.len().mean()
    cleaned_avg = bbc_df['text_cleaned'].str.len().mean()
    reduction = ((original_avg - cleaned_avg) / original_avg * 100)
    
    print(f"   • Original avg length: {original_avg:.0f} characters")
    print(f"   • Cleaned avg length: {cleaned_avg:.0f} characters")
    print(f"   • Reduction: {reduction:.1f}%")
    
    datasets['BBC_cleaned'] = bbc_df
    print("✅ BBC cleaning completed")
else:
    print("❌ BBC dataset not available")


# In[ ]:


# Clean CNN/DailyMail Dataset
if 'CNN' in datasets:
    print("🧹 Cleaning CNN/DailyMail Dataset...")
    cnn_df = datasets['CNN'].copy()
    
    # Identify text column
    text_column = 'article' if 'article' in cnn_df.columns else 'text'
    
    # Apply cleaning
    tqdm.pandas(desc="Processing CNN")
    cnn_df['text_cleaned'] = cnn_df[text_column].progress_apply(clean_text_pipeline)
    
    # Calculate metrics
    original_avg = cnn_df[text_column].str.len().mean()
    cleaned_avg = cnn_df['text_cleaned'].str.len().mean()
    reduction = ((original_avg - cleaned_avg) / original_avg * 100)
    
    print(f"   • Original avg length: {original_avg:.0f} characters")
    print(f"   • Cleaned avg length: {cleaned_avg:.0f} characters")
    print(f"   • Reduction: {reduction:.1f}%")
    
    datasets['CNN_cleaned'] = cnn_df
    print("✅ CNN cleaning completed")
else:
    print("❌ CNN dataset not available")


# In[ ]:


# Clean IMDB Dataset
if 'IMDB' in datasets:
    print("🧹 Cleaning IMDB Reviews Dataset...")
    imdb_df = datasets['IMDB'].copy()
    
    # Apply cleaning
    tqdm.pandas(desc="Processing IMDB")
    imdb_df['review_cleaned'] = imdb_df['review'].progress_apply(clean_text_pipeline)
    
    # Calculate metrics
    original_avg = imdb_df['review'].str.len().mean()
    cleaned_avg = imdb_df['review_cleaned'].str.len().mean()
    reduction = ((original_avg - cleaned_avg) / original_avg * 100)
    
    print(f"   • Original avg length: {original_avg:.0f} characters")
    print(f"   • Cleaned avg length: {cleaned_avg:.0f} characters")
    print(f"   • Reduction: {reduction:.1f}%")
    
    datasets['IMDB_cleaned'] = imdb_df
    print("✅ IMDB cleaning completed")
else:
    print("❌ IMDB dataset not available")


# In[ ]:


# Save cleaned datasets
import os
import json
import time

# Create cleaned data directory
cleaned_dir = "../data/cleaned"
os.makedirs(cleaned_dir, exist_ok=True)

saved_files = []

# Save BBC cleaned dataset
if 'BBC_cleaned' in datasets:
    filepath = os.path.join(cleaned_dir, "bbc_news_cleaned.csv")
    datasets['BBC_cleaned'].to_csv(filepath, index=False)
    saved_files.append(f"BBC: {filepath}")
    print(f"✅ BBC dataset saved: {len(datasets['BBC_cleaned'])} articles")

# Save CNN cleaned dataset
if 'CNN_cleaned' in datasets:
    filepath = os.path.join(cleaned_dir, "cnn_dailymail_cleaned.csv")
    datasets['CNN_cleaned'].to_csv(filepath, index=False)
    saved_files.append(f"CNN: {filepath}")
    print(f"✅ CNN dataset saved: {len(datasets['CNN_cleaned'])} articles")

# Save IMDB cleaned dataset
if 'IMDB_cleaned' in datasets:
    filepath = os.path.join(cleaned_dir, "imdb_reviews_cleaned.csv")
    datasets['IMDB_cleaned'].to_csv(filepath, index=False)
    saved_files.append(f"IMDB: {filepath}")
    print(f"✅ IMDB dataset saved: {len(datasets['IMDB_cleaned'])} reviews")

# Save metadata
metadata = {
    'cleaning_date': time.strftime('%Y-%m-%d %H:%M:%S'),
    'day': 'Day 8-9',
    'objective': 'Text cleaning: remove special characters, punctuation, stop words',
    'files_created': saved_files,
    'next_step': 'Week 3: Topic modeling with LDA/NMF'
}

metadata_path = os.path.join(cleaned_dir, "preprocessing_metadata.json")
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)


# ## Day 10-11: Text Normalization with Stemming and Lemmatization
# 
# **Objectives:**
# - Implement stemming using Porter Stemmer
# - Implement lemmatization using WordNet Lemmatizer
# - Compare performance between stemming and lemmatization
# - Apply normalization to all cleaned datasets
# - Analyze the impact of normalization on text data

# In[ ]:


# Import additional libraries for stemming and lemmatization
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
import time

# Download additional NLTK data
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)

# Initialize stemmer and lemmatizer
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

print("✅ Stemming and Lemmatization tools initialized")
print(f"📝 Porter Stemmer ready")
print(f"📝 WordNet Lemmatizer ready")


# In[ ]:


# Define normalization functions
def get_wordnet_pos(treebank_tag):
    """Convert TreeBank POS tags to WordNet POS tags for better lemmatization"""
    if treebank_tag.startswith('J'):
        return 'a'  # adjective
    elif treebank_tag.startswith('V'):
        return 'v'  # verb
    elif treebank_tag.startswith('N'):
        return 'n'  # noun
    elif treebank_tag.startswith('R'):
        return 'r'  # adverb
    else:
        return 'n'  # default to noun

def stem_text(text):
    """Apply Porter Stemming to text"""
    if pd.isna(text) or text == "":
        return ""
    
    text = str(text)
    tokens = word_tokenize(text.lower())
    stemmed_tokens = [stemmer.stem(token) for token in tokens if token.isalpha()]
    return ' '.join(stemmed_tokens)

def lemmatize_text(text):
    """Apply Lemmatization with POS tagging to text"""
    if pd.isna(text) or text == "":
        return ""
    
    text = str(text)
    tokens = word_tokenize(text.lower())
    
    # Filter only alphabetic tokens
    alpha_tokens = [token for token in tokens if token.isalpha()]
    
    # Get POS tags
    pos_tags = pos_tag(alpha_tokens)
    
    # Lemmatize with appropriate POS tags
    lemmatized_tokens = [
        lemmatizer.lemmatize(token, get_wordnet_pos(pos)) 
        for token, pos in pos_tags
    ]
    
    return ' '.join(lemmatized_tokens)

def normalize_text_pipeline(text, method='lemma'):
    """Complete text normalization pipeline with stemming or lemmatization"""
    if pd.isna(text) or text == "":
        return ""
    
    if method == 'stem':
        return stem_text(text)
    elif method == 'lemma':
        return lemmatize_text(text)
    else:
        raise ValueError("Method must be 'stem' or 'lemma'")

print("✅ Text normalization functions defined")
print("📋 Available methods: 'stem' (Porter Stemmer), 'lemma' (WordNet Lemmatizer)")


# In[ ]:


# Demonstrate stemming vs lemmatization
sample_text = "The children were running and jumping happily in the beautiful gardens while their parents were watching"

print("🔍 Stemming vs Lemmatization Comparison:")
print(f"Original text: {sample_text}")
print()

# Apply stemming
stemmed = stem_text(sample_text)
print(f"Stemmed text: {stemmed}")

# Apply lemmatization
lemmatized = lemmatize_text(sample_text)
print(f"Lemmatized text: {lemmatized}")

print()
print("📊 Key Differences:")
print("• Stemming: Faster, rule-based, may create non-words")
print("• Lemmatization: Slower, dictionary-based, preserves valid words")
print("• Lemmatization with POS: Most accurate, context-aware")


# In[ ]:


# Apply normalization to BBC News Dataset
if 'BBC_cleaned' in datasets:
    print("🔄 Normalizing BBC News Dataset...")
    bbc_df = datasets['BBC_cleaned'].copy()
    
    # Apply both stemming and lemmatization
    print("   📝 Applying stemming...")
    tqdm.pandas(desc="BBC Stemming")
    bbc_df['text_stemmed'] = bbc_df['text_cleaned'].progress_apply(
        lambda x: normalize_text_pipeline(x, method='stem')
    )
    
    print("   📝 Applying lemmatization...")
    tqdm.pandas(desc="BBC Lemmatization")
    bbc_df['text_lemmatized'] = bbc_df['text_cleaned'].progress_apply(
        lambda x: normalize_text_pipeline(x, method='lemma')
    )
    
    # Calculate metrics
    cleaned_avg = bbc_df['text_cleaned'].str.len().mean()
    stemmed_avg = bbc_df['text_stemmed'].str.len().mean()
    lemmatized_avg = bbc_df['text_lemmatized'].str.len().mean()
    
    stem_reduction = ((cleaned_avg - stemmed_avg) / cleaned_avg * 100)
    lemma_reduction = ((cleaned_avg - lemmatized_avg) / cleaned_avg * 100)
    
    print(f"   • Cleaned avg length: {cleaned_avg:.0f} characters")
    print(f"   • Stemmed avg length: {stemmed_avg:.0f} characters (↓{stem_reduction:.1f}%)")
    print(f"   • Lemmatized avg length: {lemmatized_avg:.0f} characters (↓{lemma_reduction:.1f}%)")
    
    datasets['BBC_normalized'] = bbc_df
    print("✅ BBC normalization completed")
else:
    print("❌ BBC cleaned dataset not available")


# In[ ]:


# Apply normalization to CNN/DailyMail Dataset
if 'CNN_cleaned' in datasets:
    print("🔄 Normalizing CNN/DailyMail Dataset...")
    cnn_df = datasets['CNN_cleaned'].copy()
    
    # Apply both stemming and lemmatization
    print("   📝 Applying stemming...")
    tqdm.pandas(desc="CNN Stemming")
    cnn_df['text_stemmed'] = cnn_df['text_cleaned'].progress_apply(
        lambda x: normalize_text_pipeline(x, method='stem')
    )
    
    print("   📝 Applying lemmatization...")
    tqdm.pandas(desc="CNN Lemmatization")
    cnn_df['text_lemmatized'] = cnn_df['text_cleaned'].progress_apply(
        lambda x: normalize_text_pipeline(x, method='lemma')
    )
    
    # Calculate metrics
    cleaned_avg = cnn_df['text_cleaned'].str.len().mean()
    stemmed_avg = cnn_df['text_stemmed'].str.len().mean()
    lemmatized_avg = cnn_df['text_lemmatized'].str.len().mean()
    
    stem_reduction = ((cleaned_avg - stemmed_avg) / cleaned_avg * 100)
    lemma_reduction = ((cleaned_avg - lemmatized_avg) / cleaned_avg * 100)
    
    print(f"   • Cleaned avg length: {cleaned_avg:.0f} characters")
    print(f"   • Stemmed avg length: {stemmed_avg:.0f} characters (↓{stem_reduction:.1f}%)")
    print(f"   • Lemmatized avg length: {lemmatized_avg:.0f} characters (↓{lemma_reduction:.1f}%)")
    
    datasets['CNN_normalized'] = cnn_df
    print("✅ CNN normalization completed")
else:
    print("❌ CNN cleaned dataset not available")


# In[ ]:


# Apply normalization to IMDB Reviews Dataset
if 'IMDB_cleaned' in datasets:
    print("🔄 Normalizing IMDB Reviews Dataset...")
    imdb_df = datasets['IMDB_cleaned'].copy()
    
    # Apply both stemming and lemmatization
    print("   📝 Applying stemming...")
    tqdm.pandas(desc="IMDB Stemming")
    imdb_df['review_stemmed'] = imdb_df['review_cleaned'].progress_apply(
        lambda x: normalize_text_pipeline(x, method='stem')
    )
    
    print("   📝 Applying lemmatization...")
    tqdm.pandas(desc="IMDB Lemmatization")
    imdb_df['review_lemmatized'] = imdb_df['review_cleaned'].progress_apply(
        lambda x: normalize_text_pipeline(x, method='lemma')
    )
    
    # Calculate metrics
    cleaned_avg = imdb_df['review_cleaned'].str.len().mean()
    stemmed_avg = imdb_df['review_stemmed'].str.len().mean()
    lemmatized_avg = imdb_df['review_lemmatized'].str.len().mean()
    
    
    stem_reduction = ((cleaned_avg - stemmed_avg) / cleaned_avg * 100)
    lemma_reduction = ((cleaned_avg - lemmatized_avg) / cleaned_avg * 100)
    
    print(f"   • Cleaned avg length: {cleaned_avg:.0f} characters")
    print(f"   • Stemmed avg length: {stemmed_avg:.0f} characters (↓{stem_reduction:.1f}%)")
    print(f"   • Lemmatized avg length: {lemmatized_avg:.0f} characters (↓{lemma_reduction:.1f}%)")
    
    datasets['IMDB_normalized'] = imdb_df
    print("✅ IMDB normalization completed")
else:
    print("❌ IMDB cleaned dataset not available")


# In[ ]:


# Comparative Analysis of Normalization Results
print("📊 Normalization Performance Summary")
print("=" * 60)

analysis_results = []

# Analyze each dataset
for dataset_name in ['BBC', 'CNN', 'IMDB']:
    normalized_key = f"{dataset_name}_normalized"
    
    if normalized_key in datasets:
        df = datasets[normalized_key]
        
        if dataset_name == 'IMDB':
            text_col = 'review_cleaned'
            stem_col = 'review_stemmed'
            lemma_col = 'review_lemmatized'
        else:
            text_col = 'text_cleaned'
            stem_col = 'text_stemmed'
            lemma_col = 'text_lemmatized'
        
        # Calculate vocabulary reduction
        def get_vocab_size(series):
            all_words = set()
            for text in series:
                if pd.notna(text) and text != "":
                    all_words.update(text.split())
            return len(all_words)
        
        # Get sample for vocabulary analysis (first 100 entries for performance)
        sample_df = df.head(100)
        
        original_vocab = get_vocab_size(sample_df[text_col])
        stemmed_vocab = get_vocab_size(sample_df[stem_col])
        lemmatized_vocab = get_vocab_size(sample_df[lemma_col])
        
        stem_vocab_reduction = ((original_vocab - stemmed_vocab) / original_vocab * 100)
        lemma_vocab_reduction = ((original_vocab - lemmatized_vocab) / original_vocab * 100)
        
        # Average lengths
        clean_len = df[text_col].str.len().mean()
        stem_len = df[stem_col].str.len().mean()
        lemma_len = df[lemma_col].str.len().mean()
        
        result = {
            'dataset': dataset_name,
            'original_vocab': original_vocab,
            'stemmed_vocab': stemmed_vocab,
            'lemmatized_vocab': lemmatized_vocab,
            'stem_vocab_reduction': stem_vocab_reduction,
            'lemma_vocab_reduction': lemma_vocab_reduction,
            'clean_avg_length': clean_len,
            'stem_avg_length': stem_len,
            'lemma_avg_length': lemma_len
        }
        
        analysis_results.append(result)
        
        print(f"\n📋 {dataset_name} Dataset Analysis:")
        print(f"   Vocabulary Size (sample):")
        print(f"     • Original: {original_vocab:,} unique words")
        print(f"     • Stemmed: {stemmed_vocab:,} unique words (↓{stem_vocab_reduction:.1f}%)")
        print(f"     • Lemmatized: {lemmatized_vocab:,} unique words (↓{lemma_vocab_reduction:.1f}%)")
        print(f"   Average Text Length:")
        print(f"     • Cleaned: {clean_len:.0f} characters")
        print(f"     • Stemmed: {stem_len:.0f} characters")
        print(f"     • Lemmatized: {lemma_len:.0f} characters")

print(f"\n✅ Normalization analysis completed for {len(analysis_results)} datasets")


# In[ ]:


# Save normalized datasets
print("💾 Saving normalized datasets...")

# Create normalized data directory
normalized_dir = "../data/normalized"
os.makedirs(normalized_dir, exist_ok=True)

saved_normalized_files = []

# Save BBC normalized dataset
if 'BBC_normalized' in datasets:
    filepath = os.path.join(normalized_dir, "bbc_news_normalized.csv")
    datasets['BBC_normalized'].to_csv(filepath, index=False)
    saved_normalized_files.append(f"BBC: {filepath}")
    print(f"✅ BBC normalized dataset saved: {len(datasets['BBC_normalized'])} articles")

# Save CNN normalized dataset
if 'CNN_normalized' in datasets:
    filepath = os.path.join(normalized_dir, "cnn_dailymail_normalized.csv")
    datasets['CNN_normalized'].to_csv(filepath, index=False)
    saved_normalized_files.append(f"CNN: {filepath}")
    print(f"✅ CNN normalized dataset saved: {len(datasets['CNN_normalized'])} articles")

# Save IMDB normalized dataset
if 'IMDB_normalized' in datasets:
    filepath = os.path.join(normalized_dir, "imdb_reviews_normalized.csv")
    datasets['IMDB_normalized'].to_csv(filepath, index=False)
    saved_normalized_files.append(f"IMDB: {filepath}")
    print(f"✅ IMDB normalized dataset saved: {len(datasets['IMDB_normalized'])} reviews")

# Update metadata with normalization information
normalization_metadata = {
    'normalization_date': time.strftime('%Y-%m-%d %H:%M:%S'),
    'day': 'Day 10-11',
    'objective': 'Text normalization: stemming and lemmatization',
    'methods_used': {
        'stemming': 'Porter Stemmer',
        'lemmatization': 'WordNet Lemmatizer with POS tagging'
    },
    'files_created': saved_normalized_files,
    'analysis_results': analysis_results,
    'next_step': 'Topic modeling and sentiment analysis with normalized text',
    'recommendations': {
        'stemming': 'Faster processing, good for large-scale analysis',
        'lemmatization': 'Better semantic preservation, recommended for accuracy'
    }
}

# Save normalization metadata
metadata_path = os.path.join(normalized_dir, "normalization_metadata.json")
with open(metadata_path, 'w') as f:
    json.dump(normalization_metadata, f, indent=2)

print(f"✅ Normalization metadata saved: {metadata_path}")
print(f"🎯 Day 10-11 objectives completed successfully!")
print(f"📁 Files ready for next phase: Topic modeling and sentiment analysis")


# In[ ]:


pip install ipykernel notebook jupyterlab
python -m ipykernel install --user




# In[ ]:


# ============================================
# 📌 STEP 1: Import required libraries
# ============================================
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF

# ============================================
# 📌 STEP 2: Choose dataset for Topic Modeling
# (BBC_cleaned is good for topic classification)
# ============================================
if 'BBC_normalized' in datasets:
    print("🔍 Using BBC dataset for Topic Modeling...")
    bbc_df = datasets['BBC_normalized'].copy()
    
    # Use lemmatized text for better quality topics
    documents = bbc_df['text_lemmatized'].dropna().tolist()
else:
    raise ValueError("BBC dataset not available for topic modeling.")

# ============================================
# 📌 STEP 3: Vectorization
# ============================================
# Count Vectorizer for LDA
count_vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
count_matrix = count_vectorizer.fit_transform(documents)

# TF-IDF Vectorizer for NMF
tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

print(f"✅ Vectorization complete")
print(f"   • Count matrix shape: {count_matrix.shape}")
print(f"   • TF-IDF matrix shape: {tfidf_matrix.shape}")

# ============================================
# 📌 STEP 4: Apply Topic Modeling (LDA & NMF)
# ============================================
n_topics = 5   # adjust this depending on dataset

# LDA
lda_model = LatentDirichletAllocation(n_components=n_topics, random_state=42)
lda_topics = lda_model.fit_transform(count_matrix)

# NMF
nmf_model = NMF(n_components=n_topics, random_state=42)
nmf_topics = nmf_model.fit_transform(tfidf_matrix)

print("✅ Topic modeling completed with LDA & NMF")

# ============================================
# 📌 STEP 5: Display Topics
# ============================================
def display_topics(model, feature_names, n_words=10):
    topics = []
    for idx, topic in enumerate(model.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-n_words - 1:-1]]
        topics.append(f"Topic {idx+1}: {', '.join(top_words)}")
    return topics

# LDA Topics
print("\n📊 LDA Topics:")
lda_topics_words = display_topics(lda_model, count_vectorizer.get_feature_names_out(), 10)
for t in lda_topics_words:
    print("   ", t)

# NMF Topics
print("\n📊 NMF Topics:")
nmf_topics_words = display_topics(nmf_model, tfidf_vectorizer.get_feature_names_out(), 10)
for t in nmf_topics_words:
    print("   ", t)

# ============================================
# 📌 STEP 6: Attach Topic Distributions to DataFrame
# ============================================
bbc_df['LDA_Topic'] = lda_topics.argmax(axis=1)
bbc_df['NMF_Topic'] = nmf_topics.argmax(axis=1)

print("\n✅ Topics assigned to BBC dataset")
print(bbc_df[['text_cleaned', 'LDA_Topic', 'NMF_Topic']].head())

# Save with topics
output_path = os.path.join(cleaned_dir, "bbc_with_topics.csv")
bbc_df.to_csv(output_path, index=False)
print(f"💾 Saved dataset with topics → {output_path}")


# In[ ]:


# Tokenization Function
def tokenize_text(text, method="word"):
    """Tokenize text into words or sentences"""
    if pd.isna(text) or text == "":
        return []
    
    text = str(text)
    
    if method == "word":
        return word_tokenize(text.lower())   # Word-level tokens
    elif method == "sentence":
        from nltk.tokenize import sent_tokenize
        return sent_tokenize(text)           # Sentence-level tokens
    else:
        raise ValueError("Method must be 'word' or 'sentence'")


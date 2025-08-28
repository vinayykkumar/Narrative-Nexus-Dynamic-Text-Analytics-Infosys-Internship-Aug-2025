#!/usr/bin/env python3
"""
AI Narrative Nexus - Main Data Processing Script
Process datasets and prepare them for machine learning model training
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import argparse
import time

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from python_preprocessing.text_preprocessor import (
    TextPreprocessor, 
    DatasetLoader, 
    FeatureExtractor,
    save_preprocessed_data,
    generate_preprocessing_report
)

def process_amazon_alexa_dataset(data_dir: str, output_dir: str):
    """Process Amazon Alexa reviews dataset"""
    print("=" * 60)
    print("Processing Amazon Alexa Reviews Dataset")
    print("=" * 60)
    
    # Load dataset
    alexa_path = Path(data_dir) / "amazon_alexa.tsv"
    if not alexa_path.exists():
        print(f"Error: Amazon Alexa dataset not found at {alexa_path}")
        return None
    
    df = DatasetLoader.load_amazon_alexa(str(alexa_path))
    print(f"Loaded {len(df)} Amazon Alexa reviews")
    
    # Initialize preprocessor
    preprocessor = TextPreprocessor(
        remove_stopwords=True,
        use_stemming=True,
        use_lemmatization=False,
        min_token_length=2,
        max_token_length=20
    )
    
    # Preprocess the dataset
    start_time = time.time()
    processed_df = preprocessor.preprocess_dataframe(df, 'text', 'label')
    processing_time = time.time() - start_time
    
    print(f"Processing completed in {processing_time:.2f} seconds")
    print(f"Processed {len(processed_df)} reviews successfully")
    
    # Show sample results
    print("\nSample processed review:")
    sample = processed_df.iloc[0]
    print(f"Original: {sample['text'][:100]}...")
    print(f"Cleaned: {sample['cleaned_text'][:100]}...")
    print(f"Normalized: {sample['normalized_text'][:100]}...")
    print(f"Tokens ({len(sample['tokens'])}): {sample['tokens'][:10]}")
    print(f"Label: {sample['label']}")
    
    # Save preprocessed data
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    save_preprocessed_data(processed_df, output_path / "amazon_alexa_processed.csv", "csv")
    save_preprocessed_data(processed_df, output_path / "amazon_alexa_processed.json", "json")
    
    # Generate report
    generate_preprocessing_report(processed_df, output_path / "amazon_alexa_report.md")
    
    # Extract features for ML
    feature_extractor = FeatureExtractor(max_features=5000, ngram_range=(1, 2))
    
    # TF-IDF features
    tfidf_features = feature_extractor.fit_transform_tfidf(processed_df['processed_text'].tolist())
    
    # Save features and labels for ML
    X = tfidf_features
    y = processed_df['label'].values
    
    # Split into train/test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Save ML-ready data
    np.save(output_path / "alexa_X_train.npy", X_train)
    np.save(output_path / "alexa_X_test.npy", X_test)
    np.save(output_path / "alexa_y_train.npy", y_train)
    np.save(output_path / "alexa_y_test.npy", y_test)
    
    # Save feature names
    feature_names = feature_extractor.get_feature_names('tfidf')
    with open(output_path / "alexa_feature_names.txt", 'w') as f:
        f.write('\n'.join(feature_names))
    
    # Save vectorizers
    feature_extractor.save_vectorizers(str(output_path / "alexa_vectorizers"))
    
    print(f"\nML-ready data saved:")
    print(f"- Training set: {X_train.shape}")
    print(f"- Test set: {X_test.shape}")
    print(f"- Features: {len(feature_names)}")
    
    return processed_df

def process_twitter_sentiment_dataset(data_dir: str, output_dir: str, sample_size: int = 10000):
    """Process Twitter sentiment dataset (with sampling for large dataset)"""
    print("=" * 60)
    print(f"Processing Twitter Sentiment Dataset (Sample: {sample_size})")
    print("=" * 60)
    
    # Load dataset
    twitter_path = Path(data_dir) / "cleaned_tweets.csv"
    if not twitter_path.exists():
        print(f"Error: Twitter dataset not found at {twitter_path}")
        return None
    
    df = DatasetLoader.load_twitter_sentiment(str(twitter_path), sample_size=sample_size)
    print(f"Loaded {len(df)} tweets")
    
    # Initialize preprocessor optimized for social media
    preprocessor = TextPreprocessor(
        remove_stopwords=True,
        use_stemming=True,
        use_lemmatization=False,
        min_token_length=2,
        max_token_length=15  # Shorter for social media
    )
    
    # Preprocess the dataset
    start_time = time.time()
    processed_df = preprocessor.preprocess_dataframe(df, 'text', 'label')
    processing_time = time.time() - start_time
    
    print(f"Processing completed in {processing_time:.2f} seconds")
    print(f"Processed {len(processed_df)} tweets successfully")
    
    # Show sample results
    print("\nSample processed tweets:")
    for i, (_, sample) in enumerate(processed_df.head(3).iterrows()):
        print(f"\nTweet {i+1}:")
        print(f"Original: {sample['text']}")
        print(f"Processed: {sample['processed_text']}")
        print(f"Tokens ({len(sample['tokens'])}): {sample['tokens']}")
        print(f"Sentiment: {sample['label']}")
    
    # Save preprocessed data
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    save_preprocessed_data(processed_df, output_path / "twitter_sentiment_processed.csv", "csv")
    save_preprocessed_data(processed_df, output_path / "twitter_sentiment_processed.json", "json")
    
    # Generate report
    generate_preprocessing_report(processed_df, output_path / "twitter_sentiment_report.md")
    
    # Extract features for ML
    feature_extractor = FeatureExtractor(max_features=8000, ngram_range=(1, 2))
    
    # TF-IDF features
    tfidf_features = feature_extractor.fit_transform_tfidf(processed_df['processed_text'].tolist())
    
    # Save features and labels for ML
    X = tfidf_features
    y = processed_df['label'].values
    
    # Split into train/test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Save ML-ready data
    np.save(output_path / "twitter_X_train.npy", X_train)
    np.save(output_path / "twitter_X_test.npy", X_test)
    np.save(output_path / "twitter_y_train.npy", y_train)
    np.save(output_path / "twitter_y_test.npy", y_test)
    
    # Save feature names
    feature_names = feature_extractor.get_feature_names('tfidf')
    with open(output_path / "twitter_feature_names.txt", 'w') as f:
        f.write('\n'.join(feature_names))
    
    # Save vectorizers
    feature_extractor.save_vectorizers(str(output_path / "twitter_vectorizers"))
    
    print(f"\nML-ready data saved:")
    print(f"- Training set: {X_train.shape}")
    print(f"- Test set: {X_test.shape}")
    print(f"- Features: {len(feature_names)}")
    
    return processed_df

def process_amazon_reviews_dataset(data_dir: str, output_dir: str, sample_size: int = 50000):
    """Process Amazon product reviews dataset (with sampling for large dataset)"""
    print("=" * 60)
    print(f"Processing Amazon Product Reviews Dataset (Sample: {sample_size})")
    print("=" * 60)
    
    # Load dataset
    reviews_path = Path(data_dir) / "amazon_review_full_csv" / "train.csv"
    if not reviews_path.exists():
        print(f"Error: Amazon reviews dataset not found at {reviews_path}")
        return None
    
    df = DatasetLoader.load_amazon_reviews(str(reviews_path), sample_size=sample_size)
    print(f"Loaded {len(df)} Amazon product reviews")
    
    # Initialize preprocessor
    preprocessor = TextPreprocessor(
        remove_stopwords=True,
        use_stemming=True,
        use_lemmatization=False,
        min_token_length=2,
        max_token_length=25
    )
    
    # Preprocess the dataset
    start_time = time.time()
    processed_df = preprocessor.preprocess_dataframe(df, 'text', 'label')
    processing_time = time.time() - start_time
    
    print(f"Processing completed in {processing_time:.2f} seconds")
    print(f"Processed {len(processed_df)} reviews successfully")
    
    # Show sample results
    print("\nSample processed review:")
    sample = processed_df.iloc[0]
    print(f"Original: {sample['text'][:150]}...")
    print(f"Processed: {sample['processed_text'][:150]}...")
    print(f"Tokens ({len(sample['tokens'])}): {sample['tokens'][:15]}")
    print(f"Label: {sample['label']}")
    
    # Save preprocessed data
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    save_preprocessed_data(processed_df, output_path / "amazon_reviews_processed.csv", "csv")
    save_preprocessed_data(processed_df, output_path / "amazon_reviews_processed.json", "json")
    
    # Generate report
    generate_preprocessing_report(processed_df, output_path / "amazon_reviews_report.md")
    
    # Extract features for ML
    feature_extractor = FeatureExtractor(max_features=10000, ngram_range=(1, 2))
    
    # TF-IDF features
    tfidf_features = feature_extractor.fit_transform_tfidf(processed_df['processed_text'].tolist())
    
    # Save features and labels for ML
    X = tfidf_features
    y = processed_df['label'].values
    
    # Split into train/test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Save ML-ready data
    np.save(output_path / "amazon_reviews_X_train.npy", X_train)
    np.save(output_path / "amazon_reviews_X_test.npy", X_test)
    np.save(output_path / "amazon_reviews_y_train.npy", y_train)
    np.save(output_path / "amazon_reviews_y_test.npy", y_test)
    
    # Save feature names
    feature_names = feature_extractor.get_feature_names('tfidf')
    with open(output_path / "amazon_reviews_feature_names.txt", 'w') as f:
        f.write('\n'.join(feature_names))
    
    # Save vectorizers
    feature_extractor.save_vectorizers(str(output_path / "amazon_reviews_vectorizers"))
    
    print(f"\nML-ready data saved:")
    print(f"- Training set: {X_train.shape}")
    print(f"- Test set: {X_test.shape}")
    print(f"- Features: {len(feature_names)}")
    
    return processed_df

def main():
    """Main processing function"""
    parser = argparse.ArgumentParser(description="AI Narrative Nexus Data Preprocessing")
    parser.add_argument("--data-dir", default="./dataset", help="Dataset directory")
    parser.add_argument("--output-dir", default="./python_preprocessing/processed_data", help="Output directory")
    parser.add_argument("--dataset", choices=["alexa", "twitter", "amazon_reviews", "all"], 
                       default="all", help="Dataset to process")
    parser.add_argument("--twitter-sample", type=int, default=10000, 
                       help="Sample size for Twitter dataset")
    parser.add_argument("--amazon-reviews-sample", type=int, default=50000,
                       help="Sample size for Amazon reviews dataset")
    
    args = parser.parse_args()
    
    print("AI Narrative Nexus - Data Preprocessing Pipeline")
    print("=" * 60)
    print(f"Data directory: {args.data_dir}")
    print(f"Output directory: {args.output_dir}")
    print("=" * 60)
    
    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    if args.dataset in ["alexa", "all"]:
        try:
            results["alexa"] = process_amazon_alexa_dataset(args.data_dir, args.output_dir)
        except Exception as e:
            print(f"Error processing Amazon Alexa dataset: {e}")
    
    if args.dataset in ["twitter", "all"]:
        try:
            results["twitter"] = process_twitter_sentiment_dataset(
                args.data_dir, args.output_dir, args.twitter_sample
            )
        except Exception as e:
            print(f"Error processing Twitter dataset: {e}")
    
    if args.dataset in ["amazon_reviews", "all"]:
        try:
            results["amazon_reviews"] = process_amazon_reviews_dataset(
                args.data_dir, args.output_dir, args.amazon_reviews_sample
            )
        except Exception as e:
            print(f"Error processing Amazon reviews dataset: {e}")
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)
    
    total_records = 0
    for dataset_name, df in results.items():
        if df is not None:
            print(f"{dataset_name.upper()}: {len(df):,} records processed")
            total_records += len(df)
        else:
            print(f"{dataset_name.upper()}: Failed to process")
    
    print(f"\nTotal records processed: {total_records:,}")
    print(f"Output saved to: {args.output_dir}")
    print("\nPreprocessing complete! Data is ready for model training.")
    
    # List generated files
    output_path = Path(args.output_dir)
    if output_path.exists():
        print(f"\nGenerated files:")
        for file in sorted(output_path.rglob("*")):
            if file.is_file():
                print(f"  {file.relative_to(output_path)}")

if __name__ == "__main__":
    main()

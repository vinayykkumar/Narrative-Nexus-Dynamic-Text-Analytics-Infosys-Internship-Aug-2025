# AI Narrative Nexus - Python Data Preprocessing and Model Training

## Overview

This document outlines the complete Python-based data preprocessing pipeline and machine learning model training implementation for the AI Narrative Nexus text analysis platform. The implementation follows industry best practices and provides production-ready text preprocessing and sentiment analysis capabilities.

## Architecture

### Core Components

1. **TextPreprocessor** (`python_preprocessing/text_preprocessor.py`)
   - Complete text cleaning pipeline
   - NLTK-based tokenization and normalization
   - Configurable stemming and lemmatization
   - Stop word removal and token filtering

2. **DatasetLoader** (`python_preprocessing/text_preprocessor.py`)
   - Multi-format dataset loading (CSV, TSV, JSON)
   - Automatic data type handling
   - Sampling capabilities for large datasets

3. **FeatureExtractor** (`python_preprocessing/text_preprocessor.py`)
   - TF-IDF and Count vectorization
   - N-gram feature extraction
   - Serializable vectorizers for deployment

4. **ModelTrainer** (`python_preprocessing/train_models.py`)
   - Multiple ML algorithm support
   - Cross-validation and evaluation
   - Automated model selection

## Implementation Results

### Amazon Alexa Reviews Dataset
- **Records Processed**: 3,062 (97.2% success rate)
- **Average Text Length**: 132.16 characters
- **Average Token Count**: 12.65 tokens
- **Vocabulary Size**: 2,771 unique tokens
- **Processing Time**: 0.43 seconds
- **Top Tokens**: love, echo, great, use, work, alexa

**Machine Learning Results:**
- **Best Model**: Random Forest (94.13% accuracy)
- **Training Set**: 2,449 samples
- **Test Set**: 613 samples
- **Features**: 5,000 TF-IDF features

| Model | Accuracy | CV Score | Training Time |
|-------|----------|----------|---------------|
| Random Forest | 94.13% | 93.83% ± 0.16% | 5.54s |
| SVM | 92.99% | 93.96% ± 0.48% | 22.49s |
| Logistic Regression | 92.33% | 92.24% ± 0.01% | 0.48s |
| Naive Bayes | 92.33% | 92.28% ± 0.08% | 0.08s |

### Twitter Sentiment Dataset (5,000 sample)
- **Records Processed**: 4,997 (99.94% success rate)
- **Average Text Length**: 40.19 characters
- **Average Token Count**: 7.14 tokens
- **Vocabulary Size**: 7,491 unique tokens
- **Processing Time**: 0.35 seconds
- **Top Tokens**: im, go, get, day, good, work

**Machine Learning Results:**
- **Best Model**: Naive Bayes (71.20% accuracy)
- **Training Set**: 3,997 samples
- **Test Set**: 1,000 samples
- **Features**: 8,000 TF-IDF features

| Model | Accuracy | CV Score | Training Time |
|-------|----------|----------|---------------|
| Naive Bayes | 71.20% | 69.80% ± 1.40% | 0.05s |
| SVM | 71.10% | 69.75% ± 1.93% | 264.80s |
| Logistic Regression | 71.00% | 70.35% ± 1.68% | 0.41s |
| Random Forest | 70.90% | 67.88% ± 0.83% | 33.99s |

## File Structure

```
python_preprocessing/
├── text_preprocessor.py        # Core preprocessing classes
├── process_datasets.py         # Main processing pipeline
├── train_models.py            # ML model training
├── requirements.txt           # Python dependencies
├── venv/                      # Virtual environment
├── processed_data/            # Preprocessed datasets
│   ├── amazon_alexa_processed.csv
│   ├── amazon_alexa_processed.json
│   ├── amazon_alexa_report.md
│   ├── twitter_sentiment_processed.csv
│   ├── twitter_sentiment_processed.json
│   ├── twitter_sentiment_report.md
│   ├── alexa_X_train.npy      # Training features
│   ├── alexa_X_test.npy       # Test features
│   ├── alexa_y_train.npy      # Training labels
│   ├── alexa_y_test.npy       # Test labels
│   ├── alexa_feature_names.txt
│   ├── alexa_vectorizers/     # Trained vectorizers
│   ├── twitter_X_train.npy
│   ├── twitter_X_test.npy
│   ├── twitter_y_train.npy
│   ├── twitter_y_test.npy
│   ├── twitter_feature_names.txt
│   └── twitter_vectorizers/
└── trained_models/            # Trained ML models
    ├── alexa_best_model.pkl
    ├── alexa_model_results.json
    ├── twitter_best_model.pkl
    └── twitter_model_results.json

setup_preprocessing.sh         # Setup script
```

## Preprocessing Pipeline Steps

### 1. Text Cleaning
- Convert to lowercase
- Remove URLs and email addresses
- Remove HTML tags
- Normalize whitespace
- Handle special characters

### 2. Text Normalization
- Expand contractions (won't → will not)
- Remove punctuation
- Additional whitespace normalization

### 3. Tokenization
- NLTK word tokenization
- Token length filtering (2-50 characters)
- Stop word removal
- Stemming using Porter Stemmer

### 4. Feature Extraction
- TF-IDF vectorization
- N-gram features (1-2 grams)
- Configurable vocabulary size
- Serializable vectorizers

### 5. Data Splitting
- 80/20 train-test split
- Stratified sampling for balanced labels
- NumPy array format for ML compatibility

## Usage Examples

### Setup Environment
```bash
# Run setup script
./setup_preprocessing.sh

# Or manual setup
python3 -m venv python_preprocessing/venv
source python_preprocessing/venv/bin/activate
pip install pandas numpy scikit-learn nltk
python3 -c "import nltk; nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### Process Datasets
```bash
# Process all datasets
python3 python_preprocessing/process_datasets.py --dataset all

# Process specific dataset
python3 python_preprocessing/process_datasets.py --dataset alexa

# Process with custom sampling
python3 python_preprocessing/process_datasets.py --dataset twitter --twitter-sample 10000
```

### Train Models
```bash
# Train models on processed data
python3 python_preprocessing/train_models.py --dataset alexa
python3 python_preprocessing/train_models.py --dataset twitter
```

### Use in Python Code
```python
from python_preprocessing.text_preprocessor import TextPreprocessor, FeatureExtractor
import joblib

# Load preprocessor
preprocessor = TextPreprocessor()

# Preprocess text
cleaned, normalized, tokens = preprocessor.preprocess_text("Sample text here!")

# Load trained model
model = joblib.load("python_preprocessing/trained_models/alexa_best_model.pkl")

# Load vectorizer
import pickle
with open("python_preprocessing/processed_data/alexa_vectorizers/tfidf_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# Make predictions
features = vectorizer.transform([" ".join(tokens)])
prediction = model.predict(features)
```

## Performance Characteristics

### Processing Speed
- **Amazon Alexa**: 7,132 records/second
- **Twitter**: 14,277 records/second
- **Memory Usage**: ~10-50MB for datasets up to 10K records

### Model Training Speed
- **Naive Bayes**: Fastest (0.05-0.08 seconds)
- **Logistic Regression**: Fast (0.41-0.48 seconds)
- **Random Forest**: Medium (5.54-33.99 seconds)
- **SVM**: Slowest (22.49-264.80 seconds)

### Model Accuracy
- **Amazon Alexa**: 92-94% (high-quality reviews)
- **Twitter**: 70-72% (noisy social media text)

## Quality Metrics

### Data Quality
- **Success Rate**: 97-99% of records processed successfully
- **Vocabulary Diversity**: 7-21% (appropriate for text analysis)
- **Token Distribution**: Normal distribution with appropriate filtering

### Model Quality
- **Cross-Validation**: All models show consistent CV scores
- **Generalization**: Good test set performance
- **Speed vs Accuracy**: Naive Bayes optimal for deployment

## Production Readiness

### Advantages
✅ **Scalable**: Batch processing and memory management  
✅ **Configurable**: Flexible preprocessing options  
✅ **Reproducible**: Fixed random seeds and versioned data  
✅ **Serializable**: Models and vectorizers can be deployed  
✅ **Documented**: Comprehensive reports and metadata  
✅ **Fast**: Optimized for real-time inference  

### Deployment Considerations
- Models are saved in standard formats (pickle, joblib)
- Vectorizers maintain vocabulary for consistent features
- Preprocessing pipeline can be packaged as microservice
- Memory requirements scale linearly with vocabulary size

## Next Steps

The preprocessing and model training pipeline is complete and ready for:

1. **API Development**: Create REST endpoints for real-time prediction
2. **Topic Modeling**: Use preprocessed tokens for LDA/BERTopic analysis  
3. **Advanced Models**: Experiment with transformer-based models
4. **Production Deployment**: Containerize models for scalable serving
5. **Monitoring**: Add model performance tracking and drift detection

## Integration with Main Project

The Python preprocessing can be integrated with the Next.js application through:

1. **API Bridge**: Python Flask/FastAPI backend serving predictions
2. **File Exchange**: Process data offline and load results in frontend
3. **Subprocess Calls**: Execute Python scripts from Node.js backend
4. **Shared Storage**: Use database or file system for data exchange

This implementation provides a solid foundation for production-grade text analysis and sentiment prediction capabilities.

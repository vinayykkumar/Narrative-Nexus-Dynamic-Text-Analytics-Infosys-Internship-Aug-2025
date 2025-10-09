import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
import os


def load_custom_format_file(file_path):
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue


                text = line[:-1]

                sentiment = int(line[-1])

                data.append({'text': text, 'sentiment': sentiment})
    except FileNotFoundError:
        print(f"Warning: Custom format file not found at '{file_path}'. Skipping.")
    except Exception as e:
        print(f"Error reading custom file {file_path}: {e}")

    return pd.DataFrame(data)

print("Downloading NLTK resources (stopwords, wordnet)...")
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
print("NLTK resources downloaded.")

print("\nStep 1: Loading and combining datasets...")

print("Loading Sentiment140 dataset...")
try:
    cols = ['sentiment', 'id', 'date', 'query', 'user', 'text']
    df_twitter = pd.read_csv(
        'sentiment140.csv',
        header=None,
        names=cols,
        encoding='ISO-8859-1'
    )
    df_twitter = df_twitter[['text', 'sentiment']]
    df_twitter['sentiment'] = df_twitter['sentiment'].replace({0: 0, 4: 1})
except FileNotFoundError:
    print("Warning: Sentiment140 file not found. Skipping.")
    df_twitter = pd.DataFrame()

print("Loading IMDB dataset...")
try:
    df_imdb = pd.read_csv('IMDB Dataset.csv')
    df_imdb = df_imdb[['review', 'sentiment']]
    df_imdb.rename(columns={'review': 'text'}, inplace=True)
    df_imdb['sentiment'] = df_imdb['sentiment'].map({'negative': 0, 'positive': 1})
except FileNotFoundError:
    print("Warning: IMDB file not found. Skipping.")
    df_imdb = pd.DataFrame()

print("Loading Sentiment Labelled Sentences datasets...")
try:
    df_amazon_labelled = pd.read_csv('amazon_cells_labelled.csv', sep='\t', header=None, names=['text', 'sentiment'])
    df_yelp_labelled = pd.read_csv('yelp_labelled.csv', sep='\t', header=None, names=['text', 'sentiment'])
    df_labelled_sentences = pd.concat([df_amazon_labelled,  df_yelp_labelled], ignore_index=True)
except FileNotFoundError:
    print("Warning: One or more Sentiment Labelled Sentences files not found. Skipping.")
    df_labelled_sentences = pd.DataFrame()

print("Loading large Amazon Reviews dataset...")
amazon_reviews_data = []
amazon_files = [
    'train.ft.txt',
    'test.ft.txt'
]

for file_path in amazon_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                label_str = line.split(' ')[0]
                text = line.replace(label_str, '', 1).strip()
                sentiment = 1 if label_str == '__label__2' else 0
                amazon_reviews_data.append({'text': text, 'sentiment': sentiment})
    except FileNotFoundError:
        print(f"Warning: Amazon review file not found at '{file_path}'. Skipping.")

df_amazon_reviews = pd.DataFrame(amazon_reviews_data)

df_custom_data = load_custom_format_file('custom_data.txt')


print("Combining all loaded datasets...")
df_combined = pd.concat([
    df_twitter,
    df_imdb,
    df_labelled_sentences,
    df_amazon_reviews,
    df_custom_data
], ignore_index=True)

df_combined.dropna(inplace=True)
df_combined.drop_duplicates(subset=['text'], inplace=True)

print(f"Total combined records after loading and cleaning: {len(df_combined):,}")

print("\nStep 2: Handling class imbalance...")
if not df_combined.empty:
    print("Original class distribution:")
    print(df_combined['sentiment'].value_counts())

    min_class_size = df_combined['sentiment'].value_counts().min()
    df_balanced = pd.concat([
        df_combined[df_combined['sentiment'] == 0].sample(min_class_size, random_state=42),
        df_combined[df_combined['sentiment'] == 1].sample(min_class_size, random_state=42)
    ])

    print("\nBalanced class distribution:")
    print(df_balanced['sentiment'].value_counts())
else:
    print("No data loaded, skipping class balancing.")
    df_balanced = pd.DataFrame()

print("\nStep 3: Preprocessing text data...")
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.lower().split()
    lemmas = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return " ".join(lemmas)

if not df_balanced.empty:
    df_balanced['clean_text'] = df_balanced['text'].apply(preprocess_text)
    print("Text preprocessing complete.")
else:
    print("No data to preprocess.")

print("\nStep 4: Training the model...")

if not df_balanced.empty and 'clean_text' in df_balanced.columns:
    X_train, X_test, y_train, y_test = train_test_split(
        df_balanced['clean_text'],
        df_balanced['sentiment'],
        test_size=0.2,
        random_state=42,
        stratify=df_balanced['sentiment']
    )

    vectorizer = TfidfVectorizer(max_features=5000)
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_tfidf, y_train)

    y_pred = model.predict(X_test_tfidf)
    print("\nModel Evaluation Report:")
    print(classification_report(y_test, y_pred, target_names=['Negative', 'Positive']))

    print("\nStep 5: Saving the model and vectorizer...")
    joblib.dump(model, 'sentiment_model.joblib')
    joblib.dump(vectorizer, 'tfidf_vectorizer.joblib')

    print("\nTraining complete. 'sentiment_model.joblib' and 'tfidf_vectorizer.joblib' are saved.")
else:
    print("Skipping model training as no data was loaded or processed.")
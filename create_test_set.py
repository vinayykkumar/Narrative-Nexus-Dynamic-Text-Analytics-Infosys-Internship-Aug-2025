import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
import os

def create_test_data_from_sources():
    """
    Loads all raw sentiment datasets, performs cleaning, balancing, and
    preprocessing, and saves a 20% test split to 'test_data.csv'.
    """
    print("--- Starting Test Data Generation ---")


    print("Downloading NLTK resources (stopwords, wordnet)...")
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)


    print("\nStep 1: Loading and combining raw datasets...")


    path_sentiment140 = 'sentiment140.csv'
    path_imdb_reviews = 'IMDB Dataset.csv'
    path_amazon_labelled = 'amazon_cells_labelled.csv'
    path_yelp_labelled = 'yelp_labelled.csv'
    amazon_fasttext_files = [
        'train.ft.txt',
        'test.ft.txt'
    ]


    # --- Load Data Sources with Error Handling ---
    try:
        cols = ['sentiment', 'id', 'date', 'query', 'user', 'text']
        df_twitter = pd.read_csv(path_sentiment140, header=None, names=cols, encoding='ISO-8859-1')
        df_twitter = df_twitter[['text', 'sentiment']]
        df_twitter['sentiment'] = df_twitter['sentiment'].replace({0: 0, 4: 1})
    except FileNotFoundError:
        print(f"Warning: File not found at '{path_sentiment140}'. Skipping.")
        df_twitter = pd.DataFrame()

    try:
        df_imdb = pd.read_csv(path_imdb_reviews)
        df_imdb = df_imdb[['review', 'sentiment']]
        df_imdb.rename(columns={'review': 'text'}, inplace=True)
        df_imdb['sentiment'] = df_imdb['sentiment'].map({'negative': 0, 'positive': 1})
    except FileNotFoundError:
        print(f"Warning: File not found at '{path_imdb_reviews}'. Skipping.")
        df_imdb = pd.DataFrame()

    try:
        df_amazon = pd.read_csv(path_amazon_labelled, sep='\t', header=None, names=['text', 'sentiment'])
        df_yelp = pd.read_csv(path_yelp_labelled, sep='\t', header=None, names=['text', 'sentiment'])
        df_labelled = pd.concat([df_amazon, df_yelp], ignore_index=True)
    except FileNotFoundError:
        print("Warning: One or more of the 'labelled' sentence files were not found. Skipping.")
        df_labelled = pd.DataFrame()

    amazon_reviews_data = []
    for file_path in amazon_fasttext_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    label_str, text = line.split(' ', 1)
                    sentiment = 1 if label_str == '__label__2' else 0
                    amazon_reviews_data.append({'text': text.strip(), 'sentiment': sentiment})
        except FileNotFoundError:
            print(f"Warning: Amazon review file not found at '{file_path}'. Skipping.")
    df_amazon_reviews = pd.DataFrame(amazon_reviews_data)

    # --- Combine and perform initial cleaning ---
    df_combined = pd.concat([df_twitter, df_imdb, df_labelled, df_amazon_reviews], ignore_index=True)
    df_combined.dropna(inplace=True)
    df_combined.drop_duplicates(subset=['text'], inplace=True)

    if df_combined.empty:
        print("\n❌ Error: No data was loaded. Please check your file paths. Aborting.")
        return

    print(f"✅ Combined {len(df_combined):,} unique records.")

    # ==============================================================================
    # 2. HANDLE CLASS IMBALANCE
    # ==============================================================================
    print("\nStep 2: Balancing classes via undersampling...")
    min_class_size = df_combined['sentiment'].value_counts().min()
    df_balanced = pd.concat([
        df_combined[df_combined['sentiment'] == 0].sample(min_class_size, random_state=42),
        df_combined[df_combined['sentiment'] == 1].sample(min_class_size, random_state=42)
    ])
    print(f"✅ Data balanced to {min_class_size:,} records per class.")

    # ==============================================================================
    # 3. PREPROCESS TEXT DATA
    # ==============================================================================
    print("\nStep 3: Preprocessing text data (cleaning, lemmatizing)...")
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    def preprocess_text(text):
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'<.*?>', '', text)
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        tokens = text.lower().split()
        lemmas = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
        return " ".join(lemmas)

    df_balanced['clean_text'] = df_balanced['text'].apply(preprocess_text)
    print("✅ Text preprocessing complete.")

    # ==============================================================================
    # 4. SPLIT DATA AND SAVE THE TEST SET
    # ==============================================================================
    print("\nStep 4: Splitting data and saving the test set...")
    _, X_test, _, y_test = train_test_split(
        df_balanced['clean_text'],
        df_balanced['sentiment'],
        test_size=0.2, # Reserve 20% for the test set
        random_state=42,
        stratify=df_balanced['sentiment']
    )

    # Combine the test features and labels into a single DataFrame
    test_data_df = pd.DataFrame({'clean_text': X_test, 'sentiment': y_test})

    # Save the DataFrame to a CSV file
    test_data_df.to_csv('test_data.csv', index=False)

    print(f"\n--- ✅ Success! ---")
    print(f"A test set with {len(test_data_df):,} records has been saved to 'test_data.csv'.")
    print("You can now use this file with the 'evaluate_model.py' script.")

if __name__ == '__main__':
    create_test_data_from_sources()

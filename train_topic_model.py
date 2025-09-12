import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB



# --- 1. LOAD THE CLEANED NEWS ARTICLE DATA ---
try:
    # This uses the cleaned data from your first dataset (the news articles)
    df = pd.read_csv('cleaned_articles.csv')
    df.dropna(subset=['cleaned_content'], inplace=True)
    print("✅ Cleaned articles data for topic modeling loaded successfully.")
except FileNotFoundError:
    print("❌ Error: 'cleaned_articles.csv' not found.")
    print("Please run the 'preprocess_data.py' script first.")
    exit()

print("-------------------------------------------\n")


# --- 2. FEATURE ENGINEERING (TF-IDF) & DATA SPLIT ---
print("🚀 Preparing data and training the topic model...")

# Initialize the Vectorizer
# Note: We are using the 'cleaned_content' column
tfidf_vectorizer = TfidfVectorizer(max_features=5000)
X = tfidf_vectorizer.fit_transform(df['cleaned_content'])
y = df['category']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)


# --- 3. TRAIN THE NAIVE BAYES CLASSIFIER ---
model = MultinomialNB()
model.fit(X_train, y_train)

print("✅ Topic model training complete.")
print("-------------------------------------------\n")


# --- 4. SAVE THE MODEL AND VECTORIZER ---
print("💾 Saving the topic model and vectorizer to files...")

# Save the vectorizer with the correct name
joblib.dump(tfidf_vectorizer, 'topic_vectorizer.joblib')

# Save the model with the correct name
joblib.dump(model, 'topic_classifier_model.joblib')

print("🎉 Success! 'topic_vectorizer.joblib' and 'topic_classifier_model.joblib' have been created.")
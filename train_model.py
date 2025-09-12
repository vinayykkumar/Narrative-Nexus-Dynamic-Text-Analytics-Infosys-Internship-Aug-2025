import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# ==============================================================================
# == SENTIMENT ANALYSIS MODEL TRAINING ==
# ==============================================================================

# --- 1. LOAD THE CLEANED SENTIMENT DATA ---
try:
    # We are now loading the output from our new preprocessing script
    df = pd.read_csv('cleaned_sentiment_data.csv')
    df.dropna(subset=['cleaned_review'], inplace=True)
    print("✅ Cleaned sentiment data loaded successfully.")
except FileNotFoundError:
    print("❌ Error: 'cleaned_sentiment_data.csv' not found.")
    print("Please run 'preprocess_sentiment_data.py' first to generate the file.")
    exit()

print("Data shape:", df.shape)
print("-------------------------------------------\n")


# --- 2. FEATURE ENGINEERING (TF-IDF) ---
print("🚀 Starting TF-IDF Vectorization...")

tfidf_vectorizer = TfidfVectorizer(max_features=5000)

# The features (X) are now from the 'cleaned_review' column
# The target (y) is the 'sentiment' column
X = tfidf_vectorizer.fit_transform(df['cleaned_review'])
y = df['sentiment']

print("✅ Text data has been converted into numerical vectors.")
print("Shape of the TF-IDF matrix:", X.shape)
print("-------------------------------------------\n")


# --- 3. SPLIT DATA INTO TRAINING AND TESTING SETS ---
print("Splitting data into training and testing sets...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set size: {X_train.shape[0]} reviews")
print(f"Testing set size: {X_test.shape[0]} reviews")
print("-------------------------------------------\n")


# --- 4. TRAIN THE NAIVE BAYES CLASSIFIER ---
print("Training the Naive Bayes model for sentiment analysis...")

model = MultinomialNB()
model.fit(X_train, y_train)

print("✅ Sentiment model training complete.")
print("-------------------------------------------\n")


# --- 5. EVALUATE THE MODEL'S PERFORMANCE ---
print("Evaluating the sentiment model's performance...")

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"📈 Model Accuracy: {accuracy * 100:.2f}%")
print("\n")

print("📊 Classification Report:")
print(classification_report(y_test, y_pred))
print("\n")

# --- 6. VISUALIZE THE CONFUSION MATRIX ---
print("Generating a heatmap for the confusion matrix...")

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens',
            xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
plt.title('Sentiment Analysis Confusion Matrix', fontsize=16)
plt.ylabel('Actual Sentiment', fontsize=14)
plt.xlabel('Predicted Sentiment', fontsize=14)
plt.show()

print("\n🎉 Sentiment analysis model has been trained and evaluated.")

import joblib

# --- 7. SAVE THE SENTIMENT MODEL AND VECTORIZER ---
print("Saving the trained sentiment model and its TF-IDF vectorizer...")

# Note: We are using different filenames to keep them separate from the topic model
joblib.dump(tfidf_vectorizer, 'sentiment_vectorizer.joblib')
joblib.dump(model, 'sentiment_model.joblib')

print("✅ Sentiment model and vectorizer have been saved successfully.")
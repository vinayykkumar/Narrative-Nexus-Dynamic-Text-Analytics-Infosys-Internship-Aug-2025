import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# ==============================================================================
# == PHASE 3: FEATURE ENGINEERING & MODEL BUILDING ==
# ==============================================================================

# --- 1. LOAD THE CLEANED DATA ---
try:
    df = pd.read_csv('cleaned_articles.csv')
    # Drop rows where cleaned_content might be empty or NaN after processing
    df.dropna(subset=['cleaned_content'], inplace=True)
    print("✅ Cleaned articles data loaded successfully.")
except FileNotFoundError:
    print("❌ Error: 'cleaned_articles.csv' not found.")
    print("Please run the 'preprocess_data.py' script first to generate the file.")
    exit()

print("Data shape:", df.shape)
print("-------------------------------------------\n")


# --- 2. FEATURE ENGINEERING (TF-IDF) ---
print("🚀 Starting TF-IDF Vectorization...")

# Initialize the TF-IDF Vectorizer
# max_features=5000 means we'll only consider the top 5,000 most frequent words
tfidf_vectorizer = TfidfVectorizer(max_features=5000)

# X contains the features (our cleaned text)
# y contains the target labels (the article categories)
X = tfidf_vectorizer.fit_transform(df['cleaned_content'])
y = df['category']

print("✅ Text data has been converted into numerical vectors.")
print("Shape of the TF-IDF matrix:", X.shape)
print("-------------------------------------------\n")


# --- 3. SPLIT DATA INTO TRAINING AND TESTING SETS ---
print("Splitting data into training and testing sets...")

# We'll use 80% of the data for training and 20% for testing
# random_state ensures we get the same split every time we run the script
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set size: {X_train.shape[0]} articles")
print(f"Testing set size: {X_test.shape[0]} articles")
print("-------------------------------------------\n")


# --- 4. TRAIN THE NAIVE BAYES CLASSIFIER ---
print("Training the Naive Bayes model...")

# Initialize the Multinomial Naive Bayes classifier
model = MultinomialNB()

# Train the model on the training data
model.fit(X_train, y_train)

print("✅ Model training complete.")
print("-------------------------------------------\n")


# --- 5. EVALUATE THE MODEL'S PERFORMANCE ---
print("Evaluating the model's performance...")

# Make predictions on the test data (data the model has never seen)
y_pred = model.predict(X_test)

# Calculate the accuracy of the model
accuracy = accuracy_score(y_test, y_pred)
print(f"📈 Model Accuracy: {accuracy * 100:.2f}%")
print("\n")

# Display a detailed classification report
print("📊 Classification Report:")
print(classification_report(y_test, y_pred))
print("\n")

# Display a confusion matrix
print("Matrix of Confusion (True Labels vs. Predicted Labels):")
cm = confusion_matrix(y_test, y_pred)
print(cm)
print("\n")


# --- 6. VISUALIZE THE CONFUSION MATRIX ---
print("Generating a heatmap for the confusion matrix...")

plt.figure(figsize=(10, 7))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=model.classes_, yticklabels=model.classes_)
plt.title('Confusion Matrix', fontsize=16)
plt.ylabel('Actual Category', fontsize=14)
plt.xlabel('Predicted Category', fontsize=14)
plt.show()

print("\n🎉 Phase 3 complete! The model has been trained and evaluated.")
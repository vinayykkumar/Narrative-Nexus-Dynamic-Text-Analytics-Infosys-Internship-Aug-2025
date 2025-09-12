import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# ==============================================================================
# == PHASE 3: TOPIC MODELING IMPLEMENTATION ==
# ==============================================================================

# --- 1. LOAD THE CLEANED DATA ---
try:
    df = pd.read_csv('cleaned_articles.csv')
    df.dropna(subset=['cleaned_content'], inplace=True)
    print("✅ Cleaned articles data loaded successfully.")
except FileNotFoundError:
    print("❌ Error: 'cleaned_articles.csv' not found.")
    print("Please run the 'preprocess_data.py' script first to generate the file.")
    exit()

print("-------------------------------------------\n")


# --- 2. PREPARE DATA FOR TOPIC MODELING ---
print("🚀 Preparing text data for LDA Topic Modeling...")
vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words='english')
doc_term_matrix = vectorizer.fit_transform(df['cleaned_content'])
print("✅ Text data has been converted into a document-term matrix.")
print("Shape of the matrix:", doc_term_matrix.shape)
print("-------------------------------------------\n")


# --- 3. IMPLEMENT AND TRAIN THE LDA MODEL ---
# THE FIX: I've renamed this variable for clarity. This is the only line you need to change for experiments.
num_topics = 9 

# THE FIX: The print statement now uses the variable.
print(f"🧠 Training the LDA model to identify {num_topics} key topics...")

# Initialize the LDA model.
# THE FIX: The model now correctly uses your 'num_topics' variable.
lda_model = LatentDirichletAllocation(n_components=num_topics, random_state=42)

# Train the LDA model on our data
lda_model.fit(doc_term_matrix)

print("✅ LDA model training complete.")
print("-------------------------------------------\n")


# --- 4. DISPLAY THE DISCOVERED TOPICS AND KEYWORDS ---
print("🔍 Displaying the top keywords for each discovered topic:")

# Get the feature names (the actual words) from the vectorizer
feature_names = vectorizer.get_feature_names_out()

# Loop through each topic and print the top 15 words
for topic_idx, topic in enumerate(lda_model.components_):
    # Get the top 15 words for the current topic
    top_words = [feature_names[i] for i in topic.argsort()[:-16:-1]]
    print(f"\nTopic #{topic_idx + 1}:")
    print(" ".join(top_words))

print("\n\n🎉 Topic modeling complete! These are the themes the model found on its own.")

# --- ADD THIS TO THE END of topic_modeling.py ---

print("-------------------------------------------\n")
print(" perplexity score...")

# The score is calculated on the document-term matrix
perplexity = lda_model.perplexity(doc_term_matrix)

print(f"📉 Perplexity Score: {perplexity:.4f}")
print("(A lower score is better)")
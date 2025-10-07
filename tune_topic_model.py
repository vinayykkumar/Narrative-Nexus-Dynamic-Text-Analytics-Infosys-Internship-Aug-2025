import pandas as pd
import spacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import GridSearchCV

# ==============================================================================
# == 1. LOAD AND PREPARE DATA ==
# ==============================================================================
# This section is the same as your topic_modeling.py script
try:
    nlp = spacy.load('en_core_web_sm')
    df = pd.read_csv('cleaned_articles.csv')
    df.dropna(subset=['cleaned_content'], inplace=True)
    print("✅ Data loaded successfully.")
except Exception as e:
    print(f"❌ Error during setup: {e}")
    exit()

def filter_nouns_spacy(text):
    if not isinstance(text, str): return ""
    doc = nlp(text)
    nouns = [token.lemma_ for token in doc if token.pos_ in ('NOUN', 'PROPN')]
    return " ".join(nouns)

print("🚀 Filtering for nouns...")
df['noun_content'] = df['cleaned_content'].apply(filter_nouns_spacy)
print("✅ Noun filtering complete.")

vectorizer = CountVectorizer(max_df=0.95, min_df=5, max_features=1000, stop_words='english')
doc_term_matrix = vectorizer.fit_transform(df['noun_content'])
print("✅ Document-term matrix created.")
print("-------------------------------------------\n")

# ==============================================================================
# == 2. SET UP AND RUN THE GRID SEARCH FOR HYPERPARAMETER TUNING ==
# ==============================================================================

print("🔍 Setting up Grid Search for LDA...")

# Define the grid of parameters to search.
# We will test different numbers of topics and different learning decay rates.
param_grid = {
    'n_components': [5, 7, 9, 11],
    'learning_decay': [0.5, 0.7, 0.9]
}

# Initialize the LDA model
lda = LatentDirichletAllocation(random_state=42)

# Set up the GridSearchCV object
# 'cv=3' means it will use 3-fold cross-validation.
# 'n_jobs=-1' tells it to use all available CPU cores to speed up the process.
search = GridSearchCV(lda, param_grid=param_grid, cv=3, n_jobs=-1, verbose=10)

print("🚀 Starting the search for the best model parameters...")
print("This will take several minutes. Please be patient.")

# Run the search
search.fit(doc_term_matrix)

print("✅ Grid Search complete!")
print("-------------------------------------------\n")

# ==============================================================================
# == 3. DISPLAY THE BEST RESULTS ==
# ==============================================================================

print("🏆 Best Model Parameters Found:")
print(search.best_params_)

print("\nBest Log-Likelihood Score:")
print(search.best_score_)

# You can now use these best parameters in your topic_modeling.py script
# to get the highest quality topics.
print("\nTo get the best topics, update your 'topic_modeling.py' script with these parameters.")
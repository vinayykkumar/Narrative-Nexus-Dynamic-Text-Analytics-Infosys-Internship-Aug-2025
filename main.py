import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# ---------------- CONFIG ---------------- #
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ✅ Change this to whichever dataset you want:
# Example: "collegereview2021.csv" or "job_postings.csv" or "bow_features.csv"
PREFERRED_DATASET = "collegereview2021.csv"
# ---------------------------------------- #

def list_datasets():
    """List available CSV datasets in the data folder."""
    return [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

def choose_dataset():
    """Automatically pick the preferred dataset if available."""
    datasets = list_datasets()
    if not datasets:
        raise FileNotFoundError(f"No CSV dataset found in {DATA_DIR}. Place at least one CSV there.")

    if PREFERRED_DATASET in datasets:
        print(f"✅ Using preferred dataset: {PREFERRED_DATASET}")
        return os.path.join(DATA_DIR, PREFERRED_DATASET)

    # fallback: pick first dataset
    print(f"⚠️ Preferred dataset '{PREFERRED_DATASET}' not found. Using: {datasets[0]}")
    return os.path.join(DATA_DIR, datasets[0])

def load_data(csv_path):
    """Load dataset from CSV file."""
    print(f"📂 Loading dataset: {csv_path}")
    return pd.read_csv(csv_path)

def vectorize_text(data, column="text", method="bow"):
    """Convert text data into BoW or TF-IDF vectors."""
    if method == "bow":
        vectorizer = CountVectorizer(stop_words="english")
    else:
        vectorizer = TfidfVectorizer(stop_words="english")

    features = vectorizer.fit_transform(data[column].astype(str))
    return features, vectorizer

def reduce_dimensions(features, n_components=2):
    """Apply PCA for dimensionality reduction."""
    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(features.toarray())
    return reduced

def visualize(reduced, title="PCA Visualization"):
    """Visualize reduced feature space."""
    plt.figure(figsize=(8, 6))
    plt.scatter(reduced[:, 0], reduced[:, 1], alpha=0.5)
    plt.title(title)
    plt.xlabel("PCA 1")
    plt.ylabel("PCA 2")
    plt.show()

def main():
    csv_path = choose_dataset()
    df = load_data(csv_path)

    # ✅ Assuming dataset has a column named "text"
    if "text" not in df.columns:
        raise KeyError("Dataset must contain a 'text' column for processing.")

    # Vectorize
    features, vectorizer = vectorize_text(df, method="tfidf")

    # Reduce dimensions
    reduced = reduce_dimensions(features)

    # Visualize
    visualize(reduced, title=f"PCA of {os.path.basename(csv_path)}")

if __name__ == "__main__":
 main()

import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def train_lda(docs, n_topics=5, max_features=10000, save_path=None):
    """Train LDA topic model"""
    vec = CountVectorizer(max_features=max_features)
    X = vec.fit_transform(docs)
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(X)
    if save_path:
        joblib.dump({'vectorizer': vec, 'model': lda}, save_path)
    return vec, lda

def print_topics(vectorizer, model, n_top_words=10):
    """Print top words for each topic"""
    feature_names = vectorizer.get_feature_names_out()
    for idx, topic in enumerate(model.components_):
        top_features = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
        print(f"Topic {idx}: {' '.join(top_features)}")

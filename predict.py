import joblib
from preprocess_data import clean_text as clean_topic_text
from preprocess_sentiment_data import clean_text as clean_sentiment_text

# ==============================================================================
# == LOAD ALL TRAINED MODELS AND VECTORIZERS ==
# ==============================================================================
print("🧠 Loading all models and vectorizers...")

# --- Load Topic Modeling Components ---

try:
    topic_vectorizer = joblib.load('topic_vectorizer.joblib')
    topic_model = joblib.load('topic_classifier_model.joblib')
    print("✅ Topic model loaded successfully.")
except FileNotFoundError:
    print("❌ Error: Topic model files not found. Please ensure 'topic_vectorizer.joblib' and 'topic_classifier_model.joblib' exist.")
    exit()


# --- Load Sentiment Analysis Components ---
try:
    sentiment_vectorizer = joblib.load('sentiment_vectorizer.joblib')
    sentiment_model = joblib.load('sentiment_model.joblib')
    print("✅ Sentiment model loaded successfully.")
except FileNotFoundError:
    print("❌ Error: Sentiment model files not found. Please ensure you have run 'train_model.py' to save the sentiment model.")
    exit()

print("-------------------------------------------\n")


# ==============================================================================
# == PREDICTION FUNCTION ==
# ==============================================================================

def get_combined_prediction(text):
    """
    Takes raw text, cleans it, and returns predictions from both models.
    """
    # --- Topic Prediction ---
    # 1. Clean the text using the same function as the topic model
    cleaned_for_topic = clean_topic_text(text)
    # 2. Transform the cleaned text using the topic vectorizer
    topic_vector = topic_vectorizer.transform([cleaned_for_topic])
    # 3. Predict the topic
    topic_prediction = topic_model.predict(topic_vector)[0]


    # --- Sentiment Prediction ---
    # 1. Clean the text using the same function as the sentiment model
    cleaned_for_sentiment = clean_sentiment_text(text)
    # 2. Transform the cleaned text using the sentiment vectorizer
    sentiment_vector = sentiment_vectorizer.transform([cleaned_for_sentiment])
    # 3. Predict the sentiment
    sentiment_prediction = sentiment_model.predict(sentiment_vector)[0]
    
    return {
        'topic': topic_prediction,
        'sentiment': sentiment_prediction
    }

# ==============================================================================
# == EXAMPLE USAGE ==
# ==============================================================================

if __name__ == '__main__':
    # Example sentence 1: A positive tech review
    sample_text_1 = "The new iPhone's camera is absolutely amazing and worth the upgrade!"
    prediction_1 = get_combined_prediction(sample_text_1)
    
    print(f"Input Text: '{sample_text_1}'")
    print(f"Predicted Topic: {prediction_1['topic']}")
    print(f"Predicted Sentiment: {prediction_1['sentiment']}")
    print("-" * 20)
    
    # Example sentence 2: A negative sports comment
    sample_text_2 = "The team played terribly in the final match, it was a disappointing performance."
    prediction_2 = get_combined_prediction(sample_text_2)
    
    print(f"Input Text: '{sample_text_2}'")
    print(f"Predicted Topic: {prediction_2['topic']}")
    print(f"Predicted Sentiment: {prediction_2['sentiment']}")
    print("-" * 20)
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import os
import docx
import PyPDF2
import pandas as pd
from wordcloud import WordCloud # <-- NEW: Import WordCloud
import io # <-- NEW: Used to handle image data in memory
import base64 # <-- NEW: Used to encode the image

from summarize import summarize_text
from preprocess_data import clean_text as clean_topic_text
from preprocess_sentiment_data import clean_text as clean_sentiment_text

# --- (Initialization and model loading remains the same) ---
app = Flask(__name__)
CORS(app)
# ... (rest of the model loading code) ...
print("🧠 Loading all models and vectorizers...")
try:
    topic_vectorizer = joblib.load('topic_vectorizer.joblib')
    topic_model = joblib.load('topic_classifier_model.joblib')
    sentiment_vectorizer = joblib.load('sentiment_vectorizer.joblib')
    sentiment_model = joblib.load('sentiment_model.joblib')
    print("✅ All models loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model files: {e}")
    exit()
print("-------------------------------------------\n")


# --- (Text extraction and prediction functions remain the same) ---
def extract_text_from_file(file):
    # ... (code for this function is unchanged) ...
    filename = file.filename
    text = ""
    if filename.endswith('.txt'):
        text = file.read().decode('utf-8')
    elif filename.endswith('.docx'):
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif filename.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    elif filename.endswith('.csv'):
        df = pd.read_csv(file)
        text = "\n".join(df.iloc[:, 0].astype(str).tolist())
    else:
        raise ValueError("Unsupported file type")
    return text

def get_combined_prediction(text):
    # ... (code for this function is unchanged) ...
    cleaned_for_topic = clean_topic_text(text)
    topic_vector = topic_vectorizer.transform([cleaned_for_topic])
    topic_prediction = topic_model.predict(topic_vector)[0]

    cleaned_for_sentiment = clean_sentiment_text(text)
    sentiment_vector = sentiment_vectorizer.transform([cleaned_for_sentiment])
    sentiment_prediction = sentiment_model.predict(sentiment_vector)[0]
    
    return {'topic': topic_prediction, 'sentiment': sentiment_prediction}
    
# ==============================================================================
# == NEW: WORD CLOUD GENERATION FUNCTION ==
# ==============================================================================
def generate_wordcloud(text):
    """
    Generates a word cloud image from text and returns it as a Base64 encoded string.
    """
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    img_buffer = io.BytesIO()
    wordcloud.to_image().save(img_buffer, format='PNG')
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

# ==============================================================================
# == UPDATED API ENDPOINTS ==
# ==============================================================================

# --- Function to handle the analysis logic for both endpoints ---
def perform_full_analysis(input_text):
    """
    Performs all analyses (topic, sentiment, summary, wordcloud) on the input text.
    """
    if not input_text or not input_text.strip():
        raise ValueError("Input text is empty.")
        
    predictions = get_combined_prediction(input_text)
    summary = summarize_text(input_text)
    wordcloud_image = generate_wordcloud(input_text) # <-- NEW
    
    return {
        'topic': predictions['topic'],
        'sentiment': predictions['sentiment'],
        'summary': summary,
        'wordcloud': wordcloud_image # <-- NEW
    }

# This endpoint handles pasted text
@app.route('/analyze_text', methods=['POST'])
def analyze_pasted_text():
    try:
        data = request.get_json()
        input_text = data['text']
        results = perform_full_analysis(input_text)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# This endpoint handles file uploads
@app.route('/analyze_file', methods=['POST'])
def analyze_uploaded_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        input_text = extract_text_from_file(file)
        results = perform_full_analysis(input_text)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==============================================================================
# == RUN FLASK APP (No changes here) ==
# ==============================================================================
if __name__ == '__main__':
    app.run(debug=True)
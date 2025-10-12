import os
import re
import logging
import torch
import PyPDF2
import docx
import joblib
import numpy as np
from collections import defaultdict
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager
from transformers import LEDForConditionalGeneration, LEDTokenizer, pipeline
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

SENTIMENT_MODEL_PATH = r"C:\Users\nithi\PycharmProjects\infosys_project_trial_2\backend\sentiment_model.joblib"
TFIDF_VECTORIZER_PATH = r"C:\Users\nithi\PycharmProjects\infosys_project_trial_2\backend\tfidf_vectorizer.joblib"
SUMMARIZER_MODEL_PATH = r"C:\Users\nithi\PycharmProjects\infosys_project_trial_2\summarzation_and_insight\led_base_universal_summarizer"
NER_MODEL_NAME = "dbmdz/bert-large-cased-finetuned-conll03-english"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(_name_)
CORS(app)

basedir = os.path.abspath(os.path.dirname(_file_))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-super-secret-key-change-this'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def _init_(self, username, password):
        self.username = username
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

device = "cuda" if torch.cuda.is_available() else "cpu"
logging.info(f"Using device: {device}")

logging.info("Loading trained sentiment model and vectorizer...")
try:
    sentiment_model = joblib.load(SENTIMENT_MODEL_PATH)
    tfidf_vectorizer = joblib.load(TFIDF_VECTORIZER_PATH)
    logging.info("Trained sentiment model loaded successfully.")
except FileNotFoundError:
    sentiment_model = None
    tfidf_vectorizer = None
    logging.warning("Sentiment model or vectorizer not found. Sentiment prediction will be unavailable.")

vader_analyzer = SentimentIntensityAnalyzer()
nltk.download('punkt', quiet=True)

logging.info("Loading fine-tuned summarization model...")
try:
    summarization_tokenizer = LEDTokenizer.from_pretrained(SUMMARIZER_MODEL_PATH)
    summarization_model = LEDForConditionalGeneration.from_pretrained(SUMMARIZER_MODEL_PATH)
    summarization_model.to(device)
    logging.info("Summarization model loaded successfully.")
except OSError:
    summarization_model = None
    summarization_tokenizer = None
    logging.warning("Summarization model not found. Summarization will be unavailable.")

logging.info("Loading NER model for insight generation...")
try:
    ner_pipeline = pipeline("ner", model=NER_MODEL_NAME, grouped_entities=True, device=0 if device == "cuda" else -1)
    logging.info("NER model loaded successfully.")
except Exception as e:
    ner_pipeline = None
    logging.warning(f"NER model could not be loaded: {e}. Insight generation will be unavailable.")

def final_clean_text(raw_text):
    text = re.sub(r'©.?www\.ijrti\.org.?\d+', '', raw_text, flags=re.DOTALL)
    text = re.sub(r'IJRTI\d+.www\.ijrti\.org.?\d+', '', text, flags=re.DOTALL)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r' +', ' ', text)
    return text

def split_text_into_sections(text):
    pattern = r'\n\s*(\d+\.\s*.|KEYWORDS.|INTRODUCTION.|ABSTRACT.|Conclusion|References|[A-Z][A-Z\s-]{5,}:)\s*\n'
    parts = re.split(f'({pattern})', text)
    if len(parts) < 3:
        return []
    sections = []
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        content = parts[i + 1].strip()
        if len(content.split()) > 20:
            sections.append({'heading': heading, 'content': content})
    return sections

def filter_insights(entities_dict):
    filtered_dict = defaultdict(set)
    blocklist = {'cha', 'nl', 'java'}
    for entity_type, entities in entities_dict.items():
        for entity in entities:
            clean_entity = entity.strip()
            if clean_entity.lower() in blocklist: continue
            if not re.search(r'[a-zA-Z]', clean_entity): continue
            if len(clean_entity) < 3 and clean_entity.upper() not in ['AI', 'ML', 'UI', 'API']: continue
            filtered_dict[entity_type].add(clean_entity)
    for key in filtered_dict:
        filtered_dict[key] = sorted(list(filtered_dict[key]))
    return dict(filtered_dict)

def extract_text_from_file(file_storage):
    filename = file_storage.filename.lower()
    text_parts = []
    if filename.endswith('.pdf'):
        try:
            pdf_reader = PyPDF2.PdfReader(file_storage.stream)
            for page in pdf_reader.pages:
                if page_text := page.extract_text(): text_parts.append(page_text)
        except Exception as e:
            logging.error(f"Error reading PDF: {e}")
    elif filename.endswith('.docx'):
        try:
            document = docx.Document(file_storage.stream)
            for para in document.paragraphs:
                if para.text: text_parts.append(para.text)
        except Exception as e:
            logging.error(f"Error reading DOCX: {e}")
    else:
        try:
            for line in file_storage.stream: text_parts.append(line.decode('utf-8'))
        except Exception as e:
            logging.error(f"Error reading text file: {e}")
    return "\n".join(text_parts)

def summarize_large_document(full_text, min_len=50, max_len=200):
    if not summarization_tokenizer or not summarization_model: return "Summarization model not available."
    if not full_text or len(full_text.split()) < 10:
        return ""
    inputs = summarization_tokenizer(full_text, return_tensors="pt", max_length=16384, truncation=True).to(device)
    summary_ids = summarization_model.generate(
        inputs['input_ids'], min_length=min_len, max_length=max_len, num_beams=4,
        early_stopping=True, no_repeat_ngram_size=3, repetition_penalty=1.2
    )
    return summarization_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def generate_insights(text):
    if not ner_pipeline: return {"error": "NER model is not loaded."}
    max_chunk_size = 500
    words = text.split()
    chunks = [" ".join(words[i:i + max_chunk_size]) for i in range(0, len(words), max_chunk_size)]
    all_entities = ner_pipeline(chunks)
    aggregated_entities = defaultdict(set)
    for chunk_entities in all_entities:
        for entity in chunk_entities:
            aggregated_entities[entity['entity_group']].add(entity['word'])
    filtered_entities = filter_insights(aggregated_entities)
    return filtered_entities

def get_top_words_for_topics(model, feature_names, n_top_words=10):
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        top_word_indices = topic.argsort()[:-n_top_words - 1:-1]
        topic_words = [feature_names[i] for i in top_word_indices]
        topics.append({"topic_id": topic_idx + 1, "top_words": topic_words})
    return topics

def analyze_topic_sentiments(model, doc_term_matrix, documents, num_topics):
    doc_topic_dist = model.transform(doc_term_matrix)
    dominant_topics = np.argmax(doc_topic_dist, axis=1)
    doc_sentiments = [{'score': vader_analyzer.polarity_scores(doc)['compound'], 'text': doc} for doc in documents]
    topic_docs = [[] for _ in range(num_topics)]
    for doc_idx, topic_idx in enumerate(dominant_topics):
        topic_docs[topic_idx].append(doc_sentiments[doc_idx])
    analysis_results = []
    for i in range(num_topics):
        topic_result = {}
        sorted_docs = sorted(topic_docs[i], key=lambda x: x['score'], reverse=True)
        if sorted_docs:
            avg_score = np.mean([d['score'] for d in sorted_docs])
            label = "Positive" if avg_score >= 0.05 else "Negative" if avg_score <= -0.05 else "Neutral"
            topic_result['sentiment'] = {"score": f"{avg_score:.2f}", "label": label}
        else:
            topic_result['sentiment'] = {"score": "0.00", "label": "Neutral"}
        positive_examples = sorted_docs[:2]
        negative_examples = sorted_docs[-2:] if len(sorted_docs) > 2 else []
        topic_result['example_sentences'] = [{'text': d['text'], 'score': d['score']} for d in positive_examples if
                                             d['score'] > 0.05] + \
                                            [{'text': d['text'], 'score': d['score']} for d in
                                             reversed(negative_examples) if d['score'] < -0.05]
        analysis_results.append(topic_result)
    return analysis_results, doc_topic_dist

def predict_sentiment(text_to_analyze):
    if not sentiment_model or not tfidf_vectorizer:
        return {"error": "Trained sentiment model is not loaded."}
    clean_text = re.sub(r'[^a-zA-Z\s]', '', text_to_analyze).lower()
    if not clean_text.strip(): return {"sentiment": "Neutral", "confidence": "1.00"}
    text_vector = tfidf_vectorizer.transform([clean_text])
    prediction = sentiment_model.predict(text_vector)
    probability = sentiment_model.predict_proba(text_vector)
    sentiment_label = "Positive" if prediction[0] == 1 else "Negative"
    confidence_score = float(np.max(probability))
    return {"sentiment": sentiment_label, "confidence": f"{confidence_score:.2f}"}

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 409
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"User {data['username']} created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.username)
        return jsonify(access_token=access_token), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/upload-and-analyze', methods=['POST', 'OPTIONS'])
def upload_and_analyze():
    if request.method == 'OPTIONS': return jsonify(success=True), 200
    if 'file' not in request.files or not request.files['file'].filename:
        return jsonify({"error": "No file selected."}), 400
    file = request.files['file']
    analysis_type = request.form.get('analysis_type', 'topic_modeling')
    results = {}
    try:
        raw_document_text = extract_text_from_file(file)
        if not raw_document_text.strip():
            return jsonify({"error": "No text could be extracted from the file."}), 400
        clean_block_of_text = final_clean_text(raw_document_text)
        if analysis_type == 'topic_modeling':
            logging.info("Starting topic modeling task...")
            documents = sent_tokenize(re.sub(r'\s+', ' ', clean_block_of_text))
            model_choice = request.form.get('model', 'LDA')
            num_topics = int(request.form.get('num_topics', 5))
            results['overall_sentiment'] = predict_sentiment(clean_block_of_text)
            vectorizer = CountVectorizer(max_df=0.9, min_df=2, stop_words='english', lowercase=True)
            doc_term_matrix = vectorizer.fit_transform(documents)
            vocabulary = vectorizer.get_feature_names_out().tolist()
            n_samples, n_features = doc_term_matrix.shape
            if n_samples < num_topics: num_topics = n_samples
            if num_topics < 2 or n_features < 2:
                return jsonify({"error": "Not enough unique content for topic modeling."}), 400
            model = None
            if model_choice == 'LDA':
                model = LatentDirichletAllocation(n_components=num_topics, random_state=42, n_jobs=-1).fit(
                    doc_term_matrix)
            elif model_choice == 'NMF':
                model = NMF(n_components=num_topics, random_state=42, init='nndsvda').fit(doc_term_matrix)
            if model:
                results['topics'] = get_top_words_for_topics(model, vocabulary)
                topic_sentiment_analysis, doc_topic_dist = analyze_topic_sentiments(model, doc_term_matrix, documents,
                                                                                    num_topics)
                topic_distribution = doc_topic_dist.sum(axis=0)
                topic_distribution_normalized = (topic_distribution / topic_distribution.sum()) * 100
                results['topic_distribution'] = [{'topic_id': i + 1, 'percentage': float(p)} for i, p in
                                                 enumerate(topic_distribution_normalized)]
                for i, topic in enumerate(results['topics']):
                    topic.update(topic_sentiment_analysis[i])
            logging.info("Topic modeling complete.")
        elif analysis_type == 'insights':
            logging.info("Starting insight generation task...")
            if not ner_pipeline: return jsonify({"error": "Insight generation model is not loaded."}), 500
            insights = generate_insights(clean_block_of_text)
            results['insights'] = insights
            results['entity_counts'] = {entity_type: len(entities) for entity_type, entities in insights.items()}
            logging.info("Insight generation complete.")
        elif analysis_type == 'summarization':
            logging.info("Starting paragraph-style summarization task...")
            chunk_size_in_words = 250
            words = clean_block_of_text.split()
            if not words:
                return jsonify({"error": "Document contains no text to summarize."}), 400
            text_chunks = [" ".join(words[i:i + chunk_size_in_words]) for i in
                           range(0, len(words), chunk_size_in_words)]
            chunk_summaries = []
            for chunk in text_chunks:
                chunk_summary = summarize_large_document(chunk, min_len=25, max_len=100)
                if chunk_summary:
                    chunk_summaries.append(chunk_summary)
            intermediate_summary = " ".join(chunk_summaries)
            final_summary = ""
            if len(intermediate_summary.split()) > 50:
                final_summary = summarize_large_document(intermediate_summary, min_len=100, max_len=400)
            if len(final_summary.split()) < 50:
                final_summary = intermediate_summary
            results['summary'] = final_summary.strip()
            results['notes'] = ["A cohesive, paragraph-style summary was generated."]
            logging.info("Paragraph-style summarization complete.")
        else:
            return jsonify({"error": f"Invalid analysis type: {analysis_type}"}), 400
        return jsonify(results)
    except Exception as e:
        logging.error(f"An error occurred during the pipeline: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500

if _name_ == '_main_':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001)

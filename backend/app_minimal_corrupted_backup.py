"""
AI Narrative Nexus - Backend API Server Following Architecture Diagram
FastAPI-based backend implementing the exact architecture flow:
User Interface → Input Data Handling → Data Processing → Text Data Storage → 
Sentiment Analysis/Topic Modeling → Insight Generation → Reporting/Visualization
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple, Union
import uvicorn
import time
import json
import uuid
import re
import math
import os
import csv
from io import StringIO
from collections import Counter, defaultdict
import random
import logging

# Import our architecture-compliant modules
# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from text_data_storage import text_storage
    from insight_generation import insight_generator
    from input_data_handling import input_handler
    from text_preprocessing import preprocess_text_comprehensive
    from advanced_topic_modeling import perform_advanced_topic_modeling, topic_modeling_engine
    ARCHITECTURE_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Architecture modules not available: {e}")
    ARCHITECTURE_MODULES_AVAILABLE = False

app = FastAPI(
    title="AI Narrative Nexus Backend - Architecture Compliant",
    description="Text Analytics API following the specified architecture diagram",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# New architecture-compliant models
class ArchitectureTextInput(BaseModel):
    text: str = Field(..., description="Text input from user interface")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    source_type: str = Field(default="direct", description="Input source type")

class ArchitectureFileUpload(BaseModel):
    session_id: Optional[str] = Field(default=None, description="Session identifier")

class DataProcessingRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for stored data")
    processing_options: Optional[Dict] = Field(default_factory=dict, description="Processing options")

class AnalysisRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for processed data")
    analysis_type: str = Field(..., description="Type of analysis: sentiment or topic")
    analysis_options: Optional[Dict] = Field(default_factory=dict, description="Analysis options")

class InsightGenerationRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for analysis results")

# ============================================================================
# ARCHITECTURE-COMPLIANT API ENDPOINTS
# Following the exact flow from the architecture diagram
# ============================================================================

@app.get("/")
async def root():
    """API Health Check"""
    return {
        "message": "AI Narrative Nexus Backend - Architecture Compliant",
        "version": "2.0.0",
        "status": "running",
        "architecture_flow": [
            "User Interface",
            "Input Data Handling", 
            "Data Processing",
            "Text Data Storage",
            "Sentiment Analysis / Topic Modeling",
            "Insight Generation and Summarization",
            "Reporting Module / Visualization Module"
        ]
    }

# ============================================================================
# STEP 1: USER INTERFACE → INPUT DATA HANDLING
# ============================================================================

@app.post("/input/text", response_model=Dict)
async def handle_text_input(request: ArchitectureTextInput):
    """
    Handle text input from User Interface
    Architecture: User Interface → Input Data Handling
    """
    logger.info(f"🎯 STEP 1: User Interface → Input Data Handling")
    logger.info(f"📝 Processing text input (length: {len(request.text)})")
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Store session data first
        text_storage.store_session(session_id, request.text)
        
        # Use Input Data Handling module
        processed_input = input_handler.handle_text_input(
            request.text, 
            request.source_type
        )
        
        # Add session information
        processed_input['session_id'] = session_id
        
        logger.info(f"✅ Input handling complete for session: {session_id}")
        return {
            "status": "success",
            "session_id": session_id,
            "processed_input": processed_input,
            "next_step": "data_processing",
            "next_endpoint": f"/process/data/{session_id}"
        }
        
    except Exception as e:
        logger.error(f"❌ Input handling failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/input/file", response_model=Dict)
async def handle_file_upload(file: UploadFile = File(...), session_id: Optional[str] = None):
    """
    Handle file upload from User Interface
    Architecture: User Interface → Input Data Handling (Upload Text Data)
    """
    logger.info(f"🎯 STEP 1: User Interface → Input Data Handling (File Upload)")
    logger.info(f"📂 Processing file: {file.filename}")
    
    try:
        # Generate session ID if not provided
        session_id = session_id or str(uuid.uuid4())
        
        # Check if it's a CSV file for special handling
        file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ''
        
        if file_ext == '.csv':
            # Handle CSV files as separate documents for topic modeling
            logger.info(f"📊 Processing CSV file as separate documents")
            
            # Extract documents from CSV
            documents = input_handler.extract_csv_documents(file)
            if not documents:
                raise HTTPException(status_code=400, detail="No valid text documents found in CSV file")
            
            # Store documents in session
            text_storage.store_session_documents(session_id, documents)
            
            # Create processed input response
            processed_input = {
                'content_type': 'csv_documents',
                'documents_count': len(documents),
                'preview_texts': documents[:3],  # Show first 3 for preview
                'total_characters': sum(len(doc) for doc in documents),
                'file_info': {
                    'filename': file.filename,
                    'size': len(str(documents)),
                    'format': 'csv'
                }
            }
            
        else:
            # Handle other file types as single document
            processed_input = input_handler.handle_file_upload(file)
            
            # Store session data after processing the file
            file_text = processed_input.get('content', '')
            text_storage.store_session(session_id, file_text)
        
        # Add session information
        processed_input['session_id'] = session_id
        
        logger.info(f"✅ File input handling complete for session: {session_id}")
        return {
            "status": "success",
            "session_id": session_id,
            "processed_input": processed_input,
            "storage_info": {
                "documents_count": processed_input.get('documents_count', 1),
                "total_texts": processed_input.get('documents_count', 1),
                "preview_texts": processed_input.get('preview_texts', [processed_input.get('content', '')[:100] + '...'])
            },
            "next_step": "analysis",
            "next_endpoint": f"/analyze/topics/{session_id}"
        }
        
    except Exception as e:
        logger.error(f"❌ File input handling failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# STEP 2: INPUT DATA HANDLING → DATA PROCESSING → TEXT DATA STORAGE
# ============================================================================

@app.post("/process/data/{session_id}", response_model=Dict)
async def process_and_store_data(session_id: str, options: Optional[Dict] = None):
    """
    Process input data and store in Text Data Storage
    Architecture: Input Data Handling → Data Processing → Text Data Storage
    """
    logger.info(f"🎯 STEP 2: Input Data Handling → Data Processing → Text Data Storage")
    logger.info(f"🔄 Processing data for session: {session_id}")
    
    try:
        options = options or {}
        
        # Get the actual text input from the session
        session_data = text_storage.get_session_data(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Use the actual input text instead of mock data
        original_text = session_data.get('text', '')
        if not original_text:
            raise HTTPException(status_code=400, detail="No text found for this session")
        
        # Process the actual text using the input handler
        processed_result = input_handler.handle_text_input(original_text, source_type="session")
        
        # Apply comprehensive text preprocessing following the specified requirements
        logger.info("🔄 Applying comprehensive text preprocessing...")
        preprocessing_options = {
            'remove_stopwords': True,
            'use_lemmatization': True,
            'min_token_length': 2,
            'max_token_length': 50
        }
        
        preprocessing_result = preprocess_text_comprehensive(original_text, preprocessing_options)
        
        # Extract comprehensive processing results
        processed_data = {
            "original_text": preprocessing_result["original_text"],
            "cleaned_text": preprocessing_result["cleaned_text"],
            "normalized_text": preprocessing_result["normalized_text"],
            "tokens": preprocessing_result["tokens"],
            "processing_stats": {
                "characters_removed": preprocessing_result["stats"]["original_length"] - preprocessing_result["stats"]["cleaned_length"],
                "tokens_generated": preprocessing_result["stats"]["token_count"],
                "vocabulary_size": preprocessing_result["stats"]["vocabulary_size"],
                "processing_time": preprocessing_result["stats"]["processing_time"],
                "urls_removed": preprocessing_result["stats"]["removed_urls"],
                "emails_removed": preprocessing_result["stats"]["removed_emails"],
                "mentions_removed": preprocessing_result["stats"]["removed_mentions"],
                "hashtags_removed": preprocessing_result["stats"]["removed_hashtags"],
                "numbers_removed": preprocessing_result["stats"]["removed_numbers"],
                "stopwords_removed": preprocessing_result["stats"]["removed_stopwords"]
            }
        }
        
        logger.info(f"✅ Comprehensive preprocessing completed:")
        logger.info(f"   • Original length: {preprocessing_result['stats']['original_length']} chars")
        logger.info(f"   • Cleaned length: {preprocessing_result['stats']['cleaned_length']} chars")
        logger.info(f"   • Token count: {preprocessing_result['stats']['token_count']}")
        logger.info(f"   • Vocabulary size: {preprocessing_result['stats']['vocabulary_size']}")
        logger.info(f"   • Stopwords removed: {preprocessing_result['stats']['removed_stopwords']}")
        logger.info(f"   • Processing time: {preprocessing_result['stats']['processing_time']:.3f}s")
        
        # Store in Text Data Storage
        text_id = text_storage.store_processed_text(
            session_id=session_id,
            original_text=processed_data["original_text"],
            cleaned_text=processed_data["cleaned_text"],
            normalized_text=processed_data["normalized_text"],
            tokens=processed_data["tokens"],
            processing_stats=processed_data["processing_stats"]
        )
        
        logger.info(f"✅ Data processing and storage complete. Text ID: {text_id}")
        return {
            "status": "success",
            "session_id": session_id,
            "text_id": text_id,
            "processing_result": processed_data,
            "next_step": "analysis",
            "available_analyses": ["sentiment", "topic_modeling"],
            "next_endpoints": {
                "sentiment": f"/analyze/sentiment/{session_id}",
                "topic_modeling": f"/analyze/topics/{session_id}"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Data processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STEP 3: TEXT DATA STORAGE → SENTIMENT ANALYSIS / TOPIC MODELING
# ============================================================================

@app.post("/analyze/sentiment/{session_id}", response_model=Dict)
async def perform_sentiment_analysis(session_id: str, options: Optional[Dict] = None):
    """
    Perform Sentiment Analysis on stored text data
    Architecture: Text Data Storage → Sentiment Analysis
    """
    logger.info(f"🎯 STEP 3: Text Data Storage → Sentiment Analysis")
    logger.info(f"💭 Performing sentiment analysis for session: {session_id}")
    
    try:
        # Retrieve processed texts from storage
        processed_texts = text_storage.get_processed_texts(session_id)
        
        if not processed_texts:
            raise HTTPException(status_code=404, detail="No processed texts found for session")
        
        # Perform sentiment analysis on the most recent text
        latest_text = processed_texts[0]
        
        # Use existing sentiment analysis logic
        text_to_analyze = latest_text['cleaned_text']
        sentiment_results = await perform_sentiment_analysis_internal({"text": text_to_analyze})
        
        # Store analysis results
        text_storage.store_analysis_result(
            text_id=latest_text['id'],
            analysis_type="sentiment",
            results=sentiment_results
        )
        
        logger.info(f"✅ Sentiment analysis complete for session: {session_id}")
        return {
            "status": "success",
            "session_id": session_id,
            "analysis_type": "sentiment",
            "results": sentiment_results,
            "next_step": "insight_generation",
            "next_endpoint": f"/insights/generate/{session_id}"
        }
        
    except Exception as e:
        logger.error(f"❌ Sentiment analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/topics/{session_id}", response_model=Dict)
async def perform_topic_analysis(session_id: str, options: Optional[Dict] = None):
    """
    Perform Topic Modeling on stored text data following specified requirements:
    ● Algorithm Selection: Choose appropriate algorithms (LDA, NMF) for topic modeling
    ● Latent Dirichlet Allocation (LDA): For identifying latent topics in text data  
    ● Non-negative Matrix Factorization (NMF): As alternative for topic extraction
    ● Model Training: Train selected models on preprocessed text data to identify key themes and topics
    
    Architecture: Text Data Storage → Topic Modeling (LDA, NMF, etc.)
    """
    logger.info(f"🎯 STEP 3: Text Data Storage → Advanced Topic Modeling")
    logger.info(f"🔍 Algorithm Selection and Model Training for session: {session_id}")
    
    try:
        # Get documents from session (handles both single text and multiple documents)
        session_documents = text_storage.get_session_documents(session_id)
        
        if not session_documents:
            raise HTTPException(status_code=404, detail="No documents found for session")
        
        logger.info(f"📄 Retrieved {len(session_documents)} documents from session")
        
        # Preprocess documents for topic modeling
        texts_for_analysis = []
        for doc in session_documents:
            if len(doc.strip()) > 10:  # Only include meaningful documents
                # Basic preprocessing for topic modeling
                cleaned_doc = preprocess_text_comprehensive(doc)
                if cleaned_doc and len(cleaned_doc.strip()) > 5:
                    texts_for_analysis.append(cleaned_doc)
        
        if not texts_for_analysis:
            raise HTTPException(status_code=400, detail="No valid texts found after preprocessing")
        
        logger.info(f"📊 Preprocessed {len(texts_for_analysis)} documents for analysis")
        
        # Handle case of single large document by splitting
        if len(texts_for_analysis) == 1 and len(texts_for_analysis[0]) > 1000:
            logger.info("📄 Single large document detected, splitting for better topic modeling...")
            large_text = texts_for_analysis[0]
            
            # Split by sentences
            sentences = re.split(r'[.!?]+', large_text)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 30]
            
            # Group sentences into chunks
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) > 1000 and current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
                else:
                    current_chunk += sentence + ". "
            
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            if len(chunks) > 1:
                texts_for_analysis = chunks
                logger.info(f"📄 Split into {len(chunks)} chunks for topic modeling")
        
        # Configure topic modeling options
        options = options or {}
        analysis_options = options.get('analysis_options', {})
        
        algorithm = analysis_options.get('algorithm', 'lda')
        num_topics = analysis_options.get('num_topics', min(5, len(texts_for_analysis)))
        
        logger.info(f"🔧 Using algorithm: {algorithm}, num_topics: {num_topics}")
        
        # Perform topic modeling using the advanced engine
        topic_results = perform_advanced_topic_modeling(
            texts=texts_for_analysis,
            num_topics=num_topics,
            algorithm=algorithm,
            options=analysis_options
        )
        
        logger.info(f"✅ Topic modeling completed successfully")
        
        return {
            "status": "success",
            "session_id": session_id,
            "analysis_type": "topic_modeling",
            "results": clean_for_json_serialization(topic_results),
            "input_info": {
                "total_documents": len(session_documents),
                "processed_documents": len(texts_for_analysis),
                "algorithm_used": algorithm,
                "topics_generated": num_topics
            },
            "next_step": "insight_generation",
            "next_endpoint": f"/generate/insights/{session_id}"
        }
        
    except Exception as e:
        logger.error(f"❌ Topic analysis failed for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Topic modeling failed: {str(e)}")

# ============================================================================
# STEP 4: SENTIMENT ANALYSIS + TOPIC MODELING → INSIGHT GENERATION
# ============================================================================

@app.post("/insights/generate/{session_id}", response_model=Dict)
async def generate_insights(session_id: str):
    """
    Generate Insights and Summarization from analysis results
    Architecture: Sentiment Analysis + Topic Modeling → Insight Generation and Summarization
    (Extracted Themes, Key Insights, Recommendations)
    """
    try:
        logger.info(f"🔍 Generating insights for session: {session_id}")
        
        # Retrieve stored analysis results
        session_data = text_storage.get_session_data(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Generate comprehensive insights
        insights = insight_generator.generate_comprehensive_insights(
            session_id=session_id,
            sentiment_results=session_data.get('sentiment_analysis', {}),
            topic_results=session_data.get('topic_modeling', {}),
            text_summaries=session_data.get('text_summaries', [])
        
        # Store insights
        text_storage.store_analysis_result(
            text_id=session_id,
            analysis_type="insights",
            results=insights
        )
        
        logger.info(f"✅ Insights generated successfully for session: {session_id}")
        
        return {
            "status": "success",
            "session_id": session_id,
            "analysis_type": "insights_generation",
            "insights": insights,
            "timestamp": time.time(),
            "next_step": "complete",
            "next_endpoint": None
        }
        
    except Exception as e:
        logger.error(f"❌ Insight generation failed for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")

# ============================================================================
# STEP 4: CSV UPLOAD AND PROCESSING
# ============================================================================

@app.post("/upload-csv", response_model=Dict)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload and process CSV files - each row becomes a separate document
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        # Read CSV content
        content = await file.read()
        csv_data = content.decode('utf-8')
        
        # Extract documents from CSV (each row as separate document)
        documents = extract_csv_documents(csv_data)
        
        logger.info(f"� Extracted {len(documents)} documents from CSV")
        
        return {
            "status": "success",
            "documents_extracted": len(documents),
            "documents": documents[:3],  # Show first 3 as preview
            "message": f"Successfully extracted {len(documents)} documents from CSV"
        }
        
    except Exception as e:
        logger.error(f"❌ CSV processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV processing failed: {str(e)}")

def extract_csv_documents(csv_content: str) -> List[str]:
    """Extract documents from CSV content - each row becomes a separate document"""
    documents = []
    
    try:
        csv_reader = csv.DictReader(StringIO(csv_content))
        
        for row in csv_reader:
            # Combine all non-empty values in the row into a single document
            row_text = ' '.join([str(value) for value in row.values() if str(value).strip()])
            if row_text.strip():
                documents.append(row_text.strip())
        
        return documents
        
    except Exception as e:
        logger.error(f"CSV extraction failed: {e}")
        return []

# ============================================================================
# TOPIC MODELING ENDPOINT
# ============================================================================

class TopicModelingInput(BaseModel):
    texts: List[str]
    num_topics: int = 5
    algorithm: str = 'lda'

@app.post("/topic-modeling", response_model=Dict)
async def topic_modeling_endpoint(input_data: TopicModelingInput):
    """
    Perform topic modeling on provided texts
    """
    try:
        logger.info(f"📊 Received {len(input_data.texts)} documents for topic modeling")
        
        # Preprocess texts individually
        processed_texts = []
        for text in input_data.texts:
            if ARCHITECTURE_MODULES_AVAILABLE:
                result = preprocess_text_comprehensive(text)
                if isinstance(result, dict):
                    processed_text = result.get('processed_text', text)
                else:
                    processed_text = result
            else:
                processed_text = text.lower().strip()
            
            if processed_text.strip():
                processed_texts.append(processed_text)
        
        logger.info(f"🔄 Preprocessed to {len(processed_texts)} valid documents")
        
        if len(processed_texts) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 valid documents required for topic modeling"
            )
        
        # Perform topic modeling
        if ARCHITECTURE_MODULES_AVAILABLE:
            result = perform_advanced_topic_modeling(
                texts=processed_texts,
                algorithm=input_data.algorithm,
                num_topics=input_data.num_topics
            )
        else:
            # Fallback simple result
            result = {
                "algorithm": input_data.algorithm.upper(),
                "num_topics": input_data.num_topics,
                "topics": [f"Topic {i+1}" for i in range(input_data.num_topics)],
                "message": "Architecture modules not available - using fallback"
            }
        
        logger.info(f"✅ Topic modeling completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"❌ Topic modeling failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Topic modeling failed: {str(e)}")

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint providing server info"""
    return {
        "message": "AI Narrative Nexus Backend - Architecture Compliant",
        "status": "running",
        "features": [
            "CSV Upload", 
            "Topic Modeling", 
            "Each Row as Document",
            "Text Preprocessing",
            "Insight Generation"
        ],
        "endpoints": {
            "csv_upload": "/upload-csv",
            "topic_modeling": "/topic-modeling", 
            "insights": "/insights/generate/{session_id}"
        }
    }

# ============================================================================
# SERVER STARTUP
# ============================================================================

def clean_for_json_serialization(obj):
    """Remove any non-JSON-serializable objects from the results"""
    if isinstance(obj, dict):
        cleaned = {}
        for key, value in obj.items():
            # Skip any model objects or other non-serializable items
            if key in ['model_object', 'trained_model', 'lda_model', 'nmf_model']:
                continue
            # Check if value contains SimpleLDA or other model classes
            if hasattr(value, '__class__') and 'LDA' in str(value.__class__):
                continue
            cleaned[key] = clean_for_json_serialization(value)
        return cleaned
    elif isinstance(obj, list):
        return [clean_for_json_serialization(item) for item in obj]
    elif isinstance(obj, set):
        # Convert sets to lists to make them JSON serializable
        return list(obj)
    else:
        return obj

if __name__ == "__main__":
    logger.info("🚀 Starting AI Narrative Nexus Backend")
    logger.info("✅ Features: CSV Upload, Topic Modeling, Insight Generation")
    if ARCHITECTURE_MODULES_AVAILABLE:
        logger.info("✅ All architecture modules loaded successfully")
    else:
        logger.warning("⚠️ Some architecture modules unavailable - using fallback modes")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
            "insights": session_summary['insights'],
            "recommendations": [],
            "appendix": {
                "session_data": session_summary,
                "methodology": "Architecture-compliant NLP pipeline"
            }
        }
        
        logger.info(f"✅ Report generation complete for session: {session_id}")
        return {
            "status": "success",
            "session_id": session_id,
            "report": report,
            "report_format": "json",
            "architecture_flow_complete": True
        }
        
    except Exception as e:
        logger.error(f"❌ Report generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/{session_id}", response_model=Dict)
async def get_dashboard_data(session_id: str):
    """
    Get dashboard data for visualization
    Architecture: Insight Generation → Visualization Module (Dashboard and charts)
    """
    logger.info(f"🎯 STEP 5: Insight Generation → Visualization Module")
    logger.info(f"📈 Generating dashboard data for session: {session_id}")
    
    try:
        # Get complete session data
        session_summary = text_storage.get_session_summary(session_id)
        
        # Format data for visualization
        dashboard_data = {
            "session_id": session_id,
            "overview": {
                "total_texts_processed": session_summary['processed_texts_count'],
                "analysis_types_completed": len(set(a['analysis_type'] for a in session_summary['analysis_results'])),
                "insights_generated": len(session_summary['insights']),
                "last_updated": session_summary['last_updated']
            },
            "visualizations": {
                "sentiment_distribution": {},
                "topic_distribution": {},
                "insight_categories": {},
                "confidence_metrics": {}
            },
            "charts_data": session_summary,
            "desktop_ready": True  # As shown in architecture diagram
        }
        
        # Extract visualization data from analysis results
        for analysis in session_summary['analysis_results']:
            if analysis['analysis_type'] == 'sentiment':
                dashboard_data['visualizations']['sentiment_distribution'] = analysis['results'].get('sentiment_distribution', {})
            elif analysis['analysis_type'] == 'topic_modeling':
                dashboard_data['visualizations']['topic_distribution'] = {
                    'topics': analysis['results'].get('topics', []),
                    'coherence_score': analysis['results'].get('coherence_score', 0)
                }
        
        logger.info(f"✅ Dashboard data ready for session: {session_id}")
        return {
            "status": "success",
            "session_id": session_id,
            "dashboard": dashboard_data,
            "architecture_complete": "User Interface → Input Data Handling → Data Processing → Text Data Storage → Analysis → Insight Generation → Visualization Module"
        }
        
    except Exception as e:
        logger.error(f"❌ Dashboard generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SUPPORTING FUNCTIONS (Existing analysis logic)
# ============================================================================

async def perform_sentiment_analysis_internal(input_data: Dict) -> Dict:
    """Internal sentiment analysis function"""
    # Use existing sentiment analysis logic
    analyzer = SimpleSentimentAnalyzer()
    return analyzer.analyze_text(input_data["text"])

async def perform_topic_modeling_simple(input_data: Dict) -> Dict:
    """Internal topic modeling function for architecture flow"""
    texts = input_data["texts"]
    
    # Use existing topic modeling logic  
    if input_data["algorithm"].lower() == "lda":
        model = SimpleLDA(num_topics=input_data["num_topics"])
        model.fit(texts)
        
        # Extract topics and their top words
        topics = []
        for topic_id in range(model.num_topics):
            top_words = model.get_top_words(topic_id, num_words=10)
            topics.append({
                "topic_id": topic_id,
                "words": [word for word, prob in top_words],
                "probabilities": [prob for word, prob in top_words]
            })
        
        return {
            "algorithm": "LDA",
            "num_topics": model.num_topics,
            "topics": topics
        }
    else:
        model = SimpleNMF(num_topics=input_data["num_topics"])
        model.fit(texts)
        
        # For NMF, implement similar topic extraction
        topics = []
        for topic_id in range(model.num_topics):
            top_words = model.get_top_words(topic_id, num_words=10)
            topics.append({
                "topic_id": topic_id,  
                "words": [word for word, prob in top_words],
                "probabilities": [prob for word, prob in top_words]
            })
        
        return {
            "algorithm": "NMF",
            "num_topics": model.num_topics,
            "topics": topics
        }

# ============================================================================
# LEGACY COMPATIBILITY ENDPOINTS (Existing API endpoints)
# ============================================================================

@app.post("/sentiment-analysis", response_model=Dict)
async def sentiment_analysis_legacy(input_data: Dict):
    """Legacy sentiment analysis endpoint for backward compatibility"""
    return await perform_sentiment_analysis_internal(input_data)

# @app.post("/topic-modeling", response_model=Dict) 
# async def topic_modeling_legacy(input_data: Dict):
#     """Legacy topic modeling endpoint for backward compatibility - DISABLED for advanced implementation"""
#     return await perform_topic_modeling_simple(input_data)

@app.post("/text-summarization", response_model=Dict)
async def text_summarization_legacy(input_data: Dict):
    """Legacy text summarization endpoint"""
    summarizer = TextSummarizer()
    return summarizer.summarize(
        text=input_data["text"],
        max_sentences=input_data.get("max_sentences", 3),
        method=input_data.get("method", "frequency")
    )

# ============================================================================
# EXISTING PYDANTIC MODELS AND CLASSES (Legacy compatibility)
# ============================================================================

# Pydantic models
class TextInput(BaseModel):
    text: str = Field(..., description="Text to be preprocessed")
    options: Optional[Dict] = Field(default_factory=dict, description="Preprocessing options")

class BatchTextInput(BaseModel):
    texts: List[str] = Field(..., description="List of texts to be preprocessed")
    options: Optional[Dict] = Field(default_factory=dict, description="Preprocessing options")

class PreprocessingResult(BaseModel):
    original_text: str
    cleaned_text: str
    normalized_text: str
    tokens: List[str]
    processed_text: str
    stats: Dict
    processing_time: float

class BatchPreprocessingResult(BaseModel):
    results: List[PreprocessingResult]
    summary: Dict

class TopicModelingInput(BaseModel):
    texts: List[str] = Field(..., description="List of texts for topic modeling")
    num_topics: int = Field(default=5, description="Number of topics to extract")
    algorithm: str = Field(default="lda", description="Algorithm: 'lda' or 'nmf'")
    options: Optional[Dict] = Field(default_factory=dict, description="Additional options")

class Topic(BaseModel):
    id: int
    words: List[Tuple[str, float]]
    coherence_score: float
    document_proportion: float

class TopicModelingResult(BaseModel):
    topics: List[Dict]
    document_topic_distribution: List[Dict]
    algorithm_used: str
    num_topics: int
    coherence_score: float
    perplexity: Optional[float]
    top_words_per_topic: Dict[int, List[Tuple[str, float]]]
    processing_time: float
    model_performance: Dict
    total_processing_time: float

def preprocess_text(text: str, options: Dict = None) -> Dict:
    """
    Comprehensive text preprocessing without external dependencies
    """
    options = options or {}
    start_time = time.time()
    
    # Log the start of preprocessing
    text_preview = text[:100] + "..." if len(text) > 100 else text
    logger.info(f"🔄 Starting text preprocessing for text: '{text_preview}'")
    logger.info(f"📊 Original text length: {len(text)} characters")
    logger.info(f"⚙️  Options: {options}")
    
    if not text or not isinstance(text, str):
        logger.warning("❌ Empty or invalid text provided")
        return {
            'original_text': text or '',
            'cleaned_text': '',
            'normalized_text': '',
            'tokens': [],
            'processed_text': '',
            'stats': {
                'original_length': 0,
                'cleaned_length': 0,
                'normalized_length': 0,
                'token_count': 0,
                'vocabulary_size': 0,
                'avg_token_length': 0,
                'compression_ratio': 0,
                'processing_time': 0,
                'removed_urls': 0,
                'removed_emails': 0,
                'removed_mentions': 0,
                'removed_hashtags': 0,
                'removed_numbers': 0,
                'removed_stopwords': 0
            },
            'processing_time': 0
        }
    
    # Track removals
    stats = {
        'removed_urls': 0,
        'removed_emails': 0,
        'removed_mentions': 0,
        'removed_hashtags': 0,
        'removed_numbers': 0,
        'removed_stopwords': 0
    }
    
    # Step 1: Text cleaning
    logger.info("🧹 Step 1: Starting text cleaning and normalization...")
    cleaned = text.lower()
    
    # Remove URLs
    logger.info("🔗 Removing URLs...")
    url_patterns = [
        r'https?://[^\s]+',
        r'www\.[^\s]+',
        r'ftp://[^\s]+'
    ]
    for pattern in url_patterns:
        matches = re.findall(pattern, cleaned)
        stats['removed_urls'] += len(matches)
        cleaned = re.sub(pattern, '', cleaned)
    if stats['removed_urls'] > 0:
        logger.info(f"   Removed {stats['removed_urls']} URLs")
    
    # Remove emails
    logger.info("📧 Removing email addresses...")
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    matches = re.findall(email_pattern, cleaned)
    stats['removed_emails'] += len(matches)
    cleaned = re.sub(email_pattern, '', cleaned)
    if stats['removed_emails'] > 0:
        logger.info(f"   Removed {stats['removed_emails']} email addresses")
    
    # Remove social media mentions and hashtags
    logger.info("📱 Removing social media mentions and hashtags...")
    mention_pattern = r'@\w+'
    matches = re.findall(mention_pattern, cleaned)
    stats['removed_mentions'] += len(matches)
    cleaned = re.sub(mention_pattern, '', cleaned)
    
    hashtag_pattern = r'#\w+'
    matches = re.findall(hashtag_pattern, cleaned)
    stats['removed_hashtags'] += len(matches)
    cleaned = re.sub(hashtag_pattern, '', cleaned)
    if stats['removed_mentions'] > 0 or stats['removed_hashtags'] > 0:
        logger.info(f"   Removed {stats['removed_mentions']} mentions and {stats['removed_hashtags']} hashtags")
    
    # Remove numbers
    logger.info("🔢 Removing numbers...")
    number_pattern = r'\d+\.?\d*'
    matches = re.findall(number_pattern, cleaned)
    stats['removed_numbers'] += len(matches)
    cleaned = re.sub(number_pattern, '', cleaned)
    if stats['removed_numbers'] > 0:
        logger.info(f"   Removed {stats['removed_numbers']} numbers")
    
    # Remove HTML tags
    logger.info("🏷️  Removing HTML tags...")
    html_count = len(re.findall(r'<[^>]+>', cleaned))
    cleaned = re.sub(r'<[^>]+>', '', cleaned)
    if html_count > 0:
        logger.info(f"   Removed {html_count} HTML tags")
    
    # Remove punctuation
    logger.info("🔤 Removing punctuation...")
    punct_count = len(re.findall(r'[^\w\s]', cleaned))
    cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
    if punct_count > 0:
        logger.info(f"   Removed {punct_count} punctuation marks")
    
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    logger.info(f"📏 Cleaned text length: {len(cleaned)} characters")
    
    # Step 2: Text normalization (contraction expansion)
    logger.info("🔄 Step 2: Expanding contractions...")
    contractions = {
        "won't": "will not", "can't": "cannot", "n't": " not",
        "'re": " are", "'ve": " have", "'ll": " will",
        "'d": " would", "'m": " am", "it's": "it is",
        "that's": "that is", "there's": "there is",
        "here's": "here is", "what's": "what is",
        "where's": "where is", "how's": "how is",
        "let's": "let us"
    }
    
    normalized = cleaned
    contractions_expanded = 0
    for contraction, expansion in contractions.items():
        count_before = normalized.count(contraction)
        normalized = normalized.replace(contraction, expansion)
        contractions_expanded += count_before
    
    if contractions_expanded > 0:
        logger.info(f"   Expanded {contractions_expanded} contractions")
    
    # Normalize whitespace again
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    logger.info(f"📏 Normalized text length: {len(normalized)} characters")
    
    # Step 3: Tokenization
    logger.info("✂️  Step 3: Tokenizing text...")
    tokens = normalized.split()
    logger.info(f"🔤 Initial tokens: {len(tokens)}")
    
    # Filter by length
    logger.info("📏 Filtering tokens by length...")
    min_length = options.get('min_token_length', 2)
    max_length = options.get('max_token_length', 50)
    initial_token_count = len(tokens)
    tokens = [token for token in tokens if min_length <= len(token) <= max_length]
    filtered_count = initial_token_count - len(tokens)
    if filtered_count > 0:
        logger.info(f"   Filtered out {filtered_count} tokens by length (keeping {min_length}-{max_length} chars)")
    
    # Remove stop words if requested
    if options.get('remove_stopwords', True):
        logger.info("🛑 Removing stop words...")
        stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
            'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
            'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'in', 'out',
            'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there',
            'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 'can', 'will', 'just', 'should', 'now'
        }
        
        initial_count = len(tokens)
        tokens = [token for token in tokens if token.lower() not in stop_words]
        stats['removed_stopwords'] = initial_count - len(tokens)
        if stats['removed_stopwords'] > 0:
            logger.info(f"   Removed {stats['removed_stopwords']} stop words")
    
    # Enhanced Tokenization
    logger.info("🎯 Step 4: Enhanced tokenization...")
    
    # Advanced tokenization - split on multiple delimiters
    import string
    
    # Create better tokens by handling punctuation and special cases
    enhanced_tokens = []
    for token in tokens:
        # Handle contractions and compound words
        if "'" in token:
            parts = token.split("'")
            enhanced_tokens.extend([part for part in parts if part])
        elif "-" in token and len(token) > 3:
            parts = token.split("-")
            enhanced_tokens.extend([part for part in parts if part and len(part) > 1])
        else:
            enhanced_tokens.append(token)
    
    tokens = enhanced_tokens
    logger.info(f"   Enhanced tokenization: {len(tokens)} tokens")
    logger.info(f"   Sample tokens: {tokens[:10]}...")  # Show first 10 tokens
    
    # Apply lemmatization if requested
    if options.get('use_lemmatization', True):
        logger.info("🧠 Step 5: Applying lemmatization...")
        lemmatized_tokens = []
        lemmatized_count = 0
        lemmatization_examples = []  # Track examples for logging
        
        # Comprehensive lemmatization dictionary
        lemma_dict = {
            # Irregular verbs
            'was': 'be', 'were': 'be', 'been': 'be', 'being': 'be',
            'had': 'have', 'has': 'have', 'having': 'have',
            'did': 'do', 'does': 'do', 'doing': 'do', 'done': 'do',
            'went': 'go', 'gone': 'go', 'going': 'go',
            'came': 'come', 'coming': 'come',
            'said': 'say', 'saying': 'say',
            'got': 'get', 'getting': 'get',
            'made': 'make', 'making': 'make',
            'took': 'take', 'taken': 'take', 'taking': 'take',
            'saw': 'see', 'seen': 'see', 'seeing': 'see',
            'knew': 'know', 'known': 'know', 'knowing': 'know',
            'thought': 'think', 'thinking': 'think',
            'felt': 'feel', 'feeling': 'feel',
            'found': 'find', 'finding': 'find',
            'gave': 'give', 'given': 'give', 'giving': 'give',
            'left': 'leave', 'leaving': 'leave',
            'told': 'tell', 'telling': 'tell',
            'became': 'become', 'becoming': 'become',
            'brought': 'bring', 'bringing': 'bring',
            'bought': 'buy', 'buying': 'buy',
            'caught': 'catch', 'catching': 'catch',
            'chose': 'choose', 'chosen': 'choose', 'choosing': 'choose',
            'drew': 'draw', 'drawn': 'draw', 'drawing': 'draw',
            'drove': 'drive', 'driven': 'drive', 'driving': 'drive',
            'ate': 'eat', 'eaten': 'eat', 'eating': 'eat',
            'fell': 'fall', 'fallen': 'fall', 'falling': 'fall',
            'flew': 'fly', 'flown': 'fly', 'flying': 'fly',
            'forgot': 'forget', 'forgotten': 'forget', 'forgetting': 'forget',
            'grew': 'grow', 'grown': 'grow', 'growing': 'grow',
            'heard': 'hear', 'hearing': 'hear',
            'held': 'hold', 'holding': 'hold',
            'kept': 'keep', 'keeping': 'keep',
            'led': 'lead', 'leading': 'lead',
            'learned': 'learn', 'learnt': 'learn', 'learning': 'learn',
            'lost': 'lose', 'losing': 'lose',
            'meant': 'mean', 'meaning': 'mean',
            'met': 'meet', 'meeting': 'meet',
            'paid': 'pay', 'paying': 'pay',
            'ran': 'run', 'running': 'run',
            'sent': 'send', 'sending': 'send',
            'sold': 'sell', 'selling': 'sell',
            'showed': 'show', 'shown': 'show', 'showing': 'show',
            'spoke': 'speak', 'spoken': 'speak', 'speaking': 'speak',
            'spent': 'spend', 'spending': 'spend',
            'stood': 'stand', 'standing': 'stand',
            'taught': 'teach', 'teaching': 'teach',
            'threw': 'throw', 'thrown': 'throw', 'throwing': 'throw',
            'understood': 'understand', 'understanding': 'understand',
            'won': 'win', 'winning': 'win',
            'wrote': 'write', 'written': 'write', 'writing': 'write',
            
            # Irregular plurals
            'children': 'child', 'people': 'person', 'men': 'man', 'women': 'woman',
            'feet': 'foot', 'teeth': 'tooth', 'geese': 'goose', 'mice': 'mouse',
            'oxen': 'ox', 'sheep': 'sheep', 'deer': 'deer', 'fish': 'fish',
            
            # Common adjective forms
            'better': 'good', 'best': 'good', 'worse': 'bad', 'worst': 'bad',
            'further': 'far', 'furthest': 'far', 'farther': 'far', 'farthest': 'far',
            'more': 'much', 'most': 'much', 'less': 'little', 'least': 'little',
            'older': 'old', 'oldest': 'old', 'elder': 'old', 'eldest': 'old',
            'bigger': 'big', 'biggest': 'big', 'smaller': 'small', 'smallest': 'small',
            'larger': 'large', 'largest': 'large', 'longer': 'long', 'longest': 'long',
            'shorter': 'short', 'shortest': 'short', 'higher': 'high', 'highest': 'high',
            'lower': 'low', 'lowest': 'low', 'stronger': 'strong', 'strongest': 'strong',
            'weaker': 'weak', 'weakest': 'weak', 'faster': 'fast', 'fastest': 'fast',
            'slower': 'slow', 'slowest': 'slow', 'newer': 'new', 'newest': 'new',
        }
        
        for token in tokens:
            original_token = token
            lemmatized_token = token.lower()
            
            # Check dictionary first
            if lemmatized_token in lemma_dict:
                lemmatized_token = lemma_dict[lemmatized_token]
                lemmatized_count += 1
                if len(lemmatization_examples) < 5:  # Keep first 5 examples
                    lemmatization_examples.append(f"'{original_token}' → '{lemmatized_token}'")
            else:
                # Apply rule-based lemmatization
                original_lemmatized = lemmatized_token
                
                # Plural nouns
                if lemmatized_token.endswith('ies') and len(lemmatized_token) > 4:
                    lemmatized_token = lemmatized_token[:-3] + 'y'
                    lemmatized_count += 1
                elif lemmatized_token.endswith('ves') and len(lemmatized_token) > 4:
                    lemmatized_token = lemmatized_token[:-3] + 'f'
                    lemmatized_count += 1
                elif lemmatized_token.endswith('ses') and len(lemmatized_token) > 4:
                    lemmatized_token = lemmatized_token[:-2]
                    lemmatized_count += 1
                elif lemmatized_token.endswith('es') and len(lemmatized_token) > 3:
                    if lemmatized_token.endswith(('ches', 'shes', 'xes', 'zes')):
                        lemmatized_token = lemmatized_token[:-2]
                        lemmatized_count += 1
                    elif not lemmatized_token.endswith(('les', 'res', 'tes', 'nes', 'mes', 'pes')):
                        lemmatized_token = lemmatized_token[:-1]
                        lemmatized_count += 1
                elif lemmatized_token.endswith('s') and len(lemmatized_token) > 3:
                    if not lemmatized_token.endswith(('ss', 'us', 'is')):
                        lemmatized_token = lemmatized_token[:-1]
                        lemmatized_count += 1
                
                # Verb forms
                elif lemmatized_token.endswith('ed') and len(lemmatized_token) > 4:
                    if lemmatized_token.endswith('ied'):
                        lemmatized_token = lemmatized_token[:-3] + 'y'
                    else:
                        lemmatized_token = lemmatized_token[:-2]
                    lemmatized_count += 1
                elif lemmatized_token.endswith('ing') and len(lemmatized_token) > 5:
                    lemmatized_token = lemmatized_token[:-3]
                    lemmatized_count += 1
                
                # Adjective forms
                elif lemmatized_token.endswith('er') and len(lemmatized_token) > 4:
                    if lemmatized_token.endswith('ier'):
                        lemmatized_token = lemmatized_token[:-3] + 'y'
                    else:
                        lemmatized_token = lemmatized_token[:-2]
                    lemmatized_count += 1
                elif lemmatized_token.endswith('est') and len(lemmatized_token) > 5:
                    if lemmatized_token.endswith('iest'):
                        lemmatized_token = lemmatized_token[:-4] + 'y'
                    else:
                        lemmatized_token = lemmatized_token[:-3]
                    lemmatized_count += 1
                
                # Adverb forms
                elif lemmatized_token.endswith('ly') and len(lemmatized_token) > 4:
                    if lemmatized_token.endswith('ily'):
                        lemmatized_token = lemmatized_token[:-3] + 'y'
                    else:
                        lemmatized_token = lemmatized_token[:-2]
                    lemmatized_count += 1
                
                # Noun forms
                elif lemmatized_token.endswith('tion') and len(lemmatized_token) > 6:
                    lemmatized_token = lemmatized_token[:-4] + 'te'
                    lemmatized_count += 1
                elif lemmatized_token.endswith('sion') and len(lemmatized_token) > 6:
                    lemmatized_token = lemmatized_token[:-4] + 'de'
                    lemmatized_count += 1
                elif lemmatized_token.endswith('ness') and len(lemmatized_token) > 6:
                    lemmatized_token = lemmatized_token[:-4]
                    lemmatized_count += 1
                elif lemmatized_token.endswith('ment') and len(lemmatized_token) > 6:
                    lemmatized_token = lemmatized_token[:-4]
                    lemmatized_count += 1
                
                # If lemmatization occurred via rules, add to examples
                if original_lemmatized != lemmatized_token and len(lemmatization_examples) < 5:
                    lemmatization_examples.append(f"'{original_token}' → '{lemmatized_token}'")
            
            lemmatized_tokens.append(lemmatized_token)
        
        tokens = lemmatized_tokens
        logger.info(f"   Applied lemmatization to {lemmatized_count} tokens")
        if lemmatization_examples:
            logger.info(f"   Examples: {', '.join(lemmatization_examples)}")
        logger.info(f"   Final tokens (first 10): {tokens[:10]}")
        logger.info(f"   Final tokens (last 10): {tokens[-10:]}")
        
    elif options.get('use_stemming', False):
        logger.info("🌱 Applying stemming (fallback)...")
        stemmed_tokens = []
        stemmed_count = 0
        stemming_examples = []  # Track examples for logging
        
        for token in tokens:
            original_token = token
            stemmed_token = token
            
            # Simple stemming rules
            if token.endswith('ing') and len(token) > 5:
                stemmed_token = token[:-3]
                stemmed_count += 1
                if len(stemming_examples) < 5:
                    stemming_examples.append(f"'{original_token}' → '{stemmed_token}'")
            elif token.endswith('ed') and len(token) > 4:
                stemmed_token = token[:-2]
                stemmed_count += 1
                if len(stemming_examples) < 5:
                    stemming_examples.append(f"'{original_token}' → '{stemmed_token}'")
            elif token.endswith('er') and len(token) > 4:
                stemmed_token = token[:-2]
                stemmed_count += 1
                if len(stemming_examples) < 5:
                    stemming_examples.append(f"'{original_token}' → '{stemmed_token}'")
            elif token.endswith('est') and len(token) > 5:
                stemmed_token = token[:-3]
                stemmed_count += 1
                if len(stemming_examples) < 5:
                    stemming_examples.append(f"'{original_token}' → '{stemmed_token}'")
            elif token.endswith('ly') and len(token) > 4:
                stemmed_token = token[:-2]
                stemmed_count += 1
                if len(stemming_examples) < 5:
                    stemming_examples.append(f"'{original_token}' → '{stemmed_token}'")
            elif token.endswith('tion') and len(token) > 6:
                stemmed_token = token[:-4] + 'te'
                stemmed_count += 1
                if len(stemming_examples) < 5:
                    stemming_examples.append(f"'{original_token}' → '{stemmed_token}'")
            elif token.endswith('ness') and len(token) > 6:
                stemmed_token = token[:-4]
                stemmed_count += 1
                if len(stemming_examples) < 5:
                    stemming_examples.append(f"'{original_token}' → '{stemmed_token}'")
            
            stemmed_tokens.append(stemmed_token)
            
        tokens = stemmed_tokens
        if stemmed_count > 0:
            logger.info(f"   Applied stemming to {stemmed_count} tokens")
            if stemming_examples:
                logger.info(f"   Examples: {', '.join(stemming_examples)}")
            logger.info(f"   Final tokens (first 10): {tokens[:10]}")
            logger.info(f"   Final tokens (last 10): {tokens[-10:]}")
    
    # Final processing
    logger.info("🔧 Step 6: Finalizing processing...")
    processed_text = ' '.join(tokens)
    processing_time = time.time() - start_time
    
    # Calculate comprehensive statistics
    final_stats = {
        'original_length': len(text),
        'cleaned_length': len(cleaned),
        'normalized_length': len(normalized),
        'token_count': len(tokens),
        'vocabulary_size': len(set(tokens)),
        'avg_token_length': sum(len(token) for token in tokens) / len(tokens) if tokens else 0,
        'compression_ratio': len(processed_text) / len(text) if text else 0,
        'processing_time': processing_time,
        **stats
    }
    
    # Log completion with summary
    logger.info("✅ Text preprocessing completed!")
    logger.info(f"📊 Final Statistics:")
    logger.info(f"   • Original length: {final_stats['original_length']} chars")
    logger.info(f"   • Final length: {len(processed_text)} chars")
    logger.info(f"   • Token count: {final_stats['token_count']}")
    logger.info(f"   • Vocabulary size: {final_stats['vocabulary_size']}")
    logger.info(f"   • Compression ratio: {final_stats['compression_ratio']:.2%}")
    logger.info(f"   • Processing time: {final_stats['processing_time']:.3f}s")
    logger.info("─" * 50)
    
    return {
        'original_text': text,
        'cleaned_text': cleaned,
        'normalized_text': normalized,
        'tokens': tokens,
        'processed_text': processed_text,
        'stats': final_stats,
        'processing_time': processing_time
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Narrative Nexus Backend API",
        "version": "1.0.0",
        "status": "running",
        "features": {
            "text_preprocessing": True,
            "batch_processing": True,
            "file_upload": True,
            "comprehensive_stats": True
        },
        "endpoints": {
            "preprocess": "/preprocess/text",
            "batch_preprocess": "/preprocess/batch",
            "file_upload": "/preprocess/file",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "preprocessor_status": "ready",
        "features": {
            "basic_preprocessing": True,
            "advanced_cleaning": True,
            "batch_processing": True,
            "file_support": True
        }
    }

@app.post("/preprocess/text", response_model=PreprocessingResult)
async def preprocess_single_text(input_data: TextInput):
    """
    Preprocess a single text input
    """
    logger.info("🚀 Received preprocessing request")
    logger.info(f"📝 Request options: {input_data.options}")
    
    try:
        result = preprocess_text_comprehensive(input_data.text, input_data.options)
        
        logger.info("✅ Preprocessing request completed successfully")
        return PreprocessingResult(
            original_text=result['original_text'],
            cleaned_text=result['cleaned_text'],
            normalized_text=result['normalized_text'],
            tokens=result['tokens'],
            processed_text=result['processed_text'],
            stats=result['stats'],
            processing_time=result['processing_time']
        )
        
    except Exception as e:
        logger.error(f"Error preprocessing text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Preprocessing failed: {str(e)}")

@app.post("/preprocess/batch", response_model=BatchPreprocessingResult)
async def preprocess_batch_texts(input_data: BatchTextInput):
    """
    Preprocess multiple texts in batch
    """
    try:
        start_time = time.time()
        results = []
        all_tokens = []
        
        for text in input_data.texts:
            result_data = preprocess_text(text, input_data.options)
            
            results.append(PreprocessingResult(
                original_text=result_data['original_text'],
                cleaned_text=result_data['cleaned_text'],
                normalized_text=result_data['normalized_text'],
                tokens=result_data['tokens'],
                processed_text=result_data['processed_text'],
                stats=result_data['stats'],
                processing_time=result_data['processing_time']
            ))
            
            all_tokens.extend(result_data['tokens'])
        
        total_processing_time = time.time() - start_time
        
        # Calculate summary statistics
        summary = {
            "batch_info": {
                "total_texts": len(input_data.texts),
                "total_processing_time": total_processing_time,
                "avg_processing_time_per_text": total_processing_time / len(input_data.texts) if input_data.texts else 0
            },
            "text_statistics": {
                "total_tokens": len(all_tokens),
                "unique_tokens": len(set(all_tokens)),
                "vocabulary_diversity": len(set(all_tokens)) / len(all_tokens) if all_tokens else 0,
                "avg_tokens_per_text": len(all_tokens) / len(input_data.texts) if input_data.texts else 0,
                "avg_token_length": sum(len(token) for token in all_tokens) / len(all_tokens) if all_tokens else 0
            },
            "removal_statistics": {
                "total_urls_removed": sum(r.stats.get('removed_urls', 0) for r in results),
                "total_emails_removed": sum(r.stats.get('removed_emails', 0) for r in results),
                "total_mentions_removed": sum(r.stats.get('removed_mentions', 0) for r in results),
                "total_hashtags_removed": sum(r.stats.get('removed_hashtags', 0) for r in results),
                "total_numbers_removed": sum(r.stats.get('removed_numbers', 0) for r in results),
                "total_stopwords_removed": sum(r.stats.get('removed_stopwords', 0) for r in results)
            }
        }
        
        return BatchPreprocessingResult(
            results=results,
            summary=summary,
            total_processing_time=total_processing_time
        )
        
    except Exception as e:
        logger.error(f"Error preprocessing batch texts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch preprocessing failed: {str(e)}")

@app.post("/preprocess/file")
async def preprocess_file(file: UploadFile = File(...)):
    """
    Upload and preprocess a text file
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension not in ['txt', 'csv', 'json']:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Please upload .txt, .csv, or .json files"
            )
        
        content = await file.read()
        
        if file_extension == 'txt':
            text = content.decode('utf-8')
            input_data = TextInput(text=text)
            return await preprocess_single_text(input_data)
            
        elif file_extension == 'csv':
            lines = content.decode('utf-8').strip().split('\n')
            if len(lines) < 2:
                raise HTTPException(status_code=400, detail="CSV file must have at least a header and one data row")
            
            header = lines[0].split(',')
            text_col_idx = 0
            for i, col in enumerate(header):
                col_clean = col.strip().strip('"').lower()
                if col_clean in ['text', 'content', 'review', 'comment', 'description', 'message']:
                    text_col_idx = i
                    break
            
            texts = []
            for line in lines[1:]:
                parts = line.split(',')
                if len(parts) > text_col_idx:
                    text = parts[text_col_idx].strip().strip('"')
                    if text:
                        texts.append(text)
            
            if not texts:
                raise HTTPException(status_code=400, detail="No text content found in CSV")
            
            input_data = BatchTextInput(texts=texts)
            return await preprocess_batch_texts(input_data)
            
        elif file_extension == 'json':
            data = json.loads(content.decode('utf-8'))
            
            if isinstance(data, list):
                if all(isinstance(item, str) for item in data):
                    texts = data
                else:
                    text_keys = ['text', 'content', 'review', 'comment', 'description', 'message']
                    texts = []
                    for item in data:
                        if isinstance(item, dict):
                            for key in text_keys:
                                if key in item:
                                    texts.append(str(item[key]))
                                    break
                
                if not texts:
                    raise HTTPException(status_code=400, detail="No text content found in JSON")
                
                input_data = BatchTextInput(texts=texts)
                return await preprocess_batch_texts(input_data)
            
            elif isinstance(data, dict):
                if 'text' in data:
                    input_data = TextInput(text=str(data['text']))
                    return await preprocess_single_text(input_data)
                else:
                    for value in data.values():
                        if isinstance(value, str):
                            input_data = TextInput(text=value)
                            return await preprocess_single_text(input_data)
                    raise HTTPException(status_code=400, detail="No text content found in JSON")
            else:
                input_data = TextInput(text=str(data))
                return await preprocess_single_text(input_data)
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

# ================================================================================================
# TOPIC MODELING IMPLEMENTATION
# ================================================================================================

class SimpleLDA:
    """
    Simplified Latent Dirichlet Allocation implementation
    """
    def __init__(self, num_topics=5, alpha=0.1, beta=0.01, num_iterations=100):
        self.num_topics = num_topics
        self.alpha = alpha  # Document-topic concentration
        self.beta = beta    # Topic-word concentration
        self.num_iterations = num_iterations
        
        # Model parameters
        self.vocabulary = None
        self.word_to_id = None
        self.id_to_word = None
        self.doc_topic_counts = None
        self.topic_word_counts = None
        self.topic_counts = None
        self.doc_lengths = None
        
    def build_vocabulary(self, documents):
        """Build vocabulary from documents"""
        word_freq = Counter()
        for doc in documents:
            words = doc.lower().split()
            word_freq.update(words)
        
        # For short texts, include all words that appear at least once
        # For longer texts, filter words that appear at least 2 times
        total_words = sum(word_freq.values())
        min_freq = 1 if total_words < 100 else 2
        
        self.vocabulary = [word for word, freq in word_freq.items() if freq >= min_freq and len(word) > 2]
        self.word_to_id = {word: i for i, word in enumerate(self.vocabulary)}
        self.id_to_word = {i: word for i, word in enumerate(self.vocabulary)}
        
    def preprocess_documents(self, documents):
        """Convert documents to word ID sequences"""
        processed_docs = []
        for doc in documents:
            words = doc.lower().split()
            word_ids = [self.word_to_id[word] for word in words if word in self.word_to_id]
            processed_docs.append(word_ids)
        return processed_docs
    
    def initialize_assignments(self, documents):
        """Initialize topic assignments randomly"""
        num_docs = len(documents)
        vocab_size = len(self.vocabulary)
        
        # Initialize count matrices
        self.doc_topic_counts = [[0] * self.num_topics for _ in range(num_docs)]
        self.topic_word_counts = [[0] * vocab_size for _ in range(self.num_topics)]
        self.topic_counts = [0] * self.num_topics
        self.doc_lengths = [len(doc) for doc in documents]
        
        # Random topic assignments
        self.topic_assignments = []
        for doc_id, doc in enumerate(documents):
            doc_assignments = []
            for word_id in doc:
                topic = random.randint(0, self.num_topics - 1)
                doc_assignments.append(topic)
                
                # Update counts
                self.doc_topic_counts[doc_id][topic] += 1
                self.topic_word_counts[topic][word_id] += 1
                self.topic_counts[topic] += 1
            
            self.topic_assignments.append(doc_assignments)
    
    def sample_topic(self, doc_id, word_id, old_topic):
        """Sample new topic for word using Gibbs sampling"""
        # Remove current assignment
        self.doc_topic_counts[doc_id][old_topic] -= 1
        self.topic_word_counts[old_topic][word_id] -= 1
        self.topic_counts[old_topic] -= 1
        
        # Calculate probabilities for each topic
        probabilities = []
        for topic in range(self.num_topics):
            # P(topic|doc) * P(word|topic)
            doc_topic_prob = (self.doc_topic_counts[doc_id][topic] + self.alpha) / \
                           (self.doc_lengths[doc_id] - 1 + self.num_topics * self.alpha)
            
            topic_word_prob = (self.topic_word_counts[topic][word_id] + self.beta) / \
                            (self.topic_counts[topic] + len(self.vocabulary) * self.beta)
            
            probabilities.append(doc_topic_prob * topic_word_prob)
        
        # Sample new topic
        total_prob = sum(probabilities)
        if total_prob == 0:
            new_topic = random.randint(0, self.num_topics - 1)
        else:
            probabilities = [p / total_prob for p in probabilities]
            rand_val = random.random()
            cumsum = 0
            new_topic = 0
            for i, prob in enumerate(probabilities):
                cumsum += prob
                if rand_val < cumsum:
                    new_topic = i
                    break
        
        # Update counts with new assignment
        self.doc_topic_counts[doc_id][new_topic] += 1
        self.topic_word_counts[new_topic][word_id] += 1
        self.topic_counts[new_topic] += 1
        
        return new_topic
    
    def fit(self, documents):
        """Train the LDA model"""
        logger.info(f"🧠 Training LDA model with {self.num_topics} topics...")
        
        # Build vocabulary
        self.build_vocabulary(documents)
        logger.info(f"📚 Vocabulary size: {len(self.vocabulary)}")
        
        # Preprocess documents
        processed_docs = self.preprocess_documents(documents)
        
        # Initialize random assignments
        self.initialize_assignments(processed_docs)
        
        # Gibbs sampling
        for iteration in range(self.num_iterations):
            for doc_id, doc in enumerate(processed_docs):
                for word_pos, word_id in enumerate(doc):
                    old_topic = self.topic_assignments[doc_id][word_pos]
                    new_topic = self.sample_topic(doc_id, word_id, old_topic)
                    self.topic_assignments[doc_id][word_pos] = new_topic
            
            if (iteration + 1) % 20 == 0:
                logger.info(f"🔄 LDA Iteration {iteration + 1}/{self.num_iterations}")
    
    def get_top_words(self, topic_id, num_words=10):
        """Get top words for a topic"""
        if topic_id >= self.num_topics:
            return []
        
        word_probs = []
        for word_id, word in self.id_to_word.items():
            prob = (self.topic_word_counts[topic_id][word_id] + self.beta) / \
                   (self.topic_counts[topic_id] + len(self.vocabulary) * self.beta)
            word_probs.append((word, prob))
        
        # Sort by probability and return top words
        word_probs.sort(key=lambda x: x[1], reverse=True)
        return word_probs[:num_words]
    
    def get_document_topics(self, doc_id):
        """Get topic distribution for a document"""
        if doc_id >= len(self.doc_topic_counts):
            return []
        
        topic_probs = []
        for topic in range(self.num_topics):
            prob = (self.doc_topic_counts[doc_id][topic] + self.alpha) / \
                   (self.doc_lengths[doc_id] + self.num_topics * self.alpha)
            topic_probs.append(prob)
        
        return topic_probs

class SimpleNMF:
    """
    Simplified Non-negative Matrix Factorization for topic modeling
    """
    def __init__(self, num_topics=5, num_iterations=100, learning_rate=0.01):
        self.num_topics = num_topics
        self.num_iterations = num_iterations
        self.learning_rate = learning_rate
        
        self.vocabulary = None
        self.word_to_id = None
        self.id_to_word = None
        self.W = None  # Document-topic matrix
        self.H = None  # Topic-word matrix
        self.document_term_matrix = None
    
    def build_vocabulary(self, documents):
        """Build vocabulary from documents"""
        word_freq = Counter()
        for doc in documents:
            words = doc.lower().split()
            word_freq.update(words)
        
        # Filter words that appear at least 2 times
        self.vocabulary = [word for word, freq in word_freq.items() if freq >= 2]
        self.word_to_id = {word: i for i, word in enumerate(self.vocabulary)}
        self.id_to_word = {i: word for i, word in enumerate(self.vocabulary)}
    
    def build_document_term_matrix(self, documents):
        """Build document-term matrix"""
        num_docs = len(documents)
        vocab_size = len(self.vocabulary)
        
        self.document_term_matrix = [[0.0] * vocab_size for _ in range(num_docs)]
        
        for doc_id, doc in enumerate(documents):
            words = doc.lower().split()
            word_counts = Counter(words)
            
            for word, count in word_counts.items():
                if word in self.word_to_id:
                    word_id = self.word_to_id[word]
                    # Use TF-IDF weighting
                    tf = count / len(words)
                    # Simple IDF approximation
                    doc_freq = sum(1 for d in documents if word in d.lower())
                    idf = math.log(num_docs / (doc_freq + 1))
                    self.document_term_matrix[doc_id][word_id] = tf * idf
    
    def initialize_matrices(self, num_docs, vocab_size):
        """Initialize W and H matrices randomly"""
        # Initialize W (document-topic matrix)
        self.W = [[random.random() for _ in range(self.num_topics)] for _ in range(num_docs)]
        
        # Initialize H (topic-word matrix)
        self.H = [[random.random() for _ in range(vocab_size)] for _ in range(self.num_topics)]
    
    def matrix_multiply(self, A, B):
        """Multiply two matrices"""
        rows_A, cols_A = len(A), len(A[0])
        rows_B, cols_B = len(B), len(B[0])
        
        if cols_A != rows_B:
            raise ValueError("Matrix dimensions don't match for multiplication")
        
        result = [[0.0] * cols_B for _ in range(rows_A)]
        
        for i in range(rows_A):
            for j in range(cols_B):
                for k in range(cols_A):
                    result[i][j] += A[i][k] * B[k][j]
        
        return result
    
    def update_matrices(self):
        """Update W and H matrices using multiplicative update rules"""
        num_docs = len(self.W)
        vocab_size = len(self.H[0])
        
        # Calculate WH
        WH = self.matrix_multiply(self.W, self.H)
        
        # Update H matrix
        new_H = [[0.0] * vocab_size for _ in range(self.num_topics)]
        for i in range(self.num_topics):
            for j in range(vocab_size):
                numerator = 0.0
                denominator = 0.0
                
                for d in range(num_docs):
                    if WH[d][j] > 0:
                        numerator += self.W[d][i] * self.document_term_matrix[d][j]
                        denominator += self.W[d][i] * WH[d][j]
                
                if denominator > 0:
                    new_H[i][j] = self.H[i][j] * (numerator / denominator)
                else:
                    new_H[i][j] = self.H[i][j]
        
        self.H = new_H
        
        # Calculate new WH
        WH = self.matrix_multiply(self.W, self.H)
        
        # Update W matrix
        new_W = [[0.0] * self.num_topics for _ in range(num_docs)]
        for i in range(num_docs):
            for j in range(self.num_topics):
                numerator = 0.0
                denominator = 0.0
                
                for v in range(vocab_size):
                    if WH[i][v] > 0:
                        numerator += self.H[j][v] * self.document_term_matrix[i][v]
                        denominator += self.H[j][v] * WH[i][v]
                
                if denominator > 0:
                    new_W[i][j] = self.W[i][j] * (numerator / denominator)
                else:
                    new_W[i][j] = self.W[i][j]
        
        self.W = new_W
    
    def fit(self, documents):
        """Train the NMF model"""
        logger.info(f"🧠 Training NMF model with {self.num_topics} topics...")
        
        # Build vocabulary
        self.build_vocabulary(documents)
        logger.info(f"📚 Vocabulary size: {len(self.vocabulary)}")
        
        # Build document-term matrix
        self.build_document_term_matrix(documents)
        
        # Initialize matrices
        num_docs = len(documents)
        vocab_size = len(self.vocabulary)
        self.initialize_matrices(num_docs, vocab_size)
        
        # Iterative updates
        for iteration in range(self.num_iterations):
            self.update_matrices()
            
            if (iteration + 1) % 20 == 0:
                logger.info(f"🔄 NMF Iteration {iteration + 1}/{self.num_iterations}")
    
    def get_top_words(self, topic_id, num_words=10):
        """Get top words for a topic"""
        if topic_id >= self.num_topics:
            return []
        
        word_weights = []
        for word_id, word in self.id_to_word.items():
            weight = self.H[topic_id][word_id]
            word_weights.append((word, weight))
        
        # Sort by weight and return top words
        word_weights.sort(key=lambda x: x[1], reverse=True)
        return word_weights[:num_words]
    
    def get_document_topics(self, doc_id):
        """Get topic distribution for a document"""
        if doc_id >= len(self.W):
            return []
        
        # Normalize to get probabilities
        total = sum(self.W[doc_id])
        if total == 0:
            return [1.0 / self.num_topics] * self.num_topics
        
        return [weight / total for weight in self.W[doc_id]]

def calculate_coherence_score(topics, documents):
    """Calculate coherence score for topics"""
    total_coherence = 0
    num_topics = len(topics)
    
    for topic in topics:
        top_words = [word for word, _ in topic[:10]]  # Top 10 words
        coherence = 0
        pairs = 0
        
        for i in range(len(top_words)):
            for j in range(i + 1, len(top_words)):
                word1, word2 = top_words[i], top_words[j]
                
                # Count co-occurrences
                cooccur = 0
                word1_count = 0
                
                for doc in documents:
                    doc_lower = doc.lower()
                    has_word1 = word1 in doc_lower
                    has_word2 = word2 in doc_lower
                    
                    if has_word1:
                        word1_count += 1
                    if has_word1 and has_word2:
                        cooccur += 1
                
                if word1_count > 0:
                    coherence += math.log((cooccur + 1) / word1_count)
                    pairs += 1
        
        if pairs > 0:
            total_coherence += coherence / pairs
    
    return total_coherence / num_topics if num_topics > 0 else 0

async def perform_topic_modeling(input_data: TopicModelingInput) -> TopicModelingResult:
    """
    Perform topic modeling on the input texts
    """
    start_time = time.time()
    
    try:
        logger.info(f"🚀 Starting topic modeling with {input_data.algorithm.upper()} algorithm")
        logger.info(f"📊 Processing {len(input_data.texts)} documents")
        logger.info(f"🎯 Extracting {input_data.num_topics} topics")
        
        # Filter out empty texts
        valid_texts = [text.strip() for text in input_data.texts if text.strip()]
        
        if len(valid_texts) < 2:
            raise HTTPException(
                status_code=400, 
                detail="At least 2 non-empty documents are required for topic modeling"
            )
        
        # Initialize model based on algorithm
        if input_data.algorithm.lower() == "lda":
            model = SimpleLDA(
                num_topics=input_data.num_topics,
                num_iterations=input_data.options.get("num_iterations", 100)
            )
        elif input_data.algorithm.lower() == "nmf":
            model = SimpleNMF(
                num_topics=input_data.num_topics,
                num_iterations=input_data.options.get("num_iterations", 100)
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Algorithm must be either 'lda' or 'nmf'"
            )
        
        # Train the model
        model.fit(valid_texts)
        
        # Extract topics
        topics = []
        top_words_per_topic = {}
        
        for topic_id in range(input_data.num_topics):
            top_words = model.get_top_words(topic_id, 10)
            
            topic_data = {
                "id": topic_id,
                "label": f"Topic {topic_id + 1}",
                "top_words": top_words,
                "keywords": [word for word, _ in top_words[:5]]
            }
            topics.append(topic_data)
            top_words_per_topic[topic_id] = top_words
        
        # Get document-topic distributions
        document_topic_distribution = []
        for doc_id in range(len(valid_texts)):
            doc_topics = model.get_document_topics(doc_id)
            
            # Find dominant topic
            dominant_topic = max(range(len(doc_topics)), key=lambda i: doc_topics[i])
            
            doc_dist = {
                "document_id": doc_id,
                "document_preview": valid_texts[doc_id][:100] + "..." if len(valid_texts[doc_id]) > 100 else valid_texts[doc_id],
                "topic_probabilities": doc_topics,
                "dominant_topic": dominant_topic,
                "dominant_topic_probability": doc_topics[dominant_topic]
            }
            document_topic_distribution.append(doc_dist)
        
        # Calculate coherence score
        topic_words = [[(word, prob) for word, prob in model.get_top_words(i, 10)] 
                      for i in range(input_data.num_topics)]
        coherence_score = calculate_coherence_score(topic_words, valid_texts)
        
        # Calculate performance metrics
        processing_time = time.time() - start_time
        
        model_performance = {
            "training_time": processing_time,
            "vocabulary_size": len(model.vocabulary),
            "documents_processed": len(valid_texts),
            "topics_extracted": input_data.num_topics,
            "algorithm_used": input_data.algorithm.upper()
        }
        
        # Perplexity calculation (simplified for LDA)
        perplexity = None
        if input_data.algorithm.lower() == "lda":
            # Simplified perplexity calculation
            perplexity = math.exp(-coherence_score) if coherence_score < 0 else None
        
        logger.info(f"✅ Topic modeling completed successfully!")
        logger.info(f"📊 Coherence score: {coherence_score:.4f}")
        logger.info(f"⏱️  Processing time: {processing_time:.2f}s")
        
        return TopicModelingResult(
            topics=topics,
            document_topic_distribution=document_topic_distribution,
            algorithm_used=input_data.algorithm.upper(),
            num_topics=input_data.num_topics,
            coherence_score=coherence_score,
            perplexity=perplexity,
            top_words_per_topic=top_words_per_topic,
            processing_time=processing_time,
            model_performance=model_performance,
            total_processing_time=processing_time  # Add the missing field
        )
        
    except Exception as e:
        logger.error(f"❌ Topic modeling failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Topic modeling failed: {str(e)}")

# Topic Modeling API Endpoints

@app.post("/topic-modeling", response_model=TopicModelingResult)
async def topic_modeling_endpoint(input_data: TopicModelingInput):
    """
    🧠 Advanced Topic Modeling following specified requirements:
    
    ● Algorithm Selection: Choose appropriate algorithms for topic modeling (LDA, NMF)
    ● Latent Dirichlet Allocation (LDA): For identifying latent topics in text data
    ● Non-negative Matrix Factorization (NMF): As alternative for topic extraction  
    ● Model Training: Train selected models on preprocessed text data to identify key themes and topics
    
    This endpoint supports both LDA and NMF algorithms with comprehensive model training.
    """
    try:
        logger.info("🎯 Advanced Topic Modeling API called")
        
        # Convert to advanced topic modeling format
        preprocessing_options = {
            'remove_stopwords': input_data.options.get('remove_stopwords', True) if input_data.options else True,
            'use_lemmatization': input_data.options.get('use_lemmatization', True) if input_data.options else True,
            'min_token_length': input_data.options.get('min_token_length', 3) if input_data.options else 3,
            'max_token_length': input_data.options.get('max_token_length', 50) if input_data.options else 50
        }
        
        training_options = {
            'num_iterations': input_data.options.get('num_iterations', 100) if input_data.options else 100,
            'alpha': input_data.options.get('alpha', 0.1) if input_data.options else 0.1,
            'beta': input_data.options.get('beta', 0.01) if input_data.options else 0.01,
            'learning_rate': input_data.options.get('learning_rate', 0.01) if input_data.options else 0.01
        }
        
        # 🔧 FIX: Handle single large document by splitting into multiple documents
        texts_to_analyze = input_data.texts
        if len(texts_to_analyze) == 1 and len(texts_to_analyze[0]) > 500:  # Lowered threshold
            logger.info("📄 Single large document detected, splitting into multiple documents...")
            large_text = texts_to_analyze[0]
            
            # Split by sentences and create chunks
            sentences = re.split(r'[.!?]+', large_text)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 50]
            
            # Group sentences into chunks
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) > 1500 and current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
                else:
                    current_chunk += sentence + ". "
            
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            if len(chunks) >= 2:
                texts_to_analyze = chunks
                logger.info(f"✅ Split into {len(texts_to_analyze)} documents")
            else:
                # Fallback: split by words
                words = large_text.split()
                chunk_size = max(len(words) // 3, 100)  # At least 100 words per chunk
                chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
                texts_to_analyze = chunks[:3] if len(chunks) > 3 else chunks
                logger.info(f"✅ Split by words into {len(texts_to_analyze)} documents")

        # Perform advanced topic modeling with algorithm selection and model training
        results = perform_advanced_topic_modeling(
            texts=texts_to_analyze,
            algorithm=input_data.algorithm,
            num_topics=input_data.num_topics,
            preprocessing_options=preprocessing_options,
            training_options=training_options
        )
        
        # Convert to expected TopicModelingResult format
        return TopicModelingResult(
            topics=results['topics'],
            document_topic_distribution=results['document_topic_distributions'],
            algorithm_used=results['algorithm'],
            num_topics=results['num_topics'],
            coherence_score=results['model_performance']['coherence_score'],
            perplexity=None,  # Will be calculated if needed
            top_words_per_topic={str(i): [(word, prob) for word, prob in topic['top_words']] 
                               for i, topic in enumerate(results['topics'])},
            processing_time=results['model_performance']['training_time'],
            model_performance=results['model_performance'],
            total_processing_time=results['pipeline_summary']['total_processing_time']
        )
        
    except Exception as e:
        logger.error(f"❌ Advanced topic modeling failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Topic modeling failed: {str(e)}")

@app.post("/topic-modeling/batch")
async def batch_topic_modeling(texts: List[str], num_topics: int = 5, algorithm: str = "lda"):
    """
    📊 Simplified batch topic modeling with advanced algorithm selection and model training
    
    ● Algorithm Selection: Choose LDA or NMF for topic modeling
    ● Model Training: Train selected models to identify key themes and topics
    """
    try:
        logger.info(f"🎯 Batch Topic Modeling: {algorithm.upper()} with {num_topics} topics")
        
        # Use advanced topic modeling engine
        results = perform_advanced_topic_modeling(
            texts=texts,
            algorithm=algorithm,
            num_topics=num_topics,
            preprocessing_options=None,  # Use defaults
            training_options=None       # Use defaults
        )
        
        return {
            "algorithm_selection": {
                "selected_algorithm": results['algorithm'],
                "algorithm_full_name": results['algorithm_full_name'],
                "purpose": results['purpose']
            },
            "model_training_results": {
                "num_topics": results['num_topics'],
                "topics": results['topics'],
                "training_time": results['model_performance']['training_time'],
                "coherence_score": results['model_performance']['coherence_score'],
                "vocabulary_size": results['model_performance']['vocabulary_size']
            },
            "pipeline_summary": results['pipeline_summary']
        }
        
    except Exception as e:
        logger.error(f"❌ Batch topic modeling failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch topic modeling failed: {str(e)}")
    return await perform_topic_modeling(input_data)

# ======================================================================
# SENTIMENT ANALYSIS IMPLEMENTATION
# ======================================================================

class SentimentAnalysisInput(BaseModel):
    text: str = Field(..., description="Text for sentiment analysis")
    options: Optional[Dict] = Field(default_factory=dict, description="Analysis options")

class SentimentResult(BaseModel):
    sentence: str
    sentiment: str
    confidence: float
    positive_score: float
    negative_score: float
    neutral_score: float

class SentimentAnalysisResult(BaseModel):
    overall_sentiment: str
    overall_confidence: float
    sentiment_distribution: Dict[str, float]
    emotional_indicators: Dict[str, float]
    results: List[SentimentResult]
    summary: Dict[str, Union[int, float]]

class AdvancedSentimentAnalyzer:
    """
    🎭 Advanced Sentiment Analysis Engine following specified requirements:
    
    ● Sentiment Detection: Implement sentiment analysis algorithms to assess 
      the emotional tone of the identified topics, categorizing sentiments 
      as positive, negative, or neutral.
    ● Integration: Combine sentiment analysis results with topic modeling 
      to provide a comprehensive view of the data.
    """
    
    def __init__(self):
        # Enhanced positive sentiment lexicon
        self.positive_words = {
            # Basic positive words
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 'perfect',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'delighted', 'thrilled',
            'brilliant', 'outstanding', 'superb', 'marvelous', 'impressive', 'beautiful', 'nice',
            'best', 'better', 'positive', 'optimistic', 'excited', 'joyful', 'cheerful', 'pleasant',
            'recommend', 'success', 'successful', 'win', 'winner', 'achieve', 'accomplished',
            'helpful', 'useful', 'valuable', 'effective', 'efficient', 'quality', 'superior',
            
            # Topic-specific positive words
            'innovative', 'breakthrough', 'revolutionary', 'advanced', 'cutting-edge', 'modern',
            'powerful', 'robust', 'reliable', 'trustworthy', 'beneficial', 'advantage', 'improved',
            'enhancement', 'optimization', 'solution', 'opportunity', 'progress', 'growth', 'increase',
            'boost', 'strengthen', 'empower', 'enable', 'facilitate', 'streamline', 'simplify'
        }
        
        # Enhanced negative sentiment lexicon
        self.negative_words = {
            # Basic negative words  
            'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate', 'dislike', 'disappointed',
            'angry', 'frustrated', 'annoyed', 'upset', 'sad', 'depressed', 'worried', 'concerned',
            'problem', 'issue', 'error', 'bug', 'fail', 'failure', 'wrong', 'broken', 'useless',
            'waste', 'poor', 'worst', 'worse', 'negative', 'pessimistic', 'difficult', 'hard',
            'impossible', 'never', 'nothing', 'nobody', 'none', 'reject', 'refuse', 'deny',
            'complain', 'complaint', 'regret', 'sorry', 'apologize', 'mistake', 'unfortunate',
            
            # Topic-specific negative words
            'outdated', 'obsolete', 'flawed', 'defective', 'inadequate', 'insufficient', 'lacking',
            'limitation', 'constraint', 'barrier', 'obstacle', 'hindrance', 'threat', 'risk',
            'decline', 'decrease', 'reduction', 'loss', 'damage', 'harm', 'compromise', 'weakness'
        }
        
        # Sentiment intensifiers
        self.intensifiers = {
            'very': 1.5, 'extremely': 2.0, 'really': 1.3, 'absolutely': 1.8, 'completely': 1.7,
            'totally': 1.6, 'quite': 1.2, 'highly': 1.4, 'deeply': 1.5, 'truly': 1.4,
            'incredibly': 1.8, 'amazingly': 1.7, 'exceptionally': 1.9, 'remarkably': 1.6
        }
        
        # Negation words
        self.negation_words = {
            'not', 'no', 'never', 'neither', 'nor', 'none', 'nobody', 'nothing',
            'nowhere', 'hardly', 'scarcely', 'barely', 'cannot', "can't", "won't",
            "shouldn't", "wouldn't", "couldn't", "mustn't", "don't", "doesn't", "didn't"
        }

    def assess_emotional_tone(self, text: str) -> Dict:
        """
        🎯 Sentiment Detection: Assess emotional tone categorizing as positive, negative, or neutral
        """
        tokens = self._tokenize(text)
        
        positive_score = 0.0
        negative_score = 0.0
        sentiment_words = []
        
        # Context tracking
        negation_active = False
        intensifier_multiplier = 1.0
        
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            
            # Check for negation
            if token_lower in self.negation_words:
                negation_active = True
                continue
            
            # Check for intensifiers
            if token_lower in self.intensifiers:
                intensifier_multiplier = self.intensifiers[token_lower]
                continue
            
            # Calculate sentiment scores
            word_positive = 0.0
            word_negative = 0.0
            
            if token_lower in self.positive_words:
                word_positive = 1.0 * intensifier_multiplier
                sentiment_words.append({'word': token, 'sentiment': 'positive', 'score': word_positive})
                
            elif token_lower in self.negative_words:
                word_negative = 1.0 * intensifier_multiplier  
                sentiment_words.append({'word': token, 'sentiment': 'negative', 'score': word_negative})
            
            # Apply negation
            if negation_active:
                word_positive, word_negative = word_negative, word_positive
                if sentiment_words:
                    sentiment_words[-1]['negated'] = True
                negation_active = False
            
            positive_score += word_positive
            negative_score += word_negative
            intensifier_multiplier = 1.0
        
        # Normalize scores
        total_tokens = len(tokens)
        if total_tokens > 0:
            positive_score = positive_score / total_tokens
            negative_score = negative_score / total_tokens
        
        # Calculate neutral score
        neutral_score = max(0.0, 1.0 - positive_score - negative_score)
        
        # Determine emotional tone category
        scores = {
            'positive': positive_score,
            'negative': negative_score, 
            'neutral': neutral_score
        }
        
        emotional_tone = max(scores.keys(), key=lambda k: scores[k])
        confidence = max(scores.values())
        
        return {
            'emotional_tone': emotional_tone,
            'confidence': confidence,
            'sentiment_scores': scores,
            'sentiment_words': sentiment_words[:10],  # Limit for readability
            'analysis_metadata': {
                'total_tokens': total_tokens,
                'sentiment_bearing_words': len(sentiment_words),
                'sentiment_density': len(sentiment_words) / max(total_tokens, 1)
            }
        }
    
    def analyze_topic_sentiment(self, topic_data: Dict, associated_texts: List[str] = None) -> Dict:
        """
        🔬 Analyze sentiment specifically for topic modeling results
        Assess emotional tone of identified topics and their associated texts
        """
        topic_sentiment_results = {
            'topic_id': topic_data.get('topic_id', topic_data.get('id', 0)),
            'topic_keywords': topic_data.get('keywords', []),
            'topic_label': topic_data.get('topic_label', f"Topic {topic_data.get('topic_id', 0)}"),
        }
        
        # Analyze sentiment of topic keywords
        if 'keywords' in topic_data:
            keywords_text = ' '.join([
                word if isinstance(word, str) else word[0] 
                for word in topic_data['keywords'][:10]
            ])
            
            topic_keywords_sentiment = self.assess_emotional_tone(keywords_text)
            topic_sentiment_results['keywords_sentiment'] = topic_keywords_sentiment
        
        # Analyze sentiment of associated texts if provided
        if associated_texts:
            text_sentiments = []
            overall_positive = 0.0
            overall_negative = 0.0
            overall_neutral = 0.0
            
            for i, text in enumerate(associated_texts):
                text_analysis = self.assess_emotional_tone(text)
                text_sentiments.append({
                    'text_id': i,
                    'text_preview': text[:100] + "..." if len(text) > 100 else text,
                    'sentiment_analysis': text_analysis
                })
                
                # Accumulate scores
                overall_positive += text_analysis['sentiment_scores']['positive']
                overall_negative += text_analysis['sentiment_scores']['negative']
                overall_neutral += text_analysis['sentiment_scores']['neutral']
            
            # Average sentiment across all texts
            num_texts = len(associated_texts)
            if num_texts > 0:
                topic_sentiment_results['texts_sentiment'] = {
                    'individual_analyses': text_sentiments,
                    'aggregated_sentiment': {
                        'positive': overall_positive / num_texts,
                        'negative': overall_negative / num_texts,
                        'neutral': overall_neutral / num_texts
                    },
                    'dominant_sentiment': max(
                        ['positive', 'negative', 'neutral'],
                        key=lambda x: {
                            'positive': overall_positive / num_texts,
                            'negative': overall_negative / num_texts, 
                            'neutral': overall_neutral / num_texts
                        }[x]
                    ),
                    'sentiment_consistency': self._calculate_sentiment_consistency(text_sentiments)
                }
        
        return topic_sentiment_results
    
    def integrate_sentiment_with_topics(self, topic_modeling_results: Dict, texts: List[str]) -> Dict:
        """
        🔗 Integration: Combine sentiment analysis results with topic modeling 
        to provide a comprehensive view of the data
        """
        logger.info("🎭 Integrating sentiment analysis with topic modeling results")
        
        integrated_results = {
            'integration_metadata': {
                'analysis_type': 'sentiment_topic_integration',
                'timestamp': time.time(),
                'num_topics': len(topic_modeling_results.get('topics', [])),
                'num_texts': len(texts),
                'algorithm_used': topic_modeling_results.get('algorithm_used', 'unknown')
            },
            'topic_sentiment_analysis': [],
            'comprehensive_insights': {},
            'sentiment_topic_matrix': {},
            'recommendations': []
        }
        
        # Analyze sentiment for each topic
        topics = topic_modeling_results.get('topics', [])
        document_topic_dist = topic_modeling_results.get('document_topic_distribution', [])
        
        for topic in topics:
            # Find texts most associated with this topic
            topic_id = topic.get('topic_id', topic.get('id', 0))
            associated_texts = []
            
            # Extract texts based on document-topic distribution
            if document_topic_dist:
                for doc_dist in document_topic_dist:
                    if doc_dist.get('dominant_topic') == topic_id:
                        doc_id = doc_dist.get('document_id', 0)
                        if doc_id < len(texts):
                            associated_texts.append(texts[doc_id])
            
            # If no specific association found, use all texts (fallback)
            if not associated_texts and texts:
                associated_texts = texts[:3]  # Use first 3 texts as sample
            
            # Perform sentiment analysis for this topic
            topic_sentiment = self.analyze_topic_sentiment(topic, associated_texts)
            integrated_results['topic_sentiment_analysis'].append(topic_sentiment)
        
        # Generate comprehensive insights
        integrated_results['comprehensive_insights'] = self._generate_comprehensive_insights(
            integrated_results['topic_sentiment_analysis'], 
            topic_modeling_results
        )
        
        # Create sentiment-topic matrix
        integrated_results['sentiment_topic_matrix'] = self._create_sentiment_topic_matrix(
            integrated_results['topic_sentiment_analysis']
        )
        
        # Generate recommendations
        integrated_results['recommendations'] = self._generate_integration_recommendations(
            integrated_results['topic_sentiment_analysis']
        )
        
        return integrated_results
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        return re.findall(r'\b\w+\b', text.lower())
    
    def _calculate_sentiment_consistency(self, text_sentiments: List[Dict]) -> Dict:
        """Calculate how consistent sentiments are across texts"""
        if not text_sentiments:
            return {'score': 0.0, 'description': 'No texts to analyze'}
        
        sentiments = [analysis['sentiment_analysis']['emotional_tone'] for analysis in text_sentiments]
        sentiment_counts = Counter(sentiments)
        most_common_sentiment, most_common_count = sentiment_counts.most_common(1)[0]
        
        consistency_score = most_common_count / len(sentiments)
        
        return {
            'score': consistency_score,
            'dominant_sentiment': most_common_sentiment,
            'description': f"{consistency_score:.1%} of texts share the same sentiment"
        }
    
    def _generate_comprehensive_insights(self, topic_sentiments: List[Dict], topic_results: Dict) -> Dict:
        """Generate comprehensive insights from integrated analysis"""
        insights = {
            'overall_sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
            'topic_sentiment_summary': [],
            'key_findings': [],
            'sentiment_patterns': {}
        }
        
        # Analyze sentiment distribution across topics
        for topic_sentiment in topic_sentiments:
            if 'texts_sentiment' in topic_sentiment:
                agg_sentiment = topic_sentiment['texts_sentiment']['aggregated_sentiment']
                insights['overall_sentiment_distribution']['positive'] += agg_sentiment['positive']
                insights['overall_sentiment_distribution']['negative'] += agg_sentiment['negative']
                insights['overall_sentiment_distribution']['neutral'] += agg_sentiment['neutral']
                
                # Topic summary
                insights['topic_sentiment_summary'].append({
                    'topic_label': topic_sentiment['topic_label'],
                    'dominant_sentiment': topic_sentiment['texts_sentiment']['dominant_sentiment'],
                    'consistency': topic_sentiment['texts_sentiment']['sentiment_consistency']['score']
                })
        
        # Normalize distribution
        total_topics = len(topic_sentiments)
        if total_topics > 0:
            for sentiment in insights['overall_sentiment_distribution']:
                insights['overall_sentiment_distribution'][sentiment] /= total_topics
        
        # Generate key findings
        if insights['topic_sentiment_summary']:
            positive_topics = sum(1 for t in insights['topic_sentiment_summary'] if t['dominant_sentiment'] == 'positive')
            negative_topics = sum(1 for t in insights['topic_sentiment_summary'] if t['dominant_sentiment'] == 'negative')
            neutral_topics = sum(1 for t in insights['topic_sentiment_summary'] if t['dominant_sentiment'] == 'neutral')
            
            insights['key_findings'] = [
                f"Analyzed {total_topics} topics with sentiment integration",
                f"{positive_topics} topics show positive sentiment dominance",
                f"{negative_topics} topics show negative sentiment dominance", 
                f"{neutral_topics} topics show neutral sentiment dominance"
            ]
        
        return insights
    
    def _create_sentiment_topic_matrix(self, topic_sentiments: List[Dict]) -> Dict:
        """Create a matrix showing sentiment distribution across topics"""
        matrix = {
            'topics': [],
            'sentiment_scores': [],
            'visualization_data': []
        }
        
        for topic_sentiment in topic_sentiments:
            topic_label = topic_sentiment['topic_label']
            matrix['topics'].append(topic_label)
            
            if 'texts_sentiment' in topic_sentiment:
                scores = topic_sentiment['texts_sentiment']['aggregated_sentiment']
                matrix['sentiment_scores'].append(scores)
                
                # Data for visualization
                matrix['visualization_data'].append({
                    'topic': topic_label,
                    'positive': scores['positive'],
                    'negative': scores['negative'],
                    'neutral': scores['neutral']
                })
        
        return matrix
    
    def _generate_integration_recommendations(self, topic_sentiments: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on sentiment-topic analysis"""
        recommendations = []
        
        if not topic_sentiments:
            return ["No topics available for sentiment analysis"]
        
        # Analyze patterns
        positive_topics = []
        negative_topics = []
        neutral_topics = []
        
        for topic_sentiment in topic_sentiments:
            topic_label = topic_sentiment['topic_label']
            if 'texts_sentiment' in topic_sentiment:
                dominant = topic_sentiment['texts_sentiment']['dominant_sentiment']
                if dominant == 'positive':
                    positive_topics.append(topic_label)
                elif dominant == 'negative':
                    negative_topics.append(topic_label)
                else:
                    neutral_topics.append(topic_label)
        
        # Generate recommendations
        if positive_topics:
            recommendations.append(f"Leverage positive sentiment in topics: {', '.join(positive_topics[:3])}")
        
        if negative_topics:
            recommendations.append(f"Address concerns in negative sentiment topics: {', '.join(negative_topics[:3])}")
        
        if neutral_topics:
            recommendations.append(f"Opportunity to enhance engagement in neutral topics: {', '.join(neutral_topics[:2])}")
        
        recommendations.append("Consider sentiment patterns when developing topic-specific strategies")
        
        return recommendations

class SimpleSentimentAnalyzer:
    """
    Simple rule-based sentiment analyzer without external dependencies
    """
    
    def __init__(self):
        # Positive words lexicon
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 'perfect',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'delighted', 'thrilled',
            'brilliant', 'outstanding', 'superb', 'marvelous', 'impressive', 'beautiful', 'nice',
            'best', 'better', 'positive', 'optimistic', 'excited', 'joyful', 'cheerful', 'pleasant',
            'recommend', 'success', 'successful', 'win', 'winner', 'achieve', 'accomplished',
            'helpful', 'useful', 'valuable', 'effective', 'efficient', 'quality', 'superior'
        }
        
        # Negative words lexicon
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate', 'dislike', 'disappointed',
            'angry', 'frustrated', 'annoyed', 'upset', 'sad', 'depressed', 'worried', 'concerned',
            'problem', 'issue', 'error', 'bug', 'fail', 'failure', 'wrong', 'broken', 'useless',
            'waste', 'poor', 'worst', 'worse', 'negative', 'pessimistic', 'difficult', 'hard',
            'impossible', 'never', 'nothing', 'nobody', 'none', 'reject', 'refuse', 'deny',
            'complain', 'complaint', 'regret', 'sorry', 'apologize', 'mistake', 'unfortunate'
        }
        
        # Intensifiers that boost sentiment
        self.intensifiers = {
            'very', 'extremely', 'really', 'absolutely', 'completely', 'totally', 'quite',
            'highly', 'deeply', 'truly', 'incredibly', 'amazingly', 'exceptionally'
        }
        
        # Negation words that flip sentiment
        self.negation_words = {
            'not', 'no', 'never', 'neither', 'nor', 'none', 'nobody', 'nothing',
            'nowhere', 'hardly', 'scarcely', 'barely', 'cannot', "can't", "won't",
            "shouldn't", "wouldn't", "couldn't", "mustn't", "don't", "doesn't", "didn't"
        }
    
    def clean_and_tokenize(self, text: str) -> List[str]:
        """Simple tokenization for sentiment analysis"""
        # Convert to lowercase and remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Split into words
        return text.split()
    
    def calculate_sentiment_scores(self, text: str) -> Dict:
        """Calculate sentiment scores for a text with improved algorithm"""
        tokens = self.clean_and_tokenize(text)
        
        positive_score = 0.0
        negative_score = 0.0
        emotional_indicators = []
        sentiment_word_count = 0
        
        # Track negation context
        negation_active = False
        intensifier_boost = 1.0
        
        for i, token in enumerate(tokens):
            # Check for negation words
            if token in self.negation_words:
                negation_active = True
                continue
                
            # Check for intensifiers
            if token in self.intensifiers:
                intensifier_boost = 1.5
                continue
            
            # Calculate sentiment
            word_positive = 0.0
            word_negative = 0.0
            
            if token in self.positive_words:
                word_positive = 1.0 * intensifier_boost
                emotional_indicators.append(f"+{token}")
                sentiment_word_count += 1
                
            elif token in self.negative_words:
                word_negative = 1.0 * intensifier_boost
                emotional_indicators.append(f"-{token}")
                sentiment_word_count += 1
            
            # Apply negation if active
            if negation_active:
                word_positive, word_negative = word_negative, word_positive
                if word_positive > 0 or word_negative > 0:
                    emotional_indicators.append("negated")
                negation_active = False
            
            positive_score += word_positive
            negative_score += word_negative
            intensifier_boost = 1.0  # Reset intensifier
        
        # Improved normalization and scoring
        total_words = len(tokens)
        
        # If no sentiment words found, it's neutral
        if sentiment_word_count == 0:
            scores = {
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0
            }
            dominant_sentiment = 'neutral'
            confidence = 0.8  # High confidence in neutrality when no sentiment words
        else:
            # Normalize by sentiment word count instead of total words
            positive_score = positive_score / sentiment_word_count if sentiment_word_count > 0 else 0.0
            negative_score = negative_score / sentiment_word_count if sentiment_word_count > 0 else 0.0
            
            # Calculate neutral based on lack of sentiment
            sentiment_density = sentiment_word_count / max(total_words, 1)
            neutral_base = max(0.0, 1.0 - sentiment_density * 2)  # Reduce neutral weight
            
            # Improved score calculation
            total_sentiment = positive_score + negative_score + neutral_base
            if total_sentiment > 0:
                scores = {
                    'positive': positive_score / total_sentiment,
                    'negative': negative_score / total_sentiment,
                    'neutral': neutral_base / total_sentiment
                }
            else:
                scores = {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
            
            # Determine dominant sentiment with minimum threshold
            sentiment_threshold = 0.3
            if scores['positive'] > sentiment_threshold and scores['positive'] > scores['negative']:
                dominant_sentiment = 'positive'
                confidence = scores['positive']
            elif scores['negative'] > sentiment_threshold and scores['negative'] > scores['positive']:
                dominant_sentiment = 'negative'
                confidence = scores['negative']
            else:
                dominant_sentiment = 'neutral'
                confidence = scores['neutral']
        
        return {
            'sentiment_scores': scores,
            'dominant_sentiment': dominant_sentiment,
            'confidence': confidence,
            'emotional_indicators': emotional_indicators[:10],  # Limit indicators
            'analysis_metadata': {
                'total_words': total_words,
                'sentiment_words': sentiment_word_count,
                'sentiment_density': sentiment_word_count / max(total_words, 1)
            }
        }
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze sentiment for a single text and return complete analysis"""
        if not text or not isinstance(text, str):
            raise ValueError("Text input must be a non-empty string")
        
        # Split text into sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            sentences = [text]  # Fallback to original text if no sentences found
        
        # Analyze each sentence
        sentence_results = []
        for sentence in sentences:
            if len(sentence.strip()) < 3:  # Skip very short sentences
                continue
                
            analysis = self.calculate_sentiment_scores(sentence)
            
            sentence_result = {
                'sentence': sentence,
                'sentiment': analysis['dominant_sentiment'],
                'confidence': analysis['confidence'],
                'positive_score': analysis['sentiment_scores']['positive'],
                'negative_score': analysis['sentiment_scores']['negative'],
                'neutral_score': analysis['sentiment_scores']['neutral']
            }
            sentence_results.append(sentence_result)
        
        # Calculate overall metrics
        if not sentence_results:
            # Fallback: analyze the full text as one sentence
            analysis = self.calculate_sentiment_scores(text)
            sentence_results = [{
                'sentence': text,
                'sentiment': analysis['dominant_sentiment'],
                'confidence': analysis['confidence'],
                'positive_score': analysis['sentiment_scores']['positive'],
                'negative_score': analysis['sentiment_scores']['negative'],
                'neutral_score': analysis['sentiment_scores']['neutral']
            }]
        
        # Aggregate results
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        total_confidence = 0.0
        all_emotional_indicators = []
        
        for result in sentence_results:
            sentiment_counts[result['sentiment']] += 1
            total_confidence += result['confidence']
        
        # Overall analysis
        overall_analysis = self.calculate_sentiment_scores(text)
        all_emotional_indicators = overall_analysis['emotional_indicators']
        
        # Calculate distributions
        total_sentences = len(sentence_results)
        sentiment_distribution = {
            'positive': sentiment_counts['positive'] / total_sentences,
            'negative': sentiment_counts['negative'] / total_sentences,
            'neutral': sentiment_counts['neutral'] / total_sentences
        }
        
        # Emotional indicators breakdown
        emotional_indicators = {
            'joy': 0.0,
            'sadness': 0.0,
            'anger': 0.0,
            'fear': 0.0
        }
        
        # Simple emotional mapping based on words found
        emotion_words = {
            'joy': ['happy', 'joy', 'excited', 'wonderful', 'amazing', 'fantastic', 'great', 'excellent', 'love'],
            'sadness': ['sad', 'disappointed', 'terrible', 'awful', 'horrible', 'bad', 'poor', 'worst'],
            'anger': ['angry', 'furious', 'mad', 'annoying', 'irritating', 'stupid', 'hate'],
            'fear': ['scary', 'afraid', 'worried', 'concerned', 'anxious', 'nervous']
        }
        
        text_lower = text.lower()
        for emotion, words in emotion_words.items():
            count = sum(1 for word in words if word in text_lower)
            emotional_indicators[emotion] = min(count / 10.0, 1.0)  # Normalize to 0-1
        
        return {
            'overall_sentiment': overall_analysis['dominant_sentiment'],
            'overall_confidence': overall_analysis['confidence'],
            'sentiment_distribution': sentiment_distribution,
            'emotional_indicators': emotional_indicators,
            'results': sentence_results,
            'summary': {
                'total_sentences': total_sentences,
                'positive_sentences': sentiment_counts['positive'],
                'negative_sentences': sentiment_counts['negative'],
                'neutral_sentences': sentiment_counts['neutral'],
                'average_confidence': total_confidence / total_sentences if total_sentences > 0 else 0.0
            }
        }
    
    def analyze_texts(self, texts: List[str]) -> List[Dict]:
        """Analyze sentiment for multiple texts"""
        results = []
        
        for i, text in enumerate(texts):
            if not text or not isinstance(text, str):
                continue
                
            analysis = self.calculate_sentiment_scores(text)
            
            result = {
                'text_id': i,
                'text_preview': text[:100] + "..." if len(text) > 100 else text,
                'sentiment_label': analysis['dominant_sentiment'],
                'confidence_score': analysis['confidence'],
                'sentiment_scores': analysis['sentiment_scores'],
                'emotional_indicators': analysis['emotional_indicators'],
                'text_length': len(text)
            }
            
            results.append(result)
        
        return results

@app.post("/sentiment-analysis", response_model=SentimentAnalysisResult)
async def sentiment_analysis_endpoint(input_data: SentimentAnalysisInput):
    """
    🎭 Perform sentiment analysis on text documents
    
    Analyzes the emotional tone of texts and categorizes them as positive, negative, or neutral.
    """
    start_time = time.time()
    
    try:
        if not input_data.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Non-empty text is required for sentiment analysis"
            )
        
        logger.info(f"🎭 Starting sentiment analysis on text of length {len(input_data.text)}")
        
        # Initialize sentiment analyzer
        analyzer = SimpleSentimentAnalyzer()
        
        # Perform analysis on the single text
        result = analyzer.analyze_text(input_data.text.strip())
        
        processing_time = time.time() - start_time
        
        logger.info(f"✅ Sentiment analysis completed successfully!")
        logger.info(f"🎯 Overall sentiment: {result['overall_sentiment']}")
        logger.info(f"⏱️  Processing time: {processing_time:.2f}s")
        
        return SentimentAnalysisResult(**result)
        
    except Exception as e:
        logger.error(f"❌ Sentiment analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

# ============================================================================
# ADVANCED SENTIMENT ANALYSIS - FOLLOWING SPECIFIED REQUIREMENTS
# ============================================================================

class SentimentTopicIntegrationInput(BaseModel):
    """Input model for sentiment-topic integration analysis"""
    texts: List[str] = Field(..., description="Texts for analysis")
    topic_modeling_algorithm: str = Field(default="lda", description="Algorithm for topic modeling: 'lda' or 'nmf'")
    num_topics: int = Field(default=5, description="Number of topics to extract")
    options: Optional[Dict] = Field(default_factory=dict, description="Additional processing options")

class SentimentTopicIntegrationResult(BaseModel):
    """Result model for integrated sentiment-topic analysis"""
    integration_metadata: Dict
    topic_sentiment_analysis: List[Dict]
    comprehensive_insights: Dict
    sentiment_topic_matrix: Dict
    recommendations: List[str]
    processing_time: float

@app.post("/sentiment-topic-integration")
async def sentiment_topic_integration_endpoint(input_data: SentimentTopicIntegrationInput):
    """
    🎭🧠 Advanced Sentiment-Topic Integration following specified requirements:
    
    ● Sentiment Detection: Implement sentiment analysis algorithms to assess 
      the emotional tone of the identified topics, categorizing sentiments 
      as positive, negative, or neutral.
    ● Integration: Combine sentiment analysis results with topic modeling 
      to provide a comprehensive view of the data.
    
    This endpoint performs both topic modeling and sentiment analysis, then
    integrates the results to provide comprehensive insights.
    """
    start_time = time.time()
    
    try:
        logger.info("🎯 Starting Sentiment-Topic Integration Analysis")
        logger.info(f"📊 Processing {len(input_data.texts)} texts with {input_data.topic_modeling_algorithm.upper()}")
        
        # Step 1: Perform Topic Modeling
        logger.info("🧠 Step 1: Performing Topic Modeling...")
        topic_modeling_payload = {
            "texts": input_data.texts,
            "algorithm": input_data.topic_modeling_algorithm,
            "num_topics": input_data.num_topics,
            "options": input_data.options
        }
        
        # Use our advanced topic modeling function
        topic_results = perform_advanced_topic_modeling(
            texts=input_data.texts,
            algorithm=input_data.topic_modeling_algorithm,
            num_topics=input_data.num_topics,
            preprocessing_options=input_data.options.get('preprocessing_options', {}),
            training_options=input_data.options.get('training_options', {})
        )
        
        # Step 2: Perform Sentiment Detection and Integration
        logger.info("🎭 Step 2: Performing Sentiment Detection and Integration...")
        advanced_analyzer = AdvancedSentimentAnalyzer()
        
        # Integrate sentiment analysis with topic modeling results
        integration_results = advanced_analyzer.integrate_sentiment_with_topics(
            topic_modeling_results=topic_results,
            texts=input_data.texts
        )
        
        processing_time = time.time() - start_time
        integration_results['processing_time'] = processing_time
        
        logger.info("✅ Sentiment-Topic Integration completed successfully!")
        logger.info(f"🎯 Analyzed {len(topic_results.get('topics', []))} topics with sentiment integration")
        logger.info(f"⏱️  Total processing time: {processing_time:.2f}s")
        
        return SentimentTopicIntegrationResult(**integration_results)
        
    except Exception as e:
        logger.error(f"❌ Sentiment-Topic Integration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Integration analysis failed: {str(e)}")

@app.post("/analyze-topic-sentiment")
async def analyze_topic_sentiment_endpoint(
    topic_data: Dict,
    associated_texts: Optional[List[str]] = None
):
    """
    🔍 Sentiment Detection for Individual Topics
    
    ● Sentiment Detection: Assess the emotional tone of specific identified topics,
      categorizing sentiments as positive, negative, or neutral.
    
    This endpoint analyzes sentiment for a specific topic and its associated texts.
    """
    try:
        logger.info(f"🔍 Analyzing sentiment for topic: {topic_data.get('topic_label', 'Unknown')}")
        
        # Initialize advanced sentiment analyzer
        advanced_analyzer = AdvancedSentimentAnalyzer()
        
        # Analyze sentiment for the specific topic
        topic_sentiment_result = advanced_analyzer.analyze_topic_sentiment(
            topic_data=topic_data,
            associated_texts=associated_texts or []
        )
        
        logger.info("✅ Topic sentiment analysis completed!")
        
        return {
            "analysis_type": "topic_sentiment_analysis",
            "topic_sentiment_result": topic_sentiment_result,
            "requirements_compliance": {
                "sentiment_detection": "✅ Emotional tone assessed and categorized as positive/negative/neutral",
                "topic_focus": "✅ Analysis performed on identified topic data"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Topic sentiment analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Topic sentiment analysis failed: {str(e)}")

@app.post("/comprehensive-sentiment-topic-view")
async def comprehensive_sentiment_topic_view_endpoint(
    texts: List[str],
    existing_topic_results: Optional[Dict] = None,
    sentiment_options: Optional[Dict] = None
):
    """
    📊 Comprehensive Data View - Integration of Sentiment and Topic Analysis
    
    ● Integration: Combine sentiment analysis results with topic modeling 
      to provide a comprehensive view of the data.
    
    This endpoint provides a unified view combining existing topic modeling 
    results with comprehensive sentiment analysis.
    """
    try:
        logger.info("📊 Creating comprehensive sentiment-topic data view")
        
        # Initialize advanced sentiment analyzer
        advanced_analyzer = AdvancedSentimentAnalyzer()
        
        # If no existing topic results provided, perform basic topic modeling
        if not existing_topic_results:
            logger.info("🧠 No existing topic results - performing basic topic modeling")
            topic_results = perform_advanced_topic_modeling(
                texts=texts,
                algorithm="lda",  # Default algorithm
                num_topics=min(5, len(texts)),  # Adaptive number of topics
                preprocessing_options={},
                training_options={}
            )
        else:
            topic_results = existing_topic_results
        
        # Perform comprehensive sentiment analysis
        logger.info("🎭 Performing comprehensive sentiment analysis")
        sentiment_analyzer = SimpleSentimentAnalyzer()
        
        # Individual text sentiment analysis
        individual_sentiments = []
        for i, text in enumerate(texts):
            sentiment_result = sentiment_analyzer.analyze_text(text)
            individual_sentiments.append({
                'text_id': i,
                'text_preview': text[:100] + "..." if len(text) > 100 else text,
                'sentiment_analysis': sentiment_result
            })
        
        # Integrate results using advanced analyzer
        integration_results = advanced_analyzer.integrate_sentiment_with_topics(
            topic_modeling_results=topic_results,
            texts=texts
        )
        
        # Create comprehensive view
        comprehensive_view = {
            'analysis_overview': {
                'total_texts': len(texts),
                'total_topics': len(topic_results.get('topics', [])),
                'algorithm_used': topic_results.get('algorithm_used', 'unknown'),
                'analysis_type': 'comprehensive_sentiment_topic_integration'
            },
            'topic_modeling_results': topic_results,
            'individual_sentiment_results': individual_sentiments,
            'integrated_analysis': integration_results,
            'comprehensive_insights': {
                'sentiment_topic_patterns': integration_results.get('comprehensive_insights', {}),
                'actionable_recommendations': integration_results.get('recommendations', []),
                'sentiment_topic_matrix': integration_results.get('sentiment_topic_matrix', {})
            },
            'requirements_compliance': {
                'sentiment_detection': "✅ Emotional tone assessed for all topics as positive/negative/neutral",
                'integration': "✅ Sentiment analysis results combined with topic modeling for comprehensive view",
                'comprehensive_view': "✅ Unified data view provided with actionable insights"
            }
        }
        
        logger.info("✅ Comprehensive sentiment-topic view created successfully!")
        
        return comprehensive_view
        
    except Exception as e:
        logger.error(f"❌ Comprehensive view creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")

# TEXT SUMMARIZATION IMPLEMENTATION
# ======================================================================

class TextSummarizationInput(BaseModel):
    text: str = Field(..., description="Text to summarize")
    max_sentences: int = Field(default=3, description="Maximum number of sentences in summary")
    method: str = Field(default="frequency", description="Summarization method: frequency, tfidf")

class SummarizationResult(BaseModel):
    original_text: str
    summary: str
    key_sentences: List[str]
    sentence_scores: Dict[str, float]
    method_used: str
    compression_ratio: float
    word_count_original: int
    word_count_summary: int

class TextSummarizer:
    """
    Extractive text summarization using frequency-based and TF-IDF methods
    """
    
    def __init__(self):
        self.stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
            'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
            'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting on periods, exclamation marks, and question marks
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def calculate_word_frequencies(self, sentences: List[str]) -> Dict[str, int]:
        """Calculate word frequencies across all sentences"""
        word_freq = defaultdict(int)
        
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence.lower())
            for word in words:
                if word not in self.stop_words and len(word) > 2:
                    word_freq[word] += 1
        
        return dict(word_freq)
    
    def score_sentences_frequency(self, sentences: List[str], word_freq: Dict[str, int]) -> Dict[str, float]:
        """Score sentences based on word frequency"""
        sentence_scores = {}
        
        for i, sentence in enumerate(sentences):
            words = re.findall(r'\b\w+\b', sentence.lower())
            valid_words = [w for w in words if w not in self.stop_words and len(w) > 2]
            
            if valid_words:
                score = sum(word_freq.get(word, 0) for word in valid_words) / len(valid_words)
                sentence_scores[sentence] = score
            else:
                sentence_scores[sentence] = 0.0
        
        return sentence_scores
    
    def calculate_tf_idf(self, sentences: List[str]) -> Dict[str, float]:
        """Calculate TF-IDF scores for sentences"""
        # Calculate TF (Term Frequency) for each sentence
        tf_scores = {}
        all_words = set()
        
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence.lower())
            words = [w for w in words if w not in self.stop_words and len(w) > 2]
            all_words.update(words)
            
            word_count = len(words)
            tf = defaultdict(float)
            
            for word in words:
                tf[word] += 1.0 / word_count
            
            tf_scores[sentence] = dict(tf)
        
        # Calculate IDF (Inverse Document Frequency)
        idf_scores = {}
        total_sentences = len(sentences)
        
        for word in all_words:
            containing_sentences = sum(1 for sentence in sentences if word in sentence.lower())
            idf_scores[word] = math.log(total_sentences / containing_sentences) if containing_sentences > 0 else 0
        
        # Calculate TF-IDF scores for each sentence
        sentence_scores = {}
        for sentence in sentences:
            tf = tf_scores[sentence]
            score = sum(tf.get(word, 0) * idf_scores.get(word, 0) for word in tf.keys())
            sentence_scores[sentence] = score
        
        return sentence_scores
    
    def summarize_text(self, text: str, max_sentences: int = 3, method: str = "frequency") -> Dict:
        """Summarize text using specified method"""
        if not text.strip():
            raise ValueError("Text input cannot be empty")
        
        # Clean and split text
        clean_text = self.clean_text(text)
        sentences = self.split_into_sentences(clean_text)
        
        if len(sentences) <= max_sentences:
            return {
                'original_text': text,
                'summary': text,
                'key_sentences': sentences,
                'sentence_scores': {s: 1.0 for s in sentences},
                'method_used': method,
                'compression_ratio': 1.0,
                'word_count_original': len(text.split()),
                'word_count_summary': len(text.split())
            }
        
        # Calculate sentence scores based on method
        if method == "tfidf":
            sentence_scores = self.calculate_tf_idf(sentences)
        else:  # default to frequency method
            word_freq = self.calculate_word_frequencies(sentences)
            sentence_scores = self.score_sentences_frequency(sentences, word_freq)
        
        # Select top sentences
        sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        top_sentences = [sent for sent, score in sorted_sentences[:max_sentences]]
        
        # Maintain original order in summary
        ordered_summary_sentences = []
        for sentence in sentences:
            if sentence in top_sentences:
                ordered_summary_sentences.append(sentence)
        
        summary = '. '.join(ordered_summary_sentences) + '.'
        
        # Calculate metrics
        word_count_original = len(text.split())
        word_count_summary = len(summary.split())
        compression_ratio = word_count_summary / word_count_original if word_count_original > 0 else 0
        
        return {
            'original_text': text,
            'summary': summary,
            'key_sentences': ordered_summary_sentences,
            'sentence_scores': sentence_scores,
            'method_used': method,
            'compression_ratio': compression_ratio,
            'word_count_original': word_count_original,
            'word_count_summary': word_count_summary
        }

@app.post("/text-summarization", response_model=SummarizationResult)
async def text_summarization_endpoint(input_data: TextSummarizationInput):
    """
    📝 Perform extractive text summarization
    
    Extracts key sentences from text to create concise summaries using frequency or TF-IDF methods.
    """
    start_time = time.time()
    
    try:
        if not input_data.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Non-empty text is required for summarization"
            )
        
        logger.info(f"📝 Starting text summarization on text of length {len(input_data.text)}")
        logger.info(f"⚙️ Method: {input_data.method}, Max sentences: {input_data.max_sentences}")
        
        # Initialize summarizer
        summarizer = TextSummarizer()
        
        # Perform summarization
        result = summarizer.summarize_text(
            input_data.text,
            max_sentences=input_data.max_sentences,
            method=input_data.method
        )
        
        processing_time = time.time() - start_time
        
        logger.info(f"✅ Text summarization completed successfully!")
        logger.info(f"📊 Compression ratio: {result['compression_ratio']:.2f}")
        logger.info(f"⏱️  Processing time: {processing_time:.2f}s")
        
        return SummarizationResult(**result)
        
    except Exception as e:
        logger.error(f"❌ Text summarization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text summarization failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

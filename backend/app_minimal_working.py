#!/usr/bin/env python3
"""
Minimal working FastAPI backend for testing CSV topic modeling
"""
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import json
import uuid
import os
import csv
from io import StringIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import working modules
try:
    from advanced_topic_modeling import perform_advanced_topic_modeling
    from text_preprocessing import preprocess_text_comprehensive
    MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some modules unavailable: {e}")
    MODULES_AVAILABLE = False

app = FastAPI(
    title="AI Narrative Nexus - Minimal Working Backend",
    description="CSV Topic Modeling Test Server",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TopicModelingInput(BaseModel):
    texts: List[str]
    num_topics: int = 5
    algorithm: str = 'lda'

def clean_for_json_serialization(obj):
    """Clean objects for JSON serialization"""
    if isinstance(obj, dict):
        cleaned = {}
        for key, value in obj.items():
            if key in ['model_object', 'trained_model', 'lda_model', 'nmf_model']:
                continue
            if hasattr(value, '__class__') and 'LDA' in str(value.__class__):
                continue
            cleaned[key] = clean_for_json_serialization(value)
        return cleaned
    elif isinstance(obj, list):
        return [clean_for_json_serialization(item) for item in obj]
    elif isinstance(obj, set):
        return list(obj)
    else:
        return obj

def extract_csv_documents(file_content: str) -> List[str]:
    """Extract each CSV row as a separate document"""
    documents = []
    csv_reader = csv.reader(StringIO(file_content))
    
    for row_num, row in enumerate(csv_reader):
        if row_num == 0:  # Skip header
            continue
        
        # Find text content (look for text in any column)
        for cell in row:
            text = cell.strip().strip('"')
            if text and len(text) > 10:  # Only meaningful text
                documents.append(text)
                break  # Take the first meaningful text from each row
    
    return documents

@app.get("/")
async def root():
    return {
        "message": "AI Narrative Nexus - Minimal Working Backend",
        "status": "running",
        "features": ["CSV Upload", "Topic Modeling", "Each Row as Document"]
    }

@app.post("/topic-modeling")
async def topic_modeling_endpoint(input_data: TopicModelingInput):
    """Direct topic modeling endpoint"""
    try:
        logger.info(f"📊 Received {len(input_data.texts)} documents for topic modeling")
        
        if not MODULES_AVAILABLE:
            raise HTTPException(status_code=500, detail="Topic modeling modules not available")
        
        # Preprocess texts
        cleaned_texts = []
        for text in input_data.texts:
            if len(text.strip()) > 5:
                preprocessing_result = preprocess_text_comprehensive(text)
                # Extract the cleaned text from the preprocessing result
                if isinstance(preprocessing_result, dict):
                    cleaned_text = preprocessing_result.get('processed_text', '') or preprocessing_result.get('cleaned_text', '')
                else:
                    cleaned_text = str(preprocessing_result)
                
                if cleaned_text and len(cleaned_text.strip()) > 3:
                    cleaned_texts.append(cleaned_text.strip())
        
        if len(cleaned_texts) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 valid documents for topic modeling")
        
        logger.info(f"🔄 Preprocessed to {len(cleaned_texts)} valid documents")
        
        # Perform topic modeling
        results = perform_advanced_topic_modeling(
            texts=cleaned_texts,
            num_topics=min(input_data.num_topics, len(cleaned_texts)),
            algorithm=input_data.algorithm
        )
        
        # Clean for JSON
        clean_results = clean_for_json_serialization(results)
        
        logger.info(f"✅ Topic modeling completed successfully")
        return clean_results
        
    except Exception as e:
        logger.error(f"❌ Topic modeling failed: {e}")
        raise HTTPException(status_code=500, detail=f"Topic modeling failed: {str(e)}")

@app.post("/upload-csv")
async def upload_csv_endpoint(file: UploadFile = File(...)):
    """Upload CSV and extract documents"""
    try:
        logger.info(f"📂 Processing CSV file: {file.filename}")
        
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Extract documents
        documents = extract_csv_documents(text_content)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No valid text documents found in CSV")
        
        logger.info(f"📄 Extracted {len(documents)} documents from CSV")
        
        return {
            "status": "success",
            "filename": file.filename,
            "documents_count": len(documents),
            "documents": documents,
            "message": f"CSV processed: {len(documents)} rows as separate documents"
        }
        
    except Exception as e:
        logger.error(f"❌ CSV upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"CSV upload failed: {str(e)}")

@app.post("/csv-topic-modeling")
async def csv_topic_modeling_endpoint(file: UploadFile = File(...), num_topics: int = 3):
    """Combined CSV upload and topic modeling"""
    try:
        logger.info(f"📊 CSV Topic Modeling: {file.filename}")
        
        # Read and parse CSV
        content = await file.read()
        text_content = content.decode('utf-8')
        documents = extract_csv_documents(text_content)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No valid text documents found in CSV")
        
        logger.info(f"📄 Extracted {len(documents)} documents from CSV")
        
        # Perform topic modeling on documents
        topic_input = TopicModelingInput(
            texts=documents,
            num_topics=min(num_topics, len(documents)),
            algorithm='lda'
        )
        
        # Call topic modeling
        topic_results = await topic_modeling_endpoint(topic_input)
        
        # Add CSV info to results
        topic_results['csv_info'] = {
            'filename': file.filename,
            'documents_processed': len(documents),
            'each_row_as_document': True
        }
        
        return topic_results
        
    except Exception as e:
        logger.error(f"❌ CSV topic modeling failed: {e}")
        raise HTTPException(status_code=500, detail=f"CSV topic modeling failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting AI Narrative Nexus - Minimal Working Backend")
    print("✅ Features: CSV Upload, Topic Modeling, Each Row as Document")
    uvicorn.run(app, host="0.0.0.0", port=8000)

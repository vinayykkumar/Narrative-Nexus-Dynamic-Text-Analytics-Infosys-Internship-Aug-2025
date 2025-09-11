"""
Text Data Storage Module - Following Architecture Diagram
Handles storage of processed text data as specified in the architecture
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

class TextDataStorage:
    """
    Text Data Storage component as shown in the architecture diagram
    Stores processed text data between processing and analysis phases
    """
    
    def __init__(self, storage_path: str = "data/text_storage.db"):
        """Initialize the text data storage"""
        self.storage_path = storage_path
        self.ensure_storage_directory()
        self.init_database()
    
    def ensure_storage_directory(self):
        """Ensure the storage directory exists"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
    
    def init_database(self):
        """Initialize the SQLite database for text storage"""
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            
            # Create sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    original_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Create processed_texts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed_texts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    original_text TEXT NOT NULL,
                    cleaned_text TEXT NOT NULL,
                    normalized_text TEXT NOT NULL,
                    tokens TEXT NOT NULL,
                    processing_stats TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'processed'
                )
            ''')
            
            # Create analysis_results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text_id INTEGER NOT NULL,
                    analysis_type TEXT NOT NULL,
                    results TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (text_id) REFERENCES processed_texts (id)
                )
            ''')
            
            # Create insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    themes TEXT NOT NULL,
                    key_insights TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def store_session(self, session_id: str, original_text: str) -> bool:
        """
        Store session data
        """
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sessions (session_id, original_text)
                VALUES (?, ?)
            ''', (session_id, original_text))
            
            conn.commit()
            return True
    
    def store_session_documents(self, session_id: str, documents: List[str]) -> bool:
        """
        Store multiple documents for a session (e.g., from CSV rows)
        """
        # Store documents as JSON array in the original_text field
        documents_json = json.dumps(documents)
        
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sessions (session_id, original_text)
                VALUES (?, ?)
            ''', (session_id, documents_json))
            
            conn.commit()
            return True
    
    def get_session_documents(self, session_id: str) -> Optional[List[str]]:
        """
        Get session documents, handling both single text and multiple documents
        """
        session_data = self.get_session_data(session_id)
        if not session_data:
            return None
            
        text_content = session_data.get('text', '')
        if not text_content:
            return None
            
        # Try to parse as JSON array first (for multiple documents)
        try:
            documents = json.loads(text_content)
            if isinstance(documents, list) and all(isinstance(doc, str) for doc in documents):
                return documents
        except (json.JSONDecodeError, TypeError):
            pass
            
        # Fall back to single document
        return [text_content]
    
    def get_session_data(self, session_id: str) -> Optional[Dict]:
        """
        Get session data by session ID
        """
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_id, original_text, created_at, status
                FROM sessions 
                WHERE session_id = ?
            ''', (session_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'session_id': row[0],
                    'text': row[1],
                    'created_at': row[2],
                    'status': row[3]
                }
            return None
    
    def store_processed_text(self, session_id: str, original_text: str, 
                           cleaned_text: str, normalized_text: str, 
                           tokens: List[str], processing_stats: Dict) -> int:
        """
        Store processed text data as per architecture flow:
        Data Processing → Text Data Storage
        """
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO processed_texts 
                (session_id, original_text, cleaned_text, normalized_text, tokens, processing_stats)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                original_text,
                cleaned_text,
                normalized_text,
                json.dumps(tokens),
                json.dumps(processing_stats)
            ))
            
            text_id = cursor.lastrowid
            conn.commit()
            return text_id
    
    def get_processed_texts(self, session_id: str) -> List[Dict]:
        """
        Retrieve processed texts for analysis phase:
        Text Data Storage → Sentiment Analysis / Topic Modeling
        """
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, original_text, cleaned_text, normalized_text, 
                       tokens, processing_stats, created_at
                FROM processed_texts 
                WHERE session_id = ?
                ORDER BY created_at DESC
            ''', (session_id,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'original_text': row[1],
                    'cleaned_text': row[2],
                    'normalized_text': row[3],
                    'tokens': json.loads(row[4]),
                    'processing_stats': json.loads(row[5]),
                    'created_at': row[6]
                })
            
            return results
    
    def store_analysis_result(self, text_id: int, analysis_type: str, results: Dict):
        """
        Store analysis results:
        Sentiment Analysis / Topic Modeling → Storage → Insight Generation
        """
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analysis_results (text_id, analysis_type, results)
                VALUES (?, ?, ?)
            ''', (text_id, analysis_type, json.dumps(results)))
            
            conn.commit()
    
    def get_analysis_results(self, text_id: int, analysis_type: Optional[str] = None) -> List[Dict]:
        """
        Retrieve analysis results for insight generation
        """
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            
            if analysis_type:
                cursor.execute('''
                    SELECT analysis_type, results, created_at
                    FROM analysis_results 
                    WHERE text_id = ? AND analysis_type = ?
                ''', (text_id, analysis_type))
            else:
                cursor.execute('''
                    SELECT analysis_type, results, created_at
                    FROM analysis_results 
                    WHERE text_id = ?
                ''', (text_id,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'analysis_type': row[0],
                    'results': json.loads(row[1]),
                    'created_at': row[2]
                })
            
            return results
    
    def store_insights(self, session_id: str, insight_type: str, 
                      themes: List[str], key_insights: List[str], 
                      recommendations: List[str], confidence_score: float):
        """
        Store generated insights:
        Insight Generation → Storage → Reporting/Visualization
        """
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO insights 
                (session_id, insight_type, themes, key_insights, recommendations, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                insight_type,
                json.dumps(themes),
                json.dumps(key_insights),
                json.dumps(recommendations),
                confidence_score
            ))
            
            conn.commit()
    
    def get_insights(self, session_id: str) -> List[Dict]:
        """
        Retrieve insights for reporting and visualization
        """
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT insight_type, themes, key_insights, recommendations, 
                       confidence_score, created_at
                FROM insights 
                WHERE session_id = ?
                ORDER BY created_at DESC
            ''', (session_id,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'insight_type': row[0],
                    'themes': json.loads(row[1]),
                    'key_insights': json.loads(row[2]),
                    'recommendations': json.loads(row[3]),
                    'confidence_score': row[4],
                    'created_at': row[5]
                })
            
            return results
    
    def get_session_summary(self, session_id: str) -> Dict:
        """
        Get complete session summary for dashboard/reporting
        """
        processed_texts = self.get_processed_texts(session_id)
        insights = self.get_insights(session_id)
        
        # Get all analysis results for this session
        all_analyses = []
        for text in processed_texts:
            analyses = self.get_analysis_results(text['id'])
            all_analyses.extend(analyses)
        
        return {
            'session_id': session_id,
            'processed_texts_count': len(processed_texts),
            'analysis_results': all_analyses,
            'insights': insights,
            'last_updated': max([text['created_at'] for text in processed_texts] + 
                              [insight['created_at'] for insight in insights]) if processed_texts or insights else None
        }

# Global storage instance
text_storage = TextDataStorage()

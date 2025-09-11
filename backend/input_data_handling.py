"""
Input Data Handling Module - Following Architecture Diagram
Handles "Upload Text Data" as specified in the architecture flow
"""

from typing import Dict, List, Any, Optional, Union
from fastapi import UploadFile, HTTPException
import tempfile
import os
import csv
import json
import docx
import PyPDF2
from io import StringIO
import logging

logger = logging.getLogger(__name__)

class InputDataHandler:
    """
    Input Data Handling component as shown in the architecture diagram
    Architecture flow: User Interface → Input Data Handling → Data Processing
    """
    
    SUPPORTED_FORMATS = {
        'text': ['.txt', '.text'],
        'document': ['.docx', '.doc'],  
        'pdf': ['.pdf'],
        'structured': ['.csv', '.json', '.tsv'],
        'web': ['html', 'xml']
    }
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_TEXT_LENGTH = 1000000  # 1M characters
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="narrative_nexus_")
        logger.info(f"📁 Input handler initialized with temp dir: {self.temp_dir}")
    
    def handle_text_input(self, text_input: str, source_type: str = "direct") -> Dict[str, Any]:
        """
        Handle direct text input from user interface
        Architecture: User Interface → Input Data Handling
        """
        logger.info(f"📝 Processing direct text input (length: {len(text_input)} characters)")
        
        # Validate text input
        validation_result = self._validate_text_input(text_input)
        if not validation_result['valid']:
            raise HTTPException(status_code=400, detail=validation_result['error'])
        
        # Process and standardize input
        processed_input = {
            'source_type': source_type,
            'content_type': 'text',
            'original_content': text_input,
            'content': text_input,
            'metadata': {
                'character_count': len(text_input),
                'word_count': len(text_input.split()),
                'source': 'direct_input',
                'timestamp': self._get_timestamp()
            },
            'validation': validation_result,
            'processing_status': 'ready'
        }
        
        logger.info(f"✅ Text input processed successfully: {processed_input['metadata']['word_count']} words")
        return processed_input
    
    def handle_file_upload(self, uploaded_file: UploadFile) -> Dict[str, Any]:
        """
        Handle file upload from user interface
        Architecture: User Interface → Input Data Handling (Upload Text Data)
        """
        logger.info(f"📂 Processing file upload: {uploaded_file.filename}")
        
        # Validate file
        validation_result = self._validate_file_upload(uploaded_file)
        if not validation_result['valid']:
            raise HTTPException(status_code=400, detail=validation_result['error'])
        
        # Extract content based on file type
        content = self._extract_file_content(uploaded_file)
        
        # Process extracted content
        processed_input = {
            'source_type': 'file_upload',
            'content_type': self._detect_content_type(uploaded_file.filename),
            'original_content': content,
            'content': content,
            'metadata': {
                'filename': uploaded_file.filename,
                'file_size': uploaded_file.size,
                'character_count': len(content),
                'word_count': len(content.split()),
                'source': 'file_upload',
                'timestamp': self._get_timestamp()
            },
            'validation': validation_result,
            'processing_status': 'ready'
        }
        
        logger.info(f"✅ File processed successfully: {uploaded_file.filename} ({processed_input['metadata']['word_count']} words)")
        return processed_input
    
    def handle_multiple_files(self, uploaded_files: List[UploadFile]) -> List[Dict[str, Any]]:
        """
        Handle multiple file uploads for batch processing
        """
        logger.info(f"📂 Processing {len(uploaded_files)} files for batch upload")
        
        results = []
        errors = []
        
        for file in uploaded_files:
            try:
                processed_file = self.handle_file_upload(file)
                results.append(processed_file)
            except Exception as e:
                error = {
                    'filename': file.filename,
                    'error': str(e),
                    'status': 'failed'
                }
                errors.append(error)
                logger.error(f"❌ Failed to process file {file.filename}: {str(e)}")
        
        batch_result = {
            'batch_type': 'multiple_files',
            'total_files': len(uploaded_files),
            'successful_files': len(results),
            'failed_files': len(errors),
            'results': results,
            'errors': errors,
            'batch_metadata': {
                'total_words': sum(r['metadata']['word_count'] for r in results),
                'total_characters': sum(r['metadata']['character_count'] for r in results),
                'timestamp': self._get_timestamp()
            }
        }
        
        logger.info(f"✅ Batch processing complete: {len(results)}/{len(uploaded_files)} files successful")
        return batch_result
    
    def handle_structured_data(self, data_input: Union[Dict, List], format_type: str = "json") -> Dict[str, Any]:
        """
        Handle structured data input (JSON, CSV data)
        """
        logger.info(f"📊 Processing structured data input (format: {format_type})")
        
        # Convert structured data to text format
        if format_type.lower() == "json":
            content = self._json_to_text(data_input)
        elif format_type.lower() == "csv":
            content = self._csv_to_text(data_input)
        else:
            content = str(data_input)
        
        processed_input = {
            'source_type': 'structured_data',
            'content_type': format_type,
            'original_content': data_input,
            'content': content,
            'metadata': {
                'format': format_type,
                'character_count': len(content),
                'word_count': len(content.split()),
                'source': 'structured_input',
                'timestamp': self._get_timestamp()
            },
            'processing_status': 'ready'
        }
        
        return processed_input
    
    def _validate_text_input(self, text: str) -> Dict[str, Any]:
        """
        Validate direct text input
        """
        if not text or not text.strip():
            return {'valid': False, 'error': 'Text input cannot be empty'}
        
        if len(text) > self.MAX_TEXT_LENGTH:
            return {
                'valid': False, 
                'error': f'Text too long. Maximum {self.MAX_TEXT_LENGTH} characters allowed.'
            }
        
        # Check for minimum meaningful content
        words = text.split()
        if len(words) < 3:
            return {
                'valid': False,
                'error': 'Text too short. Please provide at least 3 words for meaningful analysis.'
            }
        
        return {
            'valid': True,
            'word_count': len(words),
            'character_count': len(text),
            'estimated_processing_time': self._estimate_processing_time(len(words))
        }
    
    def _validate_file_upload(self, file: UploadFile) -> Dict[str, Any]:
        """
        Validate uploaded file
        """
        if not file.filename:
            return {'valid': False, 'error': 'No file provided'}
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        supported_extensions = []
        for format_list in self.SUPPORTED_FORMATS.values():
            supported_extensions.extend(format_list)
        
        if file_ext not in supported_extensions:
            return {
                'valid': False,
                'error': f'Unsupported file format. Supported: {", ".join(supported_extensions)}'
            }
        
        # Check file size
        if hasattr(file, 'size') and file.size and file.size > self.MAX_FILE_SIZE:
            return {
                'valid': False,
                'error': f'File too large. Maximum size: {self.MAX_FILE_SIZE // (1024*1024)}MB'
            }
        
        return {
            'valid': True,
            'file_type': self._detect_content_type(file.filename),
            'file_extension': file_ext
        }
    
    def _extract_file_content(self, file: UploadFile) -> str:
        """
        Extract text content from various file types
        """
        file_ext = os.path.splitext(file.filename)[1].lower()
        logger.info(f"🔍 Extracting content from {file.filename} (type: {file_ext})")
        
        try:
            if file_ext in ['.txt', '.text']:
                content = self._extract_text_file(file)
            elif file_ext in ['.csv', '.tsv']:
                content = self._extract_csv_file(file)
            elif file_ext == '.json':
                content = self._extract_json_file(file)
            elif file_ext in ['.docx']:
                content = self._extract_docx_file(file)
            elif file_ext == '.pdf':
                content = self._extract_pdf_file(file)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
            
            logger.info(f"✅ Content extracted: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"❌ Content extraction failed for {file.filename}: {str(e)}")
            raise
    
    def _extract_text_file(self, file: UploadFile) -> str:
        """Extract content from plain text file"""
        try:
            content = file.file.read()
            file.file.seek(0)  # Reset file pointer for potential reuse
            
            if not content:
                raise HTTPException(status_code=400, detail="File appears to be empty")
            
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    decoded_content = content.decode(encoding).strip()
                    if decoded_content:
                        logger.info(f"📝 Text file decoded with {encoding}: {len(decoded_content)} characters")
                        return decoded_content
                except UnicodeDecodeError:
                    continue
            
            raise HTTPException(status_code=400, detail="Unable to decode text file with any supported encoding")
            
        except Exception as e:
            logger.error(f"❌ Text file extraction failed: {str(e)}")
            raise
    
    def _extract_csv_file(self, file: UploadFile) -> str:
        """Extract content from CSV file"""
        try:
            # Read the file content
            content = file.file.read()
            file.file.seek(0)  # Reset file pointer for potential reuse
            
            # Decode with proper encoding handling
            text_content = content.decode('utf-8-sig').strip()  # utf-8-sig handles BOM
            if not text_content:
                # Try latin-1 if utf-8 fails
                file.file.seek(0)
                content = file.file.read()
                text_content = content.decode('latin-1').strip()
            
            # Parse CSV and convert to text
            csv_reader = csv.reader(StringIO(text_content))
            formatted_content = []
            
            for row_num, row in enumerate(csv_reader):
                if row_num == 0:
                    # Add headers
                    formatted_content.append("Headers: " + " | ".join(row))
                else:
                    # Add row data
                    formatted_content.append(" | ".join(row))
            
            result = "\n".join(formatted_content)
            logger.info(f"📊 CSV processed: {len(formatted_content)} rows, {len(result)} characters")
            return result
            
        except Exception as e:
            logger.error(f"❌ CSV extraction failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to process CSV file: {str(e)}")
    
    def extract_csv_documents(self, file: UploadFile) -> List[str]:
        """Extract each CSV row as separate document for topic modeling"""
        try:
            # Read the file content
            content = file.file.read()
            file.file.seek(0)  # Reset file pointer for potential reuse
            
            # Decode with proper encoding handling
            text_content = content.decode('utf-8-sig').strip()  # utf-8-sig handles BOM
            if not text_content:
                # Try latin-1 if utf-8 fails
                file.file.seek(0)
                content = file.file.read()
                text_content = content.decode('latin-1').strip()
            
            # Parse CSV and extract documents
            csv_reader = csv.reader(StringIO(text_content))
            documents = []
            text_columns = []
            
            for row_num, row in enumerate(csv_reader):
                if row_num == 0:
                    # Find text columns in header
                    headers = [col.strip().strip('"').lower() for col in row]
                    for i, header in enumerate(headers):
                        if header in ['text', 'content', 'review', 'comment', 'description', 'message', 'body']:
                            text_columns.append(i)
                    
                    # If no specific text columns found, use the first column
                    if not text_columns:
                        text_columns = [0]
                        
                    logger.info(f"📊 Found text columns at indices: {text_columns}")
                else:
                    # Extract text from identified columns
                    row_texts = []
                    for col_idx in text_columns:
                        if col_idx < len(row):
                            text = row[col_idx].strip().strip('"')
                            if text:  # Only add non-empty text
                                row_texts.append(text)
                    
                    # Combine texts from multiple columns or use single text
                    if row_texts:
                        document_text = " ".join(row_texts) if len(row_texts) > 1 else row_texts[0]
                        if len(document_text.strip()) > 5:  # Only include meaningful documents
                            documents.append(document_text)
            
            logger.info(f"📊 CSV processed into {len(documents)} separate documents")
            return documents
            
        except Exception as e:
            logger.error(f"❌ CSV document extraction failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to process CSV file for documents: {str(e)}")
    
    def _extract_json_file(self, file: UploadFile) -> str:
        """Extract content from JSON file"""
        content = file.file.read().decode('utf-8')
        try:
            json_data = json.loads(content)
            return self._json_to_text(json_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file format")
    
    def _extract_docx_file(self, file: UploadFile) -> str:
        """Extract content from DOCX file"""
        try:
            # Save uploaded file temporarily
            temp_path = os.path.join(self.temp_dir, file.filename)
            with open(temp_path, 'wb') as temp_file:
                content = file.file.read()
                temp_file.write(content)
            
            # Extract text using python-docx
            doc = docx.Document(temp_path)
            text_content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            # Clean up temp file
            os.remove(temp_path)
            
            return "\n".join(text_content)
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing DOCX file: {str(e)}")
    
    def _extract_pdf_file(self, file: UploadFile) -> str:
        """Extract content from PDF file"""
        try:
            # Save uploaded file temporarily
            temp_path = os.path.join(self.temp_dir, file.filename)
            with open(temp_path, 'wb') as temp_file:
                content = file.file.read()
                temp_file.write(content)
            
            # Extract text using PyPDF2
            text_content = []
            with open(temp_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(text)
            
            # Clean up temp file
            os.remove(temp_path)
            
            return "\n".join(text_content)
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing PDF file: {str(e)}")
    
    def _detect_content_type(self, filename: str) -> str:
        """Detect content type from filename"""
        file_ext = os.path.splitext(filename)[1].lower()
        
        for content_type, extensions in self.SUPPORTED_FORMATS.items():
            if file_ext in extensions:
                return content_type
        
        return 'unknown'
    
    def _json_to_text(self, json_data: Union[Dict, List]) -> str:
        """Convert JSON data to readable text"""
        if isinstance(json_data, dict):
            text_parts = []
            for key, value in json_data.items():
                if isinstance(value, (str, int, float)):
                    text_parts.append(f"{key}: {value}")
                elif isinstance(value, list):
                    text_parts.append(f"{key}: {', '.join(map(str, value))}")
                elif isinstance(value, dict):
                    text_parts.append(f"{key}: {self._json_to_text(value)}")
            return "\n".join(text_parts)
        elif isinstance(json_data, list):
            return "\n".join(str(item) for item in json_data)
        else:
            return str(json_data)
    
    def _csv_to_text(self, csv_data: List[Dict]) -> str:
        """Convert CSV data to readable text"""
        if not csv_data:
            return ""
        
        text_parts = []
        for row in csv_data:
            if isinstance(row, dict):
                row_text = " | ".join(f"{key}: {value}" for key, value in row.items())
                text_parts.append(row_text)
            else:
                text_parts.append(str(row))
        
        return "\n".join(text_parts)
    
    def _estimate_processing_time(self, word_count: int) -> float:
        """Estimate processing time based on word count"""
        # Rough estimate: ~1000 words per second
        base_time = word_count / 1000.0
        return max(0.5, base_time)  # Minimum 0.5 seconds
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

# Global input handler instance
input_handler = InputDataHandler()

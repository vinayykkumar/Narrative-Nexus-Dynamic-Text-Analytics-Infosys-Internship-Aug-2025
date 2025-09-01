"""
AI Narrative Nexus - Minimal Backend API Server
FastAPI-based backend for text preprocessing - No external NLP dependencies
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uvicorn
import time
import json
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Narrative Nexus Backend",
    description="Advanced text preprocessing API - Minimal Version",
    version="1.0.0",
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
        result = preprocess_text(input_data.text, input_data.options)
        
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

if __name__ == "__main__":
    uvicorn.run(
        "app_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

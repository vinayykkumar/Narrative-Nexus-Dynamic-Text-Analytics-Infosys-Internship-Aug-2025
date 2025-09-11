"""
Text Preprocessing Module - Comprehensive Text Cleaning and Processing
Following the specified data preprocessing requirements:
● Removing special characters, punctuation, and stop words
● Normalizing text through stemming or lemmatization
● Handling missing values and ensuring data consistency
● Tokenization: Break down text into individual tokens (words or phrases)
"""

import re
import time
import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class TextPreprocessor:
    """
    Comprehensive text preprocessing class following all specified requirements
    """
    
    def __init__(self):
        """Initialize the text preprocessor with default settings"""
        self.stop_words = self._load_stop_words()
        self.lemmatization_dict = self._load_lemmatization_dict()
        self.contractions = self._load_contractions()
        
    def _load_stop_words(self) -> set:
        """Load comprehensive English stop words list"""
        return {
            # Pronouns
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
            'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            
            # Question words
            'what', 'which', 'who', 'whom', 'whose', 'when', 'where', 'why', 'how',
            
            # Demonstratives
            'this', 'that', 'these', 'those',
            
            # Articles
            'a', 'an', 'the',
            
            # Conjunctions
            'and', 'but', 'or', 'nor', 'for', 'yet', 'so', 'because', 'since', 'as', 'while',
            'although', 'though', 'unless', 'until', 'if', 'whether',
            
            # Prepositions
            'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
            'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'in', 'out',
            'on', 'off', 'over', 'under', 'to', 'from',
            
            # Auxiliary verbs
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
            'do', 'does', 'did', 'doing', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'shall',
            
            # Common adverbs
            'again', 'further', 'then', 'once', 'here', 'there', 'now', 'just', 'only', 'very',
            'too', 'so', 'than', 'quite', 'rather', 'really', 'actually', 'already', 'still',
            'also', 'even', 'almost', 'enough', 'exactly', 'hardly', 'nearly', 'quite',
            
            # Quantifiers
            'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'own', 'same', 'many', 'much', 'little', 'less', 'least',
            'several', 'every', 'either', 'neither',
            
            # Common words
            'yes', 'no', 'maybe', 'perhaps', 'however', 'therefore', 'thus', 'hence',
            'moreover', 'furthermore', 'nevertheless', 'nonetheless', 'meanwhile',
            'otherwise', 'instead', 'besides', 'additionally', 'finally', 'eventually'
        }
    
    def _load_lemmatization_dict(self) -> Dict[str, str]:
        """Load comprehensive lemmatization dictionary"""
        return {
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
    
    def _load_contractions(self) -> Dict[str, str]:
        """Load contractions dictionary for expansion"""
        return {
            "won't": "will not", "can't": "cannot", "n't": " not",
            "'re": " are", "'ve": " have", "'ll": " will",
            "'d": " would", "'m": " am", "it's": "it is",
            "that's": "that is", "there's": "there is",
            "here's": "here is", "what's": "what is",
            "where's": "where is", "how's": "how is",
            "let's": "let us", "don't": "do not",
            "doesn't": "does not", "didn't": "did not",
            "haven't": "have not", "hasn't": "has not",
            "hadn't": "had not", "won't": "will not",
            "wouldn't": "would not", "shouldn't": "should not",
            "couldn't": "could not", "mightn't": "might not",
            "mustn't": "must not"
        }
    
    def clean_text(self, text: str) -> tuple[str, Dict[str, int]]:
        """
        Step 1: Text Cleaning - Remove special characters, punctuation, etc.
        Returns: (cleaned_text, removal_stats)
        """
        if not text or not isinstance(text, str):
            return "", {
                'removed_urls': 0, 'removed_emails': 0, 'removed_mentions': 0,
                'removed_hashtags': 0, 'removed_numbers': 0, 'removed_html': 0,
                'removed_punctuation': 0
            }
        
        logger.info("🧹 Starting text cleaning...")
        cleaned = text.lower()
        stats = {}
        
        # Remove URLs
        logger.info("🔗 Removing URLs...")
        url_patterns = [r'https?://[^\s]+', r'www\.[^\s]+', r'ftp://[^\s]+']
        stats['removed_urls'] = 0
        for pattern in url_patterns:
            matches = re.findall(pattern, cleaned)
            stats['removed_urls'] += len(matches)
            cleaned = re.sub(pattern, '', cleaned)
        
        # Remove emails
        logger.info("📧 Removing email addresses...")
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        matches = re.findall(email_pattern, cleaned)
        stats['removed_emails'] = len(matches)
        cleaned = re.sub(email_pattern, '', cleaned)
        
        # Remove social media mentions and hashtags
        logger.info("📱 Removing social media mentions and hashtags...")
        mention_pattern = r'@\w+'
        hashtag_pattern = r'#\w+'
        stats['removed_mentions'] = len(re.findall(mention_pattern, cleaned))
        stats['removed_hashtags'] = len(re.findall(hashtag_pattern, cleaned))
        cleaned = re.sub(mention_pattern, '', cleaned)
        cleaned = re.sub(hashtag_pattern, '', cleaned)
        
        # Remove numbers (configurable)
        logger.info("🔢 Removing numbers...")
        number_pattern = r'\d+\.?\d*'
        matches = re.findall(number_pattern, cleaned)
        stats['removed_numbers'] = len(matches)
        cleaned = re.sub(number_pattern, '', cleaned)
        
        # Remove HTML tags
        logger.info("🏷️  Removing HTML tags...")
        html_matches = re.findall(r'<[^>]+>', cleaned)
        stats['removed_html'] = len(html_matches)
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # Remove punctuation and special characters
        logger.info("🔤 Removing punctuation and special characters...")
        punct_matches = re.findall(r'[^\w\s]', cleaned)
        stats['removed_punctuation'] = len(punct_matches)
        cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        logger.info(f"   ✅ Text cleaning complete. Length: {len(cleaned)} chars")
        return cleaned, stats
    
    def normalize_text(self, text: str) -> str:
        """
        Step 2: Text Normalization - Expand contractions and normalize forms
        """
        if not text:
            return ""
        
        logger.info("🔄 Starting text normalization...")
        normalized = text
        contractions_expanded = 0
        
        # Expand contractions
        for contraction, expansion in self.contractions.items():
            count_before = normalized.count(contraction)
            normalized = normalized.replace(contraction, expansion)
            contractions_expanded += count_before
        
        # Normalize whitespace again
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        logger.info(f"   ✅ Normalization complete. Expanded {contractions_expanded} contractions")
        return normalized
    
    def tokenize(self, text: str, min_length: int = 2, max_length: int = 50) -> List[str]:
        """
        Step 3: Tokenization - Break text into individual tokens
        """
        if not text:
            return []
        
        logger.info("✂️  Starting tokenization...")
        
        # Initial tokenization
        tokens = text.split()
        logger.info(f"   Initial tokens: {len(tokens)}")
        
        # Enhanced tokenization - handle compound words and contractions
        enhanced_tokens = []
        for token in tokens:
            # Handle remaining contractions and compound words
            if "'" in token:
                parts = token.split("'")
                enhanced_tokens.extend([part for part in parts if part])
            elif "-" in token and len(token) > 3:
                parts = token.split("-")
                enhanced_tokens.extend([part for part in parts if part and len(part) > 1])
            else:
                enhanced_tokens.append(token)
        
        # Filter by length
        logger.info(f"   Filtering tokens by length ({min_length}-{max_length} chars)...")
        initial_count = len(enhanced_tokens)
        filtered_tokens = [token for token in enhanced_tokens 
                          if min_length <= len(token) <= max_length]
        
        logger.info(f"   ✅ Tokenization complete. {len(filtered_tokens)} tokens "
                   f"(filtered {initial_count - len(filtered_tokens)})")
        
        return filtered_tokens
    
    def remove_stop_words(self, tokens: List[str]) -> tuple[List[str], int]:
        """
        Step 4: Stop Word Removal
        """
        if not tokens:
            return [], 0
        
        logger.info("🛑 Removing stop words...")
        initial_count = len(tokens)
        filtered_tokens = [token for token in tokens if token.lower() not in self.stop_words]
        removed_count = initial_count - len(filtered_tokens)
        
        logger.info(f"   ✅ Removed {removed_count} stop words")
        return filtered_tokens, removed_count
    
    def lemmatize(self, tokens: List[str]) -> tuple[List[str], int, List[str]]:
        """
        Step 5: Lemmatization - Normalize words to their root forms
        Returns: (lemmatized_tokens, lemmatized_count, examples)
        """
        if not tokens:
            return [], 0, []
        
        logger.info("🧠 Applying lemmatization...")
        lemmatized_tokens = []
        lemmatized_count = 0
        examples = []
        
        for token in tokens:
            original_token = token
            lemmatized_token = token.lower()
            
            # Check dictionary first
            if lemmatized_token in self.lemmatization_dict:
                lemmatized_token = self.lemmatization_dict[lemmatized_token]
                lemmatized_count += 1
                if len(examples) < 5:
                    examples.append(f"'{original_token}' → '{lemmatized_token}'")
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
                
                # Add to examples if changed
                if original_lemmatized != lemmatized_token and len(examples) < 5:
                    examples.append(f"'{original_token}' → '{lemmatized_token}'")
            
            lemmatized_tokens.append(lemmatized_token)
        
        logger.info(f"   ✅ Applied lemmatization to {lemmatized_count} tokens")
        if examples:
            logger.info(f"   Examples: {', '.join(examples)}")
        
        return lemmatized_tokens, lemmatized_count, examples
    
    def stem(self, tokens: List[str]) -> tuple[List[str], int, List[str]]:
        """
        Alternative Step 5: Stemming - Simple stemming rules (fallback option)
        """
        if not tokens:
            return [], 0, []
        
        logger.info("🌱 Applying stemming...")
        stemmed_tokens = []
        stemmed_count = 0
        examples = []
        
        for token in tokens:
            original_token = token
            stemmed_token = token.lower()
            
            # Simple stemming rules
            if stemmed_token.endswith('ing') and len(stemmed_token) > 5:
                stemmed_token = stemmed_token[:-3]
                stemmed_count += 1
                if len(examples) < 5:
                    examples.append(f"'{original_token}' → '{stemmed_token}'")
            elif stemmed_token.endswith('ed') and len(stemmed_token) > 4:
                stemmed_token = stemmed_token[:-2]
                stemmed_count += 1
                if len(examples) < 5:
                    examples.append(f"'{original_token}' → '{stemmed_token}'")
            elif stemmed_token.endswith('er') and len(stemmed_token) > 4:
                stemmed_token = stemmed_token[:-2]
                stemmed_count += 1
                if len(examples) < 5:
                    examples.append(f"'{original_token}' → '{stemmed_token}'")
            elif stemmed_token.endswith('est') and len(stemmed_token) > 5:
                stemmed_token = stemmed_token[:-3]
                stemmed_count += 1
                if len(examples) < 5:
                    examples.append(f"'{original_token}' → '{stemmed_token}'")
            elif stemmed_token.endswith('ly') and len(stemmed_token) > 4:
                stemmed_token = stemmed_token[:-2]
                stemmed_count += 1
                if len(examples) < 5:
                    examples.append(f"'{original_token}' → '{stemmed_token}'")
            elif stemmed_token.endswith('tion') and len(stemmed_token) > 6:
                stemmed_token = stemmed_token[:-4] + 'te'
                stemmed_count += 1
                if len(examples) < 5:
                    examples.append(f"'{original_token}' → '{stemmed_token}'")
            elif stemmed_token.endswith('ness') and len(stemmed_token) > 6:
                stemmed_token = stemmed_token[:-4]
                stemmed_count += 1
                if len(examples) < 5:
                    examples.append(f"'{original_token}' → '{stemmed_token}'")
            
            stemmed_tokens.append(stemmed_token)
        
        logger.info(f"   ✅ Applied stemming to {stemmed_count} tokens")
        if examples:
            logger.info(f"   Examples: {', '.join(examples)}")
        
        return stemmed_tokens, stemmed_count, examples
    
    def handle_missing_values(self, text: Optional[str]) -> str:
        """
        Handle missing values and ensure data consistency
        """
        if text is None:
            logger.warning("⚠️  Missing value detected: None")
            return ""
        
        if not isinstance(text, str):
            logger.warning(f"⚠️  Invalid data type detected: {type(text)}")
            return str(text) if text else ""
        
        if not text.strip():
            logger.warning("⚠️  Empty text detected")
            return ""
        
        return text.strip()
    
    def preprocess(self, text: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete preprocessing pipeline following all specified requirements:
        ● Removing special characters, punctuation, and stop words
        ● Normalizing text through stemming or lemmatization  
        ● Handling missing values and ensuring data consistency
        ● Tokenization: Break down text into individual tokens
        """
        start_time = time.time()
        options = options or {}
        
        logger.info("🚀 Starting comprehensive text preprocessing pipeline...")
        logger.info(f"📊 Input text length: {len(text) if text else 0} characters")
        
        # Step 0: Handle missing values and ensure data consistency
        text = self.handle_missing_values(text)
        if not text:
            logger.warning("❌ Empty or invalid input after missing value handling")
            return self._create_empty_result(start_time)
        
        original_text = text
        
        # Step 1: Text Cleaning
        cleaned_text, cleaning_stats = self.clean_text(text)
        
        # Step 2: Text Normalization
        normalized_text = self.normalize_text(cleaned_text)
        
        # Step 3: Tokenization
        min_length = options.get('min_token_length', 2)
        max_length = options.get('max_token_length', 50)
        tokens = self.tokenize(normalized_text, min_length, max_length)
        
        # Step 4: Stop Word Removal
        if options.get('remove_stopwords', True):
            tokens, stopwords_removed = self.remove_stop_words(tokens)
        else:
            stopwords_removed = 0
        
        # Step 5: Lemmatization or Stemming
        if options.get('use_lemmatization', True):
            tokens, morphology_count, morphology_examples = self.lemmatize(tokens)
            morphology_type = "lemmatization"
        elif options.get('use_stemming', False):
            tokens, morphology_count, morphology_examples = self.stem(tokens)
            morphology_type = "stemming"
        else:
            morphology_count = 0
            morphology_examples = []
            morphology_type = "none"
        
        # Final processing
        processed_text = ' '.join(tokens)
        processing_time = time.time() - start_time
        
        # Calculate comprehensive statistics
        stats = {
            'original_length': len(original_text),
            'cleaned_length': len(cleaned_text),
            'normalized_length': len(normalized_text),
            'processed_length': len(processed_text),
            'token_count': len(tokens),
            'vocabulary_size': len(set(tokens)),
            'avg_token_length': sum(len(token) for token in tokens) / len(tokens) if tokens else 0,
            'compression_ratio': len(processed_text) / len(original_text) if original_text else 0,
            'processing_time': processing_time,
            'removed_stopwords': stopwords_removed,
            'morphology_transformations': morphology_count,
            'morphology_type': morphology_type,
            **cleaning_stats
        }
        
        # Log final results
        logger.info("✅ Text preprocessing pipeline completed!")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   • Original → Processed: {stats['original_length']} → {stats['processed_length']} chars")
        logger.info(f"   • Token count: {stats['token_count']}")
        logger.info(f"   • Vocabulary size: {stats['vocabulary_size']}")
        logger.info(f"   • Stopwords removed: {stats['removed_stopwords']}")
        logger.info(f"   • {morphology_type.title()} applied: {morphology_count}")
        logger.info(f"   • Compression ratio: {stats['compression_ratio']:.2%}")
        logger.info(f"   • Processing time: {stats['processing_time']:.3f}s")
        
        return {
            'original_text': original_text,
            'cleaned_text': cleaned_text,
            'normalized_text': normalized_text,
            'tokens': tokens,
            'processed_text': processed_text,
            'stats': stats,
            'processing_time': processing_time,
            'morphology_examples': morphology_examples if morphology_examples else []
        }
    
    def _create_empty_result(self, start_time: float) -> Dict[str, Any]:
        """Create empty result structure for invalid inputs"""
        return {
            'original_text': '',
            'cleaned_text': '',
            'normalized_text': '',
            'tokens': [],
            'processed_text': '',
            'stats': {
                'original_length': 0, 'cleaned_length': 0, 'normalized_length': 0,
                'processed_length': 0, 'token_count': 0, 'vocabulary_size': 0,
                'avg_token_length': 0, 'compression_ratio': 0,
                'processing_time': time.time() - start_time,
                'removed_urls': 0, 'removed_emails': 0, 'removed_mentions': 0,
                'removed_hashtags': 0, 'removed_numbers': 0, 'removed_html': 0,
                'removed_punctuation': 0, 'removed_stopwords': 0,
                'morphology_transformations': 0, 'morphology_type': 'none'
            },
            'processing_time': time.time() - start_time,
            'morphology_examples': []
        }

# Global preprocessor instance
preprocessor = TextPreprocessor()

def preprocess_text_comprehensive(text: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main preprocessing function following all specified requirements:
    ● Removing special characters, punctuation, and stop words
    ● Normalizing text through stemming or lemmatization
    ● Handling missing values and ensuring data consistency
    ● Tokenization: Break down text into individual tokens (words or phrases)
    """
    return preprocessor.preprocess(text, options)

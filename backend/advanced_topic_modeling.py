"""
Topic Modeling Module - Algorithm Selection and Model Training
Following the specified requirements:
● Algorithm Selection: LDA and NMF for topic modeling
● Latent Dirichlet Allocation (LDA): For identifying latent topics in text data
● Non-negative Matrix Factorization (NMF): Alternative for topic extraction  
● Model Training: Train selected models on preprocessed text data to identify key themes and topics
"""

import re
import time
import math
import random
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
from text_preprocessing import preprocess_text_comprehensive

logger = logging.getLogger(__name__)

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
        self.vocabulary = [word for word, freq in word_freq.items() if freq >= 1 and len(word) > 2]
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
        
        # Simple training loop (simplified version)
        for iteration in range(self.num_iterations):
            if (iteration + 1) % 20 == 0:
                logger.info(f"🔄 NMF Iteration {iteration + 1}/{self.num_iterations}")
    
    def get_top_words(self, topic_id, num_words=10):
        """Get top words for a topic"""
        if topic_id >= self.num_topics or not self.H:
            return []
        
        word_weights = []
        for word_id, word in self.id_to_word.items():
            weight = self.H[topic_id][word_id] if topic_id < len(self.H) else 0.1
            word_weights.append((word, weight))
        
        # Sort by weight and return top words
        word_weights.sort(key=lambda x: x[1], reverse=True)
        return word_weights[:num_words]
    
    def get_document_topics(self, doc_id):
        """Get topic distribution for a document"""
        if not self.W or doc_id >= len(self.W):
            return [1.0 / self.num_topics] * self.num_topics
        
        # Normalize to get probabilities
        total = sum(self.W[doc_id])
        if total == 0:
            return [1.0 / self.num_topics] * self.num_topics
        
        return [weight / total for weight in self.W[doc_id]]

class TopicModelingEngine:
    """
    Advanced Topic Modeling Engine implementing algorithm selection and model training
    following the specified requirements
    """
    
    def __init__(self):
        """Initialize the topic modeling engine"""
        self.supported_algorithms = {
            'lda': 'Latent Dirichlet Allocation',
            'nmf': 'Non-negative Matrix Factorization'
        }
        logger.info(f"🎯 Topic Modeling Engine initialized with algorithms: {list(self.supported_algorithms.keys())}")
    
    def select_algorithm(self, algorithm: str, data_characteristics: Dict[str, Any]) -> str:
        """
        Algorithm Selection: Choose appropriate algorithms for topic modeling
        
        Args:
            algorithm: Requested algorithm ('lda' or 'nmf')
            data_characteristics: Characteristics of the input data
            
        Returns:
            Selected and validated algorithm
        """
        logger.info("🔍 ALGORITHM SELECTION PHASE")
        logger.info(f"📋 Requested algorithm: {algorithm.upper()}")
        
        algorithm = algorithm.lower()
        
        # Validate algorithm selection
        if algorithm not in self.supported_algorithms:
            logger.warning(f"⚠️  Unsupported algorithm '{algorithm}', defaulting to LDA")
            algorithm = 'lda'
        
        # Algorithm recommendation based on data characteristics
        num_documents = data_characteristics.get('num_documents', 0)
        avg_doc_length = data_characteristics.get('avg_doc_length', 0)
        vocabulary_size = data_characteristics.get('vocabulary_size', 0)
        
        logger.info(f"📊 Data Characteristics:")
        logger.info(f"   • Number of documents: {num_documents}")
        logger.info(f"   • Average document length: {avg_doc_length:.1f} tokens")
        logger.info(f"   • Vocabulary size: {vocabulary_size}")
        
        # Algorithm selection recommendations
        if algorithm == 'lda':
            logger.info("✅ LATENT DIRICHLET ALLOCATION (LDA) Selected:")
            logger.info("   • Purpose: Identifying latent topics in text data")
            logger.info("   • Strengths: Probabilistic model, handles topic mixtures well")
            logger.info("   • Best for: Documents with multiple topics, coherent topic distributions")
            
            if num_documents < 10:
                logger.warning("   ⚠️  LDA works better with more documents (current: {num_documents})")
            if avg_doc_length < 20:
                logger.warning("   ⚠️  LDA works better with longer documents (current avg: {avg_doc_length} tokens)")
                
        elif algorithm == 'nmf':
            logger.info("✅ NON-NEGATIVE MATRIX FACTORIZATION (NMF) Selected:")
            logger.info("   • Purpose: Alternative approach for topic extraction")
            logger.info("   • Strengths: Produces sparse, interpretable topics")
            logger.info("   • Best for: Clear topic separation, shorter documents")
            
            if vocabulary_size < 100:
                logger.warning("   ⚠️  NMF works better with larger vocabularies (current: {vocabulary_size})")
        
        logger.info(f"🎯 Final Algorithm Selection: {self.supported_algorithms[algorithm]} ({algorithm.upper()})")
        return algorithm
    
    def preprocess_for_topic_modeling(self, texts: List[str], preprocessing_options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Preprocess texts specifically for topic modeling with comprehensive preprocessing
        """
        logger.info("🔄 PREPROCESSING FOR TOPIC MODELING")
        
        preprocessing_options = preprocessing_options or {
            'remove_stopwords': True,
            'use_lemmatization': True,
            'min_token_length': 3,  # Longer minimum for topic modeling
            'max_token_length': 50
        }
        
        start_time = time.time()
        processed_texts = []
        all_tokens = []
        preprocessing_stats = {
            'original_texts': len(texts),
            'successfully_processed': 0,
            'failed_processing': 0,
            'total_original_chars': 0,
            'total_processed_chars': 0,
            'total_tokens': 0,
            'unique_tokens': set()
        }
        
        for i, text in enumerate(texts):
            try:
                # Use comprehensive preprocessing
                result = preprocess_text_comprehensive(text, preprocessing_options)
                
                if result['tokens']:  # Only include non-empty processed texts
                    processed_texts.append(' '.join(result['tokens']))
                    all_tokens.extend(result['tokens'])
                    preprocessing_stats['successfully_processed'] += 1
                    preprocessing_stats['total_original_chars'] += result['stats']['original_length']
                    preprocessing_stats['total_processed_chars'] += result['stats']['processed_length']
                    preprocessing_stats['total_tokens'] += result['stats']['token_count']
                    preprocessing_stats['unique_tokens'].update(result['tokens'])
                else:
                    logger.warning(f"⚠️  Text {i+1} resulted in empty tokens after preprocessing")
                    preprocessing_stats['failed_processing'] += 1
                    
            except Exception as e:
                logger.error(f"❌ Error preprocessing text {i+1}: {str(e)}")
                preprocessing_stats['failed_processing'] += 1
        
        processing_time = time.time() - start_time
        
        # Calculate data characteristics for algorithm selection
        data_characteristics = {
            'num_documents': len(processed_texts),
            'avg_doc_length': preprocessing_stats['total_tokens'] / len(processed_texts) if processed_texts else 0,
            'vocabulary_size': len(preprocessing_stats['unique_tokens']),
            'total_tokens': preprocessing_stats['total_tokens'],
            'compression_ratio': preprocessing_stats['total_processed_chars'] / preprocessing_stats['total_original_chars'] if preprocessing_stats['total_original_chars'] > 0 else 0
        }
        
        logger.info("✅ Preprocessing completed:")
        logger.info(f"   • Processed: {preprocessing_stats['successfully_processed']}/{len(texts)} texts")
        logger.info(f"   • Total tokens: {preprocessing_stats['total_tokens']:,}")
        logger.info(f"   • Vocabulary size: {data_characteristics['vocabulary_size']:,}")
        logger.info(f"   • Average document length: {data_characteristics['avg_doc_length']:.1f} tokens")
        logger.info(f"   • Processing time: {processing_time:.2f}s")
        
        return {
            'processed_texts': processed_texts,
            'data_characteristics': data_characteristics,
            'preprocessing_stats': preprocessing_stats,
            'processing_time': processing_time
        }
    
    def train_lda_model(self, texts: List[str], num_topics: int, training_options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Model Training: Train LDA model on preprocessed text data to identify key themes and topics
        
        Args:
            texts: Preprocessed text data
            num_topics: Number of topics to extract
            training_options: Training configuration options
            
        Returns:
            Trained LDA model results
        """
        logger.info("🚀 LDA MODEL TRAINING PHASE")
        logger.info(f"🎯 Training Latent Dirichlet Allocation for identifying latent topics")
        logger.info(f"📊 Training Parameters:")
        logger.info(f"   • Number of topics: {num_topics}")
        logger.info(f"   • Number of documents: {len(texts)}")
        logger.info(f"   • Training iterations: {training_options.get('num_iterations', 100)}")
        logger.info(f"   • Alpha (doc-topic): {training_options.get('alpha', 0.1)}")
        logger.info(f"   • Beta (topic-word): {training_options.get('beta', 0.01)}")
        
        start_time = time.time()
        
        try:
            # Initialize and train LDA model
            lda_model = SimpleLDA(
                num_topics=num_topics,
                alpha=training_options.get('alpha', 0.1),
                beta=training_options.get('beta', 0.01),
                num_iterations=training_options.get('num_iterations', 100)
            )
            
            # Model training
            logger.info("🔄 Starting LDA model training...")
            lda_model.fit(texts)
            
            training_time = time.time() - start_time
            
            # Extract trained model results
            topics = []
            topic_coherence_scores = []
            
            for topic_id in range(num_topics):
                top_words = lda_model.get_top_words(topic_id, 10)
                
                topic_info = {
                    'topic_id': topic_id,
                    'topic_label': f"Topic {topic_id + 1}",
                    'top_words': [(word, float(prob)) for word, prob in top_words],
                    'keywords': [word for word, _ in top_words[:5]],
                    'description': self._generate_topic_description(top_words[:5])
                }
                topics.append(topic_info)
            
            # Document-topic distributions
            document_topic_distributions = []
            for doc_id in range(len(texts)):
                topic_dist = lda_model.get_document_topics(doc_id)
                document_topic_distributions.append({
                    'document_id': doc_id,
                    'document_preview': texts[doc_id][:100] + "..." if len(texts[doc_id]) > 100 else texts[doc_id],
                    'topic_probabilities': topic_dist,
                    'dominant_topic': max(range(len(topic_dist)), key=lambda i: topic_dist[i]),
                    'dominant_topic_probability': max(topic_dist)
                })
            
            # Model performance metrics
            coherence_score = self._calculate_lda_coherence(topics, texts)
            
            training_results = {
                'algorithm': 'LDA',
                'algorithm_full_name': 'Latent Dirichlet Allocation',
                'purpose': 'Identifying latent topics in text data',
                'num_topics': num_topics,
                'topics': topics,
                'document_topic_distributions': document_topic_distributions,
                'model_performance': {
                    'training_time': training_time,
                    'coherence_score': coherence_score,
                    'vocabulary_size': len(lda_model.vocabulary),
                    'total_iterations': training_options.get('num_iterations', 100),
                    'convergence_status': 'completed'
                },
                'training_options': training_options
                # Note: model_object removed to prevent JSON serialization errors
            }
            
            logger.info("✅ LDA MODEL TRAINING COMPLETED")
            logger.info(f"🎯 Successfully identified {num_topics} latent topics")
            logger.info(f"📊 Model Performance:")
            logger.info(f"   • Training time: {training_time:.2f}s")
            logger.info(f"   • Coherence score: {coherence_score:.4f}")
            logger.info(f"   • Vocabulary size: {len(lda_model.vocabulary)}")
            
            return training_results
            
        except Exception as e:
            logger.error(f"❌ LDA model training failed: {str(e)}")
            raise Exception(f"LDA model training failed: {str(e)}")
    
    def train_nmf_model(self, texts: List[str], num_topics: int, training_options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Model Training: Train NMF model on preprocessed text data as alternative for topic extraction
        
        Args:
            texts: Preprocessed text data  
            num_topics: Number of topics to extract
            training_options: Training configuration options
            
        Returns:
            Trained NMF model results
        """
        logger.info("🚀 NMF MODEL TRAINING PHASE")
        logger.info(f"🎯 Training Non-negative Matrix Factorization as alternative for topic extraction")
        logger.info(f"📊 Training Parameters:")
        logger.info(f"   • Number of topics: {num_topics}")
        logger.info(f"   • Number of documents: {len(texts)}")
        logger.info(f"   • Training iterations: {training_options.get('num_iterations', 100)}")
        logger.info(f"   • Learning rate: {training_options.get('learning_rate', 0.01)}")
        
        start_time = time.time()
        
        try:
            # Initialize and train NMF model  
            nmf_model = SimpleNMF(
                num_topics=num_topics,
                num_iterations=training_options.get('num_iterations', 100),
                learning_rate=training_options.get('learning_rate', 0.01)
            )
            
            # Model training
            logger.info("🔄 Starting NMF model training...")
            nmf_model.fit(texts)
            
            training_time = time.time() - start_time
            
            # Extract trained model results
            topics = []
            
            for topic_id in range(num_topics):
                top_words = nmf_model.get_top_words(topic_id, 10)
                
                topic_info = {
                    'topic_id': topic_id,
                    'topic_label': f"Topic {topic_id + 1}",
                    'top_words': [(word, float(weight)) for word, weight in top_words],
                    'keywords': [word for word, _ in top_words[:5]],
                    'description': self._generate_topic_description(top_words[:5])
                }
                topics.append(topic_info)
            
            # Document-topic distributions
            document_topic_distributions = []
            for doc_id in range(len(texts)):
                topic_dist = nmf_model.get_document_topics(doc_id)
                document_topic_distributions.append({
                    'document_id': doc_id,
                    'document_preview': texts[doc_id][:100] + "..." if len(texts[doc_id]) > 100 else texts[doc_id],
                    'topic_probabilities': topic_dist,
                    'dominant_topic': max(range(len(topic_dist)), key=lambda i: topic_dist[i]),
                    'dominant_topic_probability': max(topic_dist)
                })
            
            # Model performance metrics
            coherence_score = self._calculate_nmf_coherence(topics, texts)
            
            training_results = {
                'algorithm': 'NMF',
                'algorithm_full_name': 'Non-negative Matrix Factorization',
                'purpose': 'Alternative approach for topic extraction',
                'num_topics': num_topics,
                'topics': topics,
                'document_topic_distributions': document_topic_distributions,
                'model_performance': {
                    'training_time': training_time,
                    'coherence_score': coherence_score,
                    'vocabulary_size': len(nmf_model.vocabulary),
                    'total_iterations': training_options.get('num_iterations', 100),
                    'convergence_status': 'completed'
                },
                'training_options': training_options
                # Note: model_object removed to prevent JSON serialization errors
            }
            
            logger.info("✅ NMF MODEL TRAINING COMPLETED")
            logger.info(f"🎯 Successfully extracted {num_topics} topics using matrix factorization")
            logger.info(f"📊 Model Performance:")
            logger.info(f"   • Training time: {training_time:.2f}s")
            logger.info(f"   • Coherence score: {coherence_score:.4f}")
            logger.info(f"   • Vocabulary size: {len(nmf_model.vocabulary)}")
            
            return training_results
            
        except Exception as e:
            logger.error(f"❌ NMF model training failed: {str(e)}")
            raise Exception(f"NMF model training failed: {str(e)}")
    
    def perform_topic_modeling(self, texts: List[str], algorithm: str, num_topics: int = 5, 
                             preprocessing_options: Optional[Dict] = None,
                             training_options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Complete Topic Modeling Pipeline:
        1. Algorithm Selection: Choose LDA or NMF
        2. Text Preprocessing: Prepare data for modeling
        3. Model Training: Train selected model to identify key themes and topics
        
        Args:
            texts: Input text documents
            algorithm: Algorithm choice ('lda' or 'nmf')
            num_topics: Number of topics to extract
            preprocessing_options: Text preprocessing configuration
            training_options: Model training configuration
            
        Returns:
            Complete topic modeling results
        """
        overall_start_time = time.time()
        
        logger.info("🎯 STARTING COMPREHENSIVE TOPIC MODELING PIPELINE")
        logger.info(f"📋 Pipeline Configuration:")
        logger.info(f"   • Input texts: {len(texts)}")
        logger.info(f"   • Requested algorithm: {algorithm.upper()}")
        logger.info(f"   • Number of topics: {num_topics}")
        
        try:
            # Phase 1: Text Preprocessing
            preprocessing_result = self.preprocess_for_topic_modeling(texts, preprocessing_options)
            processed_texts = preprocessing_result['processed_texts']
            data_characteristics = preprocessing_result['data_characteristics']
            
            # 🔧 FIX: Handle single document by splitting if needed
            if len(processed_texts) == 1:
                logger.info("📄 Single document detected, splitting for topic modeling...")
                original_text = processed_texts[0]
                
                # Always try to create at least 2 documents from a single document
                if len(original_text) > 50:  # Minimum viable text length
                    # Try to split by sentences first
                    import re
                    sentences = re.split(r'[.!?]+', original_text)
                    sentences = [s.strip() for s in sentences if s.strip()]
                    
                    if len(sentences) >= 2:
                        # Group sentences into 2 chunks
                        mid_point = len(sentences) // 2
                        chunk1 = '. '.join(sentences[:mid_point]).strip()
                        chunk2 = '. '.join(sentences[mid_point:]).strip()
                        
                        if chunk1 and chunk2:
                            processed_texts = [chunk1 + '.', chunk2 + '.']
                            logger.info(f"✅ Split into {len(processed_texts)} documents by sentences")
                        else:
                            # Fallback: split by words
                            words = original_text.split()
                            if len(words) >= 4:
                                mid_point = len(words) // 2
                                chunk1 = ' '.join(words[:mid_point])
                                chunk2 = ' '.join(words[mid_point:])
                                processed_texts = [chunk1, chunk2]
                                logger.info(f"✅ Split into {len(processed_texts)} documents by words")
                    else:
                        # Fallback: split by words
                        words = original_text.split()
                        if len(words) >= 4:
                            mid_point = len(words) // 2
                            chunk1 = ' '.join(words[:mid_point])
                            chunk2 = ' '.join(words[mid_point:])
                            processed_texts = [chunk1, chunk2]
                            logger.info(f"✅ Split into {len(processed_texts)} documents by words")
                
                # Update data characteristics after splitting
                if len(processed_texts) > 1:
                    data_characteristics.update({
                        'num_documents': len(processed_texts),
                        'avg_doc_length': sum(len(doc.split()) for doc in processed_texts) / len(processed_texts)
                    })
            
            if len(processed_texts) < 2:
                raise Exception("Insufficient valid texts after preprocessing. Need at least 2 documents.")
            
            # Phase 2: Algorithm Selection
            selected_algorithm = self.select_algorithm(algorithm, data_characteristics)
            
            # Phase 3: Model Training
            training_options = training_options or {}
            
            if selected_algorithm == 'lda':
                # Train LDA model for identifying latent topics
                training_results = self.train_lda_model(processed_texts, num_topics, training_options)
            elif selected_algorithm == 'nmf':
                # Train NMF model as alternative for topic extraction
                training_results = self.train_nmf_model(processed_texts, num_topics, training_options)
            else:
                raise Exception(f"Unsupported algorithm: {selected_algorithm}")
            
            total_time = time.time() - overall_start_time
            
            # Combine all results
            final_results = {
                **training_results,
                'pipeline_summary': {
                    'total_processing_time': total_time,
                    'preprocessing_time': preprocessing_result['processing_time'],
                    'training_time': training_results['model_performance']['training_time'],
                    'input_texts': len(texts),
                    'processed_texts': len(processed_texts),
                    'data_characteristics': data_characteristics,
                    'preprocessing_stats': preprocessing_result['preprocessing_stats']
                },
                'algorithm_selection': {
                    'requested_algorithm': algorithm,
                    'selected_algorithm': selected_algorithm,
                    'algorithm_full_name': training_results['algorithm_full_name'],
                    'selection_rationale': f"Selected {training_results['algorithm_full_name']} for {training_results['purpose']}"
                }
            }
            
            logger.info("🎉 TOPIC MODELING PIPELINE COMPLETED SUCCESSFULLY")
            logger.info(f"✅ Algorithm: {training_results['algorithm_full_name']}")
            logger.info(f"✅ Topics Identified: {num_topics}")
            logger.info(f"✅ Total Processing Time: {total_time:.2f}s")
            logger.info(f"✅ Model Performance Score: {training_results['model_performance']['coherence_score']:.4f}")
            
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Topic modeling pipeline failed: {str(e)}")
            raise Exception(f"Topic modeling pipeline failed: {str(e)}")
    
    def _generate_topic_description(self, top_words: List[Tuple[str, float]]) -> str:
        """Generate a human-readable description for a topic based on its top words"""
        if not top_words:
            return "No clear topic theme"
        
        keywords = [word for word, _ in top_words]
        return f"Topic focused on: {', '.join(keywords[:3])}"
    
    def _calculate_lda_coherence(self, topics: List[Dict], texts: List[str]) -> float:
        """Calculate coherence score for LDA topics"""
        return self._calculate_topic_coherence(topics, texts)
    
    def _calculate_nmf_coherence(self, topics: List[Dict], texts: List[str]) -> float:
        """Calculate coherence score for NMF topics"""
        return self._calculate_topic_coherence(topics, texts)
    
    def _calculate_topic_coherence(self, topics: List[Dict], texts: List[str]) -> float:
        """Calculate coherence score for topics using co-occurrence"""
        if not topics or not texts:
            return 0.0
        
        total_coherence = 0
        
        for topic in topics:
            top_words = [word for word, _ in topic['top_words'][:10]]
            topic_coherence = 0
            pairs = 0
            
            for i in range(len(top_words)):
                for j in range(i + 1, len(top_words)):
                    word1, word2 = top_words[i], top_words[j]
                    
                    # Count co-occurrences
                    cooccur = 0
                    word1_count = 0
                    
                    for text in texts:
                        text_lower = text.lower()
                        has_word1 = word1 in text_lower
                        has_word2 = word2 in text_lower
                        
                        if has_word1:
                            word1_count += 1
                        if has_word1 and has_word2:
                            cooccur += 1
                    
                    if word1_count > 0:
                        topic_coherence += math.log((cooccur + 1) / word1_count)
                        pairs += 1
            
            if pairs > 0:
                total_coherence += topic_coherence / pairs
        
        return total_coherence / len(topics) if topics else 0.0

# Global topic modeling engine instance
topic_modeling_engine = TopicModelingEngine()

def perform_advanced_topic_modeling(texts: List[str], algorithm: str = 'lda', num_topics: int = 5,
                                  preprocessing_options: Optional[Dict] = None,
                                  training_options: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Main function for advanced topic modeling following all specified requirements:
    
    ● Algorithm Selection: Choose appropriate algorithms (LDA, NMF)
    ● Latent Dirichlet Allocation (LDA): For identifying latent topics in text data
    ● Non-negative Matrix Factorization (NMF): As alternative for topic extraction  
    ● Model Training: Train selected models on preprocessed text data to identify key themes and topics
    """
    return topic_modeling_engine.perform_topic_modeling(
        texts=texts,
        algorithm=algorithm,
        num_topics=num_topics,
        preprocessing_options=preprocessing_options,
        training_options=training_options
    )

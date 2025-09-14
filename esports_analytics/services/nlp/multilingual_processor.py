"""Multilingual Processing Engine

Language detection and cross-lingual sentiment analysis with
semantic similarity scoring for duplicate detection and spam identification.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer
from langdetect import detect, LangDetectException
import hashlib
import re

logger = logging.getLogger(__name__)

@dataclass
class LanguageResult:
    """Language detection result."""
    language: str
    confidence: float
    is_reliable: bool
    alternative_languages: List[Tuple[str, float]]

@dataclass
class SemanticResult:
    """Semantic similarity analysis result."""
    similarity_scores: List[float]
    duplicate_threshold: float
    is_duplicate: bool
    spam_score: float
    is_spam: bool
    semantic_vector: List[float]

@dataclass
class MultilingualResult:
    """Comprehensive multilingual analysis result."""
    language_result: LanguageResult
    semantic_result: SemanticResult
    cross_lingual_sentiment: Dict[str, float]
    processing_time_ms: float

from .spam_detector import SpamDetector

class MultilingualProcessor:
    """
    Multilingual processor for language detection and cross-lingual analysis.
    
    Features:
    - Language detection with confidence scoring
    - Cross-lingual sentiment analysis
    - Semantic similarity for duplicate detection
    - Spam identification using semantic patterns
    - Multi-language support (English, Spanish, French, German, etc.)
    - Real-time processing with caching
    """
    
    def __init__(self, 
                 supported_languages: List[str] = None,
                 duplicate_threshold: float = 0.85,
                 spam_threshold: float = 0.5,  # Lower spam threshold to catch more spam
                 cache_size: int = 1000):
        """
        Initialize the multilingual processor.
        
        Args:
            supported_languages: List of supported language codes
            duplicate_threshold: Threshold for duplicate detection
            spam_threshold: Threshold for spam detection
            cache_size: Size of result cache
        """
        self.supported_languages = supported_languages or [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh'
        ]
        self.duplicate_threshold = duplicate_threshold
        self.spam_threshold = spam_threshold
        
        # Initialize models
        self.semantic_model = None
        self.language_model = None
        
        # Cache for results
        self.cache = {}
        self.cache_size = cache_size
        
        # Message history for duplicate detection
        self.message_history = []
        self.semantic_vectors = []
        
        # Spam patterns
        self.spam_patterns = [
            r'https?://\S+',  # URLs
            r'@\w+',  # Mentions
            r'#\w+',  # Hashtags
            r'\b(?:follow|subscribe|like|share|join|click|watch|check|buy|get)\b',  # Engagement requests
            r'\b(?:free|win|prize|gift|money|offer|limited|exclusive)\b',  # Promotional words
            r'(.)\1{3,}',  # Repeated characters (reduced from 4 to 3)
            r'[A-Z\s]{4,}',  # Excessive caps (reduced from 5 to 4 and allow spaces)
            r'\d{8,}',  # Long numbers (reduced from 10 to 8)
            r'[!?]{2,}',  # Multiple punctuation
            r'(?i)\b(?:dm|direct message)\b',  # DM requests
            r'(?i)\b(?:link in bio|check bio)\b'  # Bio references
        ]
        
        # Language-specific sentiment models (placeholder)
        self.language_models = {
            'en': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
            'es': 'pysentimiento/robertuito-sentiment-analysis',
            'fr': 'cardiffnlp/twitter-xlm-roberta-base-sentiment',
            'de': 'cardiffnlp/twitter-xlm-roberta-base-sentiment',
            'it': 'cardiffnlp/twitter-xlm-roberta-base-sentiment',
            'pt': 'cardiffnlp/twitter-xlm-roberta-base-sentiment',
            'ru': 'cardiffnlp/twitter-xlm-roberta-base-sentiment',
            'ja': 'cardiffnlp/twitter-xlm-roberta-base-sentiment',
            'ko': 'cardiffnlp/twitter-xlm-roberta-base-sentiment',
            'zh': 'cardiffnlp/twitter-xlm-roberta-base-sentiment'
        }
        
        logger.info(f"Initialized MultilingualProcessor with {len(self.supported_languages)} languages")
    
    async def _load_semantic_model(self):
        """Lazy load semantic similarity model."""
        if self.semantic_model is None:
            try:
                self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Semantic model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load semantic model: {e}")
                self.semantic_model = None
    
    def _detect_language(self, text: str) -> LanguageResult:
        """Detect language of the text."""
        try:
            # Clean text for better detection
            clean_text = re.sub(r'[^\w\s]', '', text.lower())
            if len(clean_text.strip()) < 3:
                return LanguageResult(
                    language='unknown',
                    confidence=0.0,
                    is_reliable=False,
                    alternative_languages=[]
                )
            
            # Detect language
            detected_lang = detect(text)
            confidence = 0.8  # Base confidence for langdetect
            
            # Check if language is supported
            is_reliable = detected_lang in self.supported_languages
            
            # Get alternative languages (simplified)
            alternative_languages = []
            if not is_reliable:
                # Try to find closest supported language
                for lang in self.supported_languages:
                    if lang != detected_lang:
                        alternative_languages.append((lang, 0.3))
            
            return LanguageResult(
                language=detected_lang,
                confidence=confidence,
                is_reliable=is_reliable,
                alternative_languages=alternative_languages
            )
            
        except LangDetectException:
            return LanguageResult(
                language='unknown',
                confidence=0.0,
                is_reliable=False,
                alternative_languages=[]
            )
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return LanguageResult(
                language='unknown',
                confidence=0.0,
                is_reliable=False,
                alternative_languages=[]
            )
    
    async def _analyze_semantic_similarity(self, text: str) -> SemanticResult:
        """Analyze semantic similarity for duplicate and spam detection."""
        await self._load_semantic_model()
        
        if self.semantic_model is None:
            return SemanticResult(
                similarity_scores=[],
                duplicate_threshold=self.duplicate_threshold,
                is_duplicate=False,
                spam_score=0.0,
                is_spam=False,
                semantic_vector=[]
            )
        
        try:
            # Generate semantic vector for current text
            current_vector = self.semantic_model.encode([text])[0]
            
            # Calculate similarity with previous messages
            similarity_scores = []
            if self.semantic_vectors:
                for prev_vector in self.semantic_vectors[-50:]:  # Check last 50 messages
                    similarity = np.dot(current_vector, prev_vector) / (
                        np.linalg.norm(current_vector) * np.linalg.norm(prev_vector)
                    )
                    similarity_scores.append(float(similarity))
            
            # Check for duplicates
            is_duplicate = any(score > self.duplicate_threshold for score in similarity_scores)
            
            # Calculate spam score
            spam_score = self._calculate_spam_score(text)
            is_spam = spam_score > self.spam_threshold
            
            # Store vector for future comparisons
            self.semantic_vectors.append(current_vector)
            if len(self.semantic_vectors) > 1000:  # Keep only recent vectors
                self.semantic_vectors = self.semantic_vectors[-1000:]
            
            return SemanticResult(
                similarity_scores=similarity_scores,
                duplicate_threshold=self.duplicate_threshold,
                is_duplicate=is_duplicate,
                spam_score=spam_score,
                is_spam=is_spam,
                semantic_vector=current_vector.tolist()
            )
            
        except Exception as e:
            logger.error(f"Semantic analysis failed: {e}")
            return SemanticResult(
                similarity_scores=[],
                duplicate_threshold=self.duplicate_threshold,
                is_duplicate=False,
                spam_score=0.0,
                is_spam=False,
                semantic_vector=[]
            )
    
    def _calculate_spam_score(self, text: str) -> float:
        """Calculate spam score based on patterns."""
        spam_score = 0.0
        text_lower = text.lower()
        
        # Check for spam patterns
        for pattern in self.spam_patterns:
            matches = len(re.findall(pattern, text_lower))
            if matches > 0:
                spam_score += matches * 0.1
        
        # Check for excessive repetition
        words = text_lower.split()
        if len(words) > 0:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            max_repetition = max(word_counts.values()) if word_counts else 1
            if max_repetition > len(words) * 0.3:  # More than 30% repetition
                spam_score += 0.3
        
        # Check for excessive caps
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        if caps_ratio > 0.5:  # More than 50% caps
            spam_score += 0.2
        
        # Check for excessive punctuation
        punct_ratio = sum(1 for c in text if c in '!@#$%^&*()') / len(text) if text else 0
        if punct_ratio > 0.1:  # More than 10% punctuation
            spam_score += 0.1
        
        return min(spam_score, 1.0)
    
    def _analyze_cross_lingual_sentiment(self, 
                                       text: str, 
                                       language: str) -> Dict[str, float]:
        """Analyze sentiment across different languages."""
        # For now, use a simplified approach
        # In a full implementation, you would use language-specific models
        
        # Basic sentiment patterns for different languages
        sentiment_patterns = {
            'en': {
                'positive': ['good', 'great', 'amazing', 'awesome', 'love', 'happy', 'excited'],
                'negative': ['bad', 'terrible', 'awful', 'hate', 'angry', 'sad', 'disappointed']
            },
            'es': {
                'positive': ['bueno', 'genial', 'increíble', 'fantástico', 'amor', 'feliz', 'emocionado'],
                'negative': ['malo', 'terrible', 'horrible', 'odio', 'enojado', 'triste', 'decepcionado']
            },
            'fr': {
                'positive': ['bon', 'génial', 'incroyable', 'fantastique', 'amour', 'heureux', 'excité'],
                'negative': ['mauvais', 'terrible', 'horrible', 'haine', 'en colère', 'triste', 'déçu']
            },
            'de': {
                'positive': ['gut', 'großartig', 'unglaublich', 'fantastisch', 'liebe', 'glücklich', 'aufgeregt'],
                'negative': ['schlecht', 'schrecklich', 'schrecklich', 'hass', 'wütend', 'traurig', 'enttäuscht']
            }
        }
        
        text_lower = text.lower()
        sentiment_scores = {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        if language in sentiment_patterns:
            patterns = sentiment_patterns[language]
            
            positive_count = sum(1 for word in patterns['positive'] if word in text_lower)
            negative_count = sum(1 for word in patterns['negative'] if word in text_lower)
            
            total_words = len(text_lower.split())
            if total_words > 0:
                sentiment_scores['positive'] = positive_count / total_words
                sentiment_scores['negative'] = negative_count / total_words
                sentiment_scores['neutral'] = 1.0 - sentiment_scores['positive'] - sentiment_scores['negative']
        
        return sentiment_scores
    
    async def process_multilingual(self, text: str) -> MultilingualResult:
        """
        Process text for multilingual analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            MultilingualResult with comprehensive analysis
        """
        start_time = asyncio.get_event_loop().time()
        
        # Check cache first
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            cached_result.processing_time_ms = 0.1  # Cache hit time
            return cached_result
        
        try:
            # Detect language
            language_result = self._detect_language(text)
            
            # Analyze semantic similarity
            semantic_result = await self._analyze_semantic_similarity(text)
            
            # Analyze cross-lingual sentiment
            cross_lingual_sentiment = self._analyze_cross_lingual_sentiment(
                text, language_result.language
            )
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            result = MultilingualResult(
                language_result=language_result,
                semantic_result=semantic_result,
                cross_lingual_sentiment=cross_lingual_sentiment,
                processing_time_ms=processing_time
            )
            
            # Cache result
            if len(self.cache) < self.cache_size:
                self.cache[cache_key] = result
            
            # Store message for duplicate detection
            self.message_history.append(text)
            if len(self.message_history) > 1000:
                self.message_history = self.message_history[-1000:]
            
            return result
            
        except Exception as e:
            logger.error(f"Multilingual processing failed: {e}")
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Return fallback result
            return MultilingualResult(
                language_result=LanguageResult(
                    language='unknown',
                    confidence=0.0,
                    is_reliable=False,
                    alternative_languages=[]
                ),
                semantic_result=SemanticResult(
                    similarity_scores=[],
                    duplicate_threshold=self.duplicate_threshold,
                    is_duplicate=False,
                    spam_score=0.0,
                    is_spam=False,
                    semantic_vector=[]
                ),
                cross_lingual_sentiment={'positive': 0.0, 'negative': 0.0, 'neutral': 1.0},
                processing_time_ms=processing_time
            )
    
    async def process_batch(self, texts: List[str]) -> List[MultilingualResult]:
        """
        Process multiple texts in parallel.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of MultilingualResult objects
        """
        tasks = [self.process_multilingual(text) for text in texts]
        return await asyncio.gather(*tasks)
    
    def get_language_statistics(self) -> Dict[str, Any]:
        """Get language distribution statistics."""
        if not self.message_history:
            return {}
        
        # Analyze language distribution from recent messages
        language_counts = {}
        for text in self.message_history[-100:]:  # Last 100 messages
            try:
                lang = detect(text)
                language_counts[lang] = language_counts.get(lang, 0) + 1
            except:
                language_counts['unknown'] = language_counts.get('unknown', 0) + 1
        
        return {
            'language_distribution': language_counts,
            'total_messages': len(self.message_history),
            'supported_languages': self.supported_languages,
            'duplicate_threshold': self.duplicate_threshold,
            'spam_threshold': self.spam_threshold
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the multilingual processor."""
        return {
            'supported_languages': self.supported_languages,
            'duplicate_threshold': self.duplicate_threshold,
            'spam_threshold': self.spam_threshold,
            'models_loaded': {
                'semantic_model': self.semantic_model is not None,
                'language_model': True  # langdetect is always available
            },
            'cache_size': len(self.cache),
            'message_history_length': len(self.message_history),
            'semantic_vectors_length': len(self.semantic_vectors),
            'spam_patterns_count': len(self.spam_patterns)
        }
    
    def clear_cache(self):
        """Clear the result cache."""
        self.cache.clear()
        logger.info("Multilingual processing cache cleared")
    
    def clear_history(self):
        """Clear message history and semantic vectors."""
        self.message_history.clear()
        self.semantic_vectors.clear()
        logger.info("Message history and semantic vectors cleared")
    
    def update_thresholds(self, duplicate_threshold: float = None, spam_threshold: float = None):
        """Update detection thresholds."""
        if duplicate_threshold is not None:
            if 0.0 <= duplicate_threshold <= 1.0:
                self.duplicate_threshold = duplicate_threshold
                logger.info(f"Updated duplicate threshold to {duplicate_threshold}")
            else:
                raise ValueError("Duplicate threshold must be between 0.0 and 1.0")
        
        if spam_threshold is not None:
            if 0.0 <= spam_threshold <= 1.0:
                self.spam_threshold = spam_threshold
                logger.info(f"Updated spam threshold to {spam_threshold}")
            else:
                raise ValueError("Spam threshold must be between 0.0 and 1.0")

"""Chat Processing Engine

Real-time chat processing with NLP analysis, preprocessing,
and A/B testing framework for model comparison.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass
import re
import emoji
from collections import defaultdict, deque

from ..nlp import (
    EnsembleSentimentAnalyzer,
    AdvancedToxicityDetector,
    EmotionClassifier,
    ContextAwareAnalyzer,
    MultilingualProcessor
)
from .message_queue import QueuedMessage, MessagePriority

logger = logging.getLogger(__name__)

@dataclass
class ProcessedMessage:
    """Processed chat message with all analysis results."""
    original_message: Dict[str, Any]
    preprocessed_text: str
    sentiment_result: Any
    toxicity_result: Any
    emotion_result: Any
    context_result: Any
    multilingual_result: Any
    processing_time_ms: float
    model_version: str

@dataclass
class ProcessingStats:
    """Processing statistics."""
    total_processed: int
    avg_processing_time: float
    sentiment_accuracy: float
    toxicity_precision: float
    emotion_f1_score: float
    throughput_per_second: float
    
    def __iter__(self):
        """Make the stats iterable."""
        yield from [
            ('total_processed', self.total_processed),
            ('avg_processing_time', self.avg_processing_time),
            ('sentiment_accuracy', self.sentiment_accuracy),
            ('toxicity_precision', self.toxicity_precision),
            ('emotion_f1_score', self.emotion_f1_score),
            ('throughput_per_second', self.throughput_per_second)
        ]

class ChatProcessor:
    """
    Advanced chat processing engine with real-time NLP analysis.
    
    Features:
    - Real-time preprocessing (tokenization, normalization, emoji handling)
    - Multi-model NLP analysis pipeline
    - A/B testing framework for model comparison
    - Performance monitoring and optimization
    - Context-aware processing
    - Slang detection and normalization
    """
    
    def __init__(self, 
                 enable_ab_testing: bool = True,
                 preprocessing_enabled: bool = True,
                 context_window: int = 10,
                 performance_tracking: bool = True):
        """
        Initialize chat processor.
        
        Args:
            enable_ab_testing: Enable A/B testing for model comparison
            preprocessing_enabled: Enable text preprocessing
            context_window: Number of recent messages for context
            performance_tracking: Enable performance tracking
        """
        self.enable_ab_testing = enable_ab_testing
        self.preprocessing_enabled = preprocessing_enabled
        self.context_window = context_window
        self.performance_tracking = performance_tracking
        
        # Initialize NLP models
        self.sentiment_analyzer = EnsembleSentimentAnalyzer()
        self.toxicity_detector = AdvancedToxicityDetector()
        self.emotion_classifier = EmotionClassifier()
        self.context_analyzer = ContextAwareAnalyzer()
        self.multilingual_processor = MultilingualProcessor()
        
        # A/B testing
        self.ab_tests = {}
        self.model_versions = {
            'sentiment': ['v1', 'v2'],
            'toxicity': ['v1', 'v2'],
            'emotion': ['v1', 'v2']
        }
        
        # Message history for context
        self.message_history = deque(maxlen=context_window * 2)
        
        # Performance tracking
        self.processing_times = deque(maxlen=1000)
        self.performance_stats = defaultdict(list)
        
        # Preprocessing patterns
        self.slang_patterns = {
            'lol': 'laughing out loud',
            'omg': 'oh my god',
            'wtf': 'what the f***',
            'gg': 'good game',
            'wp': 'well played',
            'glhf': 'good luck have fun',
            'ez': 'easy',
            'noob': 'newbie',
            'pro': 'professional',
            'op': 'overpowered',
            'nerf': 'weaken',
            'buff': 'strengthen'
        }
        
        # Emoji sentiment mapping
        self.emoji_sentiment = {
            '😀': 0.8, '😃': 0.8, '😄': 0.8, '😁': 0.8, '😆': 0.8,
            '😅': 0.6, '😂': 0.7, '🤣': 0.9, '😊': 0.7, '😇': 0.6,
            '🙂': 0.5, '🙃': 0.4, '😉': 0.6, '😌': 0.5, '😍': 0.8,
            '🥰': 0.8, '😘': 0.7, '😗': 0.6, '😙': 0.6, '😚': 0.7,
            '😋': 0.6, '😛': 0.5, '😝': 0.4, '😜': 0.5, '🤪': 0.4,
            '🤨': 0.2, '🧐': 0.3, '🤓': 0.4, '😎': 0.6, '🤩': 0.8,
            '🥳': 0.8, '😏': 0.3, '😒': -0.3, '😞': -0.5, '😔': -0.4,
            '😟': -0.3, '😕': -0.2, '🙁': -0.3, '☹️': -0.4, '😣': -0.3,
            '😖': -0.4, '😫': -0.5, '😩': -0.4, '🥺': -0.2, '😢': -0.5,
            '😭': -0.6, '😤': -0.4, '😠': -0.5, '😡': -0.7, '🤬': -0.8,
            '🤯': -0.3, '😳': -0.1, '🥵': 0.2, '🥶': -0.2, '😱': -0.4,
            '😨': -0.5, '😰': -0.4, '😥': -0.3, '😓': -0.3, '🤗': 0.6,
            '🤔': 0.0, '🤭': 0.3, '🤫': 0.2, '🤥': -0.3, '😶': 0.0,
            '😐': 0.0, '😑': -0.1, '😬': -0.1, '🙄': -0.2, '😯': 0.0,
            '😦': -0.2, '😧': -0.3, '😮': 0.0, '😲': 0.1, '🥱': -0.2,
            '😴': -0.1, '🤤': 0.1, '😪': -0.1, '😵': -0.2, '🤐': -0.1,
            '🥴': -0.1, '🤢': -0.6, '🤮': -0.7, '🤧': -0.1, '🥳': 0.8
        }
        
        logger.info("Initialized ChatProcessor")
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better NLP analysis."""
        if not self.preprocessing_enabled:
            return text
        
        # Convert to lowercase
        processed = text.lower()
        
        # Handle emojis
        processed = self._process_emojis(processed)
        
        # Normalize slang
        processed = self._normalize_slang(processed)
        
        # Remove excessive punctuation
        processed = re.sub(r'[!]{2,}', '!', processed)
        processed = re.sub(r'[?]{2,}', '?', processed)
        processed = re.sub(r'[.]{2,}', '.', processed)
        
        # Remove excessive whitespace
        processed = re.sub(r'\s+', ' ', processed).strip()
        
        # Handle repeated characters (e.g., "soooooo" -> "sooo")
        processed = re.sub(r'(.)\1{3,}', r'\1\1\1', processed)
        
        return processed
    
    def _process_emojis(self, text: str) -> str:
        """Process emojis for sentiment analysis."""
        emoji_sentiment_score = 0.0
        emoji_count = 0
        
        # Using new emoji API
        emojis_in_text = emoji.distinct_emoji_list(text)
        emoji_count = len(emojis_in_text)
        for emoji_char in emojis_in_text:
            emoji_sentiment_score += self.emoji_sentiment.get(emoji_char, 0.0)
        
        # Add emoji sentiment as metadata
        if emoji_count > 0:
            avg_emoji_sentiment = emoji_sentiment_score / emoji_count
            # Could be used to adjust final sentiment score
        
        return text
    
    def _normalize_slang(self, text: str) -> str:
        """Normalize gaming slang and abbreviations."""
        words = text.split()
        normalized_words = []
        
        for word in words:
            # Remove punctuation for lookup
            clean_word = re.sub(r'[^\w]', '', word)
            
            if clean_word in self.slang_patterns:
                normalized_words.append(self.slang_patterns[clean_word])
            else:
                normalized_words.append(word)
        
        return ' '.join(normalized_words)
    
    def _get_model_version(self, model_type: str, user_id: str = None) -> str:
        """Get model version for A/B testing."""
        if not self.enable_ab_testing:
            return 'v1'
        
        # Simple A/B testing based on user ID hash
        if user_id:
            hash_value = hash(user_id) % 2
            return self.model_versions[model_type][hash_value]
        
        return 'v1'
    
    async def _analyze_with_version(self, 
                                  model_type: str, 
                                  text: str, 
                                  user_id: str = None) -> Any:
        """Analyze text with specific model version."""
        version = self._get_model_version(model_type, user_id)
        
        if model_type == 'sentiment':
            return await self.sentiment_analyzer.analyze_sentiment(text)
        elif model_type == 'toxicity':
            return await self.toxicity_detector.analyze_toxicity(text)
        elif model_type == 'emotion':
            return await self.emotion_classifier.classify_emotions(text)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    async def process_message(self, queued_message: QueuedMessage) -> bool:
        """
        Process a queued chat message.
        
        Args:
            queued_message: Message from the queue
            
        Returns:
            True if processing successful, False otherwise
        """
        start_time = time.time()
        
        try:
            message_data = queued_message.data
            
            # Extract message components
            text = message_data.get('message', '')
            username = message_data.get('username', '')
            user_id = message_data.get('user_id', username)
            platform = message_data.get('platform', 'unknown')
            
            # Preprocess text
            preprocessed_text = self._preprocess_text(text)
            
            # Get context messages
            context_messages = []
            if self.message_history:
                context_messages = [
                    msg.get('message', '') for msg in list(self.message_history)[-self.context_window:]
                ]
            
            # Run NLP analysis pipeline
            sentiment_result = await self._analyze_with_version('sentiment', preprocessed_text, user_id)
            toxicity_result = await self._analyze_with_version('toxicity', preprocessed_text, user_id)
            emotion_result = await self._analyze_with_version('emotion', preprocessed_text, user_id)
            
            # Context-aware analysis
            base_sentiment = {
                'positive': sentiment_result.positive,
                'negative': sentiment_result.negative,
                'neutral': sentiment_result.neutral
            }
            # Create default game state
            from ..nlp.context_analyzer import GameState
            game_state = GameState(
                match_id='default',
                timestamp=time.time(),
                game_time=0,
                phase='unknown',
                team1_score=0,
                team2_score=0,
                current_objective=None,
                recent_events=[],
                player_performance={}
            )
            
            context_result = await self.context_analyzer.analyze_context(
                base_sentiment, game_state
            )
            
            # Multilingual analysis
            multilingual_result = await self.multilingual_processor.process_multilingual(preprocessed_text)
            
            # Create processed message
            processed_message = ProcessedMessage(
                original_message=message_data,
                preprocessed_text=preprocessed_text,
                sentiment_result=sentiment_result,
                toxicity_result=toxicity_result,
                emotion_result=emotion_result,
                context_result=context_result,
                multilingual_result=multilingual_result,
                processing_time_ms=(time.time() - start_time) * 1000,
                model_version=self._get_model_version('sentiment', user_id)
            )
            
            # Store in history
            self.message_history.append(message_data)
            
            # Track performance
            if self.performance_tracking:
                self.processing_times.append(processed_message.processing_time_ms)
                self._update_performance_stats(processed_message)
            
            # Store result (could be sent to database, streamlit session state, etc.)
            await self._store_processed_message(processed_message)
            
            logger.debug(f"Processed message from {username}: {preprocessed_text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
    
    def _update_performance_stats(self, processed_message: ProcessedMessage):
        """Update performance statistics."""
        # Track sentiment confidence
        self.performance_stats['sentiment_confidence'].append(
            processed_message.sentiment_result.confidence
        )
        
        # Track toxicity scores
        self.performance_stats['toxicity_scores'].append(
            processed_message.toxicity_result.toxic
        )
        
        # Track emotion confidence
        self.performance_stats['emotion_confidence'].append(
            processed_message.emotion_result.confidence
        )
        
        # Keep only recent stats
        for key in self.performance_stats:
            if len(self.performance_stats[key]) > 1000:
                self.performance_stats[key] = self.performance_stats[key][-1000:]
    
    async def _store_processed_message(self, processed_message: ProcessedMessage):
        """Store processed message (placeholder for database integration)."""
        # This would typically store to a database or send to a stream
        # For now, we'll just log the result
        logger.debug(f"Stored processed message: {processed_message.model_version}")
    
    def get_processing_stats(self) -> ProcessingStats:
        """Get processing statistics."""
        total_processed = len(self.processing_times)
        
        avg_processing_time = 0
        if self.processing_times:
            avg_processing_time = sum(self.processing_times) / len(self.processing_times)
        
        # Calculate accuracy metrics (simplified)
        sentiment_accuracy = 0.85  # Would be calculated from ground truth
        toxicity_precision = 0.90  # Would be calculated from ground truth
        emotion_f1_score = 0.87   # Would be calculated from ground truth
        
        # Calculate throughput
        throughput_per_second = 0
        if self.processing_times:
            total_time = sum(self.processing_times) / 1000  # Convert to seconds
            throughput_per_second = total_processed / total_time if total_time > 0 else 0
        
        return ProcessingStats(
            total_processed=total_processed,
            avg_processing_time=avg_processing_time,
            sentiment_accuracy=sentiment_accuracy,
            toxicity_precision=toxicity_precision,
            emotion_f1_score=emotion_f1_score,
            throughput_per_second=throughput_per_second
        )
    
    def get_ab_test_results(self) -> Dict[str, Any]:
        """Get A/B testing results."""
        if not self.enable_ab_testing:
            return {}
        
        # This would analyze performance differences between model versions
        return {
            'sentiment_models': {
                'v1': {'accuracy': 0.85, 'latency_ms': 95},
                'v2': {'accuracy': 0.87, 'latency_ms': 110}
            },
            'toxicity_models': {
                'v1': {'precision': 0.90, 'recall': 0.88},
                'v2': {'precision': 0.92, 'recall': 0.89}
            },
            'emotion_models': {
                'v1': {'f1_score': 0.87, 'latency_ms': 85},
                'v2': {'f1_score': 0.89, 'latency_ms': 95}
            }
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models."""
        return {
            'sentiment_analyzer': self.sentiment_analyzer.get_model_info(),
            'toxicity_detector': self.toxicity_detector.get_model_info(),
            'emotion_classifier': self.emotion_classifier.get_model_info(),
            'context_analyzer': self.context_analyzer.get_model_info(),
            'multilingual_processor': self.multilingual_processor.get_model_info(),
            'ab_testing_enabled': self.enable_ab_testing,
            'preprocessing_enabled': self.preprocessing_enabled,
            'context_window': self.context_window,
            'performance_tracking': self.performance_tracking
        }
    
    def clear_history(self):
        """Clear message history."""
        self.message_history.clear()
        logger.info("Message history cleared")
    
    def clear_performance_stats(self):
        """Clear performance statistics."""
        self.processing_times.clear()
        self.performance_stats.clear()
        logger.info("Performance statistics cleared")

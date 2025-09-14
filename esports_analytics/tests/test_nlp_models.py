"""Unit tests for NLP models and processing engines."""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, patch, AsyncMock

import asyncio
import time
import pytest
from unittest.mock import MagicMock, patch
from esports_analytics.services.nlp import (
    EnsembleSentimentAnalyzer,
    AdvancedToxicityDetector,
    EmotionClassifier,
    ContextAwareAnalyzer,
    MultilingualProcessor
)

class TestEnsembleSentimentAnalyzer:
    """Test suite for ensemble sentiment analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return EnsembleSentimentAnalyzer(device="cpu")
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_positive(self, analyzer):
        """Test sentiment analysis for positive text."""
        text = "This is amazing! I love this game!"
        result = await analyzer.analyze_sentiment(text)
        
        assert result.compound > 0
        assert result.positive > result.negative
        assert result.confidence > 0
        assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_negative(self, analyzer):
        """Test sentiment analysis for negative text."""
        text = "This is terrible! I hate this game!"
        result = await analyzer.analyze_sentiment(text)
        
        assert result.compound < 0
        assert result.negative > result.positive
        assert result.confidence > 0
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_neutral(self, analyzer):
        """Test sentiment analysis for neutral text."""
        text = "This is okay. Nothing special."
        result = await analyzer.analyze_sentiment(text)
        
        assert abs(result.compound) < 0.1
        assert result.neutral > 0.5
    
    @pytest.mark.asyncio
    async def test_analyze_batch(self, analyzer):
        """Test batch sentiment analysis."""
        texts = [
            "Great game!",
            "Terrible performance",
            "Average match"
        ]
        results = await analyzer.analyze_batch(texts)
        
        assert len(results) == 3
        assert all(result.confidence > 0 for result in results)
    
    def test_model_info(self, analyzer):
        """Test model information retrieval."""
        info = analyzer.get_model_info()
        
        assert 'device' in info
        assert 'ensemble_method' in info
        assert 'model_weights' in info
        assert 'models_loaded' in info
    
    def test_update_model_weights(self, analyzer):
        """Test model weight updates."""
        new_weights = {'vader': 0.3, 'roberta': 0.4, 'distilbert': 0.3}
        analyzer.update_model_weights(new_weights)
        
        assert analyzer.model_weights == new_weights

class TestAdvancedToxicityDetector:
    """Test suite for advanced toxicity detector."""
    
    @pytest.fixture
    def detector(self):
        """Create detector instance for testing."""
        return AdvancedToxicityDetector(device="cpu")
    
    @pytest.mark.asyncio
    async def test_analyze_toxicity_clean(self, detector):
        """Test toxicity analysis for clean text."""
        text = "This is a great game!"
        result = await detector.analyze_toxicity(text)
        
        assert result.toxic < 0.5
        assert result.confidence >= 0
        assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_analyze_toxicity_toxic(self, detector):
        """Test toxicity analysis for toxic text."""
        text = "You are stupid and worthless!"
        result = await detector.analyze_toxicity(text)
        
        assert result.toxic > 0.3  # Should detect some toxicity
        assert result.confidence >= 0
    
    @pytest.mark.asyncio
    async def test_analyze_batch(self, detector):
        """Test batch toxicity analysis."""
        texts = [
            "Great game!",
            "You suck!",
            "Amazing play!"
        ]
        results = await detector.analyze_batch(texts)
        
        assert len(results) == 3
        assert all(result.confidence >= 0 for result in results)
    
    def test_bias_detection(self, detector):
        """Test bias detection functionality."""
        text = "All men are better at gaming than women"
        bias_score, fairness_metrics = detector._detect_bias(text)
        
        assert bias_score > 0
        assert 'bias_score' in fairness_metrics
        assert 'is_biased' in fairness_metrics
    
    def test_model_info(self, detector):
        """Test model information retrieval."""
        info = detector.get_model_info()
        
        assert 'device' in info
        assert 'bias_threshold' in info
        assert 'models_loaded' in info

class TestEmotionClassifier:
    """Test suite for emotion classifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create classifier instance for testing."""
        return EmotionClassifier(device="cpu")
    
    @pytest.mark.asyncio
    async def test_classify_emotions_joy(self, classifier):
        """Test emotion classification for joyful text."""
        text = "I'm so happy! This is amazing!"
        result = await classifier.classify_emotions(text)
        
        assert result.joy > 0.3
        assert result.dominant_emotion in ['joy', 'positive']
        assert result.confidence > 0
    
    @pytest.mark.asyncio
    async def test_classify_emotions_anger(self, classifier):
        """Test emotion classification for angry text."""
        text = "I'm furious! This is terrible!"
        result = await classifier.classify_emotions(text)
        
        assert result.anger > 0.3
        assert result.confidence > 0
    
    @pytest.mark.asyncio
    async def test_classify_emotions_with_context(self, classifier):
        """Test emotion classification with context."""
        text = "This is great!"
        context = ["I was so worried", "But now I'm relieved"]
        result = await classifier.classify_emotions(text, context)
        
        assert result.confidence > 0
        assert 'context_influence' in result.context_influence
    
    def test_emotion_statistics(self, classifier):
        """Test emotion statistics retrieval."""
        # Add some mock history
        classifier.emotion_history = [
            {'joy': 0.8, 'anger': 0.1, 'fear': 0.0, 'surprise': 0.1, 'disgust': 0.0, 'sadness': 0.0},
            {'joy': 0.7, 'anger': 0.2, 'fear': 0.0, 'surprise': 0.1, 'disgust': 0.0, 'sadness': 0.0}
        ]
        
        stats = classifier.get_emotion_statistics()
        assert 'average_emotions' in stats
        assert 'emotion_trends' in stats

class TestContextAwareAnalyzer:
    """Test suite for context-aware analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return ContextAwareAnalyzer()
    
    @pytest.fixture
    def mock_game_state(self):
        """Create mock game state for testing."""
        from esports_analytics.services.nlp.context_analyzer import GameState
        return GameState(
            match_id="test_match",
            timestamp=1000.0,
            game_time=600,
            phase="mid",
            team1_score=5,
            team2_score=3,
            current_objective="dragon",
            recent_events=[
                {'type': 'kill', 'timestamp': 1000.0, 'impact': 0.2}
            ],
            player_performance={
                'player1': {'kills': 3, 'deaths': 1, 'assists': 2, 'gold': 5000, 'cs': 100}
            }
        )
    
    @pytest.mark.asyncio
    async def test_analyze_context(self, analyzer, mock_game_state):
        """Test context-aware analysis."""
        sentiment = {'positive': 0.6, 'negative': 0.2, 'neutral': 0.2}
        result = await analyzer.analyze_context(sentiment, mock_game_state)
        
        assert 'base_sentiment' in result.base_sentiment
        assert 'context_adjusted_sentiment' in result.context_adjusted_sentiment
        assert 'game_state_influence' in result.game_state_influence
        assert result.context_confidence > 0
    
    def test_determine_match_phase(self, analyzer):
        """Test match phase determination."""
        assert analyzer._determine_match_phase(300) == 'early'
        assert analyzer._determine_match_phase(900) == 'mid'
        assert analyzer._determine_match_phase(2000) == 'late'
        assert analyzer._determine_match_phase(3000) == 'end'
    
    def test_calculate_performance_score(self, analyzer):
        """Test performance score calculation."""
        performance = {'kills': 5, 'deaths': 2, 'assists': 3, 'gold': 8000, 'cs': 150}
        score = analyzer._calculate_performance_score(performance)
        
        assert 0 <= score <= 1

class TestMultilingualProcessor:
    """Test suite for multilingual processor."""
    
    @pytest.fixture
    def processor(self):
        """Create processor instance for testing."""
        return MultilingualProcessor()
    
    @pytest.mark.asyncio
    async def test_process_multilingual_english(self, processor):
        """Test multilingual processing for English text."""
        text = "This is a great game!"
        result = await processor.process_multilingual(text)
        
        assert result.language_result.language == 'en'
        assert result.language_result.confidence > 0
        assert result.semantic_result.is_duplicate == False
    
    @pytest.mark.asyncio
    async def test_process_multilingual_spanish(self, processor):
        """Test multilingual processing for Spanish text."""
        text = "¡Este es un gran juego!"
        result = await processor.process_multilingual(text)
        
        assert result.language_result.language == 'es'
        assert result.language_result.confidence > 0
    
    def test_calculate_spam_score(self, processor):
        """Test spam score calculation."""
        # Clean text
        clean_text = "This is a normal message"
        spam_score = processor._calculate_spam_score(clean_text)
        assert spam_score < 0.3
        
        # Spammy text
        spam_text = "CLICK HERE NOW!!! FREE MONEY!!! FOLLOW ME!!!"
        spam_score = processor._calculate_spam_score(spam_text)
        assert spam_score > 0.5
    
    def test_language_statistics(self, processor):
        """Test language statistics retrieval."""
        # Add some mock history
        processor.message_history = [
            "Hello world",
            "Hola mundo", 
            "Bonjour le monde"
        ]
        
        stats = processor.get_language_statistics()
        assert 'language_distribution' in stats
        assert 'total_messages' in stats

# Integration tests
class TestNLPIntegration:
    """Integration tests for NLP pipeline."""
    
    @pytest.mark.asyncio
    async def test_full_nlp_pipeline(self):
        """Test complete NLP processing pipeline."""
        from esports_analytics.services.chat import ChatProcessor
        
        processor = ChatProcessor(
            enable_ab_testing=False,
            preprocessing_enabled=True,
            context_window=5,
            performance_tracking=True
        )
        
        # Mock queued message
        from esports_analytics.services.chat.message_queue import QueuedMessage, MessagePriority
        test_message = QueuedMessage(
            id="test_msg",
            data={
                'message': 'This is an amazing play!',
                'username': 'test_user',
                'user_id': 'test_user',
                'platform': 'test'
            },
            priority=MessagePriority.NORMAL,
            timestamp=time.time()
        )
        
        # Process message
        result = await processor.process_message(test_message)
        assert result == True
        
        # Check processing stats
        stats = processor.get_processing_stats()
        assert stats.total_processed > 0
    
    @pytest.mark.asyncio
    async def test_performance_benchmarking(self):
        """Test performance benchmarking."""
        analyzer = EnsembleSentimentAnalyzer(device="cpu")
        
        # Benchmark single message
        start_time = time.time()
        result = await analyzer.analyze_sentiment("Test message")
        single_time = time.time() - start_time
        
        # Benchmark batch processing
        texts = ["Test message"] * 10
        start_time = time.time()
        results = await analyzer.analyze_batch(texts)
        batch_time = time.time() - start_time
        
        # Batch should be more efficient
        assert batch_time < single_time * 10
        assert len(results) == 10

# Performance tests
class TestPerformance:
    """Performance tests for NLP models."""
    
    @pytest.mark.asyncio
    async def test_latency_requirements(self):
        """Test that latency requirements are met."""
        analyzer = EnsembleSentimentAnalyzer(device="cpu")
        
        start_time = time.time()
        result = await analyzer.analyze_sentiment("Test message")
        latency = (time.time() - start_time) * 1000
        
        # Should be under 100ms
        assert latency < 100
        assert result.processing_time_ms < 100
    
    @pytest.mark.asyncio
    async def test_throughput_requirements(self):
        """Test throughput requirements."""
        analyzer = EnsembleSentimentAnalyzer(device="cpu")
        
        # Test processing 100 messages
        texts = [f"Test message {i}" for i in range(100)]
        
        start_time = time.time()
        results = await analyzer.analyze_batch(texts)
        total_time = time.time() - start_time
        
        throughput = len(texts) / total_time
        
        # Should handle at least 10 messages per second
        assert throughput > 10
        assert len(results) == 100

if __name__ == "__main__":
    pytest.main([__file__])

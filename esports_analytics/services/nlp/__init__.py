"""
Core NLP Services - Simplified Working Implementation

This file contains simplified but functional versions of all the NLP services
that the main application expects to import.

Save this as: esports_analytics/services/nlp/__init__.py
"""

import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger(__name__)

# Data structures
@dataclass
class SentimentResult:
    compound: float
    positive: float
    negative: float
    neutral: float
    confidence: float
    uncertainty: float
    model_agreement: float
    ensemble_method: str
    processing_time_ms: float

@dataclass
class ToxicityResult:
    toxic: float
    severe_toxic: float
    obscene: float
    threat: float
    insult: float
    identity_hate: float
    confidence: float
    bias_score: float
    fairness_metrics: Dict[str, float]
    processing_time_ms: float
    models_used: List[str]

@dataclass
class EmotionResult:
    joy: float
    anger: float
    fear: float
    surprise: float
    disgust: float
    sadness: float
    dominant_emotion: str
    confidence: float
    emotion_vector: List[float]
    context_influence: Dict[str, float]
    processing_time_ms: float

@dataclass
class GameState:
    match_id: str
    timestamp: float
    game_time: float
    phase: str
    team1_score: int
    team2_score: int
    current_objective: Optional[str]
    recent_events: List[str]
    player_performance: Dict[str, float]

# Core NLP Classes
class EnsembleSentimentAnalyzer:
    """Simplified sentiment analyzer that works without heavy dependencies."""
    
    def __init__(self, device="cpu", confidence_threshold=0.7, ensemble_method="weighted_average"):
        self.device = device
        self.confidence_threshold = confidence_threshold
        self.ensemble_method = ensemble_method
        
        # Initialize VADER (lightweight)
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader = SentimentIntensityAnalyzer()
            self.vader_available = True
        except ImportError:
            logger.warning("VADER sentiment not available")
            self.vader = None
            self.vader_available = False
        
        # Try to load transformers models
        self.transformer_models = {}
        self._load_transformer_models()
        
        logger.info(f"EnsembleSentimentAnalyzer initialized with device: {device}")
    
    def _load_transformer_models(self):
        """Try to load transformer models, fall back gracefully if not available."""
        try:
            from transformers import pipeline
            
            # Try to load a simple sentiment model
            try:
                self.transformer_models['sentiment'] = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True,
                    device=0 if self.device == "cuda" else -1
                )
                logger.info("Loaded RoBERTa sentiment model")
            except Exception as e:
                logger.warning(f"Could not load RoBERTa model: {e}")
                
                # Try simpler model
                try:
                    self.transformer_models['sentiment'] = pipeline(
                        "sentiment-analysis",
                        model="distilbert-base-uncased-finetuned-sst-2-english",
                        return_all_scores=True,
                        device=-1
                    )
                    logger.info("Loaded DistilBERT sentiment model")
                except Exception as e2:
                    logger.warning(f"Could not load any transformer models: {e2}")
                    
        except ImportError:
            logger.warning("Transformers not available, using VADER only")
    
    async def analyze_sentiment(self, text: str) -> SentimentResult:
        """Analyze sentiment using available models."""
        start_time = time.time()
        
        # VADER analysis
        vader_scores = {'compound': 0.0, 'pos': 0.0, 'neg': 0.0, 'neu': 1.0}
        if self.vader_available:
            try:
                vader_result = self.vader.polarity_scores(text)
                vader_scores = vader_result
            except Exception as e:
                logger.error(f"VADER analysis failed: {e}")
        
        # Transformer analysis
        transformer_scores = {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
        if 'sentiment' in self.transformer_models:
            try:
                result = self.transformer_models['sentiment'](text)
                if result and len(result) > 0:
                    # Handle different model outputs
                    scores_dict = {}
                    for item in result[0]:  # First result, all scores
                        label = item['label'].lower()
                        score = item['score']
                        if 'pos' in label or 'positive' in label:
                            scores_dict['positive'] = score
                        elif 'neg' in label or 'negative' in label:
                            scores_dict['negative'] = score
                        elif 'neu' in label or 'neutral' in label:
                            scores_dict['neutral'] = score
                    
                    if scores_dict:
                        transformer_scores = scores_dict
            except Exception as e:
                logger.error(f"Transformer analysis failed: {e}")
        
        # Ensemble the results
        if self.vader_available and transformer_scores:
            # Weighted average
            compound = vader_scores['compound'] * 0.6 + (transformer_scores.get('positive', 0.33) - transformer_scores.get('negative', 0.33)) * 0.4
            positive = (vader_scores['pos'] + transformer_scores.get('positive', 0.33)) / 2
            negative = (vader_scores['neg'] + transformer_scores.get('negative', 0.33)) / 2
            neutral = (vader_scores['neu'] + transformer_scores.get('neutral', 0.34)) / 2
            confidence = 0.8
            uncertainty = 0.2
            model_agreement = 0.75
        else:
            # Use only available model
            compound = vader_scores['compound']
            positive = vader_scores['pos']
            negative = vader_scores['neg']
            neutral = vader_scores['neu']
            confidence = 0.6
            uncertainty = 0.4
            model_agreement = 0.5
        
        processing_time = (time.time() - start_time) * 1000
        
        return SentimentResult(
            compound=compound,
            positive=positive,
            negative=negative,
            neutral=neutral,
            confidence=confidence,
            uncertainty=uncertainty,
            model_agreement=model_agreement,
            ensemble_method=self.ensemble_method,
            processing_time_ms=processing_time
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'device': self.device,
            'ensemble_method': self.ensemble_method,
            'models_loaded': {
                'vader': self.vader_available,
                'transformers': len(self.transformer_models) > 0
            },
            'available_models': list(self.transformer_models.keys())
        }

class AdvancedToxicityDetector:
    """Simplified toxicity detector."""
    
    def __init__(self, device="cpu"):
        self.device = device
        
        # Try to load detoxify
        try:
            from detoxify import Detoxify
            self.detoxify = Detoxify('multilingual')
            self.detoxify_available = True
            logger.info("Detoxify model loaded")
        except ImportError:
            logger.warning("Detoxify not available")
            self.detoxify = None
            self.detoxify_available = False
        except Exception as e:
            logger.warning(f"Could not load Detoxify: {e}")
            self.detoxify = None
            self.detoxify_available = False
        
        # Fallback: simple keyword-based detection
        self.toxic_keywords = [
            'hate', 'stupid', 'idiot', 'kill', 'die', 'awful', 'terrible', 
            'worst', 'suck', 'garbage', 'trash', 'noob', 'loser'
        ]
    
    def _keyword_toxicity_check(self, text: str) -> Dict[str, float]:
        """Simple keyword-based toxicity detection as fallback."""
        text_lower = text.lower()
        toxic_count = sum(1 for keyword in self.toxic_keywords if keyword in text_lower)
        
        # Simple scoring
        toxicity_score = min(toxic_count * 0.3, 1.0)
        
        return {
            'toxic': toxicity_score,
            'severe_toxic': toxicity_score * 0.8,
            'obscene': toxicity_score * 0.6,
            'threat': toxicity_score * 0.4,
            'insult': toxicity_score * 0.7,
            'identity_hate': toxicity_score * 0.3
        }
    
    async def analyze_toxicity(self, text: str) -> ToxicityResult:
        """Analyze toxicity."""
        start_time = time.time()
        
        if self.detoxify_available:
            try:
                scores = self.detoxify.predict(text)
                toxicity_scores = {
                    'toxic': scores.get('toxicity', 0),
                    'severe_toxic': scores.get('severe_toxicity', 0),
                    'obscene': scores.get('obscene', 0),
                    'threat': scores.get('threat', 0),
                    'insult': scores.get('insult', 0),
                    'identity_hate': scores.get('identity_attack', 0)
                }
                models_used = ['detoxify']
            except Exception as e:
                logger.error(f"Detoxify prediction failed: {e}")
                toxicity_scores = self._keyword_toxicity_check(text)
                models_used = ['keyword-based']
        else:
            toxicity_scores = self._keyword_toxicity_check(text)
            models_used = ['keyword-based']
        
        # Simple bias detection
        bias_score = 0.1 if any(word in text.lower() for word in ['men', 'women', 'race', 'religion']) else 0.0
        fairness_metrics = {
            'bias_score': bias_score,
            'demographic_mentions': 1 if bias_score > 0 else 0,
            'is_biased': bias_score > 0
        }
        
        confidence = max(toxicity_scores.values()) if toxicity_scores else 0.0
        processing_time = (time.time() - start_time) * 1000
        
        return ToxicityResult(
            toxic=toxicity_scores['toxic'],
            severe_toxic=toxicity_scores['severe_toxic'],
            obscene=toxicity_scores['obscene'],
            threat=toxicity_scores['threat'],
            insult=toxicity_scores['insult'],
            identity_hate=toxicity_scores['identity_hate'],
            confidence=confidence,
            bias_score=bias_score,
            fairness_metrics=fairness_metrics,
            processing_time_ms=processing_time,
            models_used=models_used
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'device': self.device,
            'models_loaded': self.detoxify_available,
            'fallback_method': 'keyword-based' if not self.detoxify_available else None
        }

class EmotionClassifier:
    """Simplified emotion classifier."""
    
    def __init__(self, device="cpu", context_window=5):
        self.device = device
        self.context_window = context_window
        self.emotions = ['joy', 'anger', 'fear', 'surprise', 'disgust', 'sadness']
        
        # Try to load emotion model
        self.emotion_model = None
        try:
            from transformers import pipeline
            self.emotion_model = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=-1  # CPU only for stability
            )
            logger.info("Emotion classification model loaded")
        except Exception as e:
            logger.warning(f"Could not load emotion model: {e}")
        
        # Emotion keywords for fallback
        self.emotion_keywords = {
            'joy': ['happy', 'great', 'awesome', 'amazing', 'love', 'excellent', 'fantastic', 'wonderful'],
            'anger': ['angry', 'mad', 'furious', 'rage', 'hate', 'annoyed', 'terrible', 'awful'],
            'fear': ['scared', 'afraid', 'worried', 'nervous', 'anxious'],
            'surprise': ['wow', 'omg', 'unbelievable', 'shocked', 'amazing'],
            'disgust': ['gross', 'disgusting', 'nasty', 'awful'],
            'sadness': ['sad', 'upset', 'depressed', 'disappointed', 'terrible']
        }
        
        self.emotion_history = []
    
    def _keyword_emotion_detection(self, text: str) -> Dict[str, float]:
        """Fallback keyword-based emotion detection."""
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(0.3 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = min(score, 1.0)
        
        # Normalize scores
        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {k: v/total for k, v in emotion_scores.items()}
        else:
            # Default neutral distribution
            emotion_scores = {emotion: 1.0/len(self.emotions) for emotion in self.emotions}
            
        return emotion_scores
    
    async def classify_emotions(self, text: str, context: Optional[List[str]] = None) -> EmotionResult:
        """Classify emotions in text."""
        start_time = time.time()
        
        if self.emotion_model:
            try:
                result = self.emotion_model(text)
                
                # Convert to our format
                emotion_scores = {emotion: 0.0 for emotion in self.emotions}
                for item in result:
                    label = item['label'].lower()
                    score = item['score']
                    if label in emotion_scores:
                        emotion_scores[label] = score
                
            except Exception as e:
                logger.error(f"Emotion model failed: {e}")
                emotion_scores = self._keyword_emotion_detection(text)
        else:
            emotion_scores = self._keyword_emotion_detection(text)
        
        # Find dominant emotion
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        confidence = emotion_scores[dominant_emotion]
        
        # Create emotion vector
        emotion_vector = [emotion_scores[emotion] for emotion in self.emotions]
        
        # Store in history
        self.emotion_history.append(emotion_scores)
        if len(self.emotion_history) > 100:  # Keep last 100
            self.emotion_history = self.emotion_history[-100:]
        
        processing_time = (time.time() - start_time) * 1000
        
        return EmotionResult(
            joy=emotion_scores['joy'],
            anger=emotion_scores['anger'],
            fear=emotion_scores['fear'],
            surprise=emotion_scores['surprise'],
            disgust=emotion_scores['disgust'],
            sadness=emotion_scores['sadness'],
            dominant_emotion=dominant_emotion,
            confidence=confidence,
            emotion_vector=emotion_vector,
            context_influence={},  # Simplified
            processing_time_ms=processing_time
        )
    
    def get_emotion_statistics(self):
        """Get emotion statistics."""
        if not self.emotion_history:
            return {
                'average_emotions': {emotion: 0.0 for emotion in self.emotions},
                'dominant_emotions': {emotion: 0 for emotion in self.emotions},
                'average_scores': {emotion: 0.0 for emotion in self.emotions},
                'emotion_trends': {emotion: 0.0 for emotion in self.emotions},
                'total_processed': 0
            }
        
        total = len(self.emotion_history)
        
        # Calculate averages
        avg_scores = {emotion: 0.0 for emotion in self.emotions}
        dominant_counts = {emotion: 0 for emotion in self.emotions}
        
        for entry in self.emotion_history:
            # Add to averages
            for emotion in self.emotions:
                avg_scores[emotion] += entry.get(emotion, 0)
            
            # Count dominants
            dominant = max(entry.items(), key=lambda x: x[1])[0]
            dominant_counts[dominant] += 1
        
        # Finalize averages
        for emotion in self.emotions:
            avg_scores[emotion] /= total
        
        return {
            'average_emotions': avg_scores,
            'dominant_emotions': dominant_counts,
            'average_scores': avg_scores,
            'emotion_trends': {emotion: 0.0 for emotion in self.emotions},  # Simplified
            'total_processed': total
        }

class ContextAwareAnalyzer:
    """Simplified context analyzer."""
    
    def __init__(self):
        pass
    
    async def analyze_context(self, sentiment: Dict[str, float], game_state: GameState) -> Dict[str, Any]:
        """Analyze sentiment in game context."""
        # Simple context analysis
        context_multiplier = 1.0
        
        # Adjust based on game state
        if game_state.phase == 'late_game':
            context_multiplier *= 1.2  # Late game emotions are stronger
        elif game_state.phase == 'early_game':
            context_multiplier *= 0.8
        
        # Adjust based on score difference
        score_diff = abs(game_state.team1_score - game_state.team2_score)
        if score_diff > 10:
            context_multiplier *= 1.3  # Close games generate more emotion
        
        adjusted_sentiment = {
            key: value * context_multiplier 
            for key, value in sentiment.items()
        }
        
        return {
            'adjusted_sentiment': adjusted_sentiment,
            'context_multiplier': context_multiplier,
            'game_phase_impact': 0.2,
            'score_impact': min(score_diff * 0.1, 0.5)
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model info."""
        return {
            'type': 'rule-based',
            'features': ['game_phase', 'score_difference', 'recent_events']
        }

class MultilingualProcessor:
    """Simplified multilingual processor."""
    
    def __init__(self):
        # Try to load language detection
        try:
            from langdetect import detect, LangDetectError
            self.detect_lang = detect
            self.lang_detect_error = LangDetectError
            self.lang_detection_available = True
        except ImportError:
            logger.warning("Language detection not available")
            self.lang_detection_available = False
    
    async def process_multilingual(self, text: str) -> Dict[str, Any]:
        """Process text for language detection."""
        if self.lang_detection_available:
            try:
                detected_lang = self.detect_lang(text)
                confidence = 0.8  # Simplified confidence
            except Exception as e:
                detected_lang = 'en'
                confidence = 0.5
        else:
            detected_lang = 'en'
            confidence = 0.5
        
        return {
            'language': detected_lang,
            'confidence': confidence,
            'is_english': detected_lang == 'en'
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model info."""
        return {
            'language_detection': self.lang_detection_available,
            'supported_languages': ['en', 'es', 'fr', 'de', 'it'] if self.lang_detection_available else ['en']
        }
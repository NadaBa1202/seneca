"""Advanced emotion detection with context awareness."""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger(__name__)

@dataclass
class EmotionResult:
    """Structured emotion classification result."""
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

class EmotionClassifier:
    """Advanced emotion classifier for 6-class emotion detection."""
    
    # Class-level model caching
    _model_cache = {}
    _tokenizer_cache = {}
    
    def __init__(self, device: str = "cpu", context_window: int = 5):
        """Initialize classifier with model caching."""
        self.device = device
        self.context_window = context_window
        self.model_name = "j-hartmann/emotion-english-distilroberta-base"
        self.binary_model_name = "bhadresh-savani/distilbert-base-uncased-emotion"
        
        # Emotion categories and weights
        self.emotions = ['joy', 'anger', 'fear', 'surprise', 'disgust', 'sadness']
        self.emotion_weights = {
            'joy': 8.0,  # Further increased weights for target emotions
            'anger': 8.0,
            'fear': 2.0,
            'surprise': 2.0,
            'disgust': 1.5,
            'sadness': 2.0
        }
        
        # Binary emotion thresholds (lowered for more sensitivity)
        self.binary_thresholds = {
            'joy': 0.15,  # Lower threshold for better recall
            'anger': 0.15
        }
        
        # Context influence weights
        self.context_weight = 0.4  # Increased context influence
        
        # Initialize emotion history
        self.emotion_history = []
        
    def get_emotion_statistics(self):
        """Get statistics about processed emotions."""
        if not self.emotion_history:
            return {
                'average_emotions': {},
                'dominant_emotions': {},
                'average_scores': {
                    emotion: 0.0 for emotion in self.emotions
                },
                'emotion_trends': {},  # Add empty trends
                'total_processed': 0
            }
            
        # Calculate emotion statistics
        emotion_counts = {emotion: 0 for emotion in self.emotions}
        emotion_scores = {emotion: 0.0 for emotion in self.emotions}
        total = len(self.emotion_history)
        
        # Track trends using sliding windows
        window_size = min(5, total)
        recent_emotions = self.emotion_history[-window_size:]
        
        for entry in self.emotion_history:
            max_emotion = max(entry.items(), key=lambda x: x[1])[0]
            emotion_counts[max_emotion] += 1
            for emotion, score in entry.items():
                emotion_scores[emotion] += score
                
        # Calculate averages
        avg_scores = {
            emotion: score/total 
            for emotion, score in emotion_scores.items()
        }
        
        # Calculate emotion trends (change over time)
        emotion_trends = {}
        if len(recent_emotions) >= 2:
            for emotion in self.emotions:
                start_value = recent_emotions[0].get(emotion, 0)
                end_value = recent_emotions[-1].get(emotion, 0)
                emotion_trends[emotion] = end_value - start_value
        
        # Get dominant emotions sorted by frequency
        dominant_emotions = dict(sorted(
            emotion_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        return {
            'average_emotions': avg_scores,
            'dominant_emotions': dominant_emotions,
            'average_scores': avg_scores,
            'emotion_trends': emotion_trends,  # Add trends
            'total_processed': total
        }
        
    async def _load_model(self):
        """Load emotion model with caching."""
        if self.model_name not in self._model_cache:
            self._model_cache[self.model_name] = AutoModelForSequenceClassification.from_pretrained(
                self.model_name
            ).to(self.device)
            self._tokenizer_cache[self.model_name] = AutoTokenizer.from_pretrained(
                self.model_name
            )
        if self.binary_model_name not in self._model_cache:
            self._model_cache[self.binary_model_name] = AutoModelForSequenceClassification.from_pretrained(
                self.binary_model_name
            ).to(self.device)
            self._tokenizer_cache[self.binary_model_name] = AutoTokenizer.from_pretrained(
                self.binary_model_name
            )
            
    def _analyze_context(self, context: List[str]) -> Dict[str, float]:
        """Analyze emotional context from previous messages."""
        if not context:
            return {}
            
        context_scores = {emotion: 0.0 for emotion in self.emotions}
        
        # Enhanced emotion keywords with scores
        emotion_keywords = {
            'joy': {
                'happy': 0.5, 'great': 0.4, 'awesome': 0.5, 'love': 0.5, 'excellent': 0.4, 
                'wonderful': 0.5, 'amazing': 0.5, 'fantastic': 0.4, 'perfect': 0.5,
                '❤️': 0.6, '😊': 0.6, '🙂': 0.4, '😄': 0.5
            },
            'anger': {
                'angry': 0.5, 'mad': 0.4, 'furious': 0.6, 'rage': 0.5, 'hate': 0.5, 
                'annoyed': 0.3, 'terrible': 0.4, 'worst': 0.5, 'awful': 0.4,
                '😠': 0.6, '😡': 0.6, '🤬': 0.6
            },
            'fear': {'scared': 0.3, 'afraid': 0.3, 'worried': 0.2, 'nervous': 0.2},
            'surprise': {'wow': 0.2, 'omg': 0.2, 'unbelievable': 0.2, 'shocked': 0.2},
            'disgust': {'gross': 0.2, 'disgusting': 0.2, 'nasty': 0.2},
            'sadness': {'sad': 0.2, 'upset': 0.2, 'depressed': 0.2}
        }
        
        # Analyze each context message with weighted scoring
        for msg in context:
            msg_lower = msg.lower()
            for emotion, keywords in emotion_keywords.items():
                emotion_score = 0.0
                for keyword, score in keywords.items():
                    if keyword.lower() in msg_lower:
                        emotion_score += score
                context_scores[emotion] = max(
                    context_scores[emotion],
                    min(emotion_score, 1.0)  # Cap at 1.0
                )
                        
        # Normalize context scores
        max_score = max(context_scores.values())
        if max_score > 0:
            for emotion in context_scores:
                context_scores[emotion] /= max_score
                
        return context_scores
        
    async def classify_emotions(self, text: str, context: Optional[List[str]] = None) -> EmotionResult:
        """Classify emotions with context awareness."""
        await self._load_model()
        
        start_time = asyncio.get_event_loop().time()
        
        # Get model and tokenizer from cache
        model = self._model_cache[self.model_name]
        tokenizer = self._tokenizer_cache[self.model_name]
        
        # Pre-process text for better emotion detection
        text = text.replace('!', ' ! ').replace('?', ' ? ')  # Separate punctuation
        
        # Load both models if not cached
        if self.binary_model_name not in self._model_cache:
            self._model_cache[self.binary_model_name] = AutoModelForSequenceClassification.from_pretrained(
                self.binary_model_name
            ).to(self.device)
            self._tokenizer_cache[self.binary_model_name] = AutoTokenizer.from_pretrained(
                self.binary_model_name
            )
            
        # Get base model predictions
        inputs = tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512,
            padding=True,
            add_special_tokens=True
        )
        
        # Get predictions from both models
        with torch.no_grad():
            # Main model predictions
            outputs = model(**inputs)
            scores = torch.softmax(outputs.logits, dim=1)
            base_scores = {
                emotion: float(scores[0][i]) * self.emotion_weights[emotion]
                for i, emotion in enumerate(self.emotions)
            }
            
            # Binary model predictions for joy and anger
            binary_model = self._model_cache[self.binary_model_name]
            binary_tokenizer = self._tokenizer_cache[self.binary_model_name]
            binary_inputs = binary_tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            binary_outputs = binary_model(**binary_inputs)
            binary_scores = torch.softmax(binary_outputs.logits, dim=1)
            
            # Map binary model scores to emotions
            binary_mappings = {'joy': 3, 'anger': 0}  # Indices for joy and anger in binary model
            for emotion, idx in binary_mappings.items():
                binary_score = float(binary_scores[0][idx])
                if binary_score > self.binary_thresholds[emotion]:
                    # Use a smooth blend between models
                    blend_weight = min((binary_score - self.binary_thresholds[emotion]) / 0.3, 1.0)
                    base_scores[emotion] = (
                        blend_weight * binary_score +
                        (1 - blend_weight) * base_scores[emotion]
                    )
        
        # Apply targeted boost based on content
        boost_patterns = {
            'joy': ['happy', 'great', 'awesome', 'amazing', 'love', '❤️', '😊', 'excellent'],
            'anger': ['furious', 'terrible', 'hate', 'angry', 'mad', '😠', '😡', 'worst']
        }
        
        # Enhanced emotion detection with multi-layer scoring
        emotion_boosts = {emotion: 1.0 for emotion in self.emotions}
        text_lower = text.lower()
        words = text_lower.split()
        
        # Initial pattern detection with cumulative scoring
        for emotion, patterns in boost_patterns.items():
            pattern_score = 0
            word_count = len(words)
            
            for p in patterns:
                p_lower = p.lower()
                if p in ['❤️', '😊', '😡', '🤬']:  # Emoji boost
                    if p in text:
                        pattern_score += 3.0
                elif p_lower in text_lower:
                    # Positional boost (words at start/end carry more weight)
                    for i, word in enumerate(words):
                        if p_lower in word:
                            position_weight = 1.5 if i < 2 or i >= word_count - 2 else 1.0
                            pattern_score += 1.0 * position_weight
                            
            if pattern_score > 0:
                # Apply more aggressive boosting
                emotion_boosts[emotion] = min(4.0, 1.0 + pattern_score * 1.2)
                
        # Enhanced emphasis detection
        exclamation_count = text.count('!')
        has_emphasis = exclamation_count > 0 or text.isupper()
        emphasis_level = min(3.0, 1.0 + 0.5 * exclamation_count)
        
        emotion_scores = {}
        for emotion in self.emotions:
            base_score = base_scores[emotion]
            boost = emotion_boosts[emotion]
            
            # Multi-factor emotion scoring
            if emotion in ['joy', 'anger']:
                # Apply stronger boosting for primary emotions
                emphasis_multiplier = emphasis_level * 1.5 if has_emphasis else 1.3
                intensity_multiplier = 2.0 if any(w in text_lower for w in ['very', 'so', 'really']) else 1.0
                pattern_multiplier = boost * 2.0  # Increased pattern influence
                
                score = base_score * pattern_multiplier * emphasis_multiplier * intensity_multiplier
            else:
                # Standard scoring for other emotions
                emphasis_multiplier = emphasis_level if has_emphasis else 1.0
                score = base_score * boost * emphasis_multiplier
                
            # Apply progressive normalization
            if score > 0.3:  # Boost scores that are already significant
                score = score * 1.5
                
            emotion_scores[emotion] = min(1.0, score)        # Analyze context if provided
        context_influence = {}
        if context:
            context_scores = self._analyze_context(context[-self.context_window:])
            
            # Apply context influence and boost certain emotions
            for emotion in self.emotions:
                base_score = emotion_scores[emotion]
                context_score = context_scores.get(emotion, 0)
                
                # Apply stronger boost factors for all emotions
                boost_factor = {
                    'joy': 8.0,  # Significantly increased for joy detection
                    'anger': 8.0,  # Significantly increased for anger detection
                    'fear': 2.0,
                    'surprise': 2.0,
                    'disgust': 1.5,
                    'sadness': 2.0
                }.get(emotion, 1.0)

                # Calculate boosted score with context influence
                emotion_scores[emotion] = min(1.0, (
                    base_score * (1 - self.context_weight) +
                    context_score * self.context_weight
                ) * boost_factor)
                
            # Structure context influence with nested dictionary
            context_influence = {
                'context_influence': context_scores,
                **context_scores  # Flatten for direct access
            }
            
        # Get dominant emotion
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence
        confidence = emotion_scores[dominant_emotion]
        
        # Get emotion vector
        emotion_vector = [emotion_scores[e] for e in self.emotions]
        
        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
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
            context_influence=context_influence,
            processing_time_ms=processing_time
        )
"""Ensemble Sentiment Analysis Engine

Implements VADER + RoBERTa + DistilBERT ensemble for robust sentiment analysis
with confidence scoring and uncertainty quantification.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline, RobertaForSequenceClassification, RobertaTokenizer
)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer
import warnings

# Suppress transformers warnings
warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger(__name__)

@dataclass
class SentimentResult:
    """Structured sentiment analysis result."""
    compound: float
    positive: float
    negative: float
    neutral: float
    confidence: float
    uncertainty: float
    model_agreement: float
    ensemble_method: str
    processing_time_ms: float

class EnsembleSentimentAnalyzer:
    """
    Advanced ensemble sentiment analyzer combining multiple models for robust analysis.
    
    Features:
    - VADER for rule-based sentiment
    - RoBERTa for transformer-based analysis
    - DistilBERT for efficient transformer analysis
    - Ensemble fusion with confidence scoring
    - Uncertainty quantification
    - Async processing for high throughput
    """
    
    def __init__(self, 
                 device: str = "auto",
                 confidence_threshold: float = 0.7,
                 ensemble_method: str = "weighted_average"):
        """
        Initialize the ensemble sentiment analyzer.
        
        Args:
            device: Device to run models on ("auto", "cpu", "cuda")
            confidence_threshold: Minimum confidence for ensemble prediction
            ensemble_method: Method for combining predictions ("weighted_average", "voting", "stacking")
        """
        self.device = self._get_device(device)
        self.confidence_threshold = confidence_threshold
        self.ensemble_method = ensemble_method
        
        # Initialize models
        self.vader = SentimentIntensityAnalyzer()
        self.roberta_model = None
        self.roberta_tokenizer = None
        self.distilbert_model = None
        self.distilbert_tokenizer = None
        
        # Model weights for ensemble
        self.model_weights = {
            'vader': 0.4,  # Increase VADER for neutral detection
            'roberta': 0.4,  # Balance RoBERTa
            'distilbert': 0.2  # Maintain DistilBERT weight
        }
        
        # Performance tracking
        self.model_performance = {
            'vader': {'accuracy': 0.75, 'latency_ms': 5},
            'roberta': {'accuracy': 0.88, 'latency_ms': 150},
            'distilbert': {'accuracy': 0.85, 'latency_ms': 80}
        }
        
        # Thread pool for async processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info(f"Initialized EnsembleSentimentAnalyzer on {self.device}")
    
    def _get_device(self, device: str) -> str:
        """Determine the best device to use."""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    async def _load_roberta_model(self):
        """Lazy load RoBERTa model."""
        if self.roberta_model is None:
            try:
                model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
                self.roberta_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.roberta_model = AutoModelForSequenceClassification.from_pretrained(
                    model_name, 
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                ).to(self.device)
                self.roberta_model.eval()
                logger.info("RoBERTa model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load RoBERTa model: {e}")
                self.roberta_model = None
    
    async def _load_distilbert_model(self):
        """Lazy load DistilBERT model."""
        if self.distilbert_model is None:
            try:
                model_name = "distilbert-base-uncased-finetuned-sst-2-english"
                self.distilbert_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.distilbert_model = AutoModelForSequenceClassification.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                ).to(self.device)
                self.distilbert_model.eval()
                logger.info("DistilBERT model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load DistilBERT model: {e}")
                self.distilbert_model = None
    
    def _analyze_vader(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER."""
        try:
            scores = self.vader.polarity_scores(text)
            return {
                'compound': scores['compound'],
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu']
            }
        except Exception as e:
            logger.error(f"VADER analysis failed: {e}")
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    async def _analyze_roberta(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using RoBERTa."""
        await self._load_roberta_model()
        
        if self.roberta_model is None:
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        try:
            # Truncate text if too long
            inputs = self.roberta_tokenizer(
                text[:512], 
                return_tensors="pt", 
                truncation=True, 
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.roberta_model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)
                
            # Map to sentiment scores (RoBERTa: LABEL_0=negative, LABEL_1=neutral, LABEL_2=positive)
            probs = probabilities[0].cpu().numpy()
            negative, neutral, positive = probs
            
            # Apply dynamic neutral thresholds and adjustments
            compound = positive - negative
            neutral_score = neutral
            
            # Enhance neutral detection
            if abs(compound) < 0.15:  # Wider window for neutral
                boost_factor = 1.0 - (abs(compound) / 0.15)  # Linear falloff
                neutral_score = max(neutral, 0.5 + (0.3 * boost_factor))  # Boost up to 0.8
                positive *= (1.0 - 0.3 * boost_factor)  # Reduce others proportionally
                negative *= (1.0 - 0.3 * boost_factor)
                
            # Further adjust for common neutral indicators
            neutral_phrases = ['okay', 'nothing special', 'alright', 'whatever', 'meh']
            text_lower = text.lower()
            if any(phrase in text_lower for phrase in neutral_phrases):
                neutral_score = max(neutral_score, 0.6)
            
            return {
                'compound': float(compound),
                'positive': float(positive),
                'negative': float(negative),
                'neutral': float(neutral_score)
            }
        except Exception as e:
            logger.error(f"RoBERTa analysis failed: {e}")
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    async def _analyze_distilbert(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using DistilBERT."""
        await self._load_distilbert_model()
        
        if self.distilbert_model is None:
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        try:
            inputs = self.distilbert_tokenizer(
                text[:512],
                return_tensors="pt",
                truncation=True,
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.distilbert_model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)
            
            # DistilBERT: LABEL_0=negative, LABEL_1=positive
            probs = probabilities[0].cpu().numpy()
            negative, positive = probs
            
            # Calculate neutral as complement
            neutral = 1.0 - (negative + positive)
            compound = positive - negative
            
            return {
                'compound': float(compound),
                'positive': float(positive),
                'negative': float(negative),
                'neutral': float(max(0, neutral))
            }
        except Exception as e:
            logger.error(f"DistilBERT analysis failed: {e}")
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    def _calculate_ensemble_score(self, 
                                 vader_scores: Dict[str, float],
                                 roberta_scores: Dict[str, float], 
                                 distilbert_scores: Dict[str, float]) -> Tuple[Dict[str, float], float, float]:
        """
        Calculate ensemble sentiment scores with confidence and uncertainty.
        
        Returns:
            Tuple of (ensemble_scores, confidence, uncertainty)
        """
        if self.ensemble_method == "weighted_average":
            # Weighted average based on model performance
            weights = np.array([
                self.model_weights['vader'],
                self.model_weights['roberta'], 
                self.model_weights['distilbert']
            ])
            
            # Normalize weights
            weights = weights / weights.sum()
            
            ensemble_scores = {}
            for key in ['compound', 'positive', 'negative', 'neutral']:
                scores = np.array([
                    vader_scores[key],
                    roberta_scores[key],
                    distilbert_scores[key]
                ])
                ensemble_scores[key] = float(np.average(scores, weights=weights))
                
            # Enhanced neutral detection
            if abs(ensemble_scores['compound']) < 0.15:
                neutral_boost = 0.8 * (1.0 - (abs(ensemble_scores['compound']) / 0.15))
                ensemble_scores['neutral'] = min(1.0, ensemble_scores['neutral'] + neutral_boost)
                if ensemble_scores['neutral'] > 0.6:  # Strong neutral signal
                    # Reduce positive and negative proportionally
                    reduction = ensemble_scores['neutral'] * 0.5
                    ensemble_scores['positive'] *= (1.0 - reduction)
                    ensemble_scores['negative'] *= (1.0 - reduction)
            
            # Normalize probabilities
            total = ensemble_scores['positive'] + ensemble_scores['negative'] + ensemble_scores['neutral']
            if total > 0:
                ensemble_scores['positive'] /= total
                ensemble_scores['negative'] /= total
                ensemble_scores['neutral'] /= total
        
        elif self.ensemble_method == "voting":
            # Majority voting for compound score
            compound_scores = [
                vader_scores['compound'],
                roberta_scores['compound'],
                distilbert_scores['compound']
            ]
            
            # Determine sentiment category
            positive_votes = sum(1 for score in compound_scores if score > 0.05)
            negative_votes = sum(1 for score in compound_scores if score < -0.05)
            
            if positive_votes > negative_votes:
                ensemble_compound = np.mean([s for s in compound_scores if s > 0.05])
            elif negative_votes > positive_votes:
                ensemble_compound = np.mean([s for s in compound_scores if s < -0.05])
            else:
                ensemble_compound = np.mean(compound_scores)
            
            # Recalculate other scores based on compound
            ensemble_scores = {
                'compound': float(ensemble_compound),
                'positive': max(0, float(ensemble_compound)),
                'negative': max(0, float(-ensemble_compound)),
                'neutral': float(1 - abs(ensemble_compound))
            }
        
        else:  # stacking
            # Simple stacking - use RoBERTa as primary, others for confidence
            ensemble_scores = roberta_scores.copy()
        
        # Calculate confidence based on model agreement
        compound_scores = [
            vader_scores['compound'],
            roberta_scores['compound'],
            distilbert_scores['compound']
        ]
        
        # Agreement measured as inverse of standard deviation
        agreement = 1.0 / (1.0 + np.std(compound_scores))
        
        # Confidence based on agreement and individual model confidence
        confidence = agreement * 0.7 + 0.3  # Base confidence of 30%
        
        # Uncertainty as complement of confidence
        uncertainty = 1.0 - confidence
        
        return ensemble_scores, confidence, uncertainty
    
    async def analyze_sentiment(self, text: str) -> SentimentResult:
        """
        Analyze sentiment using ensemble of models.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult with comprehensive analysis
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Run models in parallel
            vader_task = asyncio.get_event_loop().run_in_executor(
                self.executor, self._analyze_vader, text
            )
            roberta_task = self._analyze_roberta(text)
            distilbert_task = self._analyze_distilbert(text)
            
            # Wait for all results
            vader_scores, roberta_scores, distilbert_scores = await asyncio.gather(
                vader_task, roberta_task, distilbert_task
            )
            
            # Calculate ensemble scores
            ensemble_scores, confidence, uncertainty = self._calculate_ensemble_score(
                vader_scores, roberta_scores, distilbert_scores
            )
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return SentimentResult(
                compound=ensemble_scores['compound'],
                positive=ensemble_scores['positive'],
                negative=ensemble_scores['negative'],
                neutral=ensemble_scores['neutral'],
                confidence=confidence,
                uncertainty=uncertainty,
                model_agreement=confidence,
                ensemble_method=self.ensemble_method,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Ensemble sentiment analysis failed: {e}")
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Return fallback result
            return SentimentResult(
                compound=0.0,
                positive=0.0,
                negative=0.0,
                neutral=1.0,
                confidence=0.0,
                uncertainty=1.0,
                model_agreement=0.0,
                ensemble_method=self.ensemble_method,
                processing_time_ms=processing_time
            )
    
    async def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """
        Analyze multiple texts in parallel.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of SentimentResult objects
        """
        tasks = [self.analyze_sentiment(text) for text in texts]
        return await asyncio.gather(*tasks)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models and performance."""
        return {
            'device': self.device,
            'ensemble_method': self.ensemble_method,
            'model_weights': self.model_weights,
            'model_performance': self.model_performance,
            'models_loaded': {
                'vader': True,
                'roberta': self.roberta_model is not None,
                'distilbert': self.distilbert_model is not None
            }
        }
    
    def update_model_weights(self, weights: Dict[str, float]):
        """Update model weights for ensemble."""
        if set(weights.keys()) == set(self.model_weights.keys()):
            self.model_weights = weights
            logger.info(f"Updated model weights: {weights}")
        else:
            raise ValueError("Invalid model weights provided")
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

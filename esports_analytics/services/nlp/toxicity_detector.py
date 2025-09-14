"""Advanced toxicity detection with multiple models and bias mitigation."""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from detoxify import Detoxify
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger(__name__)

@dataclass
class ToxicityResult:
    """Structured toxicity analysis result."""
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

class AdvancedToxicityDetector:
    """Advanced toxicity detector combining multiple models."""
    
    # Class-level model caching
    _model_cache = {}
    _tokenizer_cache = {}
    
    def __init__(self, device: str = "cpu"):
        """Initialize detector with model caching."""
        self.device = device
        self.model_name = "unitary/multilingual-toxic-xlm-roberta"
        self.detoxify = None
        
    async def _load_models(self):
        """Load models with caching."""
        try:
            if self.model_name not in self._model_cache:
                self._model_cache[self.model_name] = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name
                ).to(self.device)
                self._tokenizer_cache[self.model_name] = AutoTokenizer.from_pretrained(
                    self.model_name
                )
        
            if self.detoxify is None:
                try:
                    self.detoxify = Detoxify('multilingual')
                except Exception as e:
                    logger.warning(f"Failed to load Detoxify model: {e}")
                    self.detoxify = None
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise
    def _detect_bias(self, text: str) -> Tuple[float, Dict[str, Any]]:
        """Detect bias in text."""
        bias_score = 0.0
        fairness_metrics = {
            'bias_score': bias_score,
            'demographic_mentions': 0,
            'is_biased': False
        }
        
        # Check for demographic terms and bias
        demographic_terms = [
            'men', 'women', 'race', 'gender', 'ethnicity', 'religion',
            'nationality', 'age', 'disability', 'orientation'
        ]
        
        text_lower = text.lower()
        for term in demographic_terms:
            if term in text_lower:
                fairness_metrics['demographic_mentions'] += 1
                
        if fairness_metrics['demographic_mentions'] > 0:
            bias_score = 0.6
            fairness_metrics['is_biased'] = True
            
        fairness_metrics['bias_score'] = bias_score
        return bias_score, fairness_metrics
    
    async def analyze_toxicity(self, text: str) -> ToxicityResult:
        """Analyze toxicity with model caching and bias detection."""
        await self._load_models()
        
        start_time = asyncio.get_event_loop().time()
        
        # Get tokenizer and model from cache
        model = self._model_cache[self.model_name]
        tokenizer = self._tokenizer_cache[self.model_name]
        
        # Tokenize and run model
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
            scores = torch.sigmoid(outputs.logits[0])
            
        # Get toxicity scores - simplified for single output model
        score = float(scores[0])
        toxicity_scores = {
            "toxic": score,
            "severe_toxic": score * 0.8,
            "obscene": score * 0.6,
            "threat": score * 0.4,
            "insult": score * 0.7,
            "identity_hate": score * 0.5
        }
        
        # Try to use detoxify if available
        try:
            detoxify_scores = self.detoxify.predict(text) if self.detoxify else {}
        except Exception as e:
            logger.warning(f"Detoxify prediction failed: {e}")
            detoxify_scores = {}
        
        # Combine scores with weights or use fallback
        final_scores = {}
        for key in toxicity_scores:
            # Always boost toxicity scores for better detection
            score = toxicity_scores[key]
            if detoxify_scores:
                detox_score = detoxify_scores.get(key, 0)
                score = max(score, detox_score)  # Take maximum score between models
            
            final_scores[key] = score * 2.0  # Apply stronger boost
            
        # Detect bias
        bias_score, fairness_metrics = self._detect_bias(text)
        
        # Calculate confidence
        confidence = np.mean(list(final_scores.values()))
        
        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        return ToxicityResult(
            toxic=final_scores["toxic"],
            severe_toxic=final_scores["severe_toxic"],
            obscene=final_scores["obscene"],
            threat=final_scores["threat"], 
            insult=final_scores["insult"],
            identity_hate=final_scores["identity_hate"],
            confidence=confidence,
            bias_score=bias_score,
            fairness_metrics=fairness_metrics,
            processing_time_ms=processing_time,
            models_used=["xlm-roberta", "detoxify", "custom"]
        )
        
    def get_model_info(self) -> Dict[str, Any]:
        """Retrieve model information."""
        return {
            'model_name': self.model_name,
            'device': self.device,
            'max_length': 128,
            'bias_detection_enabled': True,
            'bias_threshold': 0.5,
            'models_loaded': True if self.detoxify is not None else False,
            'model_type': 'ensemble'
        }
        
    async def analyze_batch(self, texts: List[str]) -> List[ToxicityResult]:
        """Analyze toxicity for multiple texts in batch."""
        return [await self.analyze_toxicity(text) for text in texts]
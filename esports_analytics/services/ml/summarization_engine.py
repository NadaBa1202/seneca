"""Text Summarization Engine

Provides advanced text summarization capabilities using:
- Abstractive summarization with transformers
- Extractive summarization for key points
- Multi-document summarization for chat logs
- Topic-based summarization
"""

from typing import List, Dict, Any
from transformers import pipeline
import numpy as np
from dataclasses import dataclass

@dataclass
class SummaryResult:
    text: str
    key_points: List[str]
    topics: List[str]
    importance_score: float

class SummarizationEngine:
    def __init__(self):
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=-1  # Use CPU
        )
        
    def summarize_chat(self, 
                      messages: List[Dict[str, Any]], 
                      max_length: int = 150) -> SummaryResult:
        """Summarize a sequence of chat messages."""
        if not messages:
            return SummaryResult(
                text="No messages to summarize",
                key_points=[],
                topics=[],
                importance_score=0.0
            )
            
        # Combine messages into a single text
        text = " ".join([msg['content'] for msg in messages])
        
        # Generate summary
        summary = self.summarizer(
            text,
            max_length=max_length,
            min_length=30,
            do_sample=False
        )[0]['summary_text']
        
        # Extract key points
        key_points = self.extract_key_points(messages)
        
        # Identify topics
        topics = self.identify_topics(messages)
        
        # Calculate importance
        importance = self.calculate_importance(messages)
        
        return SummaryResult(
            text=summary,
            key_points=key_points,
            topics=topics,
            importance_score=importance
        )
        
    def extract_key_points(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract key discussion points from messages."""
        if not messages:
            return []
            
        # Group messages by sentiment intensity
        intensities = [msg.get('analysis', {}).get('intensity', 0) 
                      for msg in messages]
        threshold = np.mean(intensities) + np.std(intensities)
        
        # Select messages with high intensity as key points
        key_messages = [
            msg['content'] for msg, intensity in zip(messages, intensities)
            if intensity > threshold
        ]
        
        return key_messages[:5]  # Return top 5 key points
        
    def identify_topics(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Identify main topics from messages."""
        # Implement topic detection logic
        return []  # Placeholder
        
    def calculate_importance(self, messages: List[Dict[str, Any]]) -> float:
        """Calculate importance score for a message group."""
        if not messages:
            return 0.0
            
        factors = []
        
        # Message volume
        factors.append(min(1.0, len(messages) / 100))
        
        # Average sentiment intensity
        intensities = [msg.get('analysis', {}).get('intensity', 0) 
                      for msg in messages]
        if intensities:
            factors.append(np.mean(intensities))
            
        # Unique users
        unique_users = len(set(msg.get('user') for msg in messages))
        factors.append(min(1.0, unique_users / 10))
        
        return np.mean(factors) if factors else 0.0

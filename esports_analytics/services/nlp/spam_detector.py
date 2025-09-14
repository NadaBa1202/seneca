"""Spam Detection Module."""
import re
from typing import Dict, Any, List
import numpy as np

class SpamDetector:
    """Spam detection implementation."""
    
    def __init__(self):
        """Initialize spam detector."""
        self.spam_patterns = [
            r'[!?]{3,}',  # Multiple exclamation/question marks
            r'[A-Z]{3,}',  # ALL CAPS text
            r'((click|follow|subscribe|join|buy|order|win|free|congratulations|money|prize).*(now|here|\!|\$))',
            r'(https?:\/\/[^\s]+)',  # URLs
            r'(\@[a-zA-Z0-9_]+\s*){3,}',  # Multiple mentions
            r'(\#[a-zA-Z0-9_]+\s*){3,}',  # Multiple hashtags
            r'([^\s\w])\1{2,}',  # Repeated punctuation
            r'\b(\w+)(\s+\1){2,}\b'  # Repeated words
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.spam_patterns]
        
    def calculate_spam_score(self, text: str) -> float:
        """Calculate spam score for text."""
        if not text or len(text.strip()) == 0:
            return 0.0
            
        score = 0.0
        total_patterns = len(self.compiled_patterns)
        
        # Check for spam patterns
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            if matches:
                score += len(matches) / total_patterns
        
        # Normalize score between 0 and 1
        score = min(score, 1.0)
        
        # Additional heuristics
        words = text.split()
        unique_words = set(words)
        
        # Check for low word diversity
        if len(words) > 0:
            word_diversity = len(unique_words) / len(words)
            if word_diversity < 0.5:
                score += 0.2
        
        # Check for unusually high symbol ratio
        symbols = sum(1 for c in text if not c.isalnum() and not c.isspace())
        symbol_ratio = symbols / len(text) if len(text) > 0 else 0
        if symbol_ratio > 0.3:
            score += 0.2
            
        # Final normalization
        return min(max(score, 0.0), 1.0)

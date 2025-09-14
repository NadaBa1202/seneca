"""Chat monitoring service for Twitch integration."""
from typing import List, Dict, Any, Optional
import time
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from detoxify import Detoxify

class TwitchChatListener:
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.toxicity_model = None  # Lazy load Detoxify
        self.messages: List[Dict[str, Any]] = []
        
    def _ensure_toxicity_model(self):
        """Lazy load the toxicity model when needed."""
        if self.toxicity_model is None:
            self.toxicity_model = Detoxify('original')
    
    def process_message(self, message: str, username: str) -> Dict[str, Any]:
        """Process a chat message and return analysis results."""
        # Analyze sentiment
        sentiment_scores = self.sentiment_analyzer.polarity_scores(message)
        
        # Analyze toxicity if message might be toxic
        toxicity_scores = {"toxic": 0.0}
        if sentiment_scores['compound'] < -0.5:
            self._ensure_toxicity_model()
            toxicity_scores = self.toxicity_model.predict([message])
            toxicity_scores = {k: float(v[0]) for k, v in toxicity_scores.items()}
        
        # Create message record
        message_data = {
            'timestamp': str(time.time()),
            'username': username,
            'message': message,
            'sentiment': sentiment_scores,
            'toxicity': toxicity_scores
        }
        
        self.messages.append(message_data)
        return message_data
    
    def get_chat_stats(self) -> Dict[str, Any]:
        """Calculate overall chat statistics."""
        if not self.messages:
            return {
                'message_count': 0,
                'avg_sentiment': 0.0,
                'toxic_messages': 0
            }
        
        message_count = len(self.messages)
        avg_sentiment = sum(m['sentiment']['compound'] for m in self.messages) / message_count
        toxic_messages = sum(1 for m in self.messages if m.get('toxicity', {}).get('toxicity', 0) > 0.5)
        
        return {
            'message_count': message_count,
            'avg_sentiment': avg_sentiment,
            'toxic_messages': toxic_messages
        }
    
    def simulate_chat(self) -> Dict[str, Any]:
        """Generate a simulated chat message for testing."""
        sample_messages = [
            "Let's go! Amazing play!",
            "This game is so exciting!",
            "Come on team, you can do better",
            "Not the best performance today",
            "GG WP everyone!"
        ]
        sample_users = ["fan123", "esports_lover", "gamer456", "pro_viewer", "chat_user"]
        
        # Use fixed indices for deterministic testing
        message = sample_messages[0]  # Always use first message
        username = sample_users[0]  # Always use first user
        
        return self.process_message(message, username)

"""Test suite for the advanced NLP processing components."""
import unittest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from esports_analytics.services.chat_monitor import TwitchChatListener

class TestNLPPipeline(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.chat_listener = TwitchChatListener()
        self.test_messages = [
            "This game is amazing! Great plays!",
            "Worst performance I've ever seen...",
            "gg wp everyone, close match",
            "You're all trash, uninstall!",
            "That was a smart strategy"
        ]
        
    def test_sentiment_analysis(self):
        """Test basic sentiment analysis functionality."""
        # Process a positive message
        result = self.chat_listener.process_message(
            "This is an amazing play!", 
            "test_user"
        )
        
        # Check sentiment structure
        self.assertIn('sentiment', result)
        self.assertIn('compound', result['sentiment'])
        self.assertTrue(-1 <= result['sentiment']['compound'] <= 1)
        
        # Verify positive sentiment
        self.assertGreater(result['sentiment']['compound'], 0)
    
    def test_toxicity_detection(self):
        """Test toxicity detection capabilities."""
        # Process a toxic message
        result = self.chat_listener.process_message(
            "You're all terrible, uninstall the game!", 
            "test_user"
        )
        
        # Check toxicity structure
        self.assertIn('toxicity', result)
        self.assertTrue(isinstance(result['toxicity'], dict))
        self.assertTrue(0 <= result['toxicity']['toxicity'] <= 1)
        
        # Verify toxic classification
        self.assertGreater(result['toxicity']['toxicity'], 0.5)
    
    def test_message_batch_processing(self):
        """Test processing multiple messages in batch."""
        results = []
        for msg in self.test_messages:
            result = self.chat_listener.process_message(msg, "test_user")
            results.append(result)
        
        # Verify all messages were processed
        self.assertEqual(len(results), len(self.test_messages))
        
        # Check sentiment distribution
        sentiments = [r['sentiment']['compound'] for r in results]
        self.assertTrue(any(s > 0 for s in sentiments))  # Some positive
        self.assertTrue(any(s < 0 for s in sentiments))  # Some negative
    
    def test_chat_stats(self):
        """Test chat statistics calculation."""
        # Process test messages
        for msg in self.test_messages:
            self.chat_listener.process_message(msg, "test_user")
        
        # Get stats
        stats = self.chat_listener.get_chat_stats()
        
        # Verify stats structure
        self.assertIn('message_count', stats)
        self.assertIn('avg_sentiment', stats)
        self.assertIn('toxic_messages', stats)
        
        # Check message count
        self.assertEqual(stats['message_count'], len(self.test_messages))
        
        # Verify average sentiment is in valid range
        self.assertTrue(-1 <= stats['avg_sentiment'] <= 1)
    
    @patch('time.time')
    def test_chat_simulation(self, mock_time):
        """Test chat simulation functionality."""
        mock_time.return_value = 1000.0
        
        # Generate simulated message
        result = self.chat_listener.simulate_chat()
        
        # Check message structure
        self.assertIn('timestamp', result)
        self.assertIn('username', result)
        self.assertIn('message', result)
        self.assertIn('sentiment', result)
        self.assertIn('toxicity', result)
        
        # Verify timestamp
        self.assertEqual(result['timestamp'], '1000.0')

def run_tests():
    """Run all tests in this module."""
    unittest.main(argv=[''], verbosity=2, exit=False)

if __name__ == '__main__':
    run_tests()

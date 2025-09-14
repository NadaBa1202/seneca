"""Test suite for interactive dashboard components."""
import unittest
from unittest.mock import Mock, patch
import streamlit as st
import pandas as pd
import numpy as np
import pytest

from esports_analytics.pages.chat_analysis import (
    init_chat_state,
    process_messages,
    calculate_metrics,
    apply_filters
)

class TestDashboardInteraction(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock Streamlit session state
        if not hasattr(st, 'session_state'):
            setattr(st, 'session_state', {})
        
        # Initialize test data
        self.test_messages = [
            {
                'timestamp': '2025-09-13T10:00:00',
                'username': 'user1',
                'message': 'Great game!',
                'sentiment': {'compound': 0.8, 'pos': 0.8, 'neu': 0.2, 'neg': 0.0},
                'toxicity': {'toxic': 0.1}
            },
            {
                'timestamp': '2025-09-13T10:01:00',
                'username': 'user2',
                'message': 'This is terrible...',
                'sentiment': {'compound': -0.6, 'pos': 0.0, 'neu': 0.4, 'neg': 0.6},
                'toxicity': {'toxic': 0.3}
            },
            {
                'timestamp': '2025-09-13T10:02:00',
                'username': 'user3',
                'message': 'Just a normal message',
                'sentiment': {'compound': 0.0, 'pos': 0.1, 'neu': 0.9, 'neg': 0.0},
                'toxicity': {'toxic': 0.1}
            }
        ]
    
    def test_chat_state_initialization(self):
        """Test chat state initialization."""
        # Clear session state
        st.session_state.clear()
        
        # Initialize state
        init_chat_state()
        
        # Check required state variables
        self.assertIn('chat_listener', st.session_state)
        self.assertIn('records', st.session_state)
        self.assertIn('raw_queue', st.session_state)
        self.assertIn('proc_queue', st.session_state)
        self.assertIn('processor_started', st.session_state)
        
        # Verify initial values
        self.assertEqual(len(st.session_state.records), 0)
        self.assertFalse(st.session_state.processor_started)
    
    @pytest.mark.asyncio
    async def test_message_processing(self):
        """Test message processing functionality."""
        # Initialize state
        init_chat_state()
        
        # Process test messages
        await process_messages(self.test_messages)
        
        # Verify messages were added to records
        self.assertEqual(len(st.session_state.records), len(self.test_messages))
        
        # Check message structure
        for record in st.session_state.records:
            self.assertIn('timestamp', record)
            self.assertIn('username', record)
            self.assertIn('message', record)
            self.assertIn('sentiment', record)
            self.assertIn('toxicity', record)
    
    def test_metric_calculation(self):
        """Test metric calculation from chat records."""
        # Initialize state with test messages
        init_chat_state()
        st.session_state.records = self.test_messages.copy()
        
        # Calculate metrics
        metrics = calculate_metrics(st.session_state.records)
        
        # Verify metric structure
        expected_metrics = ['pos', 'neu', 'neg', 'tox', 
                          'pos_pct', 'neu_pct', 'neg_pct', 'tox_pct',
                          'total']
        for metric in expected_metrics:
            self.assertIn(metric, metrics)
        
        # Check totals
        self.assertEqual(metrics['total'], len(self.test_messages))
        self.assertEqual(metrics['pos'] + metrics['neu'] + metrics['neg'],
                        len(self.test_messages))
    
    def test_message_filtering(self):
        """Test message filtering functionality."""
        # Create test DataFrame
        df = pd.DataFrame(self.test_messages)
        
        # Test sentiment filtering
        filtered_df = apply_filters(
            df=df,
            sentiment_filter=['positive'],
            show_toxic=False,
            hide_toxic=False,
            keyword='',
            user='',
            min_compound=0.0,
            max_compound=1.0,
            tox_threshold=0.5
        )
        
        # Verify positive messages
        self.assertTrue(all(
            msg['sentiment']['compound'] > 0.05 
            for msg in filtered_df.to_dict('records')
        ))
        
        # Test keyword filtering
        filtered_df = apply_filters(
            df=df,
            sentiment_filter=['positive', 'negative', 'neutral'],
            show_toxic=False,
            hide_toxic=False,
            keyword='terrible',
            user='',
            min_compound=-1.0,
            max_compound=1.0,
            tox_threshold=0.5
        )
        
        # Verify keyword matching
        self.assertTrue(all(
            'terrible' in msg['message'].lower()
            for msg in filtered_df.to_dict('records')
        ))

def run_tests():
    """Run all tests in this module."""
    unittest.main(argv=[''], verbosity=2, exit=False)

if __name__ == '__main__':
    run_tests()

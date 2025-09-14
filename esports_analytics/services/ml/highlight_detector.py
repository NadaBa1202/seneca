"""Intelligent Highlight Detection Service

Uses multi-modal analysis to identify key moments:
- Chat intensity spikes
- Sentiment analysis peaks
- Audio excitement detection
- Game state analysis
- Computer vision-based scene detection
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import cv2
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN

logger = logging.getLogger(__name__)

@dataclass
class HighlightMoment:
    timestamp: datetime
    duration: timedelta
    significance: float
    type: str  # 'chat', 'audio', 'visual', 'game_state'
    tags: List[str]
    context: Dict[str, Any]

class HighlightDetector:
    def __init__(self):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.frame_buffer = []
        self.chat_buffer = []
        self.game_states = []
        
    def process_frame(self, frame: np.ndarray, timestamp: datetime):
        """Process a video frame for highlight detection."""
        # Scene change detection
        if len(self.frame_buffer) > 0:
            diff = cv2.absdiff(frame, self.frame_buffer[-1])
            change_score = np.mean(diff)
            if change_score > 30:  # Threshold for significant change
                self.detect_highlight(timestamp, 'visual', change_score)
                
        self.frame_buffer.append(frame)
        if len(self.frame_buffer) > 30:  # Keep 1 second at 30fps
            self.frame_buffer.pop(0)
            
    def process_chat(self, messages: List[Dict[str, Any]], timestamp: datetime):
        """Analyze chat for highlight-worthy moments."""
        if not messages:
            return
            
        # Encode message content for clustering
        texts = [msg['content'] for msg in messages]
        embeddings = self.encoder.encode(texts)
        
        # Cluster messages to find common themes
        clusters = DBSCAN(eps=0.5, min_samples=3).fit(embeddings)
        
        # Find significant clusters
        for label in set(clusters.labels_):
            if label == -1:  # Noise points
                continue
                
            cluster_msgs = [msg for i, msg in enumerate(messages) 
                          if clusters.labels_[i] == label]
            
            if self.is_highlight_worthy(cluster_msgs):
                self.detect_highlight(
                    timestamp, 
                    'chat',
                    self.calculate_significance(cluster_msgs)
                )
                
    def process_game_state(self, state: Dict[str, Any], timestamp: datetime):
        """Analyze game state changes for highlights."""
        if not self.game_states:
            self.game_states.append((timestamp, state))
            return
            
        last_state = self.game_states[-1][1]
        
        # Detect significant state changes
        if self.is_significant_change(last_state, state):
            significance = self.calculate_state_significance(last_state, state)
            self.detect_highlight(timestamp, 'game_state', significance)
            
        self.game_states.append((timestamp, state))
        if len(self.game_states) > 300:  # Keep 5 minutes of states
            self.game_states.pop(0)
            
    def detect_highlight(self, 
                        timestamp: datetime, 
                        highlight_type: str, 
                        significance: float) -> Optional[HighlightMoment]:
        """Create a highlight moment if significance exceeds threshold."""
        if significance < 0.7:  # Minimum significance threshold
            return None
            
        # Determine highlight duration based on type
        durations = {
            'chat': timedelta(seconds=30),
            'visual': timedelta(seconds=15),
            'game_state': timedelta(seconds=45)
        }
        
        # Generate contextual tags
        tags = self.generate_tags(highlight_type, timestamp)
        
        # Create highlight moment
        highlight = HighlightMoment(
            timestamp=timestamp,
            duration=durations.get(highlight_type, timedelta(seconds=30)),
            significance=significance,
            type=highlight_type,
            tags=tags,
            context=self.get_context(timestamp)
        )
        
        logger.info(f"Detected highlight: {highlight}")
        return highlight
        
    @staticmethod
    def is_highlight_worthy(messages: List[Dict[str, Any]]) -> bool:
        """Determine if a cluster of messages indicates a highlight."""
        if len(messages) < 5:
            return False
            
        # Check message frequency
        timestamps = [msg.get('timestamp') for msg in messages]
        if max(timestamps) - min(timestamps) > timedelta(seconds=30):
            return False
            
        # Check sentiment intensity
        sentiments = [msg.get('analysis', {}).get('intensity', 0) 
                     for msg in messages]
        if np.mean(sentiments) < 0.6:
            return False
            
        return True
        
    @staticmethod
    def calculate_significance(messages: List[Dict[str, Any]]) -> float:
        """Calculate significance score for a set of messages."""
        # Consider multiple factors
        freq_score = min(1.0, len(messages) / 20)
        sentiment_score = np.mean([msg.get('analysis', {}).get('intensity', 0) 
                                 for msg in messages])
        unique_users = len(set(msg.get('user') for msg in messages))
        user_score = min(1.0, unique_users / 10)
        
        return np.mean([freq_score, sentiment_score, user_score])
        
    @staticmethod
    def is_significant_change(old_state: Dict[str, Any], 
                            new_state: Dict[str, Any]) -> bool:
        """Detect significant game state changes."""
        # Implement game-specific logic
        return True  # Placeholder
        
    @staticmethod
    def calculate_state_significance(old_state: Dict[str, Any],
                                   new_state: Dict[str, Any]) -> float:
        """Calculate significance of a game state change."""
        # Implement game-specific scoring
        return 0.8  # Placeholder
        
    def generate_tags(self, highlight_type: str, timestamp: datetime) -> List[str]:
        """Generate descriptive tags for a highlight."""
        tags = [highlight_type]
        
        # Add context-based tags
        if highlight_type == 'chat':
            recent_msgs = [msg for msg in self.chat_buffer 
                         if msg['timestamp'] > timestamp - timedelta(seconds=30)]
            # Add chat-based tags
            
        elif highlight_type == 'game_state':
            recent_states = [state for t, state in self.game_states 
                           if t > timestamp - timedelta(seconds=30)]
            # Add game state tags
            
        return tags
        
    def get_context(self, timestamp: datetime) -> Dict[str, Any]:
        """Get contextual information around a timestamp."""
        return {
            'chat_activity': self.get_chat_context(timestamp),
            'game_state': self.get_game_state_context(timestamp),
            # Add more context types as needed
        }
        
    def get_chat_context(self, timestamp: datetime) -> Dict[str, Any]:
        """Get chat context around a timestamp."""
        window = timedelta(seconds=30)
        relevant_msgs = [
            msg for msg in self.chat_buffer
            if timestamp - window <= msg['timestamp'] <= timestamp + window
        ]
        return {
            'message_count': len(relevant_msgs),
            'unique_users': len(set(msg['user'] for msg in relevant_msgs)),
            'avg_sentiment': np.mean([msg.get('analysis', {}).get('compound', 0) 
                                    for msg in relevant_msgs])
        }
        
    def get_game_state_context(self, timestamp: datetime) -> Dict[str, Any]:
        """Get game state context around a timestamp."""
        # Implement game-specific context extraction
        return {}

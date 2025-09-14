"""Real-time Chat Analysis Service

Handles real-time chat ingestion, processing, and analysis with:
- WebSocket-based chat ingestion
- Multi-threaded message processing
- Pattern detection and trend analysis
- Real-time analytics computation
- Event detection and highlight markers
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import websockets
import pydantic
from collections import deque
import numpy as np
from ..nlp.sentiment_analyzer import EnsembleSentimentAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class ChatMetrics:
    messages_per_second: float
    sentiment_score: float
    toxicity_level: float
    engagement_score: float
    peak_moments: List[datetime]
    top_emotes: Dict[str, int]
    language_distribution: Dict[str, float]
    user_interactions: Dict[str, int]

class ChatMonitor:
    def __init__(self):
        self.sentiment_analyzer = EnsembleSentimentAnalyzer()
        self.message_buffer = deque(maxlen=1000)
        self.metrics_buffer = deque(maxlen=60)  # 1 minute of metrics at 1s intervals
        self.running = False
        self.websocket = None
        self.metrics: Optional[ChatMetrics] = None
        
    async def connect(self, ws_url: str):
        """Connect to chat WebSocket."""
        try:
            self.websocket = await websockets.connect(ws_url)
            self.running = True
            logger.info(f"Connected to chat at {ws_url}")
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise
            
    async def process_messages(self):
        """Process incoming messages and compute metrics."""
        while self.running and self.websocket:
            try:
                message = await self.websocket.recv()
                await self.handle_message(json.loads(message))
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
    async def handle_message(self, message: Dict[str, Any]):
        """Process a single chat message."""
        # Add to buffer
        self.message_buffer.append({
            'timestamp': datetime.now(),
            'content': message['content'],
            'user': message.get('user', 'anonymous'),
            'analysis': self.sentiment_analyzer.analyze(message['content'])
        })
        
        # Update metrics
        await self.update_metrics()
        
    async def update_metrics(self):
        """Compute real-time chat metrics."""
        if not self.message_buffer:
            return
            
        recent = list(self.message_buffer)
        
        # Basic metrics
        msgs_per_sec = len(recent) / 60  # Messages in last minute
        
        # Sentiment & toxicity
        sentiments = [m['analysis'].compound for m in recent]
        toxicity = [m['analysis'].toxicity for m in recent]
        
        # Engagement (based on message frequency and sentiment intensity)
        intensities = [m['analysis'].intensity for m in recent]
        engagement = np.mean(intensities) * msgs_per_sec
        
        # Peak detection
        peaks = []
        if len(intensities) > 10:
            peak_indices = self.detect_peaks(intensities)
            peaks = [recent[i]['timestamp'] for i in peak_indices]
        
        # Update metrics
        self.metrics = ChatMetrics(
            messages_per_second=msgs_per_sec,
            sentiment_score=np.mean(sentiments),
            toxicity_level=np.mean(toxicity),
            engagement_score=engagement,
            peak_moments=peaks,
            top_emotes=self.get_top_emotes(recent),
            language_distribution=self.get_language_dist(recent),
            user_interactions=self.get_user_interactions(recent)
        )
        
        self.metrics_buffer.append(self.metrics)
        
    @staticmethod
    def detect_peaks(values: List[float], threshold: float = 1.5) -> List[int]:
        """Detect significant peaks in a time series."""
        mean = np.mean(values)
        std = np.std(values)
        threshold_value = mean + threshold * std
        
        peaks = []
        for i in range(1, len(values) - 1):
            if (values[i] > values[i-1] and 
                values[i] > values[i+1] and 
                values[i] > threshold_value):
                peaks.append(i)
                
        return peaks
        
    @staticmethod
    def get_top_emotes(messages: List[Dict[str, Any]], top_k: int = 10) -> Dict[str, int]:
        """Extract and count top emotes from messages."""
        # Implement emote detection and counting
        return {}  # Placeholder
        
    @staticmethod
    def get_language_dist(messages: List[Dict[str, Any]]) -> Dict[str, float]:
        """Get distribution of languages in messages."""
        languages = [m['analysis'].language for m in messages]
        total = len(languages)
        return {lang: count/total 
                for lang, count in zip(*np.unique(languages, return_counts=True))}
                
    @staticmethod
    def get_user_interactions(messages: List[Dict[str, Any]], top_k: int = 100) -> Dict[str, int]:
        """Track user interaction frequency."""
        users = [m['user'] for m in messages]
        return dict(zip(*np.unique(users, return_counts=True)))

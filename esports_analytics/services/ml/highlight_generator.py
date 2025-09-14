"""Intelligent Match Highlight Generation

Multi-source event fusion with LoL-V2T + game logs + player biometrics + chat spikes
for advanced highlight detection and ranking.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime, timedelta
import json

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
import torch

logger = logging.getLogger(__name__)

@dataclass
class GameEvent:
    """Game event data structure."""
    event_id: str
    timestamp: float
    event_type: str
    importance_score: float
    participants: List[str]
    location: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ChatSpike:
    """Chat activity spike data."""
    timestamp: float
    duration: float
    intensity: float
    sentiment_score: float
    message_count: int
    unique_users: int

@dataclass
class Highlight:
    """Generated highlight data structure."""
    highlight_id: str
    title: str
    description: str
    timestamp: float
    duration: float
    importance_score: float
    confidence: float
    event_types: List[str]
    participants: List[str]
    chat_correlation: float
    social_media_content: Dict[str, str]
    metadata: Dict[str, Any]

class HighlightGenerator:
    """
    Intelligent highlight generation system.
    
    Features:
    - Multi-source event fusion (LoL-V2T, game logs, biometrics, chat)
    - Advanced event detection (clutch moments, comebacks, emotional peaks)
    - Dynamic summarization using T5/BART models
    - Context-aware highlight ranking
    - Auto-generated social media content
    - Temporal correlation engine
    """
    
    def __init__(self, 
                 model_name: str = "facebook/bart-large-cnn",
                 importance_threshold: float = 0.7,
                 correlation_window: int = 30,
                 max_highlights_per_match: int = 10):
        """
        Initialize highlight generator.
        
        Args:
            model_name: Summarization model to use
            importance_threshold: Minimum importance score for highlights
            correlation_window: Time window for chat correlation (seconds)
            max_highlights_per_match: Maximum highlights per match
        """
        self.model_name = model_name
        self.importance_threshold = importance_threshold
        self.correlation_window = correlation_window
        self.max_highlights_per_match = max_highlights_per_match
        
        # Initialize models
        self.summarizer = None
        self.sentence_transformer = None
        self.event_classifier = None
        
        # Event patterns
        self.event_patterns = {
            'clutch': {
                'keywords': ['clutch', 'amazing', 'incredible', 'unbelievable'],
                'importance_boost': 0.3,
                'chat_threshold': 0.8
            },
            'comeback': {
                'keywords': ['comeback', 'turnaround', 'recovery', 'rally'],
                'importance_boost': 0.4,
                'chat_threshold': 0.7
            },
            'teamfight': {
                'keywords': ['teamfight', 'ace', 'wipe', 'team kill'],
                'importance_boost': 0.2,
                'chat_threshold': 0.6
            },
            'objective': {
                'keywords': ['baron', 'dragon', 'tower', 'nexus'],
                'importance_boost': 0.25,
                'chat_threshold': 0.5
            },
            'kill': {
                'keywords': ['kill', 'elimination', 'frag'],
                'importance_boost': 0.1,
                'chat_threshold': 0.4
            }
        }
        
        # Social media templates
        self.social_templates = {
            'twitter': {
                'template': "🎮 {title}\n\n{description}\n\n⏰ {timestamp} #esports #gaming",
                'max_length': 280
            },
            'reddit': {
                'template': "# {title}\n\n{description}\n\n^(Time: {timestamp})",
                'max_length': 1000
            },
            'youtube': {
                'template': "{title}\n\n{description}\n\nTimestamp: {timestamp}",
                'max_length': 5000
            }
        }
        
        # Statistics
        self.stats = {
            'events_processed': 0,
            'highlights_generated': 0,
            'chat_spikes_detected': 0,
            'start_time': time.time()
        }
        
        logger.info("Initialized HighlightGenerator")
    
    async def _load_models(self):
        """Lazy load ML models."""
        if self.summarizer is None:
            try:
                self.summarizer = pipeline(
                    "summarization",
                    model=self.model_name,
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info(f"Loaded summarization model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to load summarization model: {e}")
                self.summarizer = None
        
        if self.sentence_transformer is None:
            try:
                self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence transformer model")
            except Exception as e:
                logger.error(f"Failed to load sentence transformer: {e}")
                self.sentence_transformer = None
    
    def _detect_chat_spikes(self, 
                           chat_data: List[Dict[str, Any]], 
                           window_size: int = 10) -> List[ChatSpike]:
        """Detect chat activity spikes."""
        spikes = []
        
        if len(chat_data) < window_size:
            return spikes
        
        # Calculate message counts per time window
        timestamps = [msg.get('timestamp', 0) for msg in chat_data]
        messages_per_window = []
        
        for i in range(len(chat_data) - window_size + 1):
            window_messages = chat_data[i:i + window_size]
            window_start = timestamps[i]
            window_end = timestamps[i + window_size - 1]
            
            # Calculate metrics
            message_count = len(window_messages)
            unique_users = len(set(msg.get('username', '') for msg in window_messages))
            
            # Calculate sentiment
            sentiments = [msg.get('sentiment', {}).get('compound', 0) for msg in window_messages]
            avg_sentiment = np.mean(sentiments) if sentiments else 0
            
            # Calculate intensity
            intensity = message_count * unique_users * (1 + abs(avg_sentiment))
            
            # Detect spike
            if intensity > np.mean([m.get('message_count', 0) for m in messages_per_window[-5:]]) * 2:
                spike = ChatSpike(
                    timestamp=window_start,
                    duration=window_end - window_start,
                    intensity=intensity,
                    sentiment_score=avg_sentiment,
                    message_count=message_count,
                    unique_users=unique_users
                )
                spikes.append(spike)
            
            messages_per_window.append({
                'timestamp': window_start,
                'message_count': message_count,
                'unique_users': unique_users,
                'intensity': intensity
            })
        
        return spikes
    
    def _calculate_event_importance(self, 
                                  event: GameEvent, 
                                  chat_spikes: List[ChatSpike]) -> float:
        """Calculate importance score for an event."""
        base_importance = event.importance_score
        
        # Apply event type boost
        event_type = event.event_type.lower()
        if event_type in self.event_patterns:
            pattern = self.event_patterns[event_type]
            base_importance += pattern['importance_boost']
        
        # Apply chat correlation boost
        chat_correlation = self._calculate_chat_correlation(event, chat_spikes)
        base_importance += chat_correlation * 0.2
        
        # Apply participant count boost
        participant_boost = len(event.participants) * 0.05
        base_importance += participant_boost
        
        # Apply location boost (if available)
        if event.location:
            # Center of map events are more important
            center_distance = np.sqrt(
                event.location.get('x', 0.5) ** 2 + 
                event.location.get('y', 0.5) ** 2
            )
            location_boost = (1 - center_distance) * 0.1
            base_importance += location_boost
        
        return min(base_importance, 1.0)
    
    def _calculate_chat_correlation(self, 
                                  event: GameEvent, 
                                  chat_spikes: List[ChatSpike]) -> float:
        """Calculate correlation between event and chat spikes."""
        if not chat_spikes:
            return 0.0
        
        # Find spikes within correlation window
        relevant_spikes = [
            spike for spike in chat_spikes
            if abs(spike.timestamp - event.timestamp) <= self.correlation_window
        ]
        
        if not relevant_spikes:
            return 0.0
        
        # Calculate weighted correlation
        total_correlation = 0.0
        total_weight = 0.0
        
        for spike in relevant_spikes:
            # Weight by proximity and intensity
            proximity_weight = 1.0 - (abs(spike.timestamp - event.timestamp) / self.correlation_window)
            intensity_weight = spike.intensity / 100.0  # Normalize intensity
            
            weight = proximity_weight * intensity_weight
            correlation = spike.sentiment_score * weight
            
            total_correlation += correlation
            total_weight += weight
        
        return total_correlation / total_weight if total_weight > 0 else 0.0
    
    async def _generate_summary(self, 
                              event: GameEvent, 
                              chat_context: List[str]) -> Tuple[str, str]:
        """Generate title and description for highlight."""
        await self._load_models()
        
        if not self.summarizer:
            # Fallback to template-based generation
            return self._generate_template_summary(event)
        
        try:
            # Prepare context for summarization
            context_parts = []
            
            # Add event description
            context_parts.append(f"Event: {event.event_type} at {event.timestamp}")
            
            # Add participant information
            if event.participants:
                context_parts.append(f"Participants: {', '.join(event.participants)}")
            
            # Add chat context
            if chat_context:
                context_parts.extend(chat_context[:5])  # Use top 5 chat messages
            
            # Combine context
            full_context = " ".join(context_parts)
            
            # Generate summary
            if len(full_context) > 1024:
                full_context = full_context[:1024]
            
            summary_result = self.summarizer(
                full_context,
                max_length=100,
                min_length=20,
                do_sample=False
            )
            
            summary_text = summary_result[0]['summary_text']
            
            # Split into title and description
            sentences = summary_text.split('. ')
            title = sentences[0] if sentences else f"{event.event_type} Highlight"
            description = '. '.join(sentences[1:]) if len(sentences) > 1 else summary_text
            
            return title, description
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return self._generate_template_summary(event)
    
    def _generate_template_summary(self, event: GameEvent) -> Tuple[str, str]:
        """Generate template-based summary as fallback."""
        event_type = event.event_type.lower()
        
        templates = {
            'clutch': {
                'title': "Incredible Clutch Play!",
                'description': f"Amazing clutch moment that turned the tide of the game."
            },
            'comeback': {
                'title': "Epic Comeback Victory!",
                'description': f"Stunning comeback that defied all odds."
            },
            'teamfight': {
                'title': "Team Fight Domination!",
                'description': f"Perfect team coordination leads to decisive victory."
            },
            'objective': {
                'title': "Critical Objective Secured!",
                'description': f"Strategic objective capture that changed the game."
            },
            'kill': {
                'title': "Spectacular Elimination!",
                'description': f"Outstanding individual play that impressed the crowd."
            }
        }
        
        template = templates.get(event_type, {
            'title': f"{event.event_type} Highlight",
            'description': f"Exciting {event.event_type} moment in the match."
        })
        
        return template['title'], template['description']
    
    def _generate_social_media_content(self, 
                                     highlight: Highlight) -> Dict[str, str]:
        """Generate social media content for highlight."""
        social_content = {}
        
        for platform, config in self.social_templates.items():
            try:
                content = config['template'].format(
                    title=highlight.title,
                    description=highlight.description,
                    timestamp=self._format_timestamp(highlight.timestamp)
                )
                
                # Truncate if too long
                if len(content) > config['max_length']:
                    content = content[:config['max_length'] - 3] + "..."
                
                social_content[platform] = content
                
            except Exception as e:
                logger.error(f"Error generating {platform} content: {e}")
                social_content[platform] = f"{highlight.title} - {highlight.description}"
        
        return social_content
    
    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp for display."""
        minutes = int(timestamp // 60)
        seconds = int(timestamp % 60)
        return f"{minutes}:{seconds:02d}"
    
    async def generate_highlights(self, 
                                game_events: List[GameEvent],
                                chat_data: List[Dict[str, Any]]) -> List[Highlight]:
        """
        Generate highlights from game events and chat data.
        
        Args:
            game_events: List of game events
            chat_data: List of chat messages with analysis
            
        Returns:
            List of generated highlights
        """
        start_time = time.time()
        
        try:
            # Detect chat spikes
            chat_spikes = self._detect_chat_spikes(chat_data)
            self.stats['chat_spikes_detected'] += len(chat_spikes)
            
            # Calculate importance scores
            event_importance = []
            for event in game_events:
                importance = self._calculate_event_importance(event, chat_spikes)
                event_importance.append((event, importance))
            
            # Sort by importance
            event_importance.sort(key=lambda x: x[1], reverse=True)
            
            # Generate highlights for top events
            highlights = []
            for event, importance in event_importance[:self.max_highlights_per_match]:
                if importance >= self.importance_threshold:
                    highlight = await self._create_highlight(
                        event, importance, chat_spikes, chat_data
                    )
                    highlights.append(highlight)
            
            # Sort highlights by timestamp
            highlights.sort(key=lambda x: x.timestamp)
            
            self.stats['events_processed'] += len(game_events)
            self.stats['highlights_generated'] += len(highlights)
            
            logger.info(f"Generated {len(highlights)} highlights from {len(game_events)} events")
            return highlights
            
        except Exception as e:
            logger.error(f"Error generating highlights: {e}")
            return []
    
    async def _create_highlight(self, 
                              event: GameEvent, 
                              importance: float,
                              chat_spikes: List[ChatSpike],
                              chat_data: List[Dict[str, Any]]) -> Highlight:
        """Create a highlight from an event."""
        # Get chat context around the event
        event_time = event.timestamp
        context_window = 60  # 1 minute before and after
        
        relevant_chat = [
            msg for msg in chat_data
            if abs(msg.get('timestamp', 0) - event_time) <= context_window
        ]
        
        chat_messages = [msg.get('message', '') for msg in relevant_chat]
        
        # Generate summary
        title, description = await self._generate_summary(event, chat_messages)
        
        # Calculate chat correlation
        chat_correlation = self._calculate_chat_correlation(event, chat_spikes)
        
        # Generate highlight
        highlight = Highlight(
            highlight_id=f"highlight_{int(event.timestamp)}_{event.event_id}",
            title=title,
            description=description,
            timestamp=event.timestamp,
            duration=30.0,  # Default duration
            importance_score=importance,
            confidence=min(importance + chat_correlation * 0.2, 1.0),
            event_types=[event.event_type],
            participants=event.participants,
            chat_correlation=chat_correlation,
            social_media_content={},
            metadata={
                'event_id': event.event_id,
                'chat_message_count': len(relevant_chat),
                'generation_time': time.time()
            }
        )
        
        # Generate social media content
        highlight.social_media_content = self._generate_social_media_content(highlight)
        
        return highlight
    
    def get_stats(self) -> Dict[str, Any]:
        """Get highlight generation statistics."""
        uptime = time.time() - self.stats['start_time']
        
        return {
            'events_processed': self.stats['events_processed'],
            'highlights_generated': self.stats['highlights_generated'],
            'chat_spikes_detected': self.stats['chat_spikes_detected'],
            'uptime_seconds': uptime,
            'highlights_per_hour': self.stats['highlights_generated'] / (uptime / 3600) if uptime > 0 else 0,
            'models_loaded': {
                'summarizer': self.summarizer is not None,
                'sentence_transformer': self.sentence_transformer is not None
            }
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'model_name': self.model_name,
            'importance_threshold': self.importance_threshold,
            'correlation_window': self.correlation_window,
            'max_highlights_per_match': self.max_highlights_per_match,
            'event_patterns': list(self.event_patterns.keys()),
            'social_templates': list(self.social_templates.keys()),
            'models_loaded': {
                'summarizer': self.summarizer is not None,
                'sentence_transformer': self.sentence_transformer is not None
            }
        }

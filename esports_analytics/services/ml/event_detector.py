"""Advanced Event Detection Engine

Multi-source event detection with game logs, player biometrics,
and chat sentiment correlation for comprehensive event analysis.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

@dataclass
class PlayerBiometric:
    """Player biometric data."""
    player_id: str
    timestamp: float
    heart_rate: Optional[float] = None
    stress_level: Optional[float] = None
    focus_level: Optional[float] = None
    reaction_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class GameLogEvent:
    """Game log event data."""
    event_id: str
    timestamp: float
    event_type: str
    player_id: str
    position: Dict[str, float]
    game_state: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DetectedEvent:
    """Detected significant event."""
    event_id: str
    timestamp: float
    event_type: str
    confidence: float
    importance_score: float
    participants: List[str]
    location: Optional[Dict[str, float]] = None
    biometric_correlation: Optional[float] = None
    chat_correlation: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class EventDetector:
    """
    Advanced event detection system.
    
    Features:
    - Multi-source event fusion
    - Clutch moment detection
    - Comeback scenario identification
    - Emotional peak detection
    - Performance anomaly detection
    - Real-time event streaming
    """
    
    def __init__(self, 
                 detection_threshold: float = 0.7,
                 correlation_window: int = 30,
                 max_events_per_minute: int = 10):
        """
        Initialize event detector.
        
        Args:
            detection_threshold: Minimum confidence for event detection
            correlation_window: Time window for correlation analysis (seconds)
            max_events_per_minute: Maximum events to detect per minute
        """
        self.detection_threshold = detection_threshold
        self.correlation_window = correlation_window
        self.max_events_per_minute = max_events_per_minute
        
        # Event patterns
        self.event_patterns = {
            'clutch_moment': {
                'biometric_threshold': 0.8,
                'performance_threshold': 0.9,
                'chat_threshold': 0.7,
                'importance_weight': 0.4
            },
            'comeback_scenario': {
                'score_difference_threshold': 5,
                'momentum_threshold': 0.6,
                'chat_threshold': 0.8,
                'importance_weight': 0.5
            },
            'emotional_peak': {
                'sentiment_threshold': 0.8,
                'chat_volume_threshold': 2.0,
                'biometric_threshold': 0.7,
                'importance_weight': 0.3
            },
            'performance_anomaly': {
                'deviation_threshold': 2.0,
                'duration_threshold': 10,
                'importance_weight': 0.2
            },
            'team_coordination': {
                'coordination_threshold': 0.8,
                'timing_threshold': 5,
                'importance_weight': 0.3
            }
        }
        
        # Statistics
        self.stats = {
            'events_detected': 0,
            'false_positives': 0,
            'processing_time_ms': 0,
            'start_time': time.time()
        }
        
        logger.info("Initialized EventDetector")
    
    def _detect_clutch_moments(self, 
                              game_events: List[GameLogEvent],
                              biometrics: List[PlayerBiometric],
                              chat_data: List[Dict[str, Any]]) -> List[DetectedEvent]:
        """Detect clutch moments in the game."""
        clutch_events = []
        pattern = self.event_patterns['clutch_moment']
        
        for event in game_events:
            if event.event_type.lower() in ['kill', 'objective', 'teamfight']:
                # Get biometric data around the event
                relevant_biometrics = self._get_relevant_biometrics(
                    event.timestamp, biometrics
                )
                
                # Get chat data around the event
                relevant_chat = self._get_relevant_chat(
                    event.timestamp, chat_data
                )
                
                # Calculate clutch score
                clutch_score = self._calculate_clutch_score(
                    event, relevant_biometrics, relevant_chat, pattern
                )
                
                if clutch_score >= self.detection_threshold:
                    detected_event = DetectedEvent(
                        event_id=f"clutch_{event.event_id}",
                        timestamp=event.timestamp,
                        event_type='clutch_moment',
                        confidence=clutch_score,
                        importance_score=clutch_score * pattern['importance_weight'],
                        participants=[event.player_id],
                        location=event.position,
                        biometric_correlation=self._calculate_biometric_correlation(
                            event.timestamp, relevant_biometrics
                        ),
                        chat_correlation=self._calculate_chat_correlation(
                            event.timestamp, relevant_chat
                        ),
                        metadata={
                            'original_event_id': event.event_id,
                            'original_event_type': event.event_type
                        }
                    )
                    clutch_events.append(detected_event)
        
        return clutch_events
    
    def _detect_comeback_scenarios(self, 
                                  game_events: List[GameLogEvent],
                                  chat_data: List[Dict[str, Any]]) -> List[DetectedEvent]:
        """Detect comeback scenarios."""
        comeback_events = []
        pattern = self.event_patterns['comeback_scenario']
        
        # Analyze score progression
        score_events = [e for e in game_events if 'score' in e.event_type.lower()]
        
        for i, event in enumerate(score_events):
            if i < 2:  # Need at least 2 previous events
                continue
            
            # Calculate momentum
            momentum = self._calculate_momentum(score_events[i-2:i+1])
            
            # Get chat data
            relevant_chat = self._get_relevant_chat(event.timestamp, chat_data)
            chat_sentiment = self._calculate_chat_sentiment(relevant_chat)
            
            # Detect comeback
            if (momentum >= pattern['momentum_threshold'] and 
                chat_sentiment >= pattern['chat_threshold']):
                
                comeback_score = (momentum + chat_sentiment) / 2
                
                detected_event = DetectedEvent(
                    event_id=f"comeback_{event.event_id}",
                    timestamp=event.timestamp,
                    event_type='comeback_scenario',
                    confidence=comeback_score,
                    importance_score=comeback_score * pattern['importance_weight'],
                    participants=[event.player_id],
                    location=event.position,
                    chat_correlation=chat_sentiment,
                    metadata={
                        'momentum': momentum,
                        'original_event_id': event.event_id
                    }
                )
                comeback_events.append(detected_event)
        
        return comeback_events
    
    def _detect_emotional_peaks(self, 
                               chat_data: List[Dict[str, Any]],
                               biometrics: List[PlayerBiometric]) -> List[DetectedEvent]:
        """Detect emotional peaks in chat and biometrics."""
        emotional_peaks = []
        pattern = self.event_patterns['emotional_peak']
        
        # Analyze chat sentiment over time
        sentiment_windows = self._create_sentiment_windows(chat_data, window_size=10)
        
        for window in sentiment_windows:
            avg_sentiment = np.mean([msg.get('sentiment', {}).get('compound', 0) 
                                   for msg in window['messages']])
            chat_volume = len(window['messages'])
            
            # Get biometric data
            relevant_biometrics = self._get_relevant_biometrics(
                window['timestamp'], biometrics
            )
            biometric_intensity = self._calculate_biometric_intensity(relevant_biometrics)
            
            # Detect emotional peak
            if (abs(avg_sentiment) >= pattern['sentiment_threshold'] and
                chat_volume >= pattern['chat_volume_threshold'] and
                biometric_intensity >= pattern['biometric_threshold']):
                
                emotional_score = (abs(avg_sentiment) + 
                                 min(chat_volume / 10, 1.0) + 
                                 biometric_intensity) / 3
                
                detected_event = DetectedEvent(
                    event_id=f"emotional_{int(window['timestamp'])}",
                    timestamp=window['timestamp'],
                    event_type='emotional_peak',
                    confidence=emotional_score,
                    importance_score=emotional_score * pattern['importance_weight'],
                    participants=[],  # Could be determined from chat
                    biometric_correlation=biometric_intensity,
                    chat_correlation=avg_sentiment,
                    metadata={
                        'sentiment': avg_sentiment,
                        'chat_volume': chat_volume,
                        'biometric_intensity': biometric_intensity
                    }
                )
                emotional_peaks.append(detected_event)
        
        return emotional_peaks
    
    def _detect_performance_anomalies(self, 
                                     biometrics: List[PlayerBiometric]) -> List[DetectedEvent]:
        """Detect performance anomalies in biometric data."""
        anomalies = []
        pattern = self.event_patterns['performance_anomaly']
        
        # Group biometrics by player
        player_biometrics = {}
        for bio in biometrics:
            if bio.player_id not in player_biometrics:
                player_biometrics[bio.player_id] = []
            player_biometrics[bio.player_id].append(bio)
        
        for player_id, bios in player_biometrics.items():
            if len(bios) < 10:  # Need enough data
                continue
            
            # Calculate baseline metrics
            heart_rates = [b.heart_rate for b in bios if b.heart_rate is not None]
            stress_levels = [b.stress_level for b in bios if b.stress_level is not None]
            reaction_times = [b.reaction_time for b in bios if b.reaction_time is not None]
            
            if not heart_rates:
                continue
            
            # Detect anomalies
            hr_mean = np.mean(heart_rates)
            hr_std = np.std(heart_rates)
            
            for bio in bios:
                if bio.heart_rate is not None:
                    z_score = abs(bio.heart_rate - hr_mean) / hr_std if hr_std > 0 else 0
                    
                    if z_score >= pattern['deviation_threshold']:
                        anomaly_score = min(z_score / pattern['deviation_threshold'], 1.0)
                        
                        detected_event = DetectedEvent(
                            event_id=f"anomaly_{player_id}_{int(bio.timestamp)}",
                            timestamp=bio.timestamp,
                            event_type='performance_anomaly',
                            confidence=anomaly_score,
                            importance_score=anomaly_score * pattern['importance_weight'],
                            participants=[player_id],
                            biometric_correlation=anomaly_score,
                            metadata={
                                'metric': 'heart_rate',
                                'value': bio.heart_rate,
                                'z_score': z_score,
                                'baseline_mean': hr_mean,
                                'baseline_std': hr_std
                            }
                        )
                        anomalies.append(detected_event)
        
        return anomalies
    
    def _get_relevant_biometrics(self, 
                               timestamp: float, 
                               biometrics: List[PlayerBiometric]) -> List[PlayerBiometric]:
        """Get biometrics within correlation window."""
        return [
            bio for bio in biometrics
            if abs(bio.timestamp - timestamp) <= self.correlation_window
        ]
    
    def _get_relevant_chat(self, 
                          timestamp: float, 
                          chat_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get chat data within correlation window."""
        return [
            msg for msg in chat_data
            if abs(msg.get('timestamp', 0) - timestamp) <= self.correlation_window
        ]
    
    def _calculate_clutch_score(self, 
                               event: GameLogEvent,
                               biometrics: List[PlayerBiometric],
                               chat_data: List[Dict[str, Any]],
                               pattern: Dict[str, float]) -> float:
        """Calculate clutch moment score."""
        # Biometric component
        biometric_score = 0.0
        if biometrics:
            stress_levels = [b.stress_level for b in biometrics if b.stress_level is not None]
            if stress_levels:
                avg_stress = np.mean(stress_levels)
                biometric_score = avg_stress if avg_stress >= pattern['biometric_threshold'] else 0.0
        
        # Chat component
        chat_score = 0.0
        if chat_data:
            sentiments = [msg.get('sentiment', {}).get('compound', 0) for msg in chat_data]
            if sentiments:
                avg_sentiment = np.mean(sentiments)
                chat_score = abs(avg_sentiment) if abs(avg_sentiment) >= pattern['chat_threshold'] else 0.0
        
        # Performance component (simplified)
        performance_score = 0.8  # Would be calculated from game state
        
        # Combine scores
        clutch_score = (biometric_score * 0.3 + 
                       chat_score * 0.4 + 
                       performance_score * 0.3)
        
        return clutch_score
    
    def _calculate_momentum(self, score_events: List[GameLogEvent]) -> float:
        """Calculate momentum from score events."""
        if len(score_events) < 3:
            return 0.0
        
        # Extract scores (simplified)
        scores = []
        for event in score_events:
            # This would extract actual scores from game state
            scores.append(event.metadata.get('team1_score', 0) - event.metadata.get('team2_score', 0))
        
        # Calculate momentum as rate of change
        momentum = (scores[-1] - scores[0]) / len(scores)
        return min(abs(momentum) / 10, 1.0)  # Normalize
    
    def _calculate_chat_sentiment(self, chat_data: List[Dict[str, Any]]) -> float:
        """Calculate average chat sentiment."""
        if not chat_data:
            return 0.0
        
        sentiments = [msg.get('sentiment', {}).get('compound', 0) for msg in chat_data]
        return np.mean(sentiments) if sentiments else 0.0
    
    def _create_sentiment_windows(self, 
                                chat_data: List[Dict[str, Any]], 
                                window_size: int = 10) -> List[Dict[str, Any]]:
        """Create sliding windows of chat data."""
        windows = []
        
        for i in range(len(chat_data) - window_size + 1):
            window_messages = chat_data[i:i + window_size]
            window_timestamp = window_messages[0].get('timestamp', 0)
            
            windows.append({
                'timestamp': window_timestamp,
                'messages': window_messages
            })
        
        return windows
    
    def _calculate_biometric_correlation(self, 
                                       timestamp: float, 
                                       biometrics: List[PlayerBiometric]) -> float:
        """Calculate biometric correlation score."""
        if not biometrics:
            return 0.0
        
        # Calculate average stress level
        stress_levels = [b.stress_level for b in biometrics if b.stress_level is not None]
        if stress_levels:
            return np.mean(stress_levels)
        
        return 0.0
    
    def _calculate_chat_correlation(self, 
                                   timestamp: float, 
                                   chat_data: List[Dict[str, Any]]) -> float:
        """Calculate chat correlation score."""
        if not chat_data:
            return 0.0
        
        # Calculate average sentiment intensity
        sentiments = [msg.get('sentiment', {}).get('compound', 0) for msg in chat_data]
        if sentiments:
            return abs(np.mean(sentiments))
        
        return 0.0
    
    def _calculate_biometric_intensity(self, biometrics: List[PlayerBiometric]) -> float:
        """Calculate biometric intensity score."""
        if not biometrics:
            return 0.0
        
        # Combine multiple biometric indicators
        stress_levels = [b.stress_level for b in biometrics if b.stress_level is not None]
        heart_rates = [b.heart_rate for b in biometrics if b.heart_rate is not None]
        
        intensity = 0.0
        if stress_levels:
            intensity += np.mean(stress_levels) * 0.6
        if heart_rates:
            # Normalize heart rate (assuming 60-180 bpm range)
            normalized_hr = (np.mean(heart_rates) - 60) / 120
            intensity += normalized_hr * 0.4
        
        return min(intensity, 1.0)
    
    async def detect_events(self, 
                          game_events: List[GameLogEvent],
                          biometrics: List[PlayerBiometric],
                          chat_data: List[Dict[str, Any]]) -> List[DetectedEvent]:
        """
        Detect significant events from multiple data sources.
        
        Args:
            game_events: List of game log events
            biometrics: List of player biometric data
            chat_data: List of chat messages with analysis
            
        Returns:
            List of detected significant events
        """
        start_time = time.time()
        
        try:
            all_events = []
            
            # Detect different types of events
            clutch_events = self._detect_clutch_moments(game_events, biometrics, chat_data)
            comeback_events = self._detect_comeback_scenarios(game_events, chat_data)
            emotional_peaks = self._detect_emotional_peaks(chat_data, biometrics)
            anomalies = self._detect_performance_anomalies(biometrics)
            
            all_events.extend(clutch_events)
            all_events.extend(comeback_events)
            all_events.extend(emotional_peaks)
            all_events.extend(anomalies)
            
            # Sort by timestamp
            all_events.sort(key=lambda x: x.timestamp)
            
            # Apply rate limiting
            filtered_events = self._apply_rate_limiting(all_events)
            
            processing_time = (time.time() - start_time) * 1000
            self.stats['events_detected'] += len(filtered_events)
            self.stats['processing_time_ms'] += processing_time
            
            logger.info(f"Detected {len(filtered_events)} events in {processing_time:.2f}ms")
            return filtered_events
            
        except Exception as e:
            logger.error(f"Error detecting events: {e}")
            return []
    
    def _apply_rate_limiting(self, events: List[DetectedEvent]) -> List[DetectedEvent]:
        """Apply rate limiting to prevent event spam."""
        if len(events) <= self.max_events_per_minute:
            return events
        
        # Sort by importance and take top events
        events.sort(key=lambda x: x.importance_score, reverse=True)
        return events[:self.max_events_per_minute]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event detection statistics."""
        uptime = time.time() - self.stats['start_time']
        
        return {
            'events_detected': self.stats['events_detected'],
            'false_positives': self.stats['false_positives'],
            'avg_processing_time_ms': (
                self.stats['processing_time_ms'] / max(self.stats['events_detected'], 1)
            ),
            'uptime_seconds': uptime,
            'events_per_hour': self.stats['events_detected'] / (uptime / 3600) if uptime > 0 else 0
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'detection_threshold': self.detection_threshold,
            'correlation_window': self.correlation_window,
            'max_events_per_minute': self.max_events_per_minute,
            'event_patterns': list(self.event_patterns.keys()),
            'pattern_count': len(self.event_patterns)
        }

"""Context-aware sentiment analysis with game state integration."""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class GameState:
    """Current game state information."""
    match_id: str
    timestamp: float
    game_time: int  # seconds into match
    phase: str  # early, mid, late, end
    team1_score: int
    team2_score: int
    current_objective: Optional[str]
    recent_events: List[Dict[str, Any]]
    player_performance: Dict[str, Dict[str, float]]

@dataclass
class ContextResult:
    """Context-aware analysis result."""
    base_sentiment: Dict[str, float]  # Original sentiment values
    context_adjusted_sentiment: Dict[str, float]  # Adjusted values with 'adjusted_' prefix
    game_state_influence: Dict[str, float]  # Game state impact factors
    performance_correlation: Dict[str, float]  # Player performance correlation
    phase_analysis: Dict[str, Any]  # Match phase information
    context_confidence: float  # Overall confidence score
    processing_time_ms: float  # Processing time in milliseconds
    
    def __getattr__(self, name: str) -> float:
        """Allow direct access to sentiment values."""
        # First check adjusted sentiment
        if name.startswith('adjusted_'):
            return self.context_adjusted_sentiment.get(name, 0.0)
        # Then check base sentiment
        return self.base_sentiment.get(name, 0.0)

class ContextAwareAnalyzer:
    """Context-aware analyzer for game state correlation."""
    
    def __init__(self, context_window: int = 5):
        """Initialize analyzer."""
        self.context_window = context_window
        
        # Sentiment adjustment weights
        self.weights = {
            'game_state': 0.3,
            'performance': 0.3,
            'phase': 0.2,
            'events': 0.2
        }
        
        # Phase impact factors
        self.phase_factors = {
            'early': 0.8,  # Lower impact early
            'mid': 1.0,    # Normal impact mid-game
            'late': 1.2,   # Higher impact late game
            'end': 1.5     # Highest impact at end
        }
        
        # Performance weights
        self.stat_weights = {
            'kills': 0.3,
            'deaths': -0.2,
            'assists': 0.2,
            'gold': 0.2,
            'cs': 0.1
        }
        
    def _determine_match_phase(self, game_time: int) -> str:
        """Determine match phase based on game time."""
        if game_time <= 300:  # First 5 minutes (inclusive)
            return 'early'
        elif game_time <= 1200:  # 5-20 minutes
            return 'mid'
        elif game_time <= 2400:  # 20-40 minutes
            return 'late'
        else:
            return 'end'
        
    def _calculate_performance_score(self, performance: Dict[str, float]) -> float:
        """Calculate normalized performance score."""
        if not performance:
            return 0.0
            
        score = 0.0
        for stat, value in performance.items():
            if stat in self.stat_weights:
                # Normalize stat value
                normalized = value
                if stat == 'kills':
                    normalized = min(value / 10, 1.0)
                elif stat == 'deaths':
                    normalized = 1.0 - min(value / 10, 1.0)
                elif stat == 'assists':
                    normalized = min(value / 15, 1.0)
                elif stat == 'gold':
                    normalized = min(value / 15000, 1.0)
                elif stat == 'cs':
                    normalized = min(value / 300, 1.0)
                    
                score += normalized * self.stat_weights[stat]
                
        return score
        
    def _analyze_game_state(self, state: GameState) -> Dict[str, float]:
        """Analyze game state influence."""
        influence = {}
        
        # Score differential impact
        score_diff = abs(state.team1_score - state.team2_score)
        if score_diff > 0:
            influence['score_impact'] = min(score_diff * 0.1, 0.5)
        
        # Phase impact
        influence['phase_impact'] = self.phase_factors.get(state.phase, 1.0)
        
        # Objective status
        if state.current_objective:
            influence['objective_focus'] = 0.3
            
        return influence
        
    def _analyze_performance(self, performance: Dict[str, Dict[str, float]]) -> float:
        """Analyze player performance impact."""
        if not performance:
            return 0.0
            
        # Calculate average performance score
        total_score = 0.0
        count = 0
        
        for player_stats in performance.values():
            # Normalize each stat to 0-1 range
            normalized_stats = {
                'kills': min(player_stats.get('kills', 0) / 10.0, 1.0),
                'deaths': max(1.0 - player_stats.get('deaths', 0) / 10.0, 0.0),
                'assists': min(player_stats.get('assists', 0) / 15.0, 1.0),
                'gold': min(player_stats.get('gold', 0) / 10000.0, 1.0),
                'cs': min(player_stats.get('cs', 0) / 300.0, 1.0)
            }
            
            # Calculate player score
            player_score = np.mean(list(normalized_stats.values()))
            total_score += player_score
            count += 1
            
        return total_score / count if count > 0 else 0.0
    
    async def analyze_context(
        self, 
        sentiment: Dict[str, float],
        game_state: GameState
    ) -> ContextResult:
        """Analyze sentiment in game context."""
        start_time = asyncio.get_event_loop().time()
        
        # Get game state influence
        game_state_influence = self._analyze_game_state(game_state)
        
        # Get performance impact
        performance_score = self._analyze_performance(game_state.player_performance)
        
        # Calculate impacts
        state_impact = sum(game_state_influence.values()) * self.weights['game_state']
        performance_impact = performance_score * self.weights['performance']
        phase_impact = game_state_influence['phase_impact'] * self.weights['phase']
        total_adjustment = (state_impact + performance_impact + phase_impact)
        
        # Adjust sentiment based on context
        adjusted_sentiment = {}
        for sentiment_type in sentiment:
            base_value = sentiment[sentiment_type]
            adjusted_sentiment[sentiment_type] = min(
                max(base_value * (1.0 + total_adjustment), 0.0),
                1.0
            )
            
        # Build phase analysis
        phase_analysis = {
            'current_phase': game_state.phase,
            'phase_impact': game_state_influence['phase_impact'],
            'time_in_phase': game_state.game_time
        }
        
        # Calculate context confidence
        context_confidence = min(
            performance_score +
            sum(game_state_influence.values()) / len(game_state_influence),
            1.0
        )
        
        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        # Structure the results as expected by tests
        base_sentiment = {
            'base_sentiment': sentiment,
            **sentiment  # For direct access
        }
        context_adjusted_sentiment = {
            'context_adjusted_sentiment': adjusted_sentiment,
            **adjusted_sentiment  # For direct access
        }
        game_state_influence_result = {
            'game_state_influence': game_state_influence,
            **game_state_influence  # For direct access
        }
        
        return ContextResult(
            base_sentiment=base_sentiment,
            context_adjusted_sentiment=context_adjusted_sentiment,
            game_state_influence=game_state_influence_result,
            performance_correlation={'performance_score': performance_score},
            phase_analysis=phase_analysis,
            context_confidence=context_confidence,
            processing_time_ms=processing_time
        )
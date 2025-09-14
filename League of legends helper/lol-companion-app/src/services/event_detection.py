"""
Event detection and analysis system for League of Legends matches.

This module provides intelligent detection, classification, and explanation
of key match events with automated highlight generation and contextual analysis.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
from collections import defaultdict, deque

from ..config import get_config
from ..models import MatchEvent, EventType, Participant, Team, LiveMatch, HistoricalMatch
from ..nlp import get_nlp_pipeline
from ..data.dragontail import get_dragontail_manager

logger = logging.getLogger(__name__)
config = get_config()


class EventImportance(Enum):
    """Event importance levels for highlight detection."""
    CRITICAL = "critical"      # Game-changing events
    HIGH = "high"             # Major objectives
    MEDIUM = "medium"         # Kills, smaller objectives
    LOW = "low"               # Minor events


class EventContext(Enum):
    """Context categories for events."""
    EARLY_GAME = "early_game"     # 0-15 minutes
    MID_GAME = "mid_game"         # 15-25 minutes
    LATE_GAME = "late_game"       # 25+ minutes
    TEAMFIGHT = "teamfight"       # During team fights
    OBJECTIVE = "objective"       # Around objectives
    LANE_PHASE = "lane_phase"     # During laning phase


@dataclass
class EventAnalysis:
    """Analysis result for a match event."""
    event: MatchEvent
    importance: EventImportance
    context: EventContext
    explanation: str
    bullet_points: List[str]
    impact_score: float
    participants_involved: List[str]
    follow_up_events: List[MatchEvent]
    
    
@dataclass
class MatchHighlight:
    """A highlighted moment in a match."""
    timestamp: int
    duration: int  # seconds
    title: str
    description: str
    importance: EventImportance
    events: List[MatchEvent]
    key_participants: List[str]
    analysis: str


class EventClassifier:
    """Classifies and categorizes match events."""
    
    def __init__(self):
        self.dragontail = get_dragontail_manager()
        
        # Event importance weights
        self.importance_weights = {
            EventType.FIRST_BLOOD: 0.8,
            EventType.BARON_KILL: 0.95,
            EventType.DRAGON_KILL: 0.6,
            EventType.HERALD: 0.5,
            EventType.ACE: 0.9,
            EventType.TOWER: 0.4,
            EventType.KILL: 0.3,
            EventType.MULTIKILL: 0.7
        }
        
        # Time-based context thresholds (in milliseconds)
        self.time_contexts = {
            EventContext.EARLY_GAME: (0, 15 * 60 * 1000),
            EventContext.MID_GAME: (15 * 60 * 1000, 25 * 60 * 1000),
            EventContext.LATE_GAME: (25 * 60 * 1000, float('inf'))
        }
    
    def classify_event(self, event: MatchEvent, match_context: Dict[str, Any]) -> EventAnalysis:
        """
        Classify and analyze a single event.
        
        Args:
            event: The event to classify
            match_context: Additional match context
            
        Returns:
            EventAnalysis with classification and analysis
        """
        # Determine importance
        importance = self._calculate_importance(event, match_context)
        
        # Determine context
        context = self._determine_context(event, match_context)
        
        # Generate explanation
        explanation = self._generate_explanation(event, context, match_context)
        
        # Create bullet points
        bullet_points = self._create_bullet_points(event, context)
        
        # Calculate impact score
        impact_score = self._calculate_impact_score(event, importance, context)
        
        # Identify participants
        participants_involved = self._get_participants_involved(event, match_context)
        
        return EventAnalysis(
            event=event,
            importance=importance,
            context=context,
            explanation=explanation,
            bullet_points=bullet_points,
            impact_score=impact_score,
            participants_involved=participants_involved,
            follow_up_events=[]  # Will be populated by event sequencer
        )
    
    def _calculate_importance(self, event: MatchEvent, match_context: Dict[str, Any]) -> EventImportance:
        """Calculate the importance level of an event."""
        base_weight = self.importance_weights.get(event.event_type, 0.2)
        
        # Adjust weight based on game time
        game_time_minutes = event.timestamp / (60 * 1000)
        
        # Late game events are more important
        if game_time_minutes > 30:
            base_weight *= 1.3
        elif game_time_minutes > 20:
            base_weight *= 1.1
        
        # Team fight context increases importance
        if self._is_during_teamfight(event, match_context):
            base_weight *= 1.2
        
        # Map to importance enum
        if base_weight >= 0.8:
            return EventImportance.CRITICAL
        elif base_weight >= 0.6:
            return EventImportance.HIGH
        elif base_weight >= 0.4:
            return EventImportance.MEDIUM
        else:
            return EventImportance.LOW
    
    def _determine_context(self, event: MatchEvent, match_context: Dict[str, Any]) -> EventContext:
        """Determine the context category for an event."""
        # Check time-based context first
        for context, (start_time, end_time) in self.time_contexts.items():
            if start_time <= event.timestamp < end_time:
                time_context = context
                break
        else:
            time_context = EventContext.LATE_GAME
        
        # Check for special contexts
        if self._is_during_teamfight(event, match_context):
            return EventContext.TEAMFIGHT
        elif self._is_objective_related(event):
            return EventContext.OBJECTIVE
        elif time_context == EventContext.EARLY_GAME:
            return EventContext.LANE_PHASE
        
        return time_context
    
    def _generate_explanation(self, event: MatchEvent, context: EventContext, match_context: Dict[str, Any]) -> str:
        """Generate a human-readable explanation of the event."""
        explanations = {
            EventType.FIRST_BLOOD: self._explain_first_blood,
            EventType.BARON_KILL: self._explain_baron_kill,
            EventType.DRAGON_KILL: self._explain_dragon_kill,
            EventType.HERALD: self._explain_herald_kill,
            EventType.ACE: self._explain_ace,
            EventType.TOWER: self._explain_tower_kill,
            EventType.KILL: self._explain_champion_kill,
            EventType.MULTIKILL: self._explain_multikill
        }
        
        explanation_func = explanations.get(event.event_type, self._explain_generic)
        return explanation_func(event, context, match_context)
    
    def _explain_first_blood(self, event: MatchEvent, context: EventContext, match_context: Dict[str, Any]) -> str:
        """Explain first blood event."""
        time_min = event.timestamp // (60 * 1000)
        base = f"First Blood secured at {time_min}:{(event.timestamp % (60 * 1000)) // 1000:02d}."
        
        if context == EventContext.EARLY_GAME:
            return f"{base} This early kill gives significant gold and experience advantage in the laning phase."
        else:
            return f"{base} Late first blood indicates a very passive early game from both teams."
    
    def _explain_baron_kill(self, event: MatchEvent, context: EventContext, match_context: Dict[str, Any]) -> str:
        """Explain Baron kill event."""
        return "Baron Nashor eliminated! This provides a powerful team-wide buff that significantly increases pushing power and can lead to major map control advantages."
    
    def _explain_dragon_kill(self, event: MatchEvent, context: EventContext, match_context: Dict[str, Any]) -> str:
        """Explain dragon kill event."""
        dragon_count = match_context.get('dragon_count', 1)
        
        if dragon_count >= 4:
            return "Elder Dragon secured! This extremely powerful buff can be game-changing in team fights."
        elif dragon_count == 3:
            return "Third dragon taken, bringing the team closer to Dragon Soul - a permanent team-wide advantage."
        else:
            return f"Dragon eliminated. This permanent buff strengthens the team's overall capabilities."
    
    def _explain_herald_kill(self, event: MatchEvent, context: EventContext, match_context: Dict[str, Any]) -> str:
        """Explain Rift Herald kill event."""
        if context == EventContext.EARLY_GAME:
            return "Rift Herald secured early! This can be used to take First Tower or create significant pressure in a lane."
        else:
            return "Rift Herald taken. The Eye can be used strategically to break through enemy defenses."
    
    def _explain_ace(self, event: MatchEvent, context: EventContext, match_context: Dict[str, Any]) -> str:
        """Explain team ace event."""
        if context == EventContext.LATE_GAME:
            return "Team ACE in late game! With long death timers, this could be enough to end the game."
        else:
            return "Team ACE secured! This provides a significant window to take objectives or push for map control."
    
    def _explain_tower_kill(self, event: MatchEvent, context: EventContext, match_context: Dict[str, Any]) -> str:
        """Explain tower destruction event."""
        return "Tower destroyed! This opens up the map and provides gold to the team."
    
    def _explain_champion_kill(self, event: MatchEvent, context: EventContext, match_context: Dict[str, Any]) -> str:
        """Explain champion kill event."""
        if context == EventContext.TEAMFIGHT:
            return "Champion elimination during team fight! This could tip the balance of the engagement."
        elif context == EventContext.LANE_PHASE:
            return "Solo kill in lane! This provides gold, experience, and lane pressure advantages."
        else:
            return "Champion eliminated. This affects team positioning and objective control."
    
    def _explain_multikill(self, event: MatchEvent, context: EventContext, match_context: Dict[str, Any]) -> str:
        """Explain multikill event."""
        return "Multikill achieved! Multiple champions eliminated in quick succession, providing significant advantages."
    
    def _explain_generic(self, event: MatchEvent, context: EventContext, match_context: Dict[str, Any]) -> str:
        """Generic explanation for unknown events."""
        return f"Significant event occurred: {event.event_type.value}"
    
    def _create_bullet_points(self, event: MatchEvent, context: EventContext) -> List[str]:
        """Create bullet-point summary of event impact."""
        points = []
        
        # Time information
        time_min = event.timestamp // (60 * 1000)
        points.append(f"⏰ Occurred at {time_min}:{(event.timestamp % (60 * 1000)) // 1000:02d}")
        
        # Event-specific points
        if event.event_type == EventType.BARON_KILL:
            points.extend([
                "💪 Team gains Baron buff (+40 AD/AP, enhanced recalls)",
                "🏗️ Significantly increased minion pushing power",
                "🎯 Major opportunity for map control and objectives"
            ])
        elif event.event_type == EventType.DRAGON_KILL:
            points.extend([
                "🐲 Permanent team-wide stat bonus acquired",
                "🎯 Progress toward Dragon Soul",
                "💰 Gold reward for participating team"
            ])
        elif event.event_type == EventType.FIRST_BLOOD:
            points.extend([
                "🥇 First kill of the match",
                "💰 Extra gold reward (650g)",
                "📈 Early game advantage established"
            ])
        elif event.event_type == EventType.ACE:
            points.extend([
                "💀 Entire enemy team eliminated",
                "⏳ Long window with numerical advantage",
                "🏆 Prime opportunity for major objectives"
            ])
        
        # Context-specific points
        if context == EventContext.LATE_GAME:
            points.append("⚠️ High impact due to late game timing")
        elif context == EventContext.TEAMFIGHT:
            points.append("⚔️ Occurred during team engagement")
        
        return points
    
    def _calculate_impact_score(self, event: MatchEvent, importance: EventImportance, context: EventContext) -> float:
        """Calculate numerical impact score for the event."""
        base_score = {
            EventImportance.CRITICAL: 0.9,
            EventImportance.HIGH: 0.7,
            EventImportance.MEDIUM: 0.5,
            EventImportance.LOW: 0.3
        }[importance]
        
        # Adjust for context
        context_multipliers = {
            EventContext.LATE_GAME: 1.2,
            EventContext.TEAMFIGHT: 1.1,
            EventContext.OBJECTIVE: 1.1,
            EventContext.MID_GAME: 1.0,
            EventContext.EARLY_GAME: 0.9,
            EventContext.LANE_PHASE: 0.8
        }
        
        return min(1.0, base_score * context_multipliers.get(context, 1.0))
    
    def _get_participants_involved(self, event: MatchEvent, match_context: Dict[str, Any]) -> List[str]:
        """Get list of participants involved in the event."""
        participants = []
        
        if event.participant_id:
            participants.append(str(event.participant_id))
        if event.killer_id:
            participants.append(str(event.killer_id))
        if event.victim_id:
            participants.append(str(event.victim_id))
        
        participants.extend([str(pid) for pid in event.assisting_participant_ids])
        
        return list(set(participants))  # Remove duplicates
    
    def _is_during_teamfight(self, event: MatchEvent, match_context: Dict[str, Any]) -> bool:
        """Check if event occurred during a team fight."""
        # Simple heuristic: multiple kills/events in a short time window
        recent_events = match_context.get('recent_events', [])
        
        # Look for multiple events within 30 seconds
        time_window = 30 * 1000  # 30 seconds in milliseconds
        recent_kills = [
            e for e in recent_events 
            if abs(e.timestamp - event.timestamp) <= time_window 
            and e.event_type in [EventType.KILL, EventType.DEATH, EventType.ASSIST]
        ]
        
        return len(recent_kills) >= 3
    
    def _is_objective_related(self, event: MatchEvent) -> bool:
        """Check if event is objective-related."""
        return event.event_type in [
            EventType.BARON_KILL, EventType.DRAGON_KILL, 
            EventType.HERALD, EventType.TOWER
        ]


class EventSequencer:
    """Analyzes sequences of events to identify patterns and relationships."""
    
    def __init__(self):
        self.sequence_window = 60000  # 60 seconds in milliseconds
    
    def analyze_event_sequence(self, events: List[MatchEvent]) -> Dict[str, Any]:
        """
        Analyze a sequence of events for patterns and relationships.
        
        Args:
            events: List of events in chronological order
            
        Returns:
            Analysis of event sequences and patterns
        """
        sequences = []
        
        for i, event in enumerate(events):
            # Find related events within time window
            related_events = self._find_related_events(event, events[i:], self.sequence_window)
            
            if len(related_events) > 1:  # At least the current event + one more
                sequence = {
                    'primary_event': event,
                    'related_events': related_events[1:],  # Exclude the primary event
                    'pattern_type': self._identify_pattern_type(related_events),
                    'sequence_score': self._calculate_sequence_score(related_events)
                }
                sequences.append(sequence)
        
        return {
            'sequences': sequences,
            'dominant_patterns': self._identify_dominant_patterns(sequences),
            'turning_points': self._identify_turning_points(sequences)
        }
    
    def _find_related_events(self, primary_event: MatchEvent, events: List[MatchEvent], window: int) -> List[MatchEvent]:
        """Find events related to the primary event within a time window."""
        related = [primary_event]
        
        for event in events[1:]:  # Skip the primary event
            if event.timestamp - primary_event.timestamp > window:
                break
            
            # Check if events are related (same area, participants, etc.)
            if self._are_events_related(primary_event, event):
                related.append(event)
        
        return related
    
    def _are_events_related(self, event1: MatchEvent, event2: MatchEvent) -> bool:
        """Check if two events are related."""
        # Events are related if they:
        # 1. Involve similar participants
        # 2. Occur in similar locations
        # 3. Are of related types
        
        # Check participant overlap
        participants1 = set([event1.participant_id, event1.killer_id, event1.victim_id] + event1.assisting_participant_ids)
        participants2 = set([event2.participant_id, event2.killer_id, event2.victim_id] + event2.assisting_participant_ids)
        participants1.discard(None)
        participants2.discard(None)
        
        if participants1.intersection(participants2):
            return True
        
        # Check event type relationships
        related_types = {
            EventType.BARON_KILL: [EventType.KILL, EventType.ACE, EventType.TOWER],
            EventType.DRAGON_KILL: [EventType.KILL, EventType.TOWER],
            EventType.KILL: [EventType.ASSIST, EventType.DEATH],
            EventType.ACE: [EventType.BARON_KILL, EventType.TOWER, EventType.KILL]
        }
        
        if event2.event_type in related_types.get(event1.event_type, []):
            return True
        
        return False
    
    def _identify_pattern_type(self, events: List[MatchEvent]) -> str:
        """Identify the type of pattern in an event sequence."""
        event_types = [event.event_type for event in events]
        
        # Common patterns
        if EventType.BARON_KILL in event_types and EventType.ACE in event_types:
            return "baron_teamfight"
        elif EventType.DRAGON_KILL in event_types and len([e for e in event_types if e == EventType.KILL]) >= 2:
            return "dragon_contest"
        elif event_types.count(EventType.KILL) >= 3:
            return "teamfight"
        elif EventType.TOWER in event_types and EventType.KILL in event_types:
            return "siege_sequence"
        else:
            return "general_sequence"
    
    def _calculate_sequence_score(self, events: List[MatchEvent]) -> float:
        """Calculate importance score for an event sequence."""
        base_score = len(events) * 0.1  # Base score for number of events
        
        # Add weights for important events
        importance_weights = {
            EventType.BARON_KILL: 0.4,
            EventType.ACE: 0.3,
            EventType.DRAGON_KILL: 0.2,
            EventType.FIRST_BLOOD: 0.2,
            EventType.HERALD: 0.15,
            EventType.KILL: 0.1
        }
        
        for event in events:
            base_score += importance_weights.get(event.event_type, 0.05)
        
        return min(1.0, base_score)
    
    def _identify_dominant_patterns(self, sequences: List[Dict[str, Any]]) -> Dict[str, int]:
        """Identify the most common patterns in the match."""
        pattern_counts = defaultdict(int)
        
        for sequence in sequences:
            pattern_counts[sequence['pattern_type']] += 1
        
        return dict(pattern_counts)
    
    def _identify_turning_points(self, sequences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify major turning points based on event sequences."""
        turning_points = []
        
        for sequence in sequences:
            if sequence['sequence_score'] >= 0.7:  # High-impact sequences
                turning_points.append({
                    'timestamp': sequence['primary_event'].timestamp,
                    'type': sequence['pattern_type'],
                    'impact_score': sequence['sequence_score'],
                    'description': self._describe_turning_point(sequence)
                })
        
        # Sort by impact score
        turning_points.sort(key=lambda x: x['impact_score'], reverse=True)
        return turning_points[:5]  # Return top 5 turning points
    
    def _describe_turning_point(self, sequence: Dict[str, Any]) -> str:
        """Generate description for a turning point."""
        pattern_descriptions = {
            "baron_teamfight": "Major team fight around Baron resulted in significant advantage",
            "dragon_contest": "Contested dragon fight changed team dynamics",
            "teamfight": "Large-scale team engagement shifted momentum",
            "siege_sequence": "Successful siege broke enemy defenses",
            "general_sequence": "Series of events created strategic advantage"
        }
        
        return pattern_descriptions.get(sequence['pattern_type'], "Significant sequence of events")


class HighlightGenerator:
    """Generates match highlights based on event analysis."""
    
    def __init__(self):
        self.classifier = EventClassifier()
        self.sequencer = EventSequencer()
    
    async def generate_highlights(
        self, 
        events: List[MatchEvent], 
        participants: List[Participant],
        max_highlights: int = 10
    ) -> List[MatchHighlight]:
        """
        Generate match highlights from events.
        
        Args:
            events: List of match events
            participants: List of match participants
            max_highlights: Maximum number of highlights to generate
            
        Returns:
            List of MatchHighlight objects
        """
        # Analyze individual events
        event_analyses = []
        match_context = {'recent_events': events}
        
        for event in events:
            analysis = self.classifier.classify_event(event, match_context)
            event_analyses.append(analysis)
        
        # Analyze event sequences
        sequence_analysis = self.sequencer.analyze_event_sequence(events)
        
        # Generate highlights from high-impact events and sequences
        highlights = []
        
        # Add individual high-impact events
        for analysis in event_analyses:
            if analysis.importance in [EventImportance.CRITICAL, EventImportance.HIGH]:
                highlight = await self._create_event_highlight(analysis, participants)
                highlights.append(highlight)
        
        # Add sequence-based highlights
        for sequence in sequence_analysis['sequences']:
            if sequence['sequence_score'] >= 0.6:
                highlight = await self._create_sequence_highlight(sequence, participants)
                highlights.append(highlight)
        
        # Sort by importance and deduplicate
        highlights.sort(key=lambda x: (x.importance.value, -x.timestamp), reverse=True)
        highlights = self._deduplicate_highlights(highlights)
        
        return highlights[:max_highlights]
    
    async def _create_event_highlight(self, analysis: EventAnalysis, participants: List[Participant]) -> MatchHighlight:
        """Create a highlight from an event analysis."""
        event = analysis.event
        time_min = event.timestamp // (60 * 1000)
        time_sec = (event.timestamp % (60 * 1000)) // 1000
        
        # Generate title based on event type
        titles = {
            EventType.FIRST_BLOOD: "First Blood",
            EventType.BARON_KILL: "Baron Take",
            EventType.DRAGON_KILL: "Dragon Secured",
            EventType.ACE: "Team ACE",
            EventType.HERALD: "Rift Herald",
            EventType.MULTIKILL: "Multikill"
        }
        
        title = titles.get(event.event_type, "Key Event")
        
        # Get NLP pipeline for enhanced description
        nlp = await get_nlp_pipeline()
        enhanced_description = analysis.explanation
        
        return MatchHighlight(
            timestamp=event.timestamp,
            duration=30,  # Default 30 second highlight
            title=f"{title} ({time_min}:{time_sec:02d})",
            description=enhanced_description,
            importance=analysis.importance,
            events=[event],
            key_participants=analysis.participants_involved,
            analysis="\n".join(analysis.bullet_points)
        )
    
    async def _create_sequence_highlight(self, sequence: Dict[str, Any], participants: List[Participant]) -> MatchHighlight:
        """Create a highlight from an event sequence."""
        primary_event = sequence['primary_event']
        related_events = sequence['related_events']
        all_events = [primary_event] + related_events
        
        # Calculate duration based on event span
        start_time = min(event.timestamp for event in all_events)
        end_time = max(event.timestamp for event in all_events)
        duration = min(120, max(30, (end_time - start_time) // 1000))  # 30s to 2min
        
        time_min = start_time // (60 * 1000)
        time_sec = (start_time % (60 * 1000)) // 1000
        
        # Generate title based on pattern
        pattern_titles = {
            "baron_teamfight": "Baron Team Fight",
            "dragon_contest": "Dragon Contest",
            "teamfight": "Team Fight",
            "siege_sequence": "Siege Play",
            "general_sequence": "Key Sequence"
        }
        
        title = pattern_titles.get(sequence['pattern_type'], "Event Sequence")
        
        # Determine importance based on sequence score
        if sequence['sequence_score'] >= 0.8:
            importance = EventImportance.CRITICAL
        elif sequence['sequence_score'] >= 0.6:
            importance = EventImportance.HIGH
        else:
            importance = EventImportance.MEDIUM
        
        # Collect all participants involved
        all_participants = set()
        for event in all_events:
            if event.participant_id:
                all_participants.add(str(event.participant_id))
            if event.killer_id:
                all_participants.add(str(event.killer_id))
            if event.victim_id:
                all_participants.add(str(event.victim_id))
            all_participants.update(str(pid) for pid in event.assisting_participant_ids)
        
        return MatchHighlight(
            timestamp=start_time,
            duration=duration,
            title=f"{title} ({time_min}:{time_sec:02d})",
            description=sequence.get('description', f"Sequence of {len(all_events)} related events"),
            importance=importance,
            events=all_events,
            key_participants=list(all_participants),
            analysis=f"Pattern: {sequence['pattern_type']}, Impact Score: {sequence['sequence_score']:.2f}"
        )
    
    def _deduplicate_highlights(self, highlights: List[MatchHighlight]) -> List[MatchHighlight]:
        """Remove duplicate or overlapping highlights."""
        deduplicated = []
        
        for highlight in highlights:
            # Check if this highlight overlaps significantly with existing ones
            is_duplicate = False
            
            for existing in deduplicated:
                # Calculate overlap
                start1, end1 = highlight.timestamp, highlight.timestamp + (highlight.duration * 1000)
                start2, end2 = existing.timestamp, existing.timestamp + (existing.duration * 1000)
                
                overlap_start = max(start1, start2)
                overlap_end = min(end1, end2)
                overlap_duration = max(0, overlap_end - overlap_start)
                
                # If more than 50% overlap, consider it a duplicate
                if overlap_duration > 0.5 * min(end1 - start1, end2 - start2):
                    # Keep the more important one
                    if highlight.importance.value > existing.importance.value:
                        deduplicated.remove(existing)
                        break
                    else:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                deduplicated.append(highlight)
        
        return deduplicated


class EventDetectionService:
    """
    Main service for event detection and analysis.
    
    Coordinates all event detection components and provides
    a unified interface for event analysis capabilities.
    """
    
    def __init__(self):
        self.classifier = EventClassifier()
        self.sequencer = EventSequencer()
        self.highlight_generator = HighlightGenerator()
        self.nlp = None  # Will be initialized asynchronously
        
        logger.info("Event Detection Service initialized")
    
    async def initialize(self):
        """Initialize the service with NLP components."""
        self.nlp = await get_nlp_pipeline()
        logger.info("Event Detection Service initialization complete")
    
    async def analyze_live_events(
        self, 
        events: List[MatchEvent], 
        participants: List[Participant]
    ) -> Dict[str, Any]:
        """
        Analyze live match events in real-time.
        
        Args:
            events: Current list of match events
            participants: Match participants
            
        Returns:
            Comprehensive analysis of current match state
        """
        if not events:
            return {"status": "no_events", "analysis": {}}
        
        # Get recent events (last 5 minutes)
        current_time = max(event.timestamp for event in events)
        recent_events = [
            event for event in events 
            if current_time - event.timestamp <= 5 * 60 * 1000
        ]
        
        # Analyze recent events
        match_context = {'recent_events': events}
        recent_analyses = []
        
        for event in recent_events:
            analysis = self.classifier.classify_event(event, match_context)
            recent_analyses.append(analysis)
        
        # Generate current highlights
        highlights = await self.highlight_generator.generate_highlights(events, participants, max_highlights=5)
        
        # Identify current momentum
        momentum = self._analyze_momentum(recent_analyses)
        
        return {
            "status": "active",
            "recent_events": len(recent_events),
            "recent_analyses": recent_analyses,
            "current_highlights": highlights,
            "momentum": momentum,
            "key_events_summary": [analysis.explanation for analysis in recent_analyses if analysis.importance in [EventImportance.CRITICAL, EventImportance.HIGH]]
        }
    
    async def generate_match_summary(
        self, 
        events: List[MatchEvent], 
        participants: List[Participant]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive match summary with highlights and analysis.
        
        Args:
            events: All match events
            participants: Match participants
            
        Returns:
            Complete match summary and analysis
        """
        # Analyze all events
        match_context = {'recent_events': events}
        all_analyses = []
        
        for event in events:
            analysis = self.classifier.classify_event(event, match_context)
            all_analyses.append(analysis)
        
        # Generate highlights
        highlights = await self.highlight_generator.generate_highlights(events, participants)
        
        # Analyze event sequences
        sequence_analysis = self.sequencer.analyze_event_sequence(events)
        
        # Generate NLP summary if available
        nlp_summary = None
        if self.nlp:
            nlp_summary = await self.nlp.generate_match_summary(events, participants)
        
        return {
            "total_events": len(events),
            "event_analyses": all_analyses,
            "highlights": highlights,
            "sequence_analysis": sequence_analysis,
            "nlp_summary": nlp_summary,
            "key_statistics": self._calculate_match_statistics(all_analyses),
            "turning_points": sequence_analysis['turning_points']
        }
    
    def _analyze_momentum(self, analyses: List[EventAnalysis]) -> Dict[str, Any]:
        """Analyze current match momentum based on recent events."""
        if not analyses:
            return {"status": "neutral", "trend": "stable"}
        
        # Calculate momentum score based on recent events
        momentum_score = 0
        for analysis in analyses:
            if analysis.importance == EventImportance.CRITICAL:
                momentum_score += 3
            elif analysis.importance == EventImportance.HIGH:
                momentum_score += 2
            elif analysis.importance == EventImportance.MEDIUM:
                momentum_score += 1
        
        # Determine momentum status
        if momentum_score >= 6:
            status = "high_action"
        elif momentum_score >= 3:
            status = "moderate_action"
        else:
            status = "low_action"
        
        # Determine trend (increasing/decreasing activity)
        if len(analyses) >= 2:
            recent_score = sum(3 if a.importance == EventImportance.CRITICAL else 2 if a.importance == EventImportance.HIGH else 1 for a in analyses[-2:])
            earlier_score = sum(3 if a.importance == EventImportance.CRITICAL else 2 if a.importance == EventImportance.HIGH else 1 for a in analyses[:-2]) if len(analyses) > 2 else 0
            
            if recent_score > earlier_score:
                trend = "increasing"
            elif recent_score < earlier_score:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "status": status,
            "trend": trend,
            "score": momentum_score,
            "recent_critical_events": len([a for a in analyses if a.importance == EventImportance.CRITICAL])
        }
    
    def _calculate_match_statistics(self, analyses: List[EventAnalysis]) -> Dict[str, Any]:
        """Calculate match statistics from event analyses."""
        total_events = len(analyses)
        
        importance_counts = {
            EventImportance.CRITICAL: 0,
            EventImportance.HIGH: 0,
            EventImportance.MEDIUM: 0,
            EventImportance.LOW: 0
        }
        
        context_counts = defaultdict(int)
        
        for analysis in analyses:
            importance_counts[analysis.importance] += 1
            context_counts[analysis.context] += 1
        
        return {
            "total_events": total_events,
            "importance_distribution": {k.value: v for k, v in importance_counts.items()},
            "context_distribution": dict(context_counts),
            "average_impact_score": np.mean([a.impact_score for a in analyses]) if analyses else 0,
            "high_impact_events": importance_counts[EventImportance.CRITICAL] + importance_counts[EventImportance.HIGH]
        }


# Global service instance
_event_service: Optional[EventDetectionService] = None


async def get_event_service() -> EventDetectionService:
    """Get the global event detection service instance."""
    global _event_service
    if _event_service is None:
        _event_service = EventDetectionService()
        await _event_service.initialize()
    return _event_service


if __name__ == "__main__":
    async def main():
        # Test the event detection system
        service = await get_event_service()
        
        # Create sample events for testing
        sample_events = [
            MatchEvent(
                event_type=EventType.FIRST_BLOOD,
                timestamp=180000,  # 3 minutes
                participant_id=1,
                killer_id=1,
                victim_id=6
            ),
            MatchEvent(
                event_type=EventType.DRAGON_KILL,
                timestamp=420000,  # 7 minutes
                participant_id=1
            ),
            MatchEvent(
                event_type=EventType.BARON_KILL,
                timestamp=1800000,  # 30 minutes
                participant_id=1
            )
        ]
        
        # Test live event analysis
        live_analysis = await service.analyze_live_events(sample_events, [])
        print(f"Live analysis: {live_analysis['status']}")
        print(f"Recent events: {live_analysis['recent_events']}")
        
        # Test match summary generation
        match_summary = await service.generate_match_summary(sample_events, [])
        print(f"Total events analyzed: {match_summary['total_events']}")
        print(f"Highlights generated: {len(match_summary['highlights'])}")
    
    asyncio.run(main())

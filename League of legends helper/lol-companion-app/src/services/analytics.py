"""
Advanced analytics and data processing for League of Legends matches.

This module provides comprehensive analytics including performance metrics,
trend analysis, predictive modeling, and statistical insights for matches,
players, and champions.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import statistics

from ..config import get_config
from ..models import (
    HistoricalMatch, LiveMatch, Participant, Team, MatchEvent,
    Champion, Item, ParticipantStats
)
from ..data.dragontail import get_dragontail_manager
from ..services.event_detection import get_event_service
from ..nlp import get_nlp_pipeline

logger = logging.getLogger(__name__)
config = get_config()


class MetricType(Enum):
    """Types of performance metrics."""
    DAMAGE = "damage"
    SURVIVAL = "survival"
    OBJECTIVE = "objective"
    VISION = "vision"
    FARMING = "farming"
    TEAMWORK = "teamwork"


@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    metric_type: MetricType
    value: float
    percentile: float
    trend: str  # improving, declining, stable
    benchmark: float


@dataclass
class PlayerAnalytics:
    """Comprehensive player analytics."""
    player_id: str
    champion: str
    role: str
    performance_score: float
    metrics: Dict[MetricType, PerformanceMetric]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    comparison_to_role: Dict[str, float]


@dataclass
class TeamAnalytics:
    """Team-level analytics."""
    team_id: int
    composition_score: float
    synergy_rating: float
    objective_control: float
    teamfight_potential: float
    scaling_potential: float
    weaknesses: List[str]
    strengths: List[str]


@dataclass
class MatchAnalytics:
    """Comprehensive match analytics."""
    match_id: str
    duration: int
    phase_analysis: Dict[str, Any]
    momentum_shifts: List[Dict[str, Any]]
    key_decisions: List[Dict[str, Any]]
    team_analytics: Dict[int, TeamAnalytics]
    player_analytics: Dict[str, PlayerAnalytics]
    predictive_insights: Dict[str, Any]


class PerformanceCalculator:
    """Calculates various performance metrics and analytics."""
    
    def __init__(self):
        self.dragontail = get_dragontail_manager()
        
        # Role-specific benchmarks (would be loaded from historical data)
        self.role_benchmarks = {
            "TOP": {
                "damage_per_minute": 400,
                "cs_per_minute": 7.5,
                "vision_score_per_minute": 1.2,
                "kill_participation": 0.6
            },
            "JUNGLE": {
                "damage_per_minute": 350,
                "cs_per_minute": 5.0,
                "vision_score_per_minute": 1.8,
                "kill_participation": 0.8
            },
            "MID": {
                "damage_per_minute": 500,
                "cs_per_minute": 8.0,
                "vision_score_per_minute": 1.0,
                "kill_participation": 0.7
            },
            "ADC": {
                "damage_per_minute": 600,
                "cs_per_minute": 9.0,
                "vision_score_per_minute": 0.8,
                "kill_participation": 0.6
            },
            "SUPPORT": {
                "damage_per_minute": 200,
                "cs_per_minute": 2.0,
                "vision_score_per_minute": 2.5,
                "kill_participation": 0.9
            }
        }
    
    def calculate_player_performance(self, participant: Participant, match_duration: int) -> PlayerAnalytics:
        """
        Calculate comprehensive performance analytics for a player.
        
        Args:
            participant: Player data from match
            match_duration: Match duration in seconds
            
        Returns:
            PlayerAnalytics object with comprehensive metrics
        """
        stats = participant.stats
        duration_minutes = match_duration / 60
        
        # Calculate core metrics
        metrics = {}
        
        # Damage metrics
        damage_per_minute = stats.total_damage_dealt / duration_minutes
        damage_per_gold = stats.total_damage_dealt / max(1, stats.gold_earned)
        
        metrics[MetricType.DAMAGE] = PerformanceMetric(
            metric_type=MetricType.DAMAGE,
            value=damage_per_minute,
            percentile=self._calculate_percentile(damage_per_minute, "damage_per_minute", participant.role),
            trend="stable",  # Would be calculated from historical data
            benchmark=self.role_benchmarks.get(participant.role, {}).get("damage_per_minute", 400)
        )
        
        # Survival metrics
        survival_score = self._calculate_survival_score(stats)
        metrics[MetricType.SURVIVAL] = PerformanceMetric(
            metric_type=MetricType.SURVIVAL,
            value=survival_score,
            percentile=self._calculate_percentile(survival_score, "survival_score", participant.role),
            trend="stable",
            benchmark=0.7
        )
        
        # Farming metrics
        cs_per_minute = stats.cs / duration_minutes
        metrics[MetricType.FARMING] = PerformanceMetric(
            metric_type=MetricType.FARMING,
            value=cs_per_minute,
            percentile=self._calculate_percentile(cs_per_minute, "cs_per_minute", participant.role),
            trend="stable",
            benchmark=self.role_benchmarks.get(participant.role, {}).get("cs_per_minute", 6.0)
        )
        
        # Vision metrics
        vision_per_minute = stats.vision_score / duration_minutes
        metrics[MetricType.VISION] = PerformanceMetric(
            metric_type=MetricType.VISION,
            value=vision_per_minute,
            percentile=self._calculate_percentile(vision_per_minute, "vision_per_minute", participant.role),
            trend="stable",
            benchmark=self.role_benchmarks.get(participant.role, {}).get("vision_score_per_minute", 1.5)
        )
        
        # Calculate overall performance score
        performance_score = self._calculate_overall_performance_score(metrics, stats)
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self._identify_strengths_weaknesses(metrics, participant.role)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, participant.role, stats)
        
        # Compare to role average
        role_comparison = self._calculate_role_comparison(metrics, participant.role)
        
        return PlayerAnalytics(
            player_id=participant.summoner_name,
            champion=participant.champion_name,
            role=participant.role,
            performance_score=performance_score,
            metrics=metrics,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            comparison_to_role=role_comparison
        )
    
    def _calculate_survival_score(self, stats: ParticipantStats) -> float:
        """Calculate survival score based on deaths and damage taken."""
        if stats.deaths == 0:
            return 1.0
        
        # Base score from deaths (fewer deaths = higher score)
        death_score = max(0, 1.0 - (stats.deaths / 10))
        
        # Adjust for damage taken (lower damage taken = higher score)
        damage_taken_score = max(0, 1.0 - (stats.total_damage_taken / 50000))
        
        return (death_score + damage_taken_score) / 2
    
    def _calculate_percentile(self, value: float, metric_name: str, role: str) -> float:
        """Calculate percentile rank for a metric (mock implementation)."""
        # In a real implementation, this would compare against historical data
        # For now, return a mock percentile based on role benchmarks
        benchmark = self.role_benchmarks.get(role, {}).get(metric_name, 1.0)
        
        if value >= benchmark * 1.2:
            return 0.9  # Top 10%
        elif value >= benchmark:
            return 0.7  # Top 30%
        elif value >= benchmark * 0.8:
            return 0.5  # Median
        elif value >= benchmark * 0.6:
            return 0.3  # Bottom 30%
        else:
            return 0.1  # Bottom 10%
    
    def _calculate_overall_performance_score(self, metrics: Dict[MetricType, PerformanceMetric], stats: ParticipantStats) -> float:
        """Calculate overall performance score."""
        # Weight different metrics based on role importance
        weights = {
            MetricType.DAMAGE: 0.3,
            MetricType.SURVIVAL: 0.25,
            MetricType.FARMING: 0.2,
            MetricType.VISION: 0.15,
            MetricType.TEAMWORK: 0.1
        }
        
        weighted_score = 0
        for metric_type, metric in metrics.items():
            weight = weights.get(metric_type, 0.1)
            weighted_score += metric.percentile * weight
        
        # Adjust for KDA
        kda_score = (stats.kills + stats.assists) / max(1, stats.deaths)
        kda_normalized = min(1.0, kda_score / 5.0)  # Normalize to 0-1
        
        return (weighted_score * 0.8) + (kda_normalized * 0.2)
    
    def _identify_strengths_weaknesses(self, metrics: Dict[MetricType, PerformanceMetric], role: str) -> Tuple[List[str], List[str]]:
        """Identify player strengths and weaknesses."""
        strengths = []
        weaknesses = []
        
        for metric_type, metric in metrics.items():
            if metric.percentile >= 0.8:
                strengths.append(f"Excellent {metric_type.value} performance")
            elif metric.percentile <= 0.3:
                weaknesses.append(f"Below average {metric_type.value}")
        
        return strengths, weaknesses
    
    def _generate_recommendations(self, metrics: Dict[MetricType, PerformanceMetric], role: str, stats: ParticipantStats) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Vision recommendations
        if metrics[MetricType.VISION].percentile < 0.5:
            recommendations.append("Focus on improving vision control and ward placement")
        
        # Farming recommendations
        if metrics[MetricType.FARMING].percentile < 0.5:
            recommendations.append("Work on last-hitting and farming efficiency")
        
        # Survival recommendations
        if metrics[MetricType.SURVIVAL].percentile < 0.5:
            recommendations.append("Improve positioning and map awareness to reduce deaths")
        
        # Damage recommendations
        if metrics[MetricType.DAMAGE].percentile < 0.5:
            recommendations.append("Focus on dealing more damage in team fights")
        
        return recommendations
    
    def _calculate_role_comparison(self, metrics: Dict[MetricType, PerformanceMetric], role: str) -> Dict[str, float]:
        """Calculate comparison to role average."""
        comparison = {}
        
        for metric_type, metric in metrics.items():
            comparison[f"{metric_type.value}_vs_role"] = metric.percentile
        
        return comparison


class TeamAnalyzer:
    """Analyzes team composition and synergy."""
    
    def __init__(self):
        self.dragontail = get_dragontail_manager()
    
    async def analyze_team_composition(self, participants: List[Participant]) -> TeamAnalytics:
        """
        Analyze team composition and synergy.
        
        Args:
            participants: List of team participants
            
        Returns:
            TeamAnalytics object
        """
        # Group participants by team
        teams = defaultdict(list)
        for participant in participants:
            teams[participant.team_id].append(participant)
        
        # Analyze each team
        team_analytics = {}
        for team_id, team_participants in teams.items():
            analytics = await self._analyze_single_team(team_participants)
            team_analytics[team_id] = analytics
        
        # Return the first team's analytics (would be expanded for multiple teams)
        return list(team_analytics.values())[0] if team_analytics else None
    
    async def _analyze_single_team(self, participants: List[Participant]) -> TeamAnalytics:
        """Analyze a single team's composition."""
        # Load champion data
        champions = await self.dragontail.load_champions()
        
        # Analyze composition
        composition_score = self._calculate_composition_score(participants, champions)
        synergy_rating = self._calculate_synergy_rating(participants, champions)
        objective_control = self._calculate_objective_control(participants, champions)
        teamfight_potential = self._calculate_teamfight_potential(participants, champions)
        scaling_potential = self._calculate_scaling_potential(participants, champions)
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self._identify_team_strengths_weaknesses(
            participants, champions, composition_score, synergy_rating
        )
        
        return TeamAnalytics(
            team_id=participants[0].team_id if participants else 0,
            composition_score=composition_score,
            synergy_rating=synergy_rating,
            objective_control=objective_control,
            teamfight_potential=teamfight_potential,
            scaling_potential=scaling_potential,
            weaknesses=weaknesses,
            strengths=strengths
        )
    
    def _calculate_composition_score(self, participants: List[Participant], champions: Dict[str, Champion]) -> float:
        """Calculate team composition score."""
        score = 0.0
        
        # Check role distribution
        roles = [p.role for p in participants]
        if len(set(roles)) == 5:  # All roles covered
            score += 0.3
        
        # Check champion diversity
        champion_names = [p.champion_name for p in participants]
        if len(set(champion_names)) == len(champion_names):  # No duplicates
            score += 0.2
        
        # Check damage type balance
        ad_champions = sum(1 for p in participants if "Fighter" in champions.get(p.champion_name, Champion()).tags or "Marksman" in champions.get(p.champion_name, Champion()).tags)
        ap_champions = sum(1 for p in participants if "Mage" in champions.get(p.champion_name, Champion()).tags)
        
        if 1 <= ad_champions <= 3 and 1 <= ap_champions <= 3:
            score += 0.3
        
        # Check tankiness
        tanks = sum(1 for p in participants if "Tank" in champions.get(p.champion_name, Champion()).tags)
        if tanks >= 1:
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_synergy_rating(self, participants: List[Participant], champions: Dict[str, Champion]) -> float:
        """Calculate team synergy rating."""
        # This would involve analyzing champion interactions, combos, etc.
        # For now, return a mock rating
        return 0.75
    
    def _calculate_objective_control(self, participants: List[Participant], champions: Dict[str, Champion]) -> float:
        """Calculate objective control potential."""
        # Analyze champions' ability to secure objectives
        objective_champions = 0
        
        for participant in participants:
            champion = champions.get(participant.champion_name)
            if champion:
                # Champions with good objective control (simplified)
                if any(tag in champion.tags for tag in ["Fighter", "Marksman", "Assassin"]):
                    objective_champions += 1
        
        return min(1.0, objective_champions / 3.0)
    
    def _calculate_teamfight_potential(self, participants: List[Participant], champions: Dict[str, Champion]) -> float:
        """Calculate teamfight potential."""
        # Analyze team's teamfight capabilities
        teamfight_score = 0.0
        
        for participant in participants:
            champion = champions.get(participant.champion_name)
            if champion:
                # Champions good in teamfights
                if any(tag in champion.tags for tag in ["Tank", "Mage", "Support"]):
                    teamfight_score += 0.2
        
        return min(1.0, teamfight_score)
    
    def _calculate_scaling_potential(self, participants: List[Participant], champions: Dict[str, Champion]) -> float:
        """Calculate late game scaling potential."""
        # Analyze team's late game strength
        scaling_score = 0.0
        
        for participant in participants:
            champion = champions.get(participant.champion_name)
            if champion:
                # Champions that scale well (simplified)
                if any(tag in champion.tags for tag in ["Marksman", "Mage"]):
                    scaling_score += 0.2
        
        return min(1.0, scaling_score)
    
    def _identify_team_strengths_weaknesses(self, participants: List[Participant], champions: Dict[str, Champion], composition_score: float, synergy_rating: float) -> Tuple[List[str], List[str]]:
        """Identify team strengths and weaknesses."""
        strengths = []
        weaknesses = []
        
        if composition_score >= 0.8:
            strengths.append("Well-balanced team composition")
        elif composition_score < 0.5:
            weaknesses.append("Unbalanced team composition")
        
        if synergy_rating >= 0.8:
            strengths.append("High team synergy")
        elif synergy_rating < 0.5:
            weaknesses.append("Low team synergy")
        
        return strengths, weaknesses


class MatchAnalyzer:
    """Main analytics engine for comprehensive match analysis."""
    
    def __init__(self):
        self.performance_calculator = PerformanceCalculator()
        self.team_analyzer = TeamAnalyzer()
        self.event_service = None
        self.nlp_pipeline = None
    
    async def initialize(self):
        """Initialize the match analyzer."""
        self.event_service = await get_event_service()
        self.nlp_pipeline = await get_nlp_pipeline()
        logger.info("Match Analyzer initialized")
    
    async def analyze_match(self, match: Union[HistoricalMatch, LiveMatch]) -> MatchAnalytics:
        """
        Perform comprehensive match analysis.
        
        Args:
            match: Match data to analyze
            
        Returns:
            Comprehensive MatchAnalytics object
        """
        # Analyze individual players
        player_analytics = {}
        for participant in match.participants:
            analytics = self.performance_calculator.calculate_player_performance(
                participant, match.game_duration if hasattr(match, 'game_duration') else 1800
            )
            player_analytics[participant.summoner_name] = analytics
        
        # Analyze teams
        team_analytics = {}
        teams = defaultdict(list)
        for participant in match.participants:
            teams[participant.team_id].append(participant)
        
        for team_id, team_participants in teams.items():
            analytics = await self.team_analyzer.analyze_team_composition(team_participants)
            team_analytics[team_id] = analytics
        
        # Analyze match phases
        phase_analysis = await self._analyze_match_phases(match)
        
        # Identify momentum shifts
        momentum_shifts = await self._identify_momentum_shifts(match)
        
        # Identify key decisions
        key_decisions = await self._identify_key_decisions(match)
        
        # Generate predictive insights
        predictive_insights = await self._generate_predictive_insights(match, player_analytics, team_analytics)
        
        return MatchAnalytics(
            match_id=getattr(match, 'match_id', getattr(match, 'game_id', 'unknown')),
            duration=getattr(match, 'game_duration', getattr(match, 'game_length', 1800)),
            phase_analysis=phase_analysis,
            momentum_shifts=momentum_shifts,
            key_decisions=key_decisions,
            team_analytics=team_analytics,
            player_analytics=player_analytics,
            predictive_insights=predictive_insights
        )
    
    async def _analyze_match_phases(self, match: Union[HistoricalMatch, LiveMatch]) -> Dict[str, Any]:
        """Analyze different phases of the match."""
        duration = getattr(match, 'game_duration', getattr(match, 'game_length', 1800))
        
        phases = {
            "early_game": {"start": 0, "end": duration * 0.25},
            "mid_game": {"start": duration * 0.25, "end": duration * 0.75},
            "late_game": {"start": duration * 0.75, "end": duration}
        }
        
        phase_analysis = {}
        
        for phase_name, phase_times in phases.items():
            phase_analysis[phase_name] = {
                "duration": phase_times["end"] - phase_times["start"],
                "key_events": [],  # Would extract from timeline
                "team_performance": {},  # Would analyze team performance in this phase
                "momentum": "neutral"  # Would calculate momentum for this phase
            }
        
        return phase_analysis
    
    async def _identify_momentum_shifts(self, match: Union[HistoricalMatch, LiveMatch]) -> List[Dict[str, Any]]:
        """Identify key momentum shifts in the match."""
        # This would analyze the timeline for significant events
        # For now, return mock data
        return [
            {
                "timestamp": 600000,  # 10 minutes
                "description": "First dragon secured by blue team",
                "impact": "medium",
                "team_affected": 100
            },
            {
                "timestamp": 1800000,  # 30 minutes
                "description": "Baron fight won by red team",
                "impact": "high",
                "team_affected": 200
            }
        ]
    
    async def _identify_key_decisions(self, match: Union[HistoricalMatch, LiveMatch]) -> List[Dict[str, Any]]:
        """Identify key strategic decisions in the match."""
        # This would analyze decision-making patterns
        return [
            {
                "timestamp": 900000,  # 15 minutes
                "decision": "Early Baron attempt",
                "outcome": "successful",
                "impact": "high"
            }
        ]
    
    async def _generate_predictive_insights(self, match: Union[HistoricalMatch, LiveMatch], player_analytics: Dict[str, PlayerAnalytics], team_analytics: Dict[int, TeamAnalytics]) -> Dict[str, Any]:
        """Generate predictive insights about the match."""
        insights = {
            "win_probability": {},  # Would calculate based on current state
            "key_factors": [],  # Factors that will likely determine outcome
            "recommendations": []  # Strategic recommendations
        }
        
        # Analyze team strengths
        for team_id, analytics in team_analytics.items():
            if analytics.composition_score > 0.8:
                insights["key_factors"].append(f"Team {team_id} has strong composition")
        
        # Analyze player performances
        for player_id, analytics in player_analytics.items():
            if analytics.performance_score > 0.8:
                insights["key_factors"].append(f"{player_id} is performing exceptionally")
        
        return insights


class TrendAnalyzer:
    """Analyzes trends across multiple matches and time periods."""
    
    def __init__(self):
        self.performance_calculator = PerformanceCalculator()
    
    def analyze_player_trends(self, matches: List[HistoricalMatch], player_id: str) -> Dict[str, Any]:
        """Analyze trends for a specific player across multiple matches."""
        player_matches = []
        
        for match in matches:
            for participant in match.participants:
                if participant.summoner_name == player_id:
                    player_matches.append((match, participant))
                    break
        
        if not player_matches:
            return {"error": "No matches found for player"}
        
        # Calculate performance over time
        performances = []
        for match, participant in player_matches:
            performance = self.performance_calculator.calculate_player_performance(
                participant, match.game_duration
            )
            performances.append({
                "match_id": match.match_id,
                "date": match.game_creation,
                "performance_score": performance.performance_score,
                "champion": participant.champion_name,
                "role": participant.role
            })
        
        # Sort by date
        performances.sort(key=lambda x: x["date"])
        
        # Calculate trends
        performance_scores = [p["performance_score"] for p in performances]
        
        trend_analysis = {
            "total_matches": len(performances),
            "average_performance": statistics.mean(performance_scores),
            "performance_trend": self._calculate_trend(performance_scores),
            "best_performance": max(performances, key=lambda x: x["performance_score"]),
            "worst_performance": min(performances, key=lambda x: x["performance_score"]),
            "champion_diversity": len(set(p["champion"] for p in performances)),
            "recent_form": performance_scores[-5:] if len(performance_scores) >= 5 else performance_scores
        }
        
        return trend_analysis
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values."""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.05:
            return "improving"
        elif slope < -0.05:
            return "declining"
        else:
            return "stable"


# Global instances
_match_analyzer: Optional[MatchAnalyzer] = None
_trend_analyzer: Optional[TrendAnalyzer] = None


async def get_match_analyzer() -> MatchAnalyzer:
    """Get the global match analyzer instance."""
    global _match_analyzer
    if _match_analyzer is None:
        _match_analyzer = MatchAnalyzer()
        await _match_analyzer.initialize()
    return _match_analyzer


def get_trend_analyzer() -> TrendAnalyzer:
    """Get the global trend analyzer instance."""
    global _trend_analyzer
    if _trend_analyzer is None:
        _trend_analyzer = TrendAnalyzer()
    return _trend_analyzer


# Utility functions
async def analyze_player_performance(player_id: str, matches: List[HistoricalMatch]) -> Dict[str, Any]:
    """Analyze a player's performance across multiple matches."""
    trend_analyzer = get_trend_analyzer()
    return trend_analyzer.analyze_player_trends(matches, player_id)


async def compare_players(player1_id: str, player2_id: str, matches: List[HistoricalMatch]) -> Dict[str, Any]:
    """Compare two players' performance."""
    trend_analyzer = get_trend_analyzer()
    
    player1_trends = trend_analyzer.analyze_player_trends(matches, player1_id)
    player2_trends = trend_analyzer.analyze_player_trends(matches, player2_id)
    
    return {
        "player1": player1_trends,
        "player2": player2_trends,
        "comparison": {
            "performance_difference": player1_trends.get("average_performance", 0) - player2_trends.get("average_performance", 0),
            "trend_comparison": {
                "player1_trend": player1_trends.get("performance_trend", "unknown"),
                "player2_trend": player2_trends.get("performance_trend", "unknown")
            }
        }
    }


# Global analytics service instance
_analytics_service: Optional['AnalyticsService'] = None


class AnalyticsService:
    """Main analytics service for comprehensive data analysis."""
    
    def __init__(self):
        self.match_analyzer: Optional[MatchAnalyzer] = None
        self.trend_analyzer: Optional[TrendAnalyzer] = None
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the analytics service."""
        try:
            self.match_analyzer = await get_match_analyzer()
            self.trend_analyzer = get_trend_analyzer()
            self.initialized = True
            logger.info("Analytics service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize analytics service: {e}")
            return False
    
    def get_match_analyzer(self) -> Optional[MatchAnalyzer]:
        """Get the match analyzer instance."""
        return self.match_analyzer
    
    def get_trend_analyzer(self) -> Optional[TrendAnalyzer]:
        """Get the trend analyzer instance."""
        return self.trend_analyzer


async def get_analytics_service() -> AnalyticsService:
    """Get or create the global analytics service instance."""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
        await _analytics_service.initialize()
    return _analytics_service


if __name__ == "__main__":
    async def main():
        # Test the analytics system
        analyzer = await get_match_analyzer()
        print("Analytics system initialized successfully")
        
        # Test trend analyzer
        trend_analyzer = get_trend_analyzer()
        print("Trend analyzer initialized successfully")
        
        # Test analytics service
        service = await get_analytics_service()
        print("Analytics service initialized successfully")
    
    asyncio.run(main())

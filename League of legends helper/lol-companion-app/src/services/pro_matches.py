"""
Professional match tracking and analysis for LCS and other competitive leagues.

This module provides tracking and analysis of professional League of Legends
matches with highlight detection, player performance analytics, and meta analysis.
Fixed ProPlayer initialization issues.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import requests
from bs4 import BeautifulSoup
import json

from ..config import get_config
from ..models import HistoricalMatch, Team, Participant, MatchEvent
from ..api.riot_client import RiotAPIClient
from ..services.event_detection import get_event_service
from ..nlp import get_nlp_pipeline

logger = logging.getLogger(__name__)
config = get_config()


class League(Enum):
    """Professional league identifiers."""
    LCS = "lcs"
    LEC = "lec"
    LCK = "lck"
    LPL = "lpl"
    WORLDS = "worlds"
    MSI = "msi"


@dataclass
class ProPlayer:
    """Professional player information."""
    player_id: str
    summoner_name: str
    real_name: str
    team: str
    role: str
    country: str
    league: League


@dataclass
class ProTeam:
    """Professional team information."""
    team_id: str
    name: str
    abbreviation: str
    league: League
    players: List[ProPlayer]
    current_split_record: Dict[str, int]  # wins, losses


@dataclass
class ProMatch:
    """Professional match information."""
    match_id: str
    tournament: str
    league: League
    team1: ProTeam
    team2: ProTeam
    scheduled_time: datetime
    actual_start_time: Optional[datetime]
    match_data: Optional[HistoricalMatch]
    bo_format: int  # Best of X
    current_game: int
    status: str  # scheduled, live, completed


@dataclass
class PlayerPerformance:
    """Player performance analytics."""
    player: ProPlayer
    champion: str
    kda: Tuple[int, int, int]  # kills, deaths, assists
    cs: int
    gold_earned: int
    damage_dealt: int
    vision_score: int
    performance_score: float  # Calculated performance metric


@dataclass
class MatchHighlight:
    """Professional match highlight."""
    timestamp: int
    description: str
    clip_url: Optional[str]
    players_involved: List[str]
    impact_rating: float


class ProMatchTracker:
    """
    Tracks professional League of Legends matches and provides analysis.
    
    Integrates with various data sources to provide comprehensive
    professional scene coverage and analysis.
    """
    
    def __init__(self):
        self.event_service = None
        self.nlp_pipeline = None
        self.riot_client = None
        
        # Mock data for demonstration (would be replaced with real APIs)
        self._mock_teams = self._initialize_mock_teams()
        self._mock_schedule = self._initialize_mock_schedule()
        
    async def initialize(self):
        """Initialize the pro match tracker."""
        self.event_service = await get_event_service()
        self.nlp_pipeline = await get_nlp_pipeline()
        self.riot_client = RiotAPIClient()
        
        logger.info("Pro Match Tracker initialized")
    
    def _initialize_mock_teams(self) -> Dict[str, ProTeam]:
        """Initialize mock team data for demonstration."""
        teams = {}
        
        # LCS Teams
        teams["TL"] = ProTeam(
            team_id="TL",
            name="Team Liquid",
            abbreviation="TL",
            league=League.LCS,
            players=[
                ProPlayer("impact", "Impact", "Jung Eon-yeong", "TL", "Top", "KR", League.LCS),
                ProPlayer("blaber", "Blaber", "Robert Huang", "TL", "Jungle", "US", League.LCS),
                ProPlayer("jensen", "Jensen", "Nicolaj Jensen", "TL", "Mid", "DK", League.LCS),
                ProPlayer("berserker", "Berserker", "Kim Min-cheol", "TL", "ADC", "KR", League.LCS),
                ProPlayer("corejj", "CoreJJ", "Jo Yong-in", "TL", "Support", "KR", League.LCS)
            ],
            current_split_record={"wins": 12, "losses": 6}
        )
        
        teams["C9"] = ProTeam(
            team_id="C9",
            name="Cloud9",
            abbreviation="C9",
            league=League.LCS,
            players=[
                ProPlayer("fudge", "Fudge", "Ibrahim Allami", "C9", "Top", "AU", League.LCS),
                ProPlayer("blaber_c9", "Blaber", "Robert Huang", "C9", "Jungle", "US", League.LCS),
                ProPlayer("emenes", "Emenes", "Yasin Dinçer", "C9", "Mid", "TR", League.LCS),
                ProPlayer("berserker_c9", "Berserker", "Kim Min-cheol", "C9", "ADC", "KR", League.LCS),
                ProPlayer("zven", "Zven", "Jesper Svenningsen", "C9", "Support", "DK", League.LCS)
            ],
            current_split_record={"wins": 10, "losses": 8}
        )
        
        # Add more teams as needed...
        
        return teams
    
    def _initialize_mock_schedule(self) -> List[ProMatch]:
        """Initialize mock schedule data."""
        schedule = []
        
        # Create sample matches
        base_time = datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)
        
        for i in range(7):  # Next 7 days
            match_time = base_time + timedelta(days=i)
            
            match = ProMatch(
                match_id=f"lcs_2024_split1_week{i+1}_match1",
                tournament="LCS 2024 Spring Split",
                league=League.LCS,
                team1=self._mock_teams["TL"],
                team2=self._mock_teams["C9"],
                scheduled_time=match_time,
                actual_start_time=None,
                match_data=None,
                bo_format=3,
                current_game=0,
                status="scheduled"
            )
            
            schedule.append(match)
        
        return schedule
    
    async def get_upcoming_matches(
        self, 
        league: Optional[League] = None,
        days_ahead: int = 7
    ) -> List[ProMatch]:
        """
        Get upcoming professional matches.
        
        Args:
            league: Specific league to filter by
            days_ahead: Number of days to look ahead
            
        Returns:
            List of upcoming matches
        """
        cutoff_time = datetime.now() + timedelta(days=days_ahead)
        
        upcoming = [
            match for match in self._mock_schedule
            if match.scheduled_time <= cutoff_time and match.status == "scheduled"
        ]
        
        if league:
            upcoming = [match for match in upcoming if match.league == league]
        
        return sorted(upcoming, key=lambda x: x.scheduled_time)
    
    async def get_live_matches(self, league: Optional[League] = None) -> List[ProMatch]:
        """Get currently live professional matches."""
        live_matches = [
            match for match in self._mock_schedule
            if match.status == "live"
        ]
        
        if league:
            live_matches = [match for match in live_matches if match.league == league]
        
        return live_matches
    
    async def get_recent_matches(
        self, 
        league: Optional[League] = None,
        days_back: int = 7
    ) -> List[ProMatch]:
        """Get recently completed matches."""
        cutoff_time = datetime.now() - timedelta(days=days_back)
        
        recent = [
            match for match in self._mock_schedule
            if match.actual_start_time and match.actual_start_time >= cutoff_time
            and match.status == "completed"
        ]
        
        if league:
            recent = [match for match in recent if match.league == league]
        
        return sorted(recent, key=lambda x: x.actual_start_time, reverse=True)
    
    async def analyze_match_performance(self, match: ProMatch) -> Dict[str, Any]:
        """
        Analyze player and team performance for a completed match.
        
        Args:
            match: The completed match to analyze
            
        Returns:
            Comprehensive performance analysis
        """
        if not match.match_data or match.status != "completed":
            return {"error": "Match not completed or data not available"}
        
        # Analyze individual player performances
        player_performances = []
        
        for participant in match.match_data.participants:
            performance = PlayerPerformance(
                player=ProPlayer(  # Would lookup actual player data
                    player_id=participant.summoner_name.lower(),
                    summoner_name=participant.summoner_name,
                    real_name="",
                    team="",
                    role=participant.role,
                    country="",
                    league=League.LCS  # Default league
                ),
                champion=participant.champion_name,
                kda=(
                    participant.stats.kills,
                    participant.stats.deaths,
                    participant.stats.assists
                ),
                cs=participant.stats.cs,
                gold_earned=participant.stats.gold_earned,
                damage_dealt=participant.stats.total_damage_dealt,
                vision_score=participant.stats.vision_score,
                performance_score=self._calculate_performance_score(participant.stats)
            )
            player_performances.append(performance)
        
        # Generate match highlights if event service is available
        highlights = []
        if self.event_service and match.match_data.timeline:
            event_analysis = await self.event_service.generate_match_summary(
                match.match_data.timeline,
                match.match_data.participants
            )
            
            highlights = event_analysis.get("highlights", [])
        
        # Generate AI summary
        ai_summary = None
        if self.nlp_pipeline and match.match_data.timeline:
            ai_summary = await self.nlp_pipeline.generate_match_summary(
                match.match_data.timeline,
                match.match_data.participants
            )
        
        return {
            "match_id": match.match_id,
            "player_performances": player_performances,
            "team_analysis": self._analyze_team_performance(match.match_data.teams),
            "highlights": highlights,
            "ai_summary": ai_summary,
            "mvp": self._determine_mvp(player_performances),
            "key_stats": self._extract_key_stats(match.match_data)
        }
    
    def _calculate_performance_score(self, stats: Any) -> float:
        """Calculate a performance score for a player."""
        # Simple performance calculation (could be more sophisticated)
        kda = (stats.kills + stats.assists) / max(1, stats.deaths)
        cs_per_min = stats.cs / 25  # Assuming 25 minute average game
        damage_ratio = stats.total_damage_dealt / max(1, stats.gold_earned)
        
        # Weighted score
        score = (kda * 0.3) + (cs_per_min * 0.2) + (damage_ratio * 0.3) + (stats.vision_score * 0.2)
        
        return min(10.0, score)  # Cap at 10.0
    
    def _analyze_team_performance(self, teams: List[Team]) -> Dict[str, Any]:
        """Analyze team-level performance metrics."""
        team_analysis = {}
        
        for team in teams:
            # Calculate team statistics
            total_kills = sum(p.stats.kills for p in team.participants)
            total_deaths = sum(p.stats.deaths for p in team.participants)
            total_assists = sum(p.stats.assists for p in team.participants)
            total_gold = sum(p.stats.gold_earned for p in team.participants)
            total_damage = sum(p.stats.total_damage_dealt for p in team.participants)
            
            team_analysis[f"team_{team.team_id}"] = {
                "total_kills": total_kills,
                "total_deaths": total_deaths,
                "total_assists": total_assists,
                "team_kda": (total_kills + total_assists) / max(1, total_deaths),
                "total_gold": total_gold,
                "total_damage": total_damage,
                "win": team.win,
                "objectives": team.objectives
            }
        
        return team_analysis
    
    def _determine_mvp(self, performances: List[PlayerPerformance]) -> Optional[PlayerPerformance]:
        """Determine the MVP of the match."""
        if not performances:
            return None
        
        return max(performances, key=lambda p: p.performance_score)
    
    def _extract_key_stats(self, match_data: HistoricalMatch) -> Dict[str, Any]:
        """Extract key statistics from match data."""
        return {
            "game_duration": match_data.game_duration,
            "total_kills": sum(p.stats.kills for p in match_data.participants),
            "first_blood_time": 0,  # Would extract from timeline
            "first_tower_time": 0,  # Would extract from timeline
            "baron_takes": 0,  # Would count from timeline
            "dragon_takes": 0   # Would count from timeline
        }
    
    async def get_player_stats(
        self, 
        player_id: str, 
        league: League,
        time_period: str = "split"
    ) -> Dict[str, Any]:
        """
        Get comprehensive player statistics.
        
        Args:
            player_id: Player identifier
            league: League the player competes in
            time_period: Time period for stats (split, season, career)
            
        Returns:
            Player statistics and analytics
        """
        # Mock player stats (would be fetched from real database)
        mock_stats = {
            "player_id": player_id,
            "league": league.value,
            "time_period": time_period,
            "games_played": 18,
            "wins": 12,
            "losses": 6,
            "win_rate": 66.7,
            "average_kda": {
                "kills": 3.2,
                "deaths": 1.8,
                "assists": 8.5,
                "ratio": 6.5
            },
            "average_cs": 245.3,
            "cs_per_minute": 9.8,
            "average_gold": 12840,
            "average_damage": 18750,
            "vision_score": 45.2,
            "champion_pool": [
                {"champion": "Thresh", "games": 8, "win_rate": 75.0},
                {"champion": "Nautilus", "games": 6, "win_rate": 66.7},
                {"champion": "Leona", "games": 4, "win_rate": 50.0}
            ],
            "recent_form": [1, 1, 0, 1, 1],  # Last 5 games (1=win, 0=loss)
            "performance_trend": "improving"
        }
        
        return mock_stats
    
    async def get_team_standings(self, league: League) -> List[Dict[str, Any]]:
        """Get current team standings for a league."""
        # Mock standings data
        standings = [
            {"team": "Team Liquid", "wins": 15, "losses": 3, "win_rate": 83.3},
            {"team": "Cloud9", "wins": 13, "losses": 5, "win_rate": 72.2},
            {"team": "100 Thieves", "wins": 11, "losses": 7, "win_rate": 61.1},
            {"team": "TSM", "wins": 10, "losses": 8, "win_rate": 55.6},
            {"team": "FlyQuest", "wins": 9, "losses": 9, "win_rate": 50.0},
            {"team": "Dignitas", "wins": 7, "losses": 11, "win_rate": 38.9},
            {"team": "Golden Guardians", "wins": 6, "losses": 12, "win_rate": 33.3},
            {"team": "CLG", "wins": 4, "losses": 14, "win_rate": 22.2}
        ]
        
        return standings
    
    async def get_meta_analysis(self, league: League) -> Dict[str, Any]:
        """Get meta analysis for a specific league."""
        meta_analysis = {
            "league": league.value,
            "patch_version": "14.1",
            "most_picked_champions": [
                {"champion": "Azir", "pick_rate": 45.2, "ban_rate": 12.3, "win_rate": 52.1},
                {"champion": "Jinx", "pick_rate": 38.7, "ban_rate": 8.5, "win_rate": 48.9},
                {"champion": "Thresh", "pick_rate": 35.4, "ban_rate": 15.2, "win_rate": 54.3},
                {"champion": "Graves", "pick_rate": 32.1, "ban_rate": 22.1, "win_rate": 51.7},
                {"champion": "Aatrox", "pick_rate": 29.8, "ban_rate": 18.9, "win_rate": 49.2}
            ],
            "most_banned_champions": [
                {"champion": "Zed", "ban_rate": 67.8, "pick_rate": 2.1},
                {"champion": "Yasuo", "ban_rate": 54.3, "pick_rate": 8.7},
                {"champion": "K'Sante", "ban_rate": 48.9, "pick_rate": 12.3}
            ],
            "priority_picks": {
                "blue_side": ["Azir", "Jinx", "Thresh"],
                "red_side": ["Graves", "Aatrox", "Nautilus"]
            },
            "average_game_time": "31:24",
            "first_dragon_time": "6:12",
            "first_herald_time": "8:45",
            "baron_control_rate": 78.3,
            "dominant_strategies": [
                "Early dragon priority",
                "Bot lane focus",
                "Scaling team compositions"
            ]
        }
        
        return meta_analysis
    
    async def track_streamer_highlights(self, streamer_name: str) -> List[Dict[str, Any]]:
        """Track highlights from professional player streams."""
        # Mock highlight data
        highlights = [
            {
                "timestamp": datetime.now() - timedelta(hours=2),
                "title": "Insane outplay in soloq",
                "description": "Amazing 1v3 clutch play",
                "clip_url": "https://clips.twitch.tv/example1",
                "viewer_count": 1250,
                "chat_sentiment": "positive"
            },
            {
                "timestamp": datetime.now() - timedelta(hours=4),
                "title": "Perfect team coordination",
                "description": "Textbook Baron setup and execution",
                "clip_url": "https://clips.twitch.tv/example2",
                "viewer_count": 2100,
                "chat_sentiment": "excited"
            }
        ]
        
        return highlights


# Global instance
_pro_tracker: Optional[ProMatchTracker] = None


async def get_pro_tracker() -> ProMatchTracker:
    """Get the global professional match tracker instance."""
    global _pro_tracker
    if _pro_tracker is None:
        _pro_tracker = ProMatchTracker()
        await _pro_tracker.initialize()
    return _pro_tracker


# Utility functions
async def get_league_schedule(league: League, days_ahead: int = 7) -> List[ProMatch]:
    """Get schedule for a specific league."""
    tracker = await get_pro_tracker()
    return await tracker.get_upcoming_matches(league, days_ahead)


async def get_player_comparison(player1_id: str, player2_id: str, league: League) -> Dict[str, Any]:
    """Compare two professional players."""
    tracker = await get_pro_tracker()
    
    player1_stats = await tracker.get_player_stats(player1_id, league)
    player2_stats = await tracker.get_player_stats(player2_id, league)
    
    comparison = {
        "player1": player1_stats,
        "player2": player2_stats,
        "comparison": {
            "win_rate_diff": player1_stats["win_rate"] - player2_stats["win_rate"],
            "kda_diff": player1_stats["average_kda"]["ratio"] - player2_stats["average_kda"]["ratio"],
            "cs_diff": player1_stats["average_cs"] - player2_stats["average_cs"],
            "damage_diff": player1_stats["average_damage"] - player2_stats["average_damage"]
        }
    }
    
    return comparison


if __name__ == "__main__":
    async def main():
        # Test the pro match tracker
        tracker = await get_pro_tracker()
        
        # Test upcoming matches
        upcoming = await tracker.get_upcoming_matches(League.LCS)
        print(f"Found {len(upcoming)} upcoming LCS matches")
        
        # Test team standings
        standings = await tracker.get_team_standings(League.LCS)
        print(f"LCS Standings: {len(standings)} teams")
        
        # Test meta analysis
        meta = await tracker.get_meta_analysis(League.LCS)
        print(f"Meta analysis for {meta['league']} on patch {meta['patch_version']}")
    
    asyncio.run(main())

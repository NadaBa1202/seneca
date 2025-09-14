"""
Data models and schemas for the League of Legends Companion App.

This module defines Pydantic models for all data structures used throughout
the application, ensuring type safety and data validation.
"""

# Updated to fix EventType enum issues
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class GameMode(str, Enum):
    """Supported game modes."""
    CLASSIC = "CLASSIC"
    ARAM = "ARAM"
    URF = "URF"
    ONE_FOR_ALL = "ONEFORALL"
    NEXUS_BLITZ = "NEXUSBLITZ"
    TFT = "TFT"


class MatchState(str, Enum):
    """Match state enumeration."""
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"
    PAUSED = "PAUSED"
    TERMINATED = "TERMINATED"


class EventType(str, Enum):
    """Match event types."""
    CHAMPION_KILL = "CHAMPION_KILL"
    CHAMPION_DEATH = "CHAMPION_DEATH"
    CHAMPION_ASSIST = "CHAMPION_ASSIST"
    DRAGON_KILL = "DRAGON_KILL"
    BARON_KILL = "BARON_KILL"
    RIFT_HERALD_KILL = "RIFT_HERALD_KILL"
    BUILDING_KILL = "BUILDING_KILL"
    FIRST_BLOOD = "FIRST_BLOOD"
    ACE = "ACE"
    MULTIKILL = "MULTIKILL"
    
    # Legacy aliases for backward compatibility
    KILL = "CHAMPION_KILL"
    DEATH = "CHAMPION_DEATH"
    ASSIST = "CHAMPION_ASSIST"
    DRAGON = "DRAGON_KILL"
    BARON = "BARON_KILL"
    HERALD = "RIFT_HERALD_KILL"
    TOWER = "BUILDING_KILL"


# Champion Data Models
class ChampionSpell(BaseModel):
    """Champion ability/spell model."""
    id: str
    name: str
    description: str
    tooltip: str
    max_rank: int
    cooldown: List[float]
    cost: List[int]
    range: List[int]
    image: Dict[str, Any]
    resource: str


class ChampionPassive(BaseModel):
    """Champion passive ability model."""
    name: str
    description: str
    image: Dict[str, Any]


class ChampionStats(BaseModel):
    """Champion base statistics."""
    hp: float
    hp_per_level: float
    mp: float
    mp_per_level: float
    move_speed: float
    armor: float
    armor_per_level: float
    spell_block: float
    spell_block_per_level: float
    attack_range: float
    attack_damage: float
    attack_damage_per_level: float
    attack_speed: float
    attack_speed_per_level: float


class Champion(BaseModel):
    """Complete champion data model."""
    id: str
    key: str
    name: str
    title: str
    lore: str
    blurb: str
    ally_tips: List[str]
    enemy_tips: List[str]
    tags: List[str]
    partype: str
    stats: ChampionStats
    spells: List[ChampionSpell]
    passive: ChampionPassive
    image: Dict[str, Any]
    
    class Config:
        extra = "allow"


# Item Data Models
class ItemStats(BaseModel):
    """Item statistics and bonuses."""
    stats: Dict[str, float] = Field(default_factory=dict)
    
    
class Item(BaseModel):
    """Game item model."""
    id: str
    name: str
    description: str
    short_description: str = ""
    stats: ItemStats
    gold: Dict[str, int]
    tags: List[str]
    maps: Dict[str, bool]
    image: Dict[str, Any]
    into: List[str] = Field(default_factory=list)
    from_items: List[str] = Field(default_factory=list, alias="from")
    
    class Config:
        allow_population_by_field_name = True


# Rune Data Models
class RuneSlot(BaseModel):
    """Individual rune in a slot."""
    id: int
    key: str
    icon: str
    name: str
    short_desc: str
    long_desc: str


class RuneTree(BaseModel):
    """Rune tree containing multiple slots."""
    id: int
    key: str
    icon: str
    name: str
    slots: List[List[RuneSlot]]


# Player and Match Data Models
class ParticipantStats(BaseModel):
    """Player statistics for a match."""
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    gold_earned: int = 0
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    total_heal: int = 0
    vision_score: int = 0
    cs: int = 0
    level: int = 1
    items: List[int] = Field(default_factory=list)
    summoner_spells: List[int] = Field(default_factory=list)
    runes: Dict[str, Any] = Field(default_factory=dict)


class Participant(BaseModel):
    """Match participant model."""
    summoner_name: str
    champion_id: str
    champion_name: str
    team_id: int
    role: str
    lane: str
    stats: ParticipantStats
    puuid: Optional[str] = None


class Team(BaseModel):
    """Team information and statistics."""
    team_id: int
    win: bool
    bans: List[Dict[str, Any]] = Field(default_factory=list)
    objectives: Dict[str, Any] = Field(default_factory=dict)
    participants: List[Participant] = Field(default_factory=list)


class MatchEvent(BaseModel):
    """Individual match event."""
    event_type: EventType
    timestamp: int
    participant_id: Optional[int] = None
    killer_id: Optional[int] = None
    victim_id: Optional[int] = None
    assisting_participant_ids: List[int] = Field(default_factory=list)
    position: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LiveMatch(BaseModel):
    """Live match data model."""
    game_id: str
    game_mode: GameMode
    game_start_time: datetime
    game_length: int  # seconds
    map_id: int
    state: MatchState
    teams: List[Team]
    participants: List[Participant]
    events: List[MatchEvent] = Field(default_factory=list)
    
    @validator("game_start_time", pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, int):
            return datetime.fromtimestamp(v / 1000)  # Convert from milliseconds
        return v


class HistoricalMatch(BaseModel):
    """Historical match data model."""
    match_id: str
    game_mode: GameMode
    game_duration: int
    game_creation: datetime
    game_end: datetime
    teams: List[Team]
    participants: List[Participant]
    timeline: List[MatchEvent] = Field(default_factory=list)


# NLP and Analysis Models
class QuestionAnswerPair(BaseModel):
    """Q&A model for chatbot responses."""
    question: str
    answer: str
    confidence: float
    context: Optional[str] = None
    sources: List[str] = Field(default_factory=list)


class MatchSummary(BaseModel):
    """AI-generated match summary."""
    match_id: str
    summary: str
    key_events: List[str]
    mvp_player: Optional[str] = None
    turning_points: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)


class SentimentAnalysis(BaseModel):
    """Sentiment analysis result."""
    text: str
    sentiment: str  # positive, negative, neutral
    confidence: float
    emotions: Dict[str, float] = Field(default_factory=dict)


# Configuration Models
class UserPreferences(BaseModel):
    """User preferences and settings."""
    favorite_champions: List[str] = Field(default_factory=list)
    favorite_roles: List[str] = Field(default_factory=list)
    notification_settings: Dict[str, bool] = Field(default_factory=dict)
    ui_theme: str = "dark"
    language: str = "en_US"


class StreamerConfig(BaseModel):
    """Streamer configuration for tracking."""
    streamer_name: str
    platform: str  # twitch, youtube
    stream_url: str
    auto_track: bool = True
    notification_enabled: bool = True


# API Response Models
class APIResponse(BaseModel):
    """Base API response model."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class PaginatedResponse(BaseModel):
    """Paginated API response."""
    items: List[Any]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


# Cache Models
class CacheEntry(BaseModel):
    """Cache entry with metadata."""
    key: str
    data: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    
    
class ModelMetadata(BaseModel):
    """Metadata for ML models."""
    model_name: str
    model_version: str
    download_url: str
    file_size: int
    checksum: str
    last_updated: datetime
    capabilities: List[str]


# Error Models
class AppError(BaseModel):
    """Application error model."""
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    trace_id: Optional[str] = None


# Analytics Models
class PlayerAnalytics(BaseModel):
    """Player performance analytics."""
    summoner_name: str
    puuid: str
    total_games: int
    win_rate: float
    avg_kda: float
    avg_cs_per_min: float
    avg_damage_per_min: float
    favorite_champions: List[Dict[str, Any]]
    recent_performance: List[Dict[str, Any]]
    rank_info: Optional[Dict[str, Any]] = None


class TeamAnalytics(BaseModel):
    """Team performance analytics."""
    team_name: str
    team_id: int
    total_games: int
    win_rate: float
    avg_game_duration: float
    objective_control: Dict[str, float]
    performance_trends: List[Dict[str, Any]]
    member_stats: List[PlayerAnalytics]


class MatchAnalytics(BaseModel):
    """Comprehensive match analytics."""
    match_id: str
    game_mode: str
    duration_minutes: float
    winner_team_id: int
    total_kills: int
    total_gold: int
    key_events: List[Dict[str, Any]]
    team_analytics: List[TeamAnalytics]
    mvp_candidate: Optional[str] = None
    game_pace: str  # slow, normal, fast
    comeback_potential: float

"""
Riot Games API client for League of Legends data.

This module provides async clients for interacting with various Riot Games APIs
including match data, summoner information, and live game data.
"""

import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from asyncio_throttle import Throttler
import logging

from ..config import get_config
from ..models import (
    LiveMatch, HistoricalMatch, Participant, Team, MatchEvent,
    GameMode, MatchState, EventType, APIResponse
)

logger = logging.getLogger(__name__)
config = get_config()


class RateLimiter:
    """Rate limiter for Riot API requests."""
    
    def __init__(self, requests_per_second: int = 20, requests_per_minute: int = 100):
        self.requests_per_second = requests_per_second
        self.requests_per_minute = requests_per_minute
        self.second_throttler = Throttler(rate_limit=requests_per_second, period=1.0)
        self.minute_throttler = Throttler(rate_limit=requests_per_minute, period=60.0)
        
    async def acquire(self):
        """Acquire permission to make a request."""
        await self.second_throttler.acquire()
        await self.minute_throttler.acquire()


class RiotAPIError(Exception):
    """Custom exception for Riot API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class BaseRiotClient:
    """Base client for Riot Games API with common functionality."""
    
    def __init__(self, region: str = "na1"):
        self.region = region
        self.api_key = config.riot_api.api_key
        self.base_url = f"https://{region}.api.riotgames.com"
        self.rate_limiter = RateLimiter(
            config.riot_api.rate_limit_requests_per_second,
            config.riot_api.rate_limit_requests_per_minute
        )
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=config.riot_api.request_timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={"X-Riot-Token": self.api_key}
            )
        return self.session
    
    async def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the Riot API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            retries: Number of retry attempts
            
        Returns:
            JSON response data
            
        Raises:
            RiotAPIError: If the request fails
        """
        await self.rate_limiter.acquire()
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(retries + 1):
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    
                    elif response.status == 429:  # Rate limited
                        retry_after = int(response.headers.get("Retry-After", 1))
                        logger.warning(f"Rate limited, waiting {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                        continue
                        
                    elif response.status == 503:  # Service unavailable
                        if attempt < retries:
                            wait_time = 2 ** attempt
                            logger.warning(f"Service unavailable, retrying in {wait_time} seconds")
                            await asyncio.sleep(wait_time)
                            continue
                    
                    # Handle other error responses
                    error_data = await response.text()
                    raise RiotAPIError(
                        f"API request failed: {response.status}",
                        status_code=response.status,
                        response_data={"error": error_data}
                    )
                    
            except aiohttp.ClientError as e:
                if attempt < retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request failed, retrying in {wait_time} seconds: {e}")
                    await asyncio.sleep(wait_time)
                    continue
                raise RiotAPIError(f"Network error: {e}")
        
        raise RiotAPIError("Max retries exceeded")
    
    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()


class SummonerAPI(BaseRiotClient):
    """API client for summoner-related endpoints."""
    
    async def get_summoner_by_name(self, summoner_name: str) -> Dict[str, Any]:
        """
        Get summoner information by name.
        
        Args:
            summoner_name: The summoner name
            
        Returns:
            Summoner data including PUUID, account ID, etc.
        """
        endpoint = f"/lol/summoner/v4/summoners/by-name/{summoner_name}"
        return await self._make_request(endpoint)
    
    async def get_summoner_by_puuid(self, puuid: str) -> Dict[str, Any]:
        """Get summoner information by PUUID."""
        endpoint = f"/lol/summoner/v4/summoners/by-puuid/{puuid}"
        return await self._make_request(endpoint)
    
    async def get_ranked_stats(self, summoner_id: str) -> List[Dict[str, Any]]:
        """Get ranked statistics for a summoner."""
        endpoint = f"/lol/league/v4/entries/by-summoner/{summoner_id}"
        return await self._make_request(endpoint)


class MatchAPI(BaseRiotClient):
    """API client for match-related endpoints."""
    
    def __init__(self, region: str = "americas"):  # Match API uses regional routing
        super().__init__(region)
    
    async def get_match_history(
        self, 
        puuid: str, 
        count: int = 20, 
        start: int = 0,
        queue_id: Optional[int] = None,
        game_type: Optional[str] = None
    ) -> List[str]:
        """
        Get match history for a player.
        
        Args:
            puuid: Player PUUID
            count: Number of matches to return
            start: Starting index
            queue_id: Queue ID filter
            game_type: Game type filter
            
        Returns:
            List of match IDs
        """
        endpoint = f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {
            "count": count,
            "start": start
        }
        
        if queue_id:
            params["queue"] = queue_id
        if game_type:
            params["type"] = game_type
            
        return await self._make_request(endpoint, params)
    
    async def get_match_details(self, match_id: str) -> Dict[str, Any]:
        """Get detailed match information."""
        endpoint = f"/lol/match/v5/matches/{match_id}"
        return await self._make_request(endpoint)
    
    async def get_match_timeline(self, match_id: str) -> Dict[str, Any]:
        """Get match timeline with detailed events."""
        endpoint = f"/lol/match/v5/matches/{match_id}/timeline"
        return await self._make_request(endpoint)


class SpectatorAPI(BaseRiotClient):
    """API client for live game spectator endpoints."""
    
    async def get_current_game(self, summoner_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current live game for a summoner.
        
        Args:
            summoner_id: The summoner ID
            
        Returns:
            Live game data or None if not in game
        """
        endpoint = f"/lol/spectator/v4/active-games/by-summoner/{summoner_id}"
        try:
            return await self._make_request(endpoint)
        except RiotAPIError as e:
            if e.status_code == 404:
                return None  # Not currently in game
            raise
    
    async def get_featured_games(self) -> Dict[str, Any]:
        """Get list of featured games."""
        endpoint = "/lol/spectator/v4/featured-games"
        return await self._make_request(endpoint)


class LeagueAPI(BaseRiotClient):
    """API client for league/ranked information."""
    
    async def get_challenger_league(self, queue: str = "RANKED_SOLO_5x5") -> Dict[str, Any]:
        """Get Challenger league information."""
        endpoint = f"/lol/league/v4/challengerleagues/by-queue/{queue}"
        return await self._make_request(endpoint)
    
    async def get_grandmaster_league(self, queue: str = "RANKED_SOLO_5x5") -> Dict[str, Any]:
        """Get Grandmaster league information."""
        endpoint = f"/lol/league/v4/grandmasterleagues/by-queue/{queue}"
        return await self._make_request(endpoint)
    
    async def get_master_league(self, queue: str = "RANKED_SOLO_5x5") -> Dict[str, Any]:
        """Get Master league information."""
        endpoint = f"/lol/league/v4/masterleagues/by-queue/{queue}"
        return await self._make_request(endpoint)


class RiotAPIClient:
    """
    Main Riot API client that combines all sub-clients.
    
    This provides a unified interface for all Riot Games API interactions
    with proper rate limiting, error handling, and data parsing.
    """
    
    def __init__(self, region: str = "na1", regional_routing: str = "americas"):
        self.region = region
        self.regional_routing = regional_routing
        
        # Initialize sub-clients
        self.summoner = SummonerAPI(region)
        self.match = MatchAPI(regional_routing)
        self.spectator = SpectatorAPI(region)
        self.league = LeagueAPI(region)
        
        self._cache: Dict[str, Any] = {}
        self._cache_ttl: Dict[str, datetime] = {}
    
    def _get_cache_key(self, method: str, *args, **kwargs) -> str:
        """Generate cache key for a method call."""
        return f"{method}:{hash(str(args) + str(sorted(kwargs.items())))}"
    
    def _is_cache_valid(self, key: str, ttl_seconds: int = 300) -> bool:
        """Check if cached data is still valid."""
        if key not in self._cache_ttl:
            return False
        return datetime.now() - self._cache_ttl[key] < timedelta(seconds=ttl_seconds)
    
    async def get_live_match_data(self, summoner_name: str) -> Optional[LiveMatch]:
        """
        Get live match data for a summoner.
        
        Args:
            summoner_name: The summoner name to look up
            
        Returns:
            LiveMatch object or None if not in game
        """
        try:
            # Get summoner info
            summoner_data = await self.summoner.get_summoner_by_name(summoner_name)
            summoner_id = summoner_data["id"]
            
            # Get current game
            game_data = await self.spectator.get_current_game(summoner_id)
            if not game_data:
                return None
            
            # Parse game data into our model
            return self._parse_live_match(game_data)
            
        except RiotAPIError as e:
            logger.error(f"Failed to get live match data: {e}")
            return None
    
    async def get_match_history_detailed(
        self, 
        summoner_name: str, 
        count: int = 20
    ) -> List[HistoricalMatch]:
        """
        Get detailed match history for a summoner.
        
        Args:
            summoner_name: The summoner name
            count: Number of matches to retrieve
            
        Returns:
            List of HistoricalMatch objects
        """
        try:
            # Get summoner info
            summoner_data = await self.summoner.get_summoner_by_name(summoner_name)
            puuid = summoner_data["puuid"]
            
            # Get match IDs
            match_ids = await self.match.get_match_history(puuid, count=count)
            
            # Get detailed data for each match
            matches = []
            for match_id in match_ids:
                try:
                    match_data = await self.match.get_match_details(match_id)
                    historical_match = self._parse_historical_match(match_data)
                    matches.append(historical_match)
                except Exception as e:
                    logger.error(f"Failed to parse match {match_id}: {e}")
                    continue
            
            return matches
            
        except RiotAPIError as e:
            logger.error(f"Failed to get match history: {e}")
            return []
    
    def _parse_live_match(self, game_data: Dict[str, Any]) -> LiveMatch:
        """Parse raw API data into LiveMatch model."""
        # This is a simplified parsing - you'd expand this based on the actual API response
        participants = []
        teams = []
        
        # Parse participants
        for participant in game_data.get("participants", []):
            participants.append(Participant(
                summoner_name=participant.get("summonerName", ""),
                champion_id=str(participant.get("championId", 0)),
                champion_name="",  # Would need to resolve from champion data
                team_id=participant.get("teamId", 0),
                role="",
                lane="",
                stats={}  # Live stats not available in current game API
            ))
        
        return LiveMatch(
            game_id=str(game_data.get("gameId", "")),
            game_mode=GameMode.CLASSIC,  # Would need to map from game_data
            game_start_time=datetime.fromtimestamp(game_data.get("gameStartTime", 0) / 1000),
            game_length=game_data.get("gameLength", 0),
            map_id=game_data.get("mapId", 11),
            state=MatchState.IN_PROGRESS,
            teams=teams,
            participants=participants
        )
    
    def _parse_historical_match(self, match_data: Dict[str, Any]) -> HistoricalMatch:
        """Parse raw API data into HistoricalMatch model."""
        # Simplified parsing - expand based on needs
        info = match_data.get("info", {})
        
        participants = []
        for participant in info.get("participants", []):
            participants.append(Participant(
                summoner_name=participant.get("summonerName", ""),
                champion_id=str(participant.get("championId", 0)),
                champion_name=participant.get("championName", ""),
                team_id=participant.get("teamId", 0),
                role=participant.get("individualPosition", ""),
                lane=participant.get("lane", ""),
                stats={}  # Would parse detailed stats
            ))
        
        return HistoricalMatch(
            match_id=match_data.get("metadata", {}).get("matchId", ""),
            game_mode=GameMode.CLASSIC,
            game_duration=info.get("gameDuration", 0),
            game_creation=datetime.fromtimestamp(info.get("gameCreation", 0) / 1000),
            game_end=datetime.fromtimestamp(info.get("gameEndTimestamp", 0) / 1000),
            teams=[],  # Would parse team data
            participants=participants
        )
    
    async def close(self):
        """Close all API clients."""
        await asyncio.gather(
            self.summoner.close(),
            self.match.close(),
            self.spectator.close(),
            self.league.close(),
            return_exceptions=True
        )


# Utility functions
async def get_riot_client() -> RiotAPIClient:
    """Get a configured Riot API client instance."""
    return RiotAPIClient()


async def test_api_connection() -> bool:
    """Test if the Riot API is accessible with current configuration."""
    client = await get_riot_client()
    try:
        # Try to get featured games as a simple test
        await client.spectator.get_featured_games()
        return True
    except Exception as e:
        logger.error(f"API connection test failed: {e}")
        return False
    finally:
        await client.close()


if __name__ == "__main__":
    async def main():
        # Test the API client
        client = await get_riot_client()
        try:
            # Test featured games
            featured = await client.spectator.get_featured_games()
            print(f"Found {len(featured.get('gameList', []))} featured games")
            
            # Test summoner lookup (replace with actual summoner name)
            # summoner = await client.summoner.get_summoner_by_name("SampleSummonerName")
            # print(f"Summoner info: {summoner}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await client.close()
    
    asyncio.run(main())

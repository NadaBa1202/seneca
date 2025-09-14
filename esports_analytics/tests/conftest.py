"""Pytest configuration and fixtures."""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch
from typing import Generator, AsyncGenerator

# Configure asyncio for pytest
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Mock fixtures for external dependencies
@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock = Mock()
    mock.ping = Mock(return_value=True)
    mock.lpush = Mock()
    mock.brpop = Mock(return_value=None)
    mock.llen = Mock(return_value=0)
    return mock

@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    mock = Mock()
    mock.send = Mock()
    mock.close = Mock()
    mock.recv = Mock(return_value="test message")
    return mock

@pytest.fixture
def mock_http_session():
    """Mock HTTP session."""
    mock = Mock()
    mock.get = Mock()
    mock.post = Mock()
    return mock

# Test data fixtures
@pytest.fixture
def sample_chat_messages():
    """Sample chat messages for testing."""
    return [
        {
            "message": "Great play!",
            "username": "user1",
            "timestamp": 1000.0,
            "platform": "test",
            "sentiment": {"compound": 0.8, "positive": 0.8, "negative": 0.1, "neutral": 0.1},
            "toxicity": {"toxic": 0.1, "severe_toxic": 0.0, "obscene": 0.0, "threat": 0.0, "insult": 0.0, "identity_hate": 0.0}
        },
        {
            "message": "Terrible game!",
            "username": "user2", 
            "timestamp": 1001.0,
            "platform": "test",
            "sentiment": {"compound": -0.7, "positive": 0.1, "negative": 0.8, "neutral": 0.1},
            "toxicity": {"toxic": 0.2, "severe_toxic": 0.0, "obscene": 0.0, "threat": 0.0, "insult": 0.1, "identity_hate": 0.0}
        },
        {
            "message": "Amazing comeback!",
            "username": "user3",
            "timestamp": 1002.0,
            "platform": "test", 
            "sentiment": {"compound": 0.9, "positive": 0.9, "negative": 0.0, "neutral": 0.1},
            "toxicity": {"toxic": 0.0, "severe_toxic": 0.0, "obscene": 0.0, "threat": 0.0, "insult": 0.0, "identity_hate": 0.0}
        }
    ]

@pytest.fixture
def sample_game_events():
    """Sample game events for testing."""
    return [
        {
            "event_id": "event_1",
            "timestamp": 1000.0,
            "event_type": "kill",
            "player_id": "player1",
            "position": {"x": 0.5, "y": 0.5},
            "game_state": {"team1_score": 5, "team2_score": 3},
            "importance_score": 0.7
        },
        {
            "event_id": "event_2", 
            "timestamp": 1001.0,
            "event_type": "objective",
            "player_id": "player2",
            "position": {"x": 0.3, "y": 0.7},
            "game_state": {"team1_score": 6, "team2_score": 3},
            "importance_score": 0.8
        }
    ]

@pytest.fixture
def sample_biometric_data():
    """Sample biometric data for testing."""
    return [
        {
            "player_id": "player1",
            "timestamp": 1000.0,
            "heart_rate": 85.0,
            "stress_level": 0.6,
            "focus_level": 0.8,
            "reaction_time": 0.2
        },
        {
            "player_id": "player2",
            "timestamp": 1001.0,
            "heart_rate": 95.0,
            "stress_level": 0.8,
            "focus_level": 0.7,
            "reaction_time": 0.15
        }
    ]

# Environment fixtures
@pytest.fixture
def temp_dir():
    """Temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def mock_env_vars():
    """Mock environment variables."""
    env_vars = {
        "TWITCH_CLIENT_ID": "test_client_id",
        "TWITCH_CLIENT_SECRET": "test_client_secret", 
        "TWITCH_CHANNEL": "test_channel",
        "DISCORD_BOT_TOKEN": "test_bot_token",
        "YOUTUBE_API_KEY": "test_api_key",
        "PERSPECTIVE_API_KEY": "test_perspective_key",
        "REDIS_URL": "redis://localhost:6379"
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars

# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time
    start_time = time.time()
    yield
    end_time = time.time()
    print(f"Performance test took {end_time - start_time:.3f} seconds")

# Async fixtures
@pytest.fixture
async def async_mock_processor():
    """Async mock processor for testing."""
    async def mock_process(message):
        return True
    return mock_process

# Database fixtures (for future use)
@pytest.fixture
def mock_database():
    """Mock database connection."""
    mock_db = Mock()
    mock_db.execute = Mock()
    mock_db.fetchall = Mock(return_value=[])
    mock_db.commit = Mock()
    return mock_db

# Model fixtures
@pytest.fixture
def mock_sentiment_model():
    """Mock sentiment analysis model."""
    mock_model = Mock()
    mock_model.predict = Mock(return_value=[{"label": "POSITIVE", "score": 0.9}])
    return mock_model

@pytest.fixture
def mock_toxicity_model():
    """Mock toxicity detection model."""
    mock_model = Mock()
    mock_model.predict = Mock(return_value={"toxic": 0.1, "severe_toxic": 0.0})
    return mock_model

# API fixtures
@pytest.fixture
def mock_twitch_api():
    """Mock Twitch API responses."""
    return {
        "data": [{
            "id": "test_stream_id",
            "user_id": "test_user_id",
            "user_name": "test_channel",
            "game_id": "test_game_id",
            "title": "Test Stream",
            "viewer_count": 1000
        }]
    }

@pytest.fixture
def mock_youtube_api():
    """Mock YouTube API responses."""
    return {
        "items": [{
            "id": {"videoId": "test_video_id"},
            "snippet": {
                "title": "Test Video",
                "description": "Test Description",
                "channelTitle": "Test Channel"
            },
            "liveStreamingDetails": {
                "activeLiveChatId": "test_chat_id"
            }
        }]
    }

# Error fixtures
@pytest.fixture
def mock_connection_error():
    """Mock connection error."""
    import aiohttp
    return aiohttp.ClientConnectionError("Connection failed")

@pytest.fixture
def mock_timeout_error():
    """Mock timeout error."""
    import asyncio
    return asyncio.TimeoutError("Operation timed out")

# Configuration fixtures
@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "nlp": {
            "device": "cpu",
            "confidence_threshold": 0.7,
            "ensemble_method": "weighted_average"
        },
        "chat": {
            "max_workers": 4,
            "scaling_threshold": 100,
            "processing_timeout": 30
        },
        "highlight": {
            "importance_threshold": 0.7,
            "correlation_window": 30,
            "max_highlights_per_match": 10
        },
        "monitoring": {
            "monitoring_interval": 60,
            "confidence_level": 0.95,
            "performance_threshold": 0.85
        }
    }

# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test."""
    yield
    # Add any cleanup logic here
    pass

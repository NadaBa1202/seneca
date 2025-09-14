"""Unit tests for chat processing and real-time ingestion."""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock

from esports_analytics.services.chat import (
    WebSocketChatClient,
    MessageQueue,
    ChatProcessor,
    TwitchChatIntegration,
    DiscordChatIntegration,
    YouTubeChatIntegration
)
from esports_analytics.services.chat.message_queue import QueuedMessage, MessagePriority
from esports_analytics.services.chat.websocket_client import ChatMessage, ConnectionConfig

class TestWebSocketChatClient:
    """Test suite for WebSocket chat client."""
    
    @pytest.fixture
    def config(self):
        """Create connection config for testing."""
        return ConnectionConfig(
            url="ws://test.example.com",
            reconnect_interval=1,
            max_reconnect_attempts=3
        )
    
    @pytest.fixture
    def client(self, config):
        """Create WebSocket client for testing."""
        return WebSocketChatClient(config)
    
    def test_initialization(self, client, config):
        """Test client initialization."""
        assert client.config == config
        assert client.connected == False
        assert client.reconnect_attempts == 0
    
    def test_get_stats(self, client):
        """Test statistics retrieval."""
        stats = client.get_stats()
        
        assert 'connected' in stats
        assert 'uptime_seconds' in stats
        assert 'messages_received' in stats
        assert 'connection_attempts' in stats
    
    def test_get_health_status(self, client):
        """Test health status retrieval."""
        health = client.get_health_status()
        
        assert 'connected' in health
        assert 'ping_latency' in health
        assert 'circuit_breaker_open' in health

class TestMessageQueue:
    """Test suite for message queue."""
    
    @pytest.fixture
    def queue(self):
        """Create message queue for testing."""
        return MessageQueue(
            queue_type="memory",
            max_workers=2,
            min_workers=1,
            scaling_threshold=5
        )
    
    @pytest.mark.asyncio
    async def test_initialization(self, queue):
        """Test queue initialization."""
        await queue.initialize()
        assert queue.backend == "memory"
    
    @pytest.mark.asyncio
    async def test_enqueue_dequeue(self, queue):
        """Test message enqueueing and dequeueing."""
        await queue.initialize()
        
        # Enqueue message
        message_id = await queue.enqueue(
            data={"message": "test", "user": "test_user"},
            priority=MessagePriority.NORMAL
        )
        
        assert message_id is not None
        
        # Dequeue message
        message = await queue.dequeue(timeout=1)
        assert message is not None
        assert message.data["message"] == "test"
    
    @pytest.mark.asyncio
    async def test_priority_handling(self, queue):
        """Test message priority handling."""
        await queue.initialize()
        
        # Enqueue messages with different priorities
        await queue.enqueue({"message": "low"}, MessagePriority.LOW)
        await queue.enqueue({"message": "high"}, MessagePriority.HIGH)
        await queue.enqueue({"message": "normal"}, MessagePriority.NORMAL)
        
        # High priority should be dequeued first
        high_msg = await queue.dequeue(timeout=1)
        assert high_msg.data["message"] == "high"
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, queue):
        """Test rate limiting functionality."""
        await queue.initialize()
        
        # Enable rate limiting
        queue.enable_rate_limiting(max_messages_per_second=2)
        
        # Enqueue messages rapidly
        for i in range(5):
            await queue.enqueue({"message": f"test_{i}"})
        
        # Should have some messages queued
        queue_size = await queue.get_queue_size()
        assert queue_size > 0
    
    @pytest.mark.asyncio
    async def test_get_stats(self, queue):
        """Test queue statistics."""
        stats = await queue.get_stats()
        
        assert 'total_messages' in stats
        assert 'processed_messages' in stats
        assert 'worker_count' in stats

class TestChatProcessor:
    """Test suite for chat processor."""
    
    @pytest.fixture
    def processor(self):
        """Create chat processor for testing."""
        return ChatProcessor(
            enable_ab_testing=False,
            preprocessing_enabled=True,
            context_window=5,
            performance_tracking=True
        )
    
    def test_preprocessing(self, processor):
        """Test text preprocessing."""
        # Test emoji handling
        text_with_emoji = "This is great! 😀😀😀"
        processed = processor._preprocess_text(text_with_emoji)
        assert "😀" in processed
        
        # Test slang normalization
        text_with_slang = "This is lol and omg!"
        processed = processor._preprocess_text(text_with_slang)
        assert "laughing out loud" in processed or "oh my god" in processed
        
        # Test repeated character handling
        text_repeated = "sooooooo good"
        processed = processor._preprocess_text(text_repeated)
        assert len(processed) < len(text_repeated)
    
    def test_model_version_selection(self, processor):
        """Test A/B testing model version selection."""
        # Test with user ID
        version = processor._get_model_version('sentiment', 'user123')
        assert version in ['v1', 'v2']
        
        # Test without user ID
        version = processor._get_model_version('sentiment')
        assert version == 'v1'
    
    @pytest.mark.asyncio
    async def test_process_message(self, processor):
        """Test message processing."""
        # Create test message
        test_message = QueuedMessage(
            id="test_msg",
            data={
                'message': 'This is an amazing play!',
                'username': 'test_user',
                'user_id': 'test_user',
                'platform': 'test'
            },
            priority=MessagePriority.NORMAL,
            timestamp=time.time()
        )
        
        # Process message
        result = await processor.process_message(test_message)
        assert result == True
        
        # Check processing stats
        stats = processor.get_processing_stats()
        assert stats.total_processed > 0
    
    def test_get_processing_stats(self, processor):
        """Test processing statistics retrieval."""
        stats = processor.get_processing_stats()
        
        assert 'total_processed' in stats
        assert 'avg_processing_time' in stats
        assert 'throughput_per_second' in stats
    
    def test_get_ab_test_results(self, processor):
        """Test A/B testing results."""
        results = processor.get_ab_test_results()
        
        if processor.enable_ab_testing:
            assert 'sentiment_models' in results
            assert 'toxicity_models' in results
            assert 'emotion_models' in results

class TestTwitchIntegration:
    """Test suite for Twitch chat integration."""
    
    @pytest.fixture
    def config(self):
        """Create Twitch config for testing."""
        from esports_analytics.services.chat.twitch_integration import TwitchConfig
        return TwitchConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            channel="test_channel"
        )
    
    @pytest.fixture
    def integration(self, config):
        """Create Twitch integration for testing."""
        return TwitchChatIntegration(config)
    
    def test_initialization(self, integration, config):
        """Test integration initialization."""
        assert integration.config == config
        assert integration.connected == False
    
    def test_emote_extraction(self, integration):
        """Test emote extraction."""
        text = "This is Kappa and PogChamp!"
        emotes = integration._extract_emotes(text)
        
        assert len(emotes) > 0
        assert any(emote['name'] == 'Kappa' for emote in emotes)
    
    def test_message_parsing(self, integration):
        """Test message parsing."""
        username = "test_user"
        message = "Hello world!"
        
        chat_message = asyncio.run(integration._parse_twitch_message(username, message))
        
        assert chat_message is not None
        assert chat_message.platform == "twitch"
        assert chat_message.username == username
        assert chat_message.message == message
    
    def test_get_stats(self, integration):
        """Test statistics retrieval."""
        stats = integration.get_stats()
        
        assert 'connected' in stats
        assert 'uptime_seconds' in stats
        assert 'messages_received' in stats

class TestDiscordIntegration:
    """Test suite for Discord chat integration."""
    
    @pytest.fixture
    def config(self):
        """Create Discord config for testing."""
        from esports_analytics.services.chat.discord_integration import DiscordConfig
        return DiscordConfig(
            bot_token="test_bot_token",
            guild_id="test_guild_id",
            channel_id="test_channel_id"
        )
    
    @pytest.fixture
    def integration(self, config):
        """Create Discord integration for testing."""
        return DiscordChatIntegration(config)
    
    def test_initialization(self, integration, config):
        """Test integration initialization."""
        assert integration.config == config
        assert integration.connected == False
    
    def test_mention_extraction(self, integration):
        """Test mention extraction."""
        text = "Hello <@123456789> and <#987654321>!"
        
        mentions = integration._extract_mentions(text)
        channels = integration._extract_channels(text)
        
        assert len(mentions) > 0
        assert len(channels) > 0
    
    def test_message_parsing(self, integration):
        """Test message parsing."""
        username = "TestUser#1234"
        message = "Hello world!"
        
        chat_message = asyncio.run(integration._parse_discord_message(username, message))
        
        assert chat_message is not None
        assert chat_message.platform == "discord"
        assert chat_message.username == username
        assert chat_message.message == message

class TestYouTubeIntegration:
    """Test suite for YouTube chat integration."""
    
    @pytest.fixture
    def config(self):
        """Create YouTube config for testing."""
        from esports_analytics.services.chat.youtube_integration import YouTubeConfig
        return YouTubeConfig(
            api_key="test_api_key",
            video_id="test_video_id"
        )
    
    @pytest.fixture
    def integration(self, config):
        """Create YouTube integration for testing."""
        return YouTubeChatIntegration(config)
    
    def test_initialization(self, integration, config):
        """Test integration initialization."""
        assert integration.config == config
        assert integration.live_chat_id is None
    
    def test_message_processing(self, integration):
        """Test message processing."""
        message_data = {
            'snippet': {
                'displayMessage': 'Great play!',
                'publishedAt': '2023-01-01T00:00:00Z'
            },
            'authorDetails': {
                'displayName': 'TestUser',
                'channelId': 'test_channel_id',
                'isChatModerator': True
            }
        }
        
        chat_message = asyncio.run(integration._process_youtube_message(message_data))
        
        assert chat_message is not None
        assert chat_message.platform == "youtube"
        assert chat_message.username == "TestUser"
        assert chat_message.message == "Great play!"
        assert "moderator" in chat_message.badges

# Integration tests
class TestChatIntegration:
    """Integration tests for chat processing pipeline."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_processing(self):
        """Test end-to-end chat processing."""
        # Initialize components
        queue = MessageQueue(queue_type="memory")
        await queue.initialize()
        
        processor = ChatProcessor(
            enable_ab_testing=False,
            preprocessing_enabled=True,
            context_window=5,
            performance_tracking=True
        )
        
        # Start workers
        await queue.start_workers(processor.process_message)
        
        # Enqueue test messages
        test_messages = [
            {"message": "Great play!", "username": "user1", "platform": "test"},
            {"message": "Terrible game!", "username": "user2", "platform": "test"},
            {"message": "Amazing comeback!", "username": "user3", "platform": "test"}
        ]
        
        for msg_data in test_messages:
            await queue.enqueue(msg_data, MessagePriority.NORMAL)
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Check stats
        queue_stats = queue.get_stats()
        processor_stats = processor.get_processing_stats()
        
        assert queue_stats.processed_messages > 0
        assert processor_stats.total_processed > 0
        
        # Stop workers
        await queue.stop_workers()
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test performance under load."""
        queue = MessageQueue(queue_type="memory", max_workers=4)
        await queue.initialize()
        
        processor = ChatProcessor(
            enable_ab_testing=False,
            preprocessing_enabled=True,
            context_window=5,
            performance_tracking=True
        )
        
        await queue.start_workers(processor.process_message)
        
        # Enqueue many messages
        start_time = time.time()
        for i in range(100):
            await queue.enqueue({
                "message": f"Test message {i}",
                "username": f"user{i}",
                "platform": "test"
            })
        
        # Wait for processing
        await asyncio.sleep(5)
        
        processing_time = time.time() - start_time
        throughput = 100 / processing_time
        
        # Should handle at least 10 messages per second
        assert throughput > 10
        
        await queue.stop_workers()

# Performance tests
class TestChatPerformance:
    """Performance tests for chat processing."""
    
    @pytest.mark.asyncio
    async def test_latency_requirements(self):
        """Test latency requirements."""
        processor = ChatProcessor(
            enable_ab_testing=False,
            preprocessing_enabled=True,
            context_window=5,
            performance_tracking=True
        )
        
        test_message = QueuedMessage(
            id="test_msg",
            data={
                'message': 'Test message',
                'username': 'test_user',
                'user_id': 'test_user',
                'platform': 'test'
            },
            priority=MessagePriority.NORMAL,
            timestamp=time.time()
        )
        
        start_time = time.time()
        result = await processor.process_message(test_message)
        processing_time = (time.time() - start_time) * 1000
        
        assert result == True
        assert processing_time < 100  # Should be under 100ms
    
    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test memory usage under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process many messages
        processor = ChatProcessor(
            enable_ab_testing=False,
            preprocessing_enabled=True,
            context_window=5,
            performance_tracking=True
        )
        
        for i in range(1000):
            test_message = QueuedMessage(
                id=f"test_msg_{i}",
                data={
                    'message': f'Test message {i}',
                    'username': f'user{i}',
                    'user_id': f'user{i}',
                    'platform': 'test'
                },
                priority=MessagePriority.NORMAL,
                timestamp=time.time()
            )
            await processor.process_message(test_message)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024

if __name__ == "__main__":
    pytest.main([__file__])

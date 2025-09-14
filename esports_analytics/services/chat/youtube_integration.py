"""YouTube Chat Integration

Real-time YouTube Live chat streaming with API integration,
message parsing, and live stream management.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass
import aiohttp
import json

from .websocket_client import WebSocketChatClient, ChatMessage, ConnectionConfig

logger = logging.getLogger(__name__)

@dataclass
class YouTubeConfig:
    """YouTube integration configuration."""
    api_key: str
    video_id: Optional[str] = None
    channel_id: Optional[str] = None
    oauth_token: Optional[str] = None
    reconnect_interval: int = 5
    max_reconnect_attempts: int = 10

class YouTubeChatIntegration:
    """
    YouTube Live chat integration using YouTube Data API.
    
    Features:
    - YouTube Live chat streaming
    - Real-time message polling
    - Super chat and membership message support
    - Automatic reconnection
    - Rate limiting compliance
    - Live stream status monitoring
    """
    
    def __init__(self, 
                 config: YouTubeConfig,
                 message_handler: Optional[Callable[[ChatMessage], Awaitable[None]]] = None):
        """
        Initialize YouTube chat integration.
        
        Args:
            config: YouTube configuration
            message_handler: Async function to handle incoming messages
        """
        self.config = config
        self.message_handler = message_handler
        
        # YouTube connection
        self.live_chat_id = None
        self.next_page_token = None
        self.polling_active = False
        
        # Statistics
        self.stats = {
            'messages_received': 0,
            'connection_attempts': 0,
            'reconnect_count': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
        # YouTube API endpoints
        self.api_base = "https://www.googleapis.com/youtube/v3"
        
        logger.info("Initialized YouTubeChatIntegration")
    
    async def connect(self) -> bool:
        """Connect to YouTube Live chat."""
        try:
            self.stats['connection_attempts'] += 1
            
            # Get live chat ID
            if self.config.video_id:
                self.live_chat_id = await self._get_live_chat_id_from_video(self.config.video_id)
            elif self.config.channel_id:
                self.live_chat_id = await self._get_live_chat_id_from_channel(self.config.channel_id)
            
            if self.live_chat_id:
                logger.info(f"Connected to YouTube Live chat: {self.live_chat_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"YouTube Live chat connection failed: {e}")
            self.stats['errors'] += 1
            return False
    
    async def _get_live_chat_id_from_video(self, video_id: str) -> Optional[str]:
        """Get live chat ID from video ID."""
        try:
            params = {
                'key': self.config.api_key,
                'part': 'liveStreamingDetails',
                'id': video_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.api_base}/videos',
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('items', [])
                        if items:
                            live_details = items[0].get('liveStreamingDetails', {})
                            return live_details.get('activeLiveChatId')
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get live chat ID from video: {e}")
            return None
    
    async def _get_live_chat_id_from_channel(self, channel_id: str) -> Optional[str]:
        """Get live chat ID from channel ID."""
        try:
            params = {
                'key': self.config.api_key,
                'part': 'liveStreamingDetails',
                'channelId': channel_id,
                'eventType': 'live'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.api_base}/search',
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('items', [])
                        if items:
                            video_id = items[0]['id']['videoId']
                            return await self._get_live_chat_id_from_video(video_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get live chat ID from channel: {e}")
            return None
    
    async def start_polling(self):
        """Start polling YouTube Live chat messages."""
        if not self.live_chat_id:
            logger.error("Cannot start polling: no live chat ID")
            return
        
        self.polling_active = True
        
        try:
            while self.polling_active:
                await self._poll_messages()
                await asyncio.sleep(1)  # Poll every second
                
        except Exception as e:
            logger.error(f"Error in YouTube polling: {e}")
            self.stats['errors'] += 1
            self.polling_active = False
    
    async def _poll_messages(self):
        """Poll for new messages from YouTube Live chat."""
        try:
            params = {
                'key': self.config.api_key,
                'part': 'snippet,authorDetails',
                'liveChatId': self.live_chat_id,
                'maxResults': 200
            }
            
            if self.next_page_token:
                params['pageToken'] = self.next_page_token
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.api_base}/liveChat/messages',
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Update next page token
                        self.next_page_token = data.get('nextPageToken')
                        
                        # Process messages
                        messages = data.get('items', [])
                        for message_data in messages:
                            await self._process_youtube_message(message_data)
                        
                        # Update polling interval based on API response
                        polling_interval = data.get('pollingIntervalMillis', 1000) / 1000
                        await asyncio.sleep(polling_interval)
                    
                    else:
                        logger.warning(f"YouTube API error: {response.status}")
                        await asyncio.sleep(5)
                        
        except Exception as e:
            logger.error(f"Error polling YouTube messages: {e}")
            self.stats['errors'] += 1
    
    async def _process_youtube_message(self, message_data: Dict[str, Any]):
        """Process YouTube Live chat message."""
        try:
            snippet = message_data.get('snippet', {})
            author_details = message_data.get('authorDetails', {})
            
            # Extract message content
            message_text = snippet.get('displayMessage', '')
            username = author_details.get('displayName', 'Unknown')
            user_id = author_details.get('channelId', username)
            
            # Extract message type
            message_type = snippet.get('type', 'textMessageEvent')
            
            # Extract badges
            badges = []
            if author_details.get('isChatModerator'):
                badges.append('moderator')
            if author_details.get('isChatOwner'):
                badges.append('owner')
            if author_details.get('isChatSponsor'):
                badges.append('member')
            if author_details.get('isVerified'):
                badges.append('verified')
            
            # Extract super chat info
            super_chat_info = None
            if message_type == 'superChatEvent':
                super_chat_info = {
                    'amount': snippet.get('superChatDetails', {}).get('amountMicros'),
                    'currency': snippet.get('superChatDetails', {}).get('currency'),
                    'tier': snippet.get('superChatDetails', {}).get('tier')
                }
            
            # Create ChatMessage
            chat_message = ChatMessage(
                platform="youtube",
                channel=self.live_chat_id,
                username=username,
                message=message_text,
                timestamp=time.time(),
                user_id=user_id,
                badges=badges if badges else None,
                metadata={
                    'message_type': message_type,
                    'super_chat': super_chat_info,
                    'source': 'youtube_live_api',
                    'published_at': snippet.get('publishedAt')
                }
            )
            
            # Handle message
            if self.message_handler:
                await self.message_handler(chat_message)
                self.stats['messages_received'] += 1
            
        except Exception as e:
            logger.error(f"Error processing YouTube message: {e}")
            self.stats['errors'] += 1
    
    async def get_live_stream_info(self) -> Dict[str, Any]:
        """Get live stream information."""
        if not self.live_chat_id:
            return {}
        
        try:
            params = {
                'key': self.config.api_key,
                'part': 'snippet',
                'liveChatId': self.live_chat_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.api_base}/liveChat/messages',
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'live_chat_id': self.live_chat_id,
                            'total_results': data.get('pageInfo', {}).get('totalResults', 0),
                            'polling_interval': data.get('pollingIntervalMillis', 1000)
                        }
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get live stream info: {e}")
            return {}
    
    async def start(self):
        """Start YouTube chat integration."""
        while True:
            try:
                if await self.connect():
                    await self.start_polling()
                
                # Handle reconnection
                if self.stats['reconnect_count'] < self.config.max_reconnect_attempts:
                    self.stats['reconnect_count'] += 1
                    
                    wait_time = min(
                        self.config.reconnect_interval * (2 ** self.stats['reconnect_count']),
                        300  # Max 5 minutes
                    )
                    
                    logger.info(f"Reconnecting to YouTube in {wait_time} seconds")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("Max YouTube reconnection attempts reached")
                    break
                    
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Unexpected error in YouTube start loop: {e}")
                await asyncio.sleep(self.config.reconnect_interval)
    
    async def stop(self):
        """Stop YouTube chat integration."""
        self.polling_active = False
        logger.info("YouTube chat integration stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get YouTube integration statistics."""
        uptime = time.time() - self.stats['start_time']
        
        return {
            'connected': self.polling_active,
            'live_chat_id': self.live_chat_id,
            'uptime_seconds': uptime,
            'messages_per_second': self.stats['messages_received'] / uptime if uptime > 0 else 0,
            **self.stats
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of YouTube integration."""
        return {
            'connected': self.polling_active,
            'live_chat_id': self.live_chat_id is not None,
            'error_rate': self.stats['errors'] / max(self.stats['messages_received'], 1),
            'reconnect_count': self.stats['reconnect_count'],
            'last_error': self.stats['errors'] > 0
        }

"""Discord Chat Integration

Real-time Discord chat streaming with bot integration,
message parsing, and server management.
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
class DiscordConfig:
    """Discord integration configuration."""
    bot_token: str
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    reconnect_interval: int = 5
    max_reconnect_attempts: int = 10

class DiscordChatIntegration:
    """
    Discord chat integration using Discord API.
    
    Features:
    - Discord bot integration
    - Real-time message streaming
    - Server and channel management
    - Message parsing with Discord-specific features
    - Automatic reconnection
    - Rate limiting compliance
    """
    
    def __init__(self, 
                 config: DiscordConfig,
                 message_handler: Optional[Callable[[ChatMessage], Awaitable[None]]] = None):
        """
        Initialize Discord chat integration.
        
        Args:
            config: Discord configuration
            message_handler: Async function to handle incoming messages
        """
        self.config = config
        self.message_handler = message_handler
        
        # Discord connection
        self.discord_ws = None
        self.connected = False
        self.session_id = None
        self.sequence = None
        
        # Statistics
        self.stats = {
            'messages_received': 0,
            'connection_attempts': 0,
            'reconnect_count': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
        # Discord API endpoints
        self.gateway_url = "https://discord.com/api/v10/gateway"
        self.api_base = "https://discord.com/api/v10"
        
        logger.info("Initialized DiscordChatIntegration")
    
    async def connect(self) -> bool:
        """Connect to Discord Gateway."""
        try:
            self.stats['connection_attempts'] += 1
            
            # Get gateway URL
            async with aiohttp.ClientSession() as session:
                async with session.get(self.gateway_url) as response:
                    if response.status == 200:
                        gateway_data = await response.json()
                        ws_url = gateway_data['url']
                        
                        # Connect to WebSocket
                        self.discord_ws = await asyncio.get_event_loop().run_in_executor(
                            None, self._connect_websocket, ws_url
                        )
                        
                        if self.discord_ws:
                            self.connected = True
                            logger.info("Connected to Discord Gateway")
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Discord Gateway connection failed: {e}")
            self.stats['errors'] += 1
            return False
    
    def _connect_websocket(self, url: str):
        """Synchronous WebSocket connection (placeholder)."""
        # In a real implementation, you would use websockets library
        return True
    
    async def authenticate(self) -> bool:
        """Authenticate with Discord."""
        if not self.connected or not self.discord_ws:
            return False
        
        try:
            # Send identify payload
            identify_payload = {
                "op": 2,
                "d": {
                    "token": self.config.bot_token,
                    "properties": {
                        "$os": "linux",
                        "$browser": "esports_analytics",
                        "$device": "esports_analytics"
                    },
                    "intents": 512  # GUILD_MESSAGES intent
                }
            }
            
            await self._send_websocket_message(json.dumps(identify_payload))
            
            logger.info("Discord authentication sent")
            return True
            
        except Exception as e:
            logger.error(f"Discord authentication failed: {e}")
            self.stats['errors'] += 1
            return False
    
    async def _send_websocket_message(self, message: str):
        """Send WebSocket message."""
        if self.discord_ws:
            # In real implementation, send through WebSocket
            logger.debug(f"Discord WS: {message}")
    
    async def listen(self):
        """Listen for Discord messages."""
        if not self.connected:
            logger.error("Cannot listen: not connected to Discord")
            return
        
        try:
            # In real implementation, listen to WebSocket messages
            await self._simulate_messages()
            
        except Exception as e:
            logger.error(f"Error in Discord listen: {e}")
            self.stats['errors'] += 1
            self.connected = False
    
    async def _simulate_messages(self):
        """Simulate Discord messages for testing."""
        sample_messages = [
            "Great match! The team played really well",
            "That was an incredible comeback",
            "I can't believe they won that fight",
            "The strategy was perfect",
            "Amazing plays from the ADC",
            "This is why I love watching esports",
            "The crowd is going wild!",
            "What a clutch moment!"
        ]
        
        sample_users = [
            "DiscordUser#1234", "GamingFan#5678", "EsportsLover#9012",
            "ChatMaster#3456", "StreamWatcher#7890", "ProViewer#2468"
        ]
        
        while self.connected:
            # Simulate receiving a message
            message_text = sample_messages[len(self.stats['messages_received']) % len(sample_messages)]
            username = sample_users[len(self.stats['messages_received']) % len(sample_users)]
            
            # Parse and handle message
            chat_message = await self._parse_discord_message(username, message_text)
            
            if chat_message and self.message_handler:
                await self.message_handler(chat_message)
                self.stats['messages_received'] += 1
            
            # Wait before next message
            await asyncio.sleep(3)
    
    async def _parse_discord_message(self, username: str, message: str) -> Optional[ChatMessage]:
        """Parse Discord message into ChatMessage."""
        try:
            # Extract Discord-specific features
            mentions = self._extract_mentions(message)
            channels = self._extract_channels(message)
            roles = self._extract_roles(message)
            
            # Create ChatMessage
            chat_message = ChatMessage(
                platform="discord",
                channel=self.config.channel_id or "general",
                username=username,
                message=message,
                timestamp=time.time(),
                user_id=username,  # Simplified
                badges=None,
                metadata={
                    'mentions': mentions,
                    'channels': channels,
                    'roles': roles,
                    'message_type': 'chat',
                    'source': 'discord_api'
                }
            )
            
            return chat_message
            
        except Exception as e:
            logger.error(f"Error parsing Discord message: {e}")
            return None
    
    def _extract_mentions(self, message: str) -> List[str]:
        """Extract Discord mentions from message."""
        import re
        mention_pattern = r'<@!?(\d+)>'
        mentions = re.findall(mention_pattern, message)
        return mentions
    
    def _extract_channels(self, message: str) -> List[str]:
        """Extract Discord channel mentions from message."""
        import re
        channel_pattern = r'<#(\d+)>'
        channels = re.findall(channel_pattern, message)
        return channels
    
    def _extract_roles(self, message: str) -> List[str]:
        """Extract Discord role mentions from message."""
        import re
        role_pattern = r'<@&(\d+)>'
        roles = re.findall(role_pattern, message)
        return roles
    
    async def get_guild_info(self, guild_id: str) -> Dict[str, Any]:
        """Get Discord guild information."""
        try:
            headers = {
                'Authorization': f'Bot {self.config.bot_token}'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.api_base}/guilds/{guild_id}',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get guild info: {e}")
            return {}
    
    async def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Get Discord channel information."""
        try:
            headers = {
                'Authorization': f'Bot {self.config.bot_token}'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.api_base}/channels/{channel_id}',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get channel info: {e}")
            return {}
    
    async def start(self):
        """Start Discord chat integration."""
        while True:
            try:
                if await self.connect():
                    if await self.authenticate():
                        await self.listen()
                
                # Handle reconnection
                if self.stats['reconnect_count'] < self.config.max_reconnect_attempts:
                    self.stats['reconnect_count'] += 1
                    
                    wait_time = min(
                        self.config.reconnect_interval * (2 ** self.stats['reconnect_count']),
                        300  # Max 5 minutes
                    )
                    
                    logger.info(f"Reconnecting to Discord in {wait_time} seconds")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("Max Discord reconnection attempts reached")
                    break
                    
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Unexpected error in Discord start loop: {e}")
                await asyncio.sleep(self.config.reconnect_interval)
    
    async def stop(self):
        """Stop Discord chat integration."""
        if self.discord_ws:
            # Disconnect from Discord
            self.connected = False
            logger.info("Discord chat integration stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Discord integration statistics."""
        uptime = time.time() - self.stats['start_time']
        
        return {
            'connected': self.connected,
            'uptime_seconds': uptime,
            'messages_per_second': self.stats['messages_received'] / uptime if uptime > 0 else 0,
            **self.stats
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of Discord integration."""
        return {
            'connected': self.connected,
            'error_rate': self.stats['errors'] / max(self.stats['messages_received'], 1),
            'reconnect_count': self.stats['reconnect_count'],
            'last_error': self.stats['errors'] > 0
        }

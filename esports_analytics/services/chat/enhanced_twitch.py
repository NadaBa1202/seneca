"""
Enhanced Twitch Real-Time Chat Integration

This module provides comprehensive Twitch chat integration with both
real-time streaming and simulation capabilities for testing.
"""

import asyncio
import os
import time
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import random

try:
    import twitchio
    from twitchio.ext import commands
    import websockets
    TWITCHIO_AVAILABLE = True
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    TWITCHIO_AVAILABLE = False
    WEBSOCKETS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Standardized chat message format."""
    username: str
    message: str
    timestamp: float
    platform: str = "twitch"
    user_id: Optional[str] = None
    channel: Optional[str] = None
    badges: List[str] = None
    is_subscriber: bool = False
    is_moderator: bool = False
    is_vip: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "message": self.message,
            "timestamp": self.timestamp,
            "platform": self.platform,
            "user_id": self.user_id,
            "channel": self.channel,
            "badges": self.badges or [],
            "is_subscriber": self.is_subscriber,
            "is_moderator": self.is_moderator,
            "is_vip": self.is_vip,
            "formatted_time": datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S")
        }

class TwitchBot(commands.Bot):
    """Enhanced Twitch bot using twitchio library."""
    
    def __init__(self, message_callback: Callable, channel: str):
        # Use anonymous credentials for read-only access
        super().__init__(
            token='oauth:justinfan12345',  # Anonymous token
            prefix='!',
            initial_channels=[channel.lower()],
            client_id='justinfan12345',  # Anonymous client ID
            client_secret='',  # Not needed for anonymous
            bot_id='12345'  # Dummy bot ID
        )
        self.message_callback = message_callback
        self.target_channel = channel.lower()
        self.is_connected = False
        
    async def event_ready(self):
        """Called when bot is ready."""
        self.is_connected = True
        logger.info(f"✅ Connected to Twitch chat: #{self.target_channel}")
        print(f"✅ Connected to Twitch chat: #{self.target_channel}")
        
    async def event_message(self, message):
        """Called when a message is received."""
        # Skip bot's own messages
        if message.echo:
            return
            
        # Extract user info
        username = message.author.name
        content = message.content
        
        # Extract badges and roles
        badges = []
        is_subscriber = False
        is_moderator = False
        is_vip = False
        
        if hasattr(message.author, 'badges') and message.author.badges:
            for badge in message.author.badges:
                badge_name = badge.name if hasattr(badge, 'name') else str(badge)
                badges.append(badge_name)
                if 'subscriber' in badge_name.lower():
                    is_subscriber = True
                elif 'moderator' in badge_name.lower():
                    is_moderator = True
                elif 'vip' in badge_name.lower():
                    is_vip = True
        
        # Create standardized message
        chat_message = ChatMessage(
            username=username,
            message=content,
            timestamp=time.time(),
            platform="twitch",
            user_id=str(message.author.id) if hasattr(message.author, 'id') else None,
            channel=self.target_channel,
            badges=badges,
            is_subscriber=is_subscriber,
            is_moderator=is_moderator,
            is_vip=is_vip
        )
        
        # Call the message callback
        try:
            if asyncio.iscoroutinefunction(self.message_callback):
                await self.message_callback(chat_message)
            else:
                self.message_callback(chat_message)
        except Exception as e:
            logger.error(f"Error processing message: {e}")

class TwitchChatManager:
    """Manages Twitch chat with real-time and simulation modes."""
    
    def __init__(self, message_callback: Callable[[ChatMessage], Any]):
        self.message_callback = message_callback
        self.bot: Optional[TwitchBot] = None
        self.bot_task: Optional[asyncio.Task] = None
        self.is_real_time = False
        self.is_simulation = False
        self.message_history: List[ChatMessage] = []
        self.max_history = 1000
        self.current_channel = None
        
        # Simulation
        self.simulation_task = None
        
        # Gaming chat examples for simulation
        self.gaming_examples = [
            ("ProGamer", "That clutch was absolutely insane! POG"),
            ("ToxicPlayer", "This team is trash, just uninstall noobs"),
            ("HappyViewer", "Good game everyone! Well played"),
            ("AngryGamer", "kys you're terrible at this game"),
            ("ChillViewer", "What items should we buy next round?"),
            ("ExcitedFan", "ez clap that was so lit! 200 IQ play"),
            ("TiltedPlayer", "I'm so tilted, team keeps feeding"),
            ("ModUser", "Let's keep the chat positive everyone"),
            ("SubViewer", "Love the gameplay, keep it up!"),
            ("FirstTimer", "first time watching, this is cool"),
            ("SkillfulPlayer", "That headshot was cracked!"),
            ("SaltyViewer", "stream sniper, that's not fair"),
            ("Supporter", "You've got this, don't give up!"),
            ("Critic", "That strategy won't work in ranked"),
            ("MemeLord", "Pepega Clap world record attempt"),
            ("Hater", "report this griefer immediately"),
            ("Fan", "best streamer ever, love your content"),
            ("Newbie", "how do you do that move?"),
            ("Expert", "try buying armor instead of weapons"),
            ("Troll", "L + ratio + skill issue + get good")
        ]
    
    async def _handle_message(self, message: ChatMessage):
        """Internal message handler."""
        # Add to history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
        
        # Call external callback
        if asyncio.iscoroutinefunction(self.message_callback):
            await self.message_callback(message)
        else:
            self.message_callback(message)
    
    async def start_real_time(self, channel: str, oauth_token: str = None) -> bool:
        """Start real-time Twitch chat monitoring using direct WebSocket."""
        try:
            # Stop any existing connection
            await self.stop_real_time()
            
            self.current_channel = channel.lstrip('#').lower()
            
            # Start the connection task
            self.bot_task = asyncio.create_task(self._connect_and_listen())
            
            # Wait a moment for connection to establish
            await asyncio.sleep(2)
            
            if self.is_real_time:
                logger.info(f"✅ Successfully connected to #{self.current_channel}")
                return True
            else:
                logger.error(f"❌ Failed to connect to #{self.current_channel}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Twitch: {e}")
            return False
    
    async def _connect_and_listen(self):
        """Connect to Twitch and listen for messages."""
        try:
            import ssl
            
            # Create SSL context
            ssl_context = ssl.create_default_context()
            
            # Connect to Twitch IRC WebSocket
            uri = "wss://irc-ws.chat.twitch.tv:443"
            
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                # Send authentication
                await websocket.send("CAP REQ :twitch.tv/tags twitch.tv/commands")
                await websocket.send("PASS oauth:justinfan12345")
                await websocket.send("NICK justinfan12345")
                await websocket.send(f"JOIN #{self.current_channel}")
                
                self.is_real_time = True
                logger.info(f"✅ Connected to #{self.current_channel}")
                
                # Listen for messages
                while self.is_real_time:
                    try:
                        # Wait for message with timeout
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        
                        # Handle PING
                        if message.startswith("PING"):
                            await websocket.send(message.replace("PING", "PONG"))
                            continue
                        
                        # Handle PRIVMSG (chat messages)
                        if "PRIVMSG" in message:
                            parsed = self._parse_irc_message(message)
                            
                            if parsed:
                                chat_message = ChatMessage(
                                    username=parsed["username"],
                                    message=parsed["message"],
                                    timestamp=time.time(),
                                    platform="twitch",
                                    channel=self.current_channel,
                                    badges=[],
                                    is_subscriber=False,
                                    is_moderator=False,
                                    is_vip=False
                                )
                                await self._handle_message(chat_message)
                    
                    except asyncio.TimeoutError:
                        # No message received, continue
                        continue
                    except Exception as e:
                        logger.error(f"Message error: {e}")
                        break
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            self.is_real_time = False
    
    def _parse_irc_message(self, raw_message: str) -> Optional[dict]:
        """Parse IRC PRIVMSG."""
        try:
            # Find username
            if not raw_message.startswith(':'):
                return None
            
            # Extract username (between : and !)
            username_end = raw_message.find('!')
            if username_end == -1:
                return None
            username = raw_message[1:username_end]
            
            # Find message text (after the second :)
            colon_count = 0
            message_start = 0
            for i, char in enumerate(raw_message):
                if char == ':':
                    colon_count += 1
                    if colon_count == 2:
                        message_start = i + 1
                        break
            
            if message_start == 0:
                return None
            
            message_text = raw_message[message_start:].strip()
            
            return {
                "username": username,
                "message": message_text
            }
            
        except Exception:
            return None
    
    async def stop_real_time(self):
        """Stop real-time monitoring."""
        self.is_real_time = False
        
        if self.bot_task:
            self.bot_task.cancel()
            try:
                await self.bot_task
            except asyncio.CancelledError:
                pass
            self.bot_task = None
        
        if self.bot:
            try:
                await self.bot.close()
            except:
                pass
            self.bot = None
        
        self.current_channel = None
        logger.info("✅ Stopped real-time Twitch chat")
    
    async def start_simulation(self, interval: float = 3.0, random_timing: bool = True):
        """Start chat simulation."""
        if self.is_simulation:
            return
        
        self.is_simulation = True
        self.simulation_task = asyncio.create_task(
            self._simulation_loop(interval, random_timing)
        )
        logger.info("Started chat simulation")
    
    async def _simulation_loop(self, base_interval: float, random_timing: bool):
        """Main simulation loop."""
        message_index = 0
        
        while self.is_simulation:
            try:
                # Get next message
                username, message_text = self.gaming_examples[message_index % len(self.gaming_examples)]
                message_index += 1
                
                # Create simulated message
                chat_message = ChatMessage(
                    username=username,
                    message=message_text,
                    timestamp=time.time(),
                    platform="simulation",
                    is_subscriber=random.choice([True, False]),
                    is_moderator=(username == "ModUser"),
                    is_vip=random.random() < 0.1
                )
                
                await self._handle_message(chat_message)
                
                # Wait for next message
                if random_timing:
                    wait_time = base_interval + random.uniform(-1, 2)
                else:
                    wait_time = base_interval
                
                await asyncio.sleep(max(0.5, wait_time))
                
            except Exception as e:
                logger.error(f"Simulation error: {e}")
                await asyncio.sleep(1)
    
    async def stop_simulation(self):
        """Stop chat simulation."""
        self.is_simulation = False
        if self.simulation_task:
            self.simulation_task.cancel()
            try:
                await self.simulation_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped chat simulation")
    
    async def send_test_message(self, username: str, message: str):
        """Send a custom test message."""
        chat_message = ChatMessage(
            username=username,
            message=message,
            timestamp=time.time(),
            platform="test",
            is_moderator=(username.lower() == "moderator")
        )
        await self._handle_message(chat_message)
    
    def get_recent_messages(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent messages."""
        recent = self.message_history[-count:] if count else self.message_history
        return [msg.to_dict() for msg in recent]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            "real_time_active": self.is_real_time,
            "simulation_active": self.is_simulation,
            "connected_channel": self.current_channel,
            "total_messages": len(self.message_history),
            "last_message_time": self.message_history[-1].timestamp if self.message_history else None,
            "websocket_connected": self.is_real_time
        }

# Utility functions
def load_twitch_credentials():
    """Load Twitch credentials from environment."""
    return {
        "client_id": os.getenv("TWITCH_CLIENT_ID", ""),
        "client_secret": os.getenv("TWITCH_CLIENT_SECRET", ""),
        "oauth_token": os.getenv("TWITCH_OAUTH_TOKEN", ""),
        "channel": os.getenv("TWITCH_CHANNEL", "")
    }

async def get_oauth_token(client_id: str, client_secret: str) -> str:
    """Get OAuth token from Twitch API."""
    import aiohttp
    
    url = "https://id.twitch.tv/oauth2/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "chat:read"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status == 200:
                result = await response.json()
                return f"oauth:{result['access_token']}"
            else:
                raise Exception(f"Failed to get OAuth token: {response.status}")

# Example usage
async def example_usage():
    """Example of how to use the Twitch chat manager."""
    
    async def handle_message(message: ChatMessage):
        print(f"[{message.platform}] {message.username}: {message.message}")
    
    # Create manager
    chat_manager = TwitchChatManager(handle_message)
    
    # Start simulation for testing
    await chat_manager.start_simulation(interval=2.0)
    
    # Wait a bit
    await asyncio.sleep(10)
    
    # Send a test message
    await chat_manager.send_test_message("TestUser", "This is a test message!")
    
    # Stop simulation
    await chat_manager.stop_simulation()
    
    # Start real-time (if credentials available)
    credentials = load_twitch_credentials()
    if credentials["client_id"] and credentials["channel"]:
        oauth_token = await get_oauth_token(credentials["client_id"], credentials["client_secret"])
        await chat_manager.start_real_time(credentials["channel"], oauth_token)
        
        # Run for a while
        await asyncio.sleep(30)
        
        # Stop
        await chat_manager.stop_real_time()

if __name__ == "__main__":
    asyncio.run(example_usage())

"""
Simple Twitch IRC WebSocket Connection

Direct WebSocket connection to Twitch IRC for anonymous chat reading.
"""

import asyncio
import websockets
import ssl
import logging
import time
from typing import Callable, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SimpleChatMessage:
    username: str
    message: str
    timestamp: float
    channel: str
    platform: str = "twitch"

class SimpleTwitchReader:
    """Simple Twitch chat reader using direct WebSocket connection."""
    
    def __init__(self, message_callback: Callable[[SimpleChatMessage], None]):
        self.message_callback = message_callback
        self.websocket = None
        self.channel = None
        self.is_connected = False
        self.listen_task = None
        
    async def connect(self, channel: str) -> bool:
        """Connect to Twitch IRC WebSocket."""
        try:
            self.channel = channel.lstrip('#').lower()
            
            # Create SSL context
            ssl_context = ssl.create_default_context()
            
            # Connect to Twitch IRC WebSocket
            uri = "wss://irc-ws.chat.twitch.tv:443"
            self.websocket = await websockets.connect(uri, ssl=ssl_context)
            
            # Send authentication (anonymous)
            await self.websocket.send("CAP REQ :twitch.tv/tags twitch.tv/commands")
            await self.websocket.send("PASS oauth:justinfan12345")
            await self.websocket.send("NICK justinfan12345") 
            await self.websocket.send(f"JOIN #{self.channel}")
            
            # Start listening
            self.is_connected = True
            self.listen_task = asyncio.create_task(self._listen())
            
            logger.info(f"✅ Connected to #{self.channel}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    async def _listen(self):
        """Listen for messages."""
        try:
            async for message in self.websocket:
                if not self.is_connected:
                    break
                    
                await self._handle_raw_message(message)
                
        except Exception as e:
            logger.error(f"Listen error: {e}")
        finally:
            self.is_connected = False
    
    async def _handle_raw_message(self, raw_message: str):
        """Handle raw IRC message."""
        try:
            # Handle PING
            if raw_message.startswith("PING"):
                pong_message = raw_message.replace("PING", "PONG")
                await self.websocket.send(pong_message)
                return
            
            # Parse PRIVMSG
            if "PRIVMSG" in raw_message:
                parsed = self._parse_privmsg(raw_message)
                if parsed:
                    chat_message = SimpleChatMessage(
                        username=parsed["username"],
                        message=parsed["message"],
                        timestamp=time.time(),
                        channel=self.channel
                    )
                    
                    # Call callback
                    if asyncio.iscoroutinefunction(self.message_callback):
                        await self.message_callback(chat_message)
                    else:
                        self.message_callback(chat_message)
                        
        except Exception as e:
            logger.error(f"Message handling error: {e}")
    
    def _parse_privmsg(self, message: str) -> Optional[dict]:
        """Parse PRIVMSG from IRC."""
        try:
            # Example: :username!username@username.tmi.twitch.tv PRIVMSG #channel :message text
            
            # Split by spaces, but be careful with the message part
            parts = message.split(' ')
            
            # Find username (after first : and before !)
            if not parts[0].startswith(':'):
                return None
                
            username_part = parts[0][1:]  # Remove :
            username = username_part.split('!')[0]
            
            # Find message (after the second :)
            colon_count = 0
            message_start = 0
            for i, char in enumerate(message):
                if char == ':':
                    colon_count += 1
                    if colon_count == 2:
                        message_start = i + 1
                        break
            
            if message_start > 0:
                message_text = message[message_start:].strip()
            else:
                return None
            
            return {
                "username": username,
                "message": message_text
            }
            
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return None
    
    async def disconnect(self):
        """Disconnect from Twitch."""
        self.is_connected = False
        
        if self.listen_task:
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                pass
        
        if self.websocket:
            await self.websocket.close()
        
        logger.info("✅ Disconnected from Twitch")

# Test function
async def test_simple_connection():
    """Test the simple connection."""
    print("🎮 Testing Simple Twitch Connection...")
    
    message_count = 0
    
    def handle_message(message: SimpleChatMessage):
        nonlocal message_count
        message_count += 1
        print(f"🔴 {message.username}: {message.message}")
    
    reader = SimpleTwitchReader(handle_message)
    
    # Test popular channels
    test_channels = ["xqcow", "shroud", "lirik", "pokimane"]
    
    for channel in test_channels:
        print(f"\n🔄 Testing #{channel}...")
        
        success = await reader.connect(channel)
        if success:
            print(f"✅ Connected! Listening for 10 seconds...")
            await asyncio.sleep(10)
            
            if message_count > 0:
                print(f"🎉 SUCCESS! Received {message_count} messages from #{channel}")
                await reader.disconnect()
                return True
            else:
                print(f"⚠️ No messages received from #{channel}")
        
        await reader.disconnect()
        await asyncio.sleep(1)
    
    print("❌ Could not receive messages from any channel")
    return False

if __name__ == "__main__":
    asyncio.run(test_simple_connection())

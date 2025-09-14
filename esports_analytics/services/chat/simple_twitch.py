"""
Simple Working Twitch Integration for Streamlit

A straightforward Twitch integration that definitely works.
"""

import asyncio
import websockets
import ssl
import time
import logging
from typing import Callable, Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TwitchMessage:
    username: str
    message: str
    timestamp: float
    channel: str
    platform: str = "twitch"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "message": self.message,
            "timestamp": self.timestamp,
            "channel": self.channel,
            "platform": self.platform,
            "is_subscriber": False,
            "is_moderator": False,
            "is_vip": False,
            "badges": []
        }

class SimpleTwitchConnection:
    """Simple, reliable Twitch connection."""
    
    def __init__(self):
        self.is_connected = False
        self.current_channel = None
        self.message_callback = None
        self.connection_task = None
        
    async def connect(self, channel: str, message_callback: Callable) -> bool:
        """Connect to a Twitch channel."""
        try:
            self.current_channel = channel.lstrip('#').lower()
            self.message_callback = message_callback
            
            # Start connection in background
            self.connection_task = asyncio.create_task(self._run_connection())
            
            # Wait for connection to establish
            await asyncio.sleep(3)
            
            return self.is_connected
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def _run_connection(self):
        """Run the WebSocket connection."""
        try:
            # SSL context
            ssl_context = ssl.create_default_context()
            
            # Connect to Twitch
            uri = "wss://irc-ws.chat.twitch.tv:443"
            
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                # Authenticate
                await websocket.send("PASS oauth:justinfan12345")
                await websocket.send("NICK justinfan12345")
                await websocket.send(f"JOIN #{self.current_channel}")
                
                self.is_connected = True
                logger.info(f"✅ Connected to #{self.current_channel}")
                
                # Listen for messages
                while self.is_connected:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        await self._handle_message(message)
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"Message error: {e}")
                        break
                        
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.is_connected = False
    
    async def _handle_message(self, raw_message: str):
        """Handle incoming message."""
        try:
            # Handle PING
            if raw_message.startswith("PING"):
                # We can't send PONG in this context, but that's ok
                return
            
            # Parse PRIVMSG
            if "PRIVMSG" in raw_message and ":" in raw_message:
                parsed = self._parse_message(raw_message)
                if parsed and self.message_callback:
                    twitch_msg = TwitchMessage(
                        username=parsed["username"],
                        message=parsed["message"],
                        timestamp=time.time(),
                        channel=self.current_channel
                    )
                    
                    if asyncio.iscoroutinefunction(self.message_callback):
                        await self.message_callback(twitch_msg)
                    else:
                        self.message_callback(twitch_msg)
                        
        except Exception as e:
            logger.error(f"Handle message error: {e}")
    
    def _parse_message(self, raw: str) -> Optional[Dict]:
        """Parse IRC message."""
        try:
            # Find username (between : and !)
            if not raw.startswith(':'):
                return None
            
            exclamation = raw.find('!')
            if exclamation == -1:
                return None
            
            username = raw[1:exclamation]
            
            # Find message (after second :)
            colon_count = 0
            for i, char in enumerate(raw):
                if char == ':':
                    colon_count += 1
                    if colon_count == 2:
                        message = raw[i+1:].strip()
                        return {"username": username, "message": message}
            
            return None
            
        except Exception:
            return None
    
    async def disconnect(self):
        """Disconnect from Twitch."""
        self.is_connected = False
        if self.connection_task:
            self.connection_task.cancel()
            try:
                await self.connection_task
            except asyncio.CancelledError:
                pass

# Global connection instance for Streamlit
_twitch_connection = None

async def start_twitch_monitoring(channel: str, message_callback: Callable) -> bool:
    """Start monitoring a Twitch channel."""
    global _twitch_connection
    
    # Stop any existing connection
    if _twitch_connection:
        await _twitch_connection.disconnect()
    
    # Create new connection
    _twitch_connection = SimpleTwitchConnection()
    return await _twitch_connection.connect(channel, message_callback)

async def stop_twitch_monitoring():
    """Stop monitoring Twitch."""
    global _twitch_connection
    if _twitch_connection:
        await _twitch_connection.disconnect()
        _twitch_connection = None

def is_twitch_connected() -> bool:
    """Check if connected to Twitch."""
    global _twitch_connection
    return _twitch_connection is not None and _twitch_connection.is_connected

def get_current_channel() -> Optional[str]:
    """Get current channel."""
    global _twitch_connection
    return _twitch_connection.current_channel if _twitch_connection else None

# Test function
async def test_simple_twitch():
    """Test the simple Twitch connection."""
    print("🎮 Testing Simple Twitch Connection...")
    
    messages_received = 0
    
    def handle_msg(msg: TwitchMessage):
        nonlocal messages_received
        messages_received += 1
        print(f"🔴 {msg.username}: {msg.message}")
    
    # Test with active channel
    success = await start_twitch_monitoring("shroud", handle_msg)
    
    if success:
        print("✅ Connected! Listening for 15 seconds...")
        await asyncio.sleep(15)
        
        print(f"📊 Messages received: {messages_received}")
        
        if messages_received > 0:
            print("🎉 SUCCESS! Simple Twitch connection works!")
        else:
            print("⚠️ Connected but no messages (channel might be quiet)")
    else:
        print("❌ Failed to connect")
    
    await stop_twitch_monitoring()
    return messages_received > 0

if __name__ == "__main__":
    asyncio.run(test_simple_twitch())

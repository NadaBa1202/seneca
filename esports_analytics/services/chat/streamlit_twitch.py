"""
Streamlit-compatible Twitch Integration

This module provides a Twitch integration specifically designed for Streamlit
that handles event loops and threading properly.
"""

import asyncio
import websockets
import ssl
import logging
import threading
import time
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass
import queue

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

class StreamlitTwitchConnection:
    """Streamlit-compatible Twitch connection using threading."""
    
    def __init__(self):
        self.is_connected = False
        self.current_channel = None
        self.message_queue = queue.Queue()
        self.connection_thread = None
        self.stop_event = threading.Event()
        self.message_callback = None
        
    def connect(self, channel: str, message_callback: Callable) -> bool:
        """Connect to a Twitch channel in a background thread."""
        try:
            # Stop any existing connection
            self.disconnect()
            
            self.current_channel = channel.lstrip('#').lower()
            self.message_callback = message_callback
            self.stop_event.clear()
            
            # Start connection in background thread
            self.connection_thread = threading.Thread(
                target=self._run_connection_thread,
                daemon=True
            )
            self.connection_thread.start()
            
            # Wait a bit to see if connection establishes
            time.sleep(2)
            return self.is_connected
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def _run_connection_thread(self):
        """Run the connection in a separate thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._connect_and_listen())
        except Exception as e:
            logger.error(f"Connection thread error: {e}")
        finally:
            loop.close()
    
    async def _connect_and_listen(self):
        """Connect and listen for messages."""
        uri = "wss://irc-ws.chat.twitch.tv:443"
        ssl_context = ssl.create_default_context()
        
        try:
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                # Authenticate
                await websocket.send("PASS oauth:justinfan12345")
                await websocket.send("NICK justinfan12345")
                await websocket.send(f"JOIN #{self.current_channel}")
                
                self.is_connected = True
                logger.info(f"✅ Connected to #{self.current_channel}")
                
                # Listen for messages
                while not self.stop_event.is_set():
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
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
            logger.info("🔌 Disconnected from Twitch")
    
    async def _handle_message(self, raw_message: str):
        """Handle incoming IRC message."""
        try:
            if "PRIVMSG" in raw_message:
                # Parse IRC PRIVMSG format
                parts = raw_message.split()
                if len(parts) >= 4:
                    # Extract username from :username!username@username.tmi.twitch.tv
                    user_part = parts[0][1:]  # Remove leading ':'
                    username = user_part.split('!')[0]
                    
                    # Extract channel (remove #)
                    channel = parts[2][1:]
                    
                    # Extract message (everything after the third :)
                    message_start = raw_message.find(':', raw_message.find(':', 1) + 1)
                    if message_start != -1:
                        message = raw_message[message_start + 1:].strip()
                        
                        # Create message object
                        twitch_msg = TwitchMessage(
                            username=username,
                            message=message,
                            timestamp=time.time(),
                            channel=channel
                        )
                        
                        # Call the callback if provided
                        if self.message_callback:
                            try:
                                self.message_callback(twitch_msg.to_dict())
                                logger.info(f"💬 {username}: {message}")
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                        
        except Exception as e:
            logger.error(f"Message parsing error: {e}")
    
    def disconnect(self):
        """Disconnect from Twitch."""
        self.stop_event.set()
        self.is_connected = False
        
        if self.connection_thread and self.connection_thread.is_alive():
            # Give the thread time to stop gracefully
            self.connection_thread.join(timeout=3)
        
        logger.info("🔌 Disconnected from Twitch")

# Global connection instance
_twitch_connection = None

def start_twitch_monitoring(channel: str, message_callback: Callable) -> bool:
    """Start monitoring a Twitch channel."""
    global _twitch_connection
    
    # Stop any existing connection
    if _twitch_connection:
        _twitch_connection.disconnect()
    
    # Create new connection
    _twitch_connection = StreamlitTwitchConnection()
    return _twitch_connection.connect(channel, message_callback)

def stop_twitch_monitoring():
    """Stop monitoring Twitch."""
    global _twitch_connection
    if _twitch_connection:
        _twitch_connection.disconnect()
        _twitch_connection = None

def is_twitch_connected() -> bool:
    """Check if connected to Twitch."""
    global _twitch_connection
    return _twitch_connection is not None and _twitch_connection.is_connected

def get_current_channel() -> Optional[str]:
    """Get the current channel being monitored."""
    global _twitch_connection
    if _twitch_connection:
        return _twitch_connection.current_channel
    return None

# For testing
if __name__ == "__main__":
    def test_callback(message):
        print(f"Received: {message['username']}: {message['message']}")
    
    print("Testing Streamlit Twitch connection...")
    success = start_twitch_monitoring("shroud", test_callback)
    
    if success:
        print("Connected! Listening for messages for 30 seconds...")
        time.sleep(30)
    else:
        print("Failed to connect")
    
    stop_twitch_monitoring()
    print("Done!")

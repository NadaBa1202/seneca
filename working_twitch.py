"""
Working Twitch IRC Connection

Fixed WebSocket connection to Twitch IRC that actually works.
"""

import asyncio
import websockets
import ssl
import time
from typing import Callable, Optional

class WorkingTwitchReader:
    """Working Twitch chat reader."""
    
    def __init__(self, message_callback: Callable):
        self.message_callback = message_callback
        self.websocket = None
        self.channel = None
        self.is_connected = False
        
    async def connect_and_listen(self, channel: str, duration: int = 30):
        """Connect to channel and listen for specified duration."""
        try:
            self.channel = channel.lstrip('#').lower()
            print(f"🔄 Connecting to #{self.channel}...")
            
            # Create SSL context
            ssl_context = ssl.create_default_context()
            
            # Connect to Twitch IRC WebSocket
            uri = "wss://irc-ws.chat.twitch.tv:443"
            
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                self.websocket = websocket
                print("✅ WebSocket connected")
                
                # Send authentication
                await websocket.send("CAP REQ :twitch.tv/tags twitch.tv/commands")
                await websocket.send("PASS oauth:justinfan12345")
                await websocket.send("NICK justinfan12345")
                await websocket.send(f"JOIN #{self.channel}")
                
                print(f"📤 Joined #{self.channel}, listening for {duration} seconds...")
                
                self.is_connected = True
                message_count = 0
                start_time = time.time()
                
                # Listen for messages
                while time.time() - start_time < duration:
                    try:
                        # Wait for message with timeout
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        
                        # Handle PING
                        if message.startswith("PING"):
                            await websocket.send(message.replace("PING", "PONG"))
                            continue
                        
                        # Handle PRIVMSG (chat messages)
                        if "PRIVMSG" in message:
                            message_count += 1
                            parsed = self._parse_message(message)
                            
                            if parsed:
                                print(f"🔴 {parsed['username']}: {parsed['message']}")
                                
                                # Call callback
                                if self.message_callback:
                                    await self.message_callback(parsed)
                        
                        # Other IRC messages
                        elif any(x in message for x in ["JOIN", "PART", "366", "353"]):
                            # IRC join/part/userlist messages - just show them
                            if "366" in message:  # End of names list
                                print(f"✅ Successfully joined #{self.channel}")
                    
                    except asyncio.TimeoutError:
                        # No message received in 1 second, continue
                        continue
                    except Exception as e:
                        print(f"❌ Message error: {e}")
                        break
                
                self.is_connected = False
                print(f"📊 Total messages received: {message_count}")
                return message_count > 0
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            self.is_connected = False
            return False
    
    def _parse_message(self, raw_message: str) -> Optional[dict]:
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
                "message": message_text,
                "timestamp": time.time(),
                "channel": self.channel
            }
            
        except Exception:
            return None

# Test function
async def test_working_connection():
    """Test the working connection with multiple channels."""
    
    async def handle_message(parsed_msg):
        """Handle received message."""
        pass  # Just print in the main function
    
    reader = WorkingTwitchReader(handle_message)
    
    # Try multiple popular channels
    test_channels = [
        "monstercat",      # 24/7 music
        "nasa",            # Space content
        "twitchpresents",  # Official Twitch
        "shroud",          # Gaming
        "xqcow",           # Variety
        "pokimane",        # Gaming/variety
        "lirik",           # Gaming
        "sodapoppin",      # Gaming
        "asmongold",       # Gaming/reactions
        "summit1g"         # Gaming
    ]
    
    for channel in test_channels:
        print(f"\n{'='*50}")
        print(f"Testing #{channel}")
        print(f"{'='*50}")
        
        success = await reader.connect_and_listen(channel, duration=15)
        
        if success:
            print(f"🎉 SUCCESS! #{channel} has active chat!")
            return True
        else:
            print(f"⚠️ No activity in #{channel}")
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    print("\n❌ No active channels found")
    print("💡 This could be because:")
    print("   - Streamers are offline")
    print("   - Low chat activity during this time")
    print("   - Your IP might be rate limited")
    
    return False

if __name__ == "__main__":
    print("🎮 Testing Working Twitch Connection...")
    success = asyncio.run(test_working_connection())
    
    if success:
        print("\n✅ Twitch connection is WORKING!")
    else:
        print("\n⚠️ Consider using simulation mode for reliable testing")

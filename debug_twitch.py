"""
Debug Twitch Connection

Test with always-active channels and debug output.
"""

import asyncio
import websockets
import ssl
import logging
import time

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def debug_twitch_connection():
    """Debug Twitch connection with detailed output."""
    
    # Test with channels that usually have activity
    test_channels = [
        "monstercat",  # 24/7 music stream
        "gamesdonequick",  # Usually active
        "nasa",  # NASA stream
        "twitchpresents",  # Twitch official
        "loserfruit",  # Popular streamer
        "ninja"  # Popular streamer
    ]
    
    for channel in test_channels:
        print(f"\n🔄 Testing #{channel} with full debug...")
        
        try:
            # Create SSL context
            ssl_context = ssl.create_default_context()
            
            # Connect
            uri = "wss://irc-ws.chat.twitch.tv:443"
            print(f"Connecting to {uri}...")
            
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                print("✅ WebSocket connected")
                
                # Send authentication
                await websocket.send("CAP REQ :twitch.tv/tags twitch.tv/commands")
                print("📤 Sent CAP REQ")
                
                await websocket.send("PASS oauth:justinfan12345")
                print("📤 Sent PASS")
                
                await websocket.send("NICK justinfan12345")
                print("📤 Sent NICK")
                
                await websocket.send(f"JOIN #{channel}")
                print(f"📤 Sent JOIN #{channel}")
                
                # Listen for responses
                print("👂 Listening for messages...")
                message_count = 0
                
                try:
                    # Set a timeout for receiving messages
                    async for message in asyncio.wait_for(websocket, timeout=15.0):
                        print(f"📥 Raw: {message[:100]}...")
                        
                        # Handle PING
                        if message.startswith("PING"):
                            pong = message.replace("PING", "PONG")
                            await websocket.send(pong)
                            print("📤 Sent PONG")
                            continue
                        
                        # Look for PRIVMSG
                        if "PRIVMSG" in message:
                            message_count += 1
                            
                            # Try to parse username and message
                            try:
                                parts = message.split(' ')
                                if len(parts) >= 4 and parts[0].startswith(':'):
                                    username = parts[0][1:].split('!')[0]
                                    
                                    # Find message text (after second :)
                                    colon_indices = [i for i, char in enumerate(message) if char == ':']
                                    if len(colon_indices) >= 2:
                                        msg_text = message[colon_indices[1]+1:].strip()
                                        print(f"🔴 {username}: {msg_text}")
                                    
                            except Exception as e:
                                print(f"Parse error: {e}")
                        
                        # Success if we get any chat messages
                        if message_count >= 3:
                            print(f"🎉 SUCCESS! Received {message_count} messages from #{channel}")
                            return True
                            
                except asyncio.TimeoutError:
                    print(f"⏰ Timeout after 15 seconds")
                
                print(f"📊 Total messages from #{channel}: {message_count}")
                
                if message_count > 0:
                    print(f"🎉 SUCCESS! Found active chat in #{channel}")
                    return True
                
        except Exception as e:
            print(f"❌ Error with #{channel}: {e}")
            
        await asyncio.sleep(2)
    
    print("❌ No active chat found in any channel")
    return False

if __name__ == "__main__":
    asyncio.run(debug_twitch_connection())

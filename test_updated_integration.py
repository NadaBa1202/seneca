#!/usr/bin/env python3
"""
Test Updated Twitch Integration

Test the fixed Twitch integration in the chat manager.
"""

import asyncio
import sys
import os
sys.path.append('.')

from esports_analytics.services.chat.enhanced_twitch import TwitchChatManager

async def test_updated_integration():
    print("🎮 Testing Updated Twitch Integration...")
    
    message_count = 0
    
    async def handle_message(message):
        nonlocal message_count
        message_count += 1
        
        platform_icon = "🔴" if message.platform == "twitch" else "🤖"
        print(f"{platform_icon} {message.username}: {message.message}")
    
    # Create chat manager
    chat_manager = TwitchChatManager(handle_message)
    
    # Test with a channel that had activity
    test_channel = "shroud"  # This one worked in our test
    
    print(f"\n🔄 Testing connection to #{test_channel}...")
    
    try:
        success = await chat_manager.start_real_time(test_channel)
        
        if success:
            print(f"✅ Connected to #{test_channel}! Listening for 20 seconds...")
            
            # Listen for 20 seconds
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 20:
                await asyncio.sleep(1)
                
                # Show status every 5 seconds
                if int(asyncio.get_event_loop().time() - start_time) % 5 == 0:
                    status = chat_manager.get_status()
                    print(f"📊 Status: {message_count} messages, connected: {status['websocket_connected']}")
            
            print(f"✅ Test complete. Total messages: {message_count}")
            
            await chat_manager.stop_real_time()
            
            if message_count > 0:
                print(f"🎉 SUCCESS! Received {message_count} real Twitch messages!")
            else:
                print("⚠️ Connected but no messages received")
        else:
            print(f"❌ Failed to connect to #{test_channel}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test simulation too
    print(f"\n🤖 Testing simulation mode...")
    await chat_manager.start_simulation(interval=2.0)
    await asyncio.sleep(8)
    await chat_manager.stop_simulation()
    
    status = chat_manager.get_status()
    print(f"📊 Final status: {status}")
    print(f"Total history: {len(chat_manager.get_recent_messages())}")

if __name__ == "__main__":
    asyncio.run(test_updated_integration())

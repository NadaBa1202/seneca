#!/usr/bin/env python3
"""
Simple Twitch Connection Test

Tests the real Twitch connection to verify it works.
"""

import asyncio
import sys
import os
sys.path.append('.')

from esports_analytics.services.chat.enhanced_twitch import TwitchChatManager

async def test_real_twitch():
    print("🎮 Testing REAL Twitch Connection...")
    
    message_count = 0
    
    async def handle_message(message):
        nonlocal message_count
        message_count += 1
        
        platform_icon = "🔴" if message.platform == "twitch" else "🤖"
        badges_str = f" [{', '.join(message.badges)}]" if message.badges else ""
        
        print(f"{platform_icon} {message.username}{badges_str}: {message.message}")
        
        # Show special attributes
        if message.is_moderator:
            print("  👮 MODERATOR")
        if message.is_subscriber:
            print("  ⭐ SUBSCRIBER")
        if message.is_vip:
            print("  💎 VIP")
    
    # Create chat manager
    chat_manager = TwitchChatManager(handle_message)
    
    # Test channels (popular ones with active chat)
    test_channels = ["xqcow", "shroud", "lirik", "pokimane", "sodapoppin"]
    
    for channel in test_channels:
        print(f"\n🔄 Testing connection to #{channel}...")
        
        try:
            success = await chat_manager.start_real_time(channel)
            
            if success:
                print(f"✅ Connected to #{channel}! Listening for 15 seconds...")
                
                # Listen for 15 seconds
                start_time = asyncio.get_event_loop().time()
                while asyncio.get_event_loop().time() - start_time < 15:
                    await asyncio.sleep(1)
                    
                    # Show status every 5 seconds
                    if int(asyncio.get_event_loop().time() - start_time) % 5 == 0:
                        status = chat_manager.get_status()
                        print(f"📊 Status: {message_count} messages received, bot_connected: {status['bot_connected']}")
                
                print(f"✅ Test complete for #{channel}. Total messages: {message_count}")
                
                await chat_manager.stop_real_time()
                
                if message_count > 0:
                    print(f"🎉 SUCCESS! Real Twitch connection working on #{channel}")
                    break
                else:
                    print(f"⚠️ Connected but no messages received from #{channel}")
            else:
                print(f"❌ Failed to connect to #{channel}")
                
        except Exception as e:
            print(f"❌ Error testing #{channel}: {e}")
        
        await asyncio.sleep(2)  # Wait between tests
    
    if message_count == 0:
        print("\n❌ No messages received from any channel.")
        print("💡 This might be because:")
        print("   - Channels are offline or have low activity")
        print("   - Network connectivity issues")
        print("   - Twitch rate limiting")
        
        print("\n🤖 Testing simulation as fallback...")
        await chat_manager.start_simulation(interval=1.0)
        await asyncio.sleep(5)
        await chat_manager.stop_simulation()
        
        status = chat_manager.get_status()
        print(f"📊 Final status: {status}")
    else:
        print(f"\n🎉 Real Twitch integration is WORKING! Received {message_count} messages.")

if __name__ == "__main__":
    asyncio.run(test_real_twitch())

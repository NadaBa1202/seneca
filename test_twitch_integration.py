#!/usr/bin/env python3
"""
Test Twitch Real-time Integration

This script tests the enhanced Twitch chat integration with both
real-time and simulation capabilities.
"""

import asyncio
import sys
import os
sys.path.append('.')

from esports_analytics.services.chat.enhanced_twitch import TwitchChatManager

async def test_twitch_integration():
    print("🎮 Testing Twitch Real-time Integration...")
    
    # Message handler
    async def handle_message(message):
        platform_icon = "🔴" if message.platform == "twitch" else "🤖" if message.platform == "simulation" else "💬"
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
    
    print("\n🤖 Testing simulation mode...")
    
    # Start simulation
    await chat_manager.start_simulation(interval=2.0, random_timing=True)
    print("✅ Simulation started")
    
    # Let it run for a bit
    await asyncio.sleep(10)
    
    # Send a test message
    print("\n💬 Sending test message...")
    await chat_manager.send_test_message("TestUser", "This is a test message from the script!")
    
    # Wait a bit more
    await asyncio.sleep(5)
    
    # Stop simulation
    await chat_manager.stop_simulation()
    print("✅ Simulation stopped")
    
    # Show status
    status = chat_manager.get_status()
    print(f"\n📊 Status: {status}")
    
    # Show recent messages
    recent = chat_manager.get_recent_messages(5)
    print(f"\n📝 Recent messages ({len(recent)}):")
    for msg in recent:
        print(f"  {msg['username']}: {msg['message'][:50]}...")
    
    print("\n🎯 Testing real-time connection (manual)...")
    print("To test real-time Twitch:")
    print("1. Get Twitch channel name (e.g., 'xqcow', 'shroud')")
    print("2. Run: await chat_manager.start_real_time('channel_name')")
    print("3. Watch messages flow in real-time!")
    
    print("\n✅ Integration test complete!")

if __name__ == "__main__":
    asyncio.run(test_twitch_integration())

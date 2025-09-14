#!/usr/bin/env python3
"""
Test the gaming sentiment integration in chat analysis
"""

import sys
import os
sys.path.append('.')

import asyncio
from esports_analytics.pages.chat_analysis import analyze_message_ml

async def test_gaming_sentiment():
    print("🎮 Testing Gaming Sentiment Integration...")
    
    test_messages = [
        "That clutch play was absolutely insane! POG",
        "This team is complete trash, just uninstall the game",
        "kys noob you're terrible at this game", 
        "Good game everyone, well played",
        "What items should I buy next round?",
        "ez clap that was so lit! 200 IQ play",
        "I'm so tilted right now, team is feeding",
        "Report this toxic griefer immediately"
    ]
    
    print("\n🎯 Testing messages with new gaming sentiment model:")
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test {i} ---")
        print(f"Message: '{message}'")
        
        try:
            analysis = await analyze_message_ml(message)
            
            sentiment = analysis['sentiment_category']
            confidence = analysis['confidence']
            compound = analysis['sentiment']['compound']
            toxicity = analysis['toxicity']['toxic']
            
            print(f"Result: {sentiment} (confidence: {confidence:.2f})")
            print(f"Compound: {compound:.2f}, Toxicity: {toxicity:.2f}")
            
            # Show full sentiment breakdown
            sent_scores = analysis['sentiment']
            print(f"Breakdown: Pos:{sent_scores['positive']:.2f} Neg:{sent_scores['negative']:.2f} Neu:{sent_scores['neutral']:.2f}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Gaming sentiment testing complete!")

if __name__ == "__main__":
    asyncio.run(test_gaming_sentiment())

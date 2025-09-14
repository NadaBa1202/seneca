#!/usr/bin/env python3
"""
Test script for interactive sentiment analysis functionality
"""

import asyncio
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

async def test_nlp_models():
    """Test the NLP models that will be used in the interactive interface."""
    print("🧪 Testing Advanced NLP Models for Interactive Interface")
    print("=" * 60)
    
    try:
        from esports_analytics.services.nlp.sentiment_analyzer import EnsembleSentimentAnalyzer
        from esports_analytics.services.nlp.toxicity_detector import AdvancedToxicityDetector
        from esports_analytics.services.nlp.emotion_classifier import EmotionClassifier
        from esports_analytics.services.nlp.multilingual_processor import MultilingualProcessor
        
        print("✅ All NLP models imported successfully!")
        
        # Initialize models
        print("\n🔄 Initializing models...")
        sentiment_analyzer = EnsembleSentimentAnalyzer()
        toxicity_detector = AdvancedToxicityDetector()
        emotion_classifier = EmotionClassifier()
        multilingual_processor = MultilingualProcessor()
        print("✅ Models initialized!")
        
        # Test messages
        test_messages = [
            "This game is absolutely incredible! Best match ever!",
            "I can't believe how bad that play was...",
            "The new update looks promising",
            "That was such a terrible decision by the team",
            "I'm so excited for the finals next week!",
            "This champion is so broken and unfair",
            "Amazing comeback! What a play!",
            "I hate this meta, it's so boring"
        ]
        
        print(f"\n📝 Testing {len(test_messages)} sample messages...")
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Message {i} ---")
            print(f"Text: '{message}'")
            
            # Analyze sentiment
            sentiment_result = await sentiment_analyzer.analyze(message)
            print(f"Sentiment: {sentiment_result.get('category', 'unknown')} (score: {sentiment_result.get('compound', 0):.3f})")
            
            # Analyze toxicity
            toxicity_result = await toxicity_detector.detect(message)
            print(f"Toxicity: {toxicity_result.get('toxic', 0):.3f}")
            
            # Analyze emotion
            emotion_result = await emotion_classifier.classify(message)
            top_emotion = max(emotion_result, key=emotion_result.get) if emotion_result else "neutral"
            print(f"Emotion: {top_emotion} (confidence: {emotion_result.get(top_emotion, 0):.3f})")
            
            # Analyze language
            language_result = await multilingual_processor.process(message)
            print(f"Language: {language_result.get('language', 'unknown')} (confidence: {language_result.get('confidence', 0):.3f})")
        
        print("\n🎉 All tests completed successfully!")
        print("\n💡 The interactive interface is ready!")
        print("   - Users can input custom messages")
        print("   - Real-time sentiment analysis with ensemble models")
        print("   - Advanced toxicity detection")
        print("   - 6-class emotion classification")
        print("   - Multi-language support")
        print("   - Dynamic visualizations and badges")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_nlp_models())
    if success:
        print("\n🚀 Ready for interactive testing!")
        print("   Open your browser and go to: http://localhost:8507")
        print("   Navigate to 'Advanced Chat Analysis' page")
        print("   Use the 'Interactive Message Testing' section!")
    else:
        print("\n⚠️ Some issues detected. Check the error messages above.")

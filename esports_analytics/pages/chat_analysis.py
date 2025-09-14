"""
Working Chat Analysis Page

Save this as: esports_analytics/pages/chat_analysis.py

This is a simplified but fully functional chat analysis page that works
without complex dependencies.
"""

import os
import sys
import time
import asyncio
from typing import Dict, Any, List
import streamlit as st
import pandas as pd
import altair as alt
import random
import logging

# ML imports for better sentiment analysis
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from textblob import TextBlob
    import torch
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Gaming sentiment trainer
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from esports_analytics.services.ml.sentiment_trainer import GamingSentimentTrainer
    from esports_analytics.services.chat.streamlit_twitch import (
        start_twitch_monitoring, stop_twitch_monitoring, 
        is_twitch_connected, get_current_channel
    )
    GAMING_ML_AVAILABLE = True
    TWITCH_AVAILABLE = True
except ImportError as e:
    GAMING_ML_AVAILABLE = False
    TWITCH_AVAILABLE = False

logger = logging.getLogger(__name__)

# Initialize gaming sentiment model (cached)
@st.cache_resource
def load_gaming_sentiment_model():
    """Load the custom gaming sentiment model."""
    if GAMING_ML_AVAILABLE:
        try:
            trainer = GamingSentimentTrainer()
            
            # Try to load pre-trained model
            model_path = "gaming_sentiment_model.pkl"
            if os.path.exists(model_path):
                trainer.load_model(model_path)
                return trainer
            else:
                # Quick training with gaming examples
                st.info("🔧 Training gaming sentiment model...")
                gaming_examples = [
                    "clutch play! that was insane!", "pog champion amazing",
                    "ez clap well played", "200 IQ play right there",
                    "trash team uninstall game", "noob players tilted af",
                    "kys noob you suck", "toxic player reported",
                    "good game everyone", "next round starting soon"
                ]
                labels = trainer.auto_label_data(gaming_examples)
                trainer.train_custom_model(gaming_examples, labels)
                return trainer
        except Exception as e:
            st.warning(f"Could not load gaming sentiment model: {e}")
            return None
    return None

# Twitch message handler
async def handle_twitch_message(twitch_msg):
    """Handle incoming Twitch messages."""
    # Analyze the message
    analysis = await analyze_message(twitch_msg.message)
    
    # Create record
    record = {
        "user": twitch_msg.username,
        "text": twitch_msg.message,
        "timestamp": twitch_msg.timestamp,
        "platform": twitch_msg.platform,
        "channel": twitch_msg.channel,
        **analysis
    }
    
    # Add to session state
    if 'chat_records' not in st.session_state:
        st.session_state.chat_records = []
    st.session_state.chat_records.append(record)
    
    # Keep only recent messages
    if len(st.session_state.chat_records) > 1000:
        st.session_state.chat_records = st.session_state.chat_records[-1000:]

# Initialize ML models (cached)
@st.cache_resource
def load_sentiment_models():
    """Load pre-trained sentiment analysis models."""
    models = {}
    
    if ML_AVAILABLE:
        try:
            # Load a gaming/social media optimized sentiment model
            models['sentiment_pipeline'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # Load emotion detection model
            models['emotion_pipeline'] = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            
            # Backup: Basic sentiment with TextBlob
            models['textblob_available'] = True
            
            print("✅ ML models loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading ML models: {e}")
            models['sentiment_pipeline'] = None
            models['emotion_pipeline'] = None
            models['textblob_available'] = True
    
    return models

def get_ml_models():
    """Get ML models with caching."""
    return load_sentiment_models()

def generate_sample_message() -> Dict[str, Any]:
    """Generate a realistic sample esports chat message."""
    
    # Sample usernames
    usernames = [
        "ProGamer2024", "xXNoobSlayerXx", "EsportsChamp", "GameMaster99", 
        "TwitchViewer42", "StreamSniper", "ChatLurker", "MemeLord", 
        "PogChampion", "KappaPride", "ClutchPlayer", "FragHunter"
    ]
    
    # Sample messages with different sentiment categories
    positive_messages = [
        "This game is absolutely incredible! Best match ever!",
        "What an amazing play! PogChamp",
        "I love this team so much! They're unstoppable!",
        "That was the most insane clutch I've ever seen!",
        "This streamer is so good, learning so much!",
        "Great game everyone! Well played!",
        "This tournament has been fantastic!",
        "Incredible teamwork! They deserve the win!",
        "That strategy was genius! 5Head",
        "So hyped for this match! Let's go!"
    ]
    
    neutral_messages = [
        "The new update looks promising",
        "Next match starts in 10 minutes",
        "Anyone know the current score?",
        "This map is pretty balanced",
        "Standard play from both teams",
        "The meta is evolving",
        "Interesting champion pick",
        "Game 2 coming up next",
        "That's one way to play it",
        "Regular rotation there"
    ]
    
    negative_messages = [
        "This game is so boring... ResidentSleeper",
        "I can't believe how bad that play was",
        "What a terrible decision by the team",
        "This is the worst match I've ever watched",
        "That player is having an awful game",
        "Such a disappointing performance",
        "This team needs to practice more",
        "That was a really bad call",
        "Not their best game today",
        "Expected better from this team"
    ]
    
    toxic_messages = [
        "This player is trash, should quit",
        "What an idiot move, uninstall the game",
        "This team is garbage, waste of time",
        "Worst player I've ever seen, pathetic",
        "These noobs don't deserve to be here"
    ]
    
    # Choose message category based on probability
    rand = random.random()
    if rand < 0.4:  # 40% positive
        message = random.choice(positive_messages)
        expected_sentiment = "positive"
    elif rand < 0.75:  # 35% neutral
        message = random.choice(neutral_messages)
        expected_sentiment = "neutral"
    elif rand < 0.95:  # 20% negative
        message = random.choice(negative_messages)
        expected_sentiment = "negative"
    else:  # 5% toxic
        message = random.choice(toxic_messages)
        expected_sentiment = "negative"
    
    username = random.choice(usernames)
    
    return {
        "user": username,
        "text": message,
        "timestamp": time.time(),
        "expected_sentiment": expected_sentiment
    }

async def analyze_message_ml(text: str) -> Dict[str, Any]:
    """Advanced ML-based message analysis using transformer models."""
    
    models = get_ml_models()
    
    # Initialize result structure
    result = {
        "sentiment": {"compound": 0.0, "positive": 0.0, "negative": 0.0, "neutral": 1.0},
        "sentiment_category": "neutral",
        "toxicity": {"toxic": 0.0, "severe_toxic": 0.0, "obscene": 0.0, "threat": 0.0, "insult": 0.0, "identity_hate": 0.0},
        "emotion": "neutral",
        "emotion_scores": {},
        "confidence": 0.5,
        "language": "en"
    }
    
    if not text.strip():
        return result
    
    try:
        # 1. Sentiment Analysis with RoBERTa (trained on social media)
        if models.get('sentiment_pipeline'):
            sentiment_results = models['sentiment_pipeline'](text)
            
            # Process sentiment scores
            sentiment_scores = {item['label'].lower(): item['score'] for item in sentiment_results[0]}
            
            # Map to our format (be more aggressive)
            positive_score = sentiment_scores.get('positive', sentiment_scores.get('label_2', 0.0))
            negative_score = sentiment_scores.get('negative', sentiment_scores.get('label_0', 0.0))
            neutral_score = sentiment_scores.get('neutral', sentiment_scores.get('label_1', 0.0))
            
            # BOOST non-neutral scores significantly
            if positive_score > 0.3:  # Lower threshold
                positive_score = min(positive_score * 1.5, 1.0)  # Amplify positive
            if negative_score > 0.3:  # Lower threshold  
                negative_score = min(negative_score * 1.5, 1.0)  # Amplify negative
            
            # Suppress neutral if there's any clear sentiment
            if positive_score > 0.4 or negative_score > 0.4:
                neutral_score = neutral_score * 0.3  # Dramatically reduce neutral
            
            # Calculate compound score (more extreme)
            compound = (positive_score - negative_score) * 1.5  # Amplify difference
            compound = max(-1.0, min(1.0, compound))  # Clamp to [-1, 1]
            
            # Determine category with MUCH lower thresholds
            if positive_score > 0.25 and positive_score > negative_score:  # Very low threshold
                sentiment_category = "positive"
            elif negative_score > 0.25 and negative_score > positive_score:  # Very low threshold
                sentiment_category = "negative"
            else:
                sentiment_category = "neutral"
            
            # Renormalize scores
            total = positive_score + negative_score + neutral_score
            if total > 0:
                positive_score = positive_score / total
                negative_score = negative_score / total
                neutral_score = neutral_score / total
            
            result["sentiment"] = {
                "compound": round(compound, 3),
                "positive": round(positive_score, 3),
                "negative": round(negative_score, 3),
                "neutral": round(neutral_score, 3)
            }
            result["sentiment_category"] = sentiment_category
            result["confidence"] = round(max(positive_score, negative_score, neutral_score), 3)
        
        # 2. Gaming-Specific Sentiment Analysis (NEW!)
        gaming_model = load_gaming_sentiment_model()
        if gaming_model:
            try:
                gaming_prediction = gaming_model.predict_sentiment(text)
                
                # If gaming model is confident, use its prediction
                if gaming_prediction and 'sentiment' in gaming_prediction:
                    gaming_sentiment = gaming_prediction['sentiment']
                    gaming_confidence = gaming_prediction.get('confidence', 0.5)
                    
                    # Override general sentiment if gaming model is confident
                    if gaming_confidence > 0.6:
                        if gaming_sentiment == 'positive':
                            result["sentiment"]["positive"] = 0.8
                            result["sentiment"]["negative"] = 0.1
                            result["sentiment"]["neutral"] = 0.1
                            result["sentiment"]["compound"] = 0.7
                            result["sentiment_category"] = "positive"
                            result["confidence"] = gaming_confidence
                        elif gaming_sentiment == 'negative':
                            result["sentiment"]["positive"] = 0.1
                            result["sentiment"]["negative"] = 0.8
                            result["sentiment"]["neutral"] = 0.1
                            result["sentiment"]["compound"] = -0.7
                            result["sentiment_category"] = "negative"
                            result["confidence"] = gaming_confidence
                        elif gaming_sentiment == 'toxic':
                            result["sentiment"]["positive"] = 0.05
                            result["sentiment"]["negative"] = 0.9
                            result["sentiment"]["neutral"] = 0.05
                            result["sentiment"]["compound"] = -0.9
                            result["sentiment_category"] = "negative"
                            result["confidence"] = gaming_confidence
                            # Also boost toxicity scores
                            result["toxicity"]["toxic"] = min(result["toxicity"].get("toxic", 0) + 0.4, 1.0)
            except Exception as e:
                logger.warning(f"Gaming sentiment model error: {e}")
        
        # 3. Emotion Analysis
        if models.get('emotion_pipeline'):
            emotion_results = models['emotion_pipeline'](text)
            
            # Process emotion scores
            emotion_scores = {item['label'].lower(): item['score'] for item in emotion_results[0]}
            
            # Find dominant emotion
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            
            result["emotion"] = dominant_emotion
            result["emotion_scores"] = {k: round(v, 3) for k, v in emotion_scores.items()}
        
        # 4. Enhanced Toxicity Detection (combine ML + rules)
        toxicity_score = await detect_toxicity_enhanced(text, result["sentiment"])
        result["toxicity"] = toxicity_score
        
        # 5. Gaming-specific adjustments
        result = apply_gaming_context_adjustments(text, result)
        
    except Exception as e:
        logger.error(f"ML analysis error: {e}")
        # Fallback to rule-based analysis
        return await analyze_message_simple(text)
    
    return result

async def detect_toxicity_enhanced(text: str, sentiment: Dict) -> Dict[str, float]:
    """Enhanced toxicity detection combining multiple approaches."""
    
    # Gaming-specific toxic patterns
    toxic_patterns = {
        'extreme_toxic': ['kill yourself', 'kys', 'neck yourself', 'rope', 'end yourself'],
        'insults': ['idiot', 'stupid', 'retard', 'braindead', 'monkey', 'ape', 'dog'],
        'gaming_toxic': ['trash player', 'delete game', 'uninstall', 'get good', 'skill issue', 'hardstuck'],
        'profanity': ['fuck', 'shit', 'bitch', 'damn', 'hell', 'ass'],
        'hate_speech': ['gay', 'fag', 'cancer', 'aids', 'autistic'],
        'threats': ['going to kill', 'find you', 'come for you', 'destroy you']
    }
    
    text_lower = text.lower()
    words = text_lower.split()
    total_words = max(len(words), 1)
    
    # Base toxicity from patterns
    toxic_scores = {
        'extreme_toxic': 0.0,
        'insults': 0.0,
        'gaming_toxic': 0.0,
        'profanity': 0.0,
        'hate_speech': 0.0,
        'threats': 0.0
    }
    
    # Check for toxic patterns
    for category, patterns in toxic_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                toxic_scores[category] += 0.3  # High weight for exact matches
    
    # Calculate overall toxicity
    base_toxic = max(toxic_scores.values())
    
    # Boost based on sentiment
    if sentiment['negative'] > 0.7:
        base_toxic = min(base_toxic + 0.2, 1.0)
    
    # Boost for all caps (shouting)
    if text.isupper() and len(text) > 3:
        base_toxic = min(base_toxic + 0.1, 1.0)
    
    # Boost for excessive punctuation
    if text.count('!') > 2 or text.count('?') > 2:
        base_toxic = min(base_toxic + 0.05, 1.0)
    
    return {
        "toxic": round(base_toxic, 3),
        "severe_toxic": round(base_toxic * 0.9, 3),
        "obscene": round(toxic_scores['profanity'], 3),
        "threat": round(toxic_scores['threats'], 3),
        "insult": round(max(toxic_scores['insults'], toxic_scores['gaming_toxic']), 3),
        "identity_hate": round(toxic_scores['hate_speech'], 3)
    }

def apply_gaming_context_adjustments(text: str, result: Dict) -> Dict:
    """Apply gaming-specific context adjustments to improve accuracy."""
    
    text_lower = text.lower()
    
    # Expanded gaming positive terms
    gaming_positive = [
        'clutch', 'pog', 'pogchamp', 'poggers', 'lit', 'fire', 'cracked', 'nutty', 
        'insane play', 'sick', 'clean', 'smooth', 'crisp', 'nice play', 'well played',
        'good job', 'gj', 'wp', 'gg', 'pro', 'beast', 'goat', 'carry', 'mvp',
        'hype', 'hyped', 'legendary', 'godlike', 'flawless', 'dominating'
    ]
    
    # Expanded gaming negative terms
    gaming_negative = [
        'tilted', 'griefing', 'throwing', 'feeding', 'inting', 'boosted', 'carried',
        'hardstuck', 'washed', 'overrated', 'lucky', 'lag', 'lagging', 'broken',
        'unfair', 'rigged', 'camping', 'sweaty', 'tryhard', 'meta slave', 'cheese',
        'skill issue', 'get good', 'trash', 'garbage', 'noob', 'bot'
    ]
    
    # Count matches
    positive_matches = sum(1 for term in gaming_positive if term in text_lower)
    negative_matches = sum(1 for term in gaming_negative if term in text_lower)
    
    # AGGRESSIVE adjustments
    if positive_matches > 0:
        # Force positive if gaming positive terms found
        boost = min(positive_matches * 0.4, 0.8)  # Strong boost
        result['sentiment']['positive'] = min(result['sentiment']['positive'] + boost, 1.0)
        result['sentiment']['compound'] = min(result['sentiment']['compound'] + boost, 1.0)
        result['sentiment']['neutral'] = max(result['sentiment']['neutral'] - boost, 0.0)
        
        # Override category if boost is significant
        if boost > 0.3:
            result['sentiment_category'] = 'positive'
    
    if negative_matches > 0:
        # Force negative if gaming negative terms found
        boost = min(negative_matches * 0.4, 0.8)  # Strong boost
        result['sentiment']['negative'] = min(result['sentiment']['negative'] + boost, 1.0)
        result['sentiment']['compound'] = max(result['sentiment']['compound'] - boost, -1.0)
        result['sentiment']['neutral'] = max(result['sentiment']['neutral'] - boost, 0.0)
        
        # Override category if boost is significant
        if boost > 0.3:
            result['sentiment_category'] = 'negative'
    
    # Additional keyword-based overrides for very clear cases
    very_positive = ['amazing', 'incredible', 'fantastic', 'awesome', 'perfect', 'love this']
    very_negative = ['hate', 'terrible', 'awful', 'worst', 'horrible', 'disgusting']
    
    for term in very_positive:
        if term in text_lower:
            result['sentiment_category'] = 'positive'
            result['sentiment']['positive'] = max(result['sentiment']['positive'], 0.7)
            result['sentiment']['compound'] = max(result['sentiment']['compound'], 0.5)
            break
    
    for term in very_negative:
        if term in text_lower:
            result['sentiment_category'] = 'negative'
            result['sentiment']['negative'] = max(result['sentiment']['negative'], 0.7)
            result['sentiment']['compound'] = min(result['sentiment']['compound'], -0.5)
            break
    
    # Recalculate neutral (make it much smaller)
    total_sentiment = result['sentiment']['positive'] + result['sentiment']['negative']
    if total_sentiment > 0.5:  # If there's clear sentiment
        result['sentiment']['neutral'] = max(0.1, 1 - total_sentiment)  # Minimum neutral
    
    return result

async def analyze_message_simple(text: str) -> Dict[str, Any]:
    """Fallback rule-based analysis with aggressive sentiment detection."""
    
    # Expanded keyword lists
    positive_words = [
        'amazing', 'awesome', 'great', 'good', 'love', 'excellent', 'perfect', 
        'clutch', 'pog', 'pogchamp', 'lit', 'fire', 'sick', 'insane', 'incredible',
        'fantastic', 'wonderful', 'beautiful', 'brilliant', 'outstanding', 'epic',
        'legendary', 'godlike', 'beast', 'clean', 'smooth', 'crisp'
    ]
    
    negative_words = [
        'terrible', 'awful', 'bad', 'hate', 'worst', 'stupid', 'trash', 'garbage',
        'horrible', 'disgusting', 'pathetic', 'useless', 'boring', 'annoying',
        'frustrating', 'disappointing', 'tilted', 'broken', 'unfair', 'rigged'
    ]
    
    text_lower = text.lower()
    words = text_lower.split()
    
    # Count matches with higher weight for emotional words
    pos_count = 0
    neg_count = 0
    
    for word in words:
        if word in positive_words:
            pos_count += 2  # Double weight
        if word in negative_words:
            neg_count += 2  # Double weight
    
    # Check for phrases
    if any(phrase in text_lower for phrase in ['nice play', 'well played', 'good job', 'great game']):
        pos_count += 3
    if any(phrase in text_lower for phrase in ['skill issue', 'get good', 'trash player']):
        neg_count += 3
    
    total_words = max(len(words), 1)
    
    # MUCH more aggressive scoring
    if pos_count > 0 and neg_count == 0:
        sentiment_category = "positive"
        compound = min(0.8, pos_count / total_words * 3)  # Amplified
        pos_score = min(0.8, pos_count / total_words * 2)
        neg_score = 0.0
        neutral_score = max(0.1, 1 - pos_score)
    elif neg_count > 0 and pos_count == 0:
        sentiment_category = "negative"
        compound = max(-0.8, -(neg_count / total_words * 3))  # Amplified
        neg_score = min(0.8, neg_count / total_words * 2)
        pos_score = 0.0
        neutral_score = max(0.1, 1 - neg_score)
    elif pos_count > neg_count:
        sentiment_category = "positive"
        compound = 0.4
        pos_score = 0.6
        neg_score = 0.2
        neutral_score = 0.2
    elif neg_count > pos_count:
        sentiment_category = "negative"
        compound = -0.4
        neg_score = 0.6
        pos_score = 0.2
        neutral_score = 0.2
    else:
        sentiment_category = "neutral"
        compound = 0.0
        pos_score = 0.1
        neg_score = 0.1
        neutral_score = 0.8
    
    return {
        "sentiment": {
            "compound": round(compound, 3), 
            "positive": round(pos_score, 3), 
            "negative": round(neg_score, 3), 
            "neutral": round(neutral_score, 3)
        },
        "sentiment_category": sentiment_category,
        "toxicity": {"toxic": max(0, neg_count/total_words), "severe_toxic": 0, "obscene": 0, "threat": 0, "insult": 0, "identity_hate": 0},
        "emotion": "joy" if sentiment_category == "positive" else "anger" if sentiment_category == "negative" else "neutral",
        "emotion_scores": {},
        "confidence": 0.8,  # Higher confidence
        "language": "en"
    }

async def analyze_message(text: str) -> Dict[str, Any]:
    """Main analysis function that tries ML first, falls back to simple."""
    try:
        if ML_AVAILABLE:
            return await analyze_message_ml(text)
        else:
            return await analyze_message_simple(text)
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return await analyze_message_simple(text)
    """Enhanced rule-based message analysis with better sensitivity."""
    
    # Expanded positive words (including gaming slang)
    positive_words = [
        'amazing', 'awesome', 'great', 'incredible', 'fantastic', 'wonderful',
        'excellent', 'perfect', 'love', 'best', 'good', 'nice', 'cool', 'epic',
        'pogchamp', 'pog', 'clutch', 'insane', 'genius', 'beautiful', 'sick',
        'fire', 'lit', 'legendary', 'godlike', 'beast', 'monster', 'goat',
        'clean', 'smooth', 'crisp', 'nutty', 'mental', 'cracked', 'skilled',
        'wp', 'gg', 'gj', 'nice play', 'well played', 'pro', 'carry', 'mvp',
        'hype', 'hyped', 'excited', 'pumped', 'winning', 'victory', 'champion',
        'flawless', 'dominating', 'unstoppable', 'legendary', 'masterpiece'
    ]
    
    # Expanded negative words (including gaming frustration)
    negative_words = [
        'awful', 'terrible', 'bad', 'worst', 'hate', 'suck', 'garbage', 'trash',
        'stupid', 'idiot', 'noob', 'pathetic', 'disappointing', 'boring',
        'useless', 'worthless', 'horrible', 'disgusting', 'annoying', 'frustrating',
        'tilted', 'tilting', 'toxic', 'griefing', 'throwing', 'int', 'feeding',
        'boosted', 'hardstuck', 'washed', 'overrated', 'carried', 'lucky',
        'lag', 'lagging', 'broken', 'op', 'unfair', 'rigged', 'scripting',
        'smurfing', 'camping', 'sweaty', 'tryhard', 'meta slave', 'cheese'
    ]
    
    # Enhanced toxic words (stronger detection)
    toxic_words = [
        'trash', 'garbage', 'idiot', 'stupid', 'pathetic', 'quit', 'uninstall',
        'noob', 'scrub', 'loser', 'kill yourself', 'kys', 'retard', 'retarded',
        'cancer', 'aids', 'gay', 'fag', 'bitch', 'whore', 'slut', 'cunt',
        'fuck you', 'go die', 'neck yourself', 'rope', 'end yourself',
        'braindead', 'monkey', 'ape', 'dog', 'bot', 'waste of space',
        'should never play', 'delete game', 'get good', 'skill issue'
    ]
    
    emotion_words = {
        'joy': ['happy', 'excited', 'love', 'amazing', 'fantastic', 'pog', 'hype', 'lit', 'fire', 'epic', 'pogchamp', 'hyped', 'pumped', 'cheerful', 'thrilled'],
        'anger': ['angry', 'mad', 'hate', 'terrible', 'awful', 'stupid', 'rage', 'furious', 'pissed', 'tilted', 'frustrated', 'annoyed', 'trash', 'garbage'],
        'fear': ['scared', 'worried', 'nervous', 'afraid', 'anxious', 'concerned'],
        'surprise': ['wow', 'omg', 'incredible', 'insane', 'wtf', 'holy', 'damn', 'whoa', 'no way', 'unbelievable'],
        'sadness': ['sad', 'disappointed', 'depressed', 'down', 'upset', 'heartbroken', 'devastated'],
        'disgust': ['gross', 'disgusting', 'awful', 'nasty', 'sick', 'pathetic', 'repulsive']
    }
    
    text_lower = text.lower()
    words = text_lower.split()
    
    # Enhanced scoring with phrase detection
    positive_count = 0
    negative_count = 0
    toxic_count = 0
    
    # Check for exact phrases first (higher weight)
    for phrase in ['nice play', 'well played', 'good job', 'great game', 'kill yourself', 'go die', 'fuck you', 'skill issue']:
        if phrase in text_lower:
            if phrase in ['kill yourself', 'go die', 'fuck you']:
                toxic_count += 3
                negative_count += 2
            elif phrase in ['skill issue']:
                negative_count += 2
            elif phrase in ['nice play', 'well played', 'good job', 'great game']:
                positive_count += 2
    
    # Count individual words
    for word in words:
        if word in positive_words:
            positive_count += 1
        if word in negative_words:
            negative_count += 1
        if word in toxic_words:
            toxic_count += 2  # Toxic words get double weight
    
    # Calculate enhanced sentiment scores (more sensitive)
    total_words = max(len(words), 1)
    
    # Boost the impact of sentiment words
    pos_score = min((positive_count * 2) / total_words, 1.0)  # Double impact
    neg_score = min((negative_count * 2) / total_words, 1.0)  # Double impact
    
    # Calculate compound score with better sensitivity
    if positive_count > 0 and negative_count == 0:
        compound = min(0.8, pos_score * 2)  # Strong positive
    elif negative_count > 0 and positive_count == 0:
        compound = max(-0.8, -(neg_score * 2))  # Strong negative
    elif positive_count > negative_count:
        compound = pos_score - (neg_score * 0.5)
    elif negative_count > positive_count:
        compound = -(neg_score - (pos_score * 0.5))
    else:
        compound = 0.0
    
    # Determine sentiment category with lower thresholds
    if compound > 0.15:  # Lower threshold for positive
        sentiment_category = "positive"
        neutral_score = max(0, 1 - pos_score - neg_score)
    elif compound < -0.15:  # Lower threshold for negative
        sentiment_category = "negative"
        neutral_score = max(0, 1 - pos_score - neg_score)
    else:
        sentiment_category = "neutral"
        neutral_score = max(0.3, 1 - pos_score - neg_score)
    
    # Enhanced emotion analysis
    emotion_scores = {}
    for emotion, words in emotion_words.items():
        score = 0
        for word in words:
            if word in text_lower:
                score += 2  # Higher weight for emotion detection
        emotion_scores[emotion] = min(score / total_words, 1.0)
    
    # Find dominant emotion
    if any(emotion_scores.values()):
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
    else:
        dominant_emotion = "neutral"
    
    # Enhanced toxicity score with phrase detection
    toxicity_base = min((toxic_count * 3) / total_words, 1.0)  # Triple weight for toxic words
    
    # Boost toxicity for very negative sentiment
    if compound < -0.5:
        toxicity_base = min(toxicity_base + 0.3, 1.0)
    
    # Special toxicity boost for gaming-specific toxic phrases
    toxic_phrases = ['skill issue', 'trash player', 'get good', 'delete game', 'go die']
    for phrase in toxic_phrases:
        if phrase in text_lower:
            toxicity_base = min(toxicity_base + 0.4, 1.0)
    
    return {
        "sentiment": {
            "compound": round(compound, 3),
            "positive": round(pos_score, 3),
            "negative": round(neg_score, 3),
            "neutral": round(neutral_score, 3)
        },
        "sentiment_category": sentiment_category,
        "toxicity": {
            "toxic": round(toxicity_base, 3),
            "severe_toxic": round(toxicity_base * 0.9, 3),
            "obscene": round(toxicity_base * 0.7, 3),
            "threat": round(min(toxic_count / total_words, 1.0), 3),
            "insult": round(toxicity_base * 0.8, 3),
            "identity_hate": round(toxicity_base * 0.4, 3)
        },
        "emotion": dominant_emotion,
        "emotion_scores": {k: round(v, 3) for k, v in emotion_scores.items()},
        "confidence": 0.85,  # Higher confidence in enhanced system
        "language": "en"
    }

def init_session_state():
    """Initialize session state for chat analysis."""
    if 'chat_records' not in st.session_state:
        st.session_state.chat_records = []
    if 'auto_generate' not in st.session_state:
        st.session_state.auto_generate = False
    if 'last_generation' not in st.session_state:
        st.session_state.last_generation = 0

def render_chat_page():
    """Render the chat analysis page."""
    import asyncio  # Ensure asyncio is available in this scope
    
    st.title("💬 Advanced Chat Analysis")
    st.markdown("### Real-time sentiment and toxicity analysis")
    
    init_session_state()
    
    # Sidebar controls
    with st.sidebar:
        st.header("Chat Analysis Settings")
        
        # Data source
        st.subheader("Data Source")
        source_type = st.radio(
            "Choose source:",
            ["Simulation", "Twitch Real-time", "Manual Input", "File Upload"],
            index=0
        )
        
        if source_type == "Twitch Real-time":
            st.subheader("🎮 Twitch Real-time Chat")
            
            if TWITCH_AVAILABLE:
                # Connection status indicator
                if is_twitch_connected():
                    st.success(f"🔴 **LIVE** - Connected to #{get_current_channel()}")
                    st.caption("Real-time messages are being received")
                else:
                    st.info("⚪ **OFFLINE** - Not connected to Twitch")
                
                # Configuration
                twitch_channel = st.text_input(
                    "Twitch Channel (without #):",
                    value="shroud",
                    help="Enter the Twitch channel name to monitor"
                )
                
                # Show current status
                if is_twitch_connected():
                    current_channel = get_current_channel()
                    st.success(f"🔴 LIVE: Connected to #{current_channel}")
                else:
                    st.info("⏸️ Not connected to any channel")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔴 Connect to Twitch"):
                        if twitch_channel:
                            with st.spinner(f"Connecting to #{twitch_channel}..."):
                                try:
                                    # Start monitoring (no asyncio needed - handled internally)
                                    success = start_twitch_monitoring(twitch_channel, handle_twitch_message)
                                    
                                    if success:
                                        st.success(f"✅ Connected to #{twitch_channel}!")
                                        st.info("💡 Real-time messages will appear in the dashboard below")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to connect. Channel might be offline or invalid.")
                                        
                                except Exception as e:
                                    st.error(f"❌ Connection error: {e}")
                        else:
                            st.warning("Please enter a channel name")
                
                with col2:
                    if st.button("⏹️ Disconnect"):
                        try:
                            stop_twitch_monitoring()
                            st.success("✅ Disconnected from Twitch")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Disconnect error: {e}")
                
                # Popular channels to try
                st.markdown("---")
                st.markdown("**🎯 Popular channels to try:**")
                
                popular_channels = ["shroud", "xqcow", "pokimane", "lirik", "sodapoppin", "asmongold"]
                
                cols = st.columns(3)
                for i, channel in enumerate(popular_channels):
                    with cols[i % 3]:
                        if st.button(f"#{channel}", key=f"quick_{channel}"):
                            # Quick connect to popular channel
                            with st.spinner(f"Quick connecting to #{channel}..."):
                                try:
                                    success = start_twitch_monitoring(channel, handle_twitch_message)
                                    
                                    if success:
                                        st.success(f"✅ Connected to #{channel}!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ #{channel} might be offline")
                                        
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                
            else:
                st.error("❌ Twitch integration not available")
                st.code("pip install websockets", language="bash")
        
        elif source_type == "Simulation":
            st.subheader("Simulation Controls")
            auto_generate = st.toggle("Auto-generate messages", value=False)
            
            if auto_generate != st.session_state.auto_generate:
                st.session_state.auto_generate = auto_generate
            
            if auto_generate:
                generation_rate = st.slider("Messages per minute", 1, 60, 10)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Generate Message"):
                    sample = generate_sample_message()
                    analysis = asyncio.run(analyze_message(sample["text"]))
                    
                    record = {
                        **sample,
                        **analysis,
                        "timestamp": time.time()
                    }
                    st.session_state.chat_records.append(record)
                    st.rerun()
            
            with col2:
                if st.button("Generate 10"):
                    for _ in range(10):
                        sample = generate_sample_message()
                        analysis = asyncio.run(analyze_message(sample["text"]))
                        
                        record = {
                            **sample,
                            **analysis,
                            "timestamp": time.time()
                        }
                        st.session_state.chat_records.append(record)
                    st.rerun()        # Display settings
        st.subheader("Display Settings")
        max_messages = st.slider("Max messages to show", 50, 1000, 200)
        refresh_interval = st.slider("Auto-refresh (seconds)", 1.0, 10.0, 3.0)
        
        # Filters
        st.subheader("Filters")
        sentiment_filter = st.multiselect(
            "Show sentiment:",
            ["positive", "neutral", "negative"],
            default=["positive", "neutral", "negative"]
        )
        
        min_toxicity = st.slider("Min toxicity threshold", 0.0, 1.0, 0.0)
        max_toxicity = st.slider("Max toxicity threshold", 0.0, 1.0, 1.0)
        
        keyword_filter = st.text_input("Filter by keyword:")
        
        # Actions
        st.subheader("Actions")
        if st.button("Clear All Data"):
            st.session_state.chat_records = []
            st.rerun()
        
        if st.button("Export CSV") and st.session_state.chat_records:
            df = pd.DataFrame(st.session_state.chat_records)
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                data=csv,
                file_name=f"chat_data_{int(time.time())}.csv",
                mime="text/csv"
            )
    
    # Auto-generation logic
    if st.session_state.auto_generate:
        current_time = time.time()
        if source_type == "Simulation" and 'generation_rate' in locals():
            time_between_messages = 60 / generation_rate  # Convert to seconds
            
            if current_time - st.session_state.last_generation > time_between_messages:
                sample = generate_sample_message()
                analysis = asyncio.run(analyze_message(sample["text"]))
                
                record = {
                    **sample,
                    **analysis,
                    "timestamp": current_time
                }
                st.session_state.chat_records.append(record)
                st.session_state.last_generation = current_time
                st.rerun()
    
    # Manual input section
    if source_type == "Manual Input":
        st.markdown("### Manual Message Input")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_input = st.text_input("Enter message:", key="manual_input")
            username_input = st.text_input("Username:", value="TestUser", key="username_input")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            if st.button("Analyze Message") and user_input:
                analysis = asyncio.run(analyze_message(user_input))
                
                record = {
                    "user": username_input or "TestUser",
                    "text": user_input,
                    **analysis,
                    "timestamp": time.time()
                }
                st.session_state.chat_records.append(record)
                
                st.rerun()
    
    # File upload section
    if source_type == "File Upload":
        st.markdown("### Upload Chat Data")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Validate columns
                required_cols = ["user", "text"]
                if all(col in df.columns for col in required_cols):
                    if st.button("Process Uploaded Data"):
                        with st.spinner("Processing messages..."):
                            processed_records = []
                            
                            for _, row in df.iterrows():
                                analysis = asyncio.run(analyze_message(row["text"]))
                                
                                record = {
                                    "user": row["user"],
                                    "text": row["text"],
                                    "timestamp": row.get("timestamp", time.time()),
                                    **analysis
                                }
                                processed_records.append(record)
                            
                            st.session_state.chat_records.extend(processed_records)
                            st.success(f"Processed {len(processed_records)} messages!")
                            st.rerun()
                else:
                    st.error(f"CSV must contain columns: {required_cols}")
                    st.info(f"Found columns: {list(df.columns)}")
            
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
    
    # Main dashboard
    if st.session_state.chat_records:
        # Apply filters
        filtered_records = st.session_state.chat_records.copy()
        
        # Sentiment filter
        if sentiment_filter:
            filtered_records = [
                r for r in filtered_records 
                if r.get("sentiment_category", "neutral") in sentiment_filter
            ]
        
        # Toxicity filter
        if min_toxicity > 0 or max_toxicity < 1:
            filtered_records = [
                r for r in filtered_records 
                if min_toxicity <= r.get("toxicity", {}).get("toxic", 0) <= max_toxicity
            ]
        
        # Keyword filter
        if keyword_filter:
            filtered_records = [
                r for r in filtered_records 
                if keyword_filter.lower() in r.get("text", "").lower()
            ]
        
        # Limit to max messages
        filtered_records = filtered_records[-max_messages:]
        
        # Metrics
        if filtered_records:
            total = len(filtered_records)
            positive = sum(1 for r in filtered_records if r.get("sentiment_category") == "positive")
            neutral = sum(1 for r in filtered_records if r.get("sentiment_category") == "neutral")
            negative = sum(1 for r in filtered_records if r.get("sentiment_category") == "negative")
            toxic = sum(1 for r in filtered_records if r.get("toxicity", {}).get("toxic", 0) > 0.5)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("😊 Positive", f"{positive} ({positive/total*100:.1f}%)")
            col2.metric("😐 Neutral", f"{neutral} ({neutral/total*100:.1f}%)")
            col3.metric("😠 Negative", f"{negative} ({negative/total*100:.1f}%)")
            col4.metric("🚨 Toxic", f"{toxic} ({toxic/total*100:.1f}%)")
            
            # Sentiment timeline
            if len(filtered_records) > 1:
                df = pd.DataFrame(filtered_records)
                df['compound_sentiment'] = df['sentiment'].apply(lambda x: x.get('compound', 0))
                df['toxicity_score'] = df['toxicity'].apply(lambda x: x.get('toxic', 0))
                
                # Create timeline chart
                chart = alt.Chart(df.tail(100)).mark_line(point=True).encode(
                    x=alt.X('timestamp:T', title='Time'),
                    y=alt.Y('compound_sentiment:Q', title='Sentiment Score'),
                    color=alt.Color('sentiment_category:N', title='Category'),
                    tooltip=['user:N', 'text:N', 'compound_sentiment:Q', 'sentiment_category:N']
                ).properties(
                    title="Sentiment Timeline",
                    height=300
                )
                
                st.altair_chart(chart, use_container_width=True)
            
            # Recent messages
            st.markdown("### Recent Messages")
            
            for record in reversed(filtered_records[-20:]):  # Show last 20
                sentiment = record.get("sentiment", {})
                sentiment_cat = record.get("sentiment_category", "neutral")
                toxicity = record.get("toxicity", {}).get("toxic", 0)
                
                # Sentiment badge
                if sentiment_cat == "positive":
                    badge = "😊"
                elif sentiment_cat == "negative":
                    badge = "😠"
                else:
                    badge = "😐"
                
                # Toxicity warning
                toxic_warning = " 🚨" if toxicity > 0.5 else ""
                
                # Format timestamp
                import datetime
                ts = datetime.datetime.fromtimestamp(record.get("timestamp", time.time()))
                time_str = ts.strftime("%H:%M:%S")
                
                st.markdown(f"""
                **{badge} {record.get('user', 'Unknown')}** {toxic_warning} ({time_str})  
                {record.get('text', '')}  
                *Sentiment: {sentiment.get('compound', 0):.2f} | Toxicity: {toxicity:.2f} | Emotion: {record.get('emotion', 'neutral')}*
                """)
                st.markdown("---")
        
        else:
            st.info("No messages match the current filters.")
    
    else:
        st.info("No chat data available. Use the sidebar to generate or input messages.")
    
    # Auto-refresh
    if st.session_state.auto_generate:
        time.sleep(refresh_interval)
        st.rerun()

# Main execution
if __name__ == "__main__":
    render_chat_page()
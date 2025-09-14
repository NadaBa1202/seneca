#!/usr/bin/env python3

import sys
sys.path.append('.')
from esports_analytics.services.ml.sentiment_trainer import GamingSentimentTrainer
import pandas as pd

def train_gaming_model():
    print("🎮 Training Gaming Sentiment Model...")
    
    # Initialize trainer
    trainer = GamingSentimentTrainer()
    
    # Create a larger training dataset with gaming examples
    gaming_data = [
        # Positive gaming expressions
        "clutch play! that was insane!",
        "pog champion that was amazing",
        "ez clap well played team",
        "200 IQ play right there",
        "lit performance by everyone",
        "goat player carrying hard",
        "cracked aim on that shot",
        "based and skilled gameplay",
        "fire round everyone",
        "nice shot well done",
        "good game everyone",
        "wp team effort",
        "gg ez but fun match",
        "sick plays all around",
        "legendary performance",
        
        # Negative gaming expressions  
        "trash team uninstall game",
        "noob players tilted af",
        "bot gameplay delete this",
        "bronze level plays here",
        "feeding team bad game",
        "terrible performance today",
        "disappointing match overall",
        "weak plays this round",
        "poor coordination team",
        "bad aim this game",
        
        # Toxic gaming expressions
        "kys noob you suck",
        "trash player uninstall now",
        "get cancer and die",
        "kill yourself loser",
        "end your life noob",
        "neck yourself trash",
        "rope yourself bad player",
        "delete account and leave",
        "toxic player reported",
        "griefing team on purpose",
        
        # Neutral gaming expressions
        "next round starting soon",
        "what map are we playing",
        "checking my settings now",
        "buying equipment this round",
        "rotating to different position",
        "economy reset this round",
        "saving for next round",
        "team strategy discussion",
        "technical timeout called",
        "match starting in 5 minutes"
    ]
    
    # Auto-label the expanded dataset
    print("🏷️  Auto-labeling gaming data...")
    labels = trainer.auto_label_data(gaming_data)
    
    print(f"📊 Label distribution:")
    label_counts = pd.Series(labels).value_counts()
    print(label_counts)
    
    # Train the model with enough data for each class
    if len(set(labels)) >= 2 and min(label_counts) >= 3:
        print("\n🔧 Training custom gaming model...")
        try:
            results = trainer.train_custom_model(gaming_data, labels)
            print("✅ Training completed successfully!")
            
            # Test on various gaming phrases
            test_phrases = [
                "That clutch was pog!",
                "This team is trash",
                "kys noob", 
                "good game everyone",
                "what items should I buy",
                "ez clap that was lit",
                "tilted and feeding now",
                "report this toxic player"
            ]
            
            print("\n🎯 Testing trained model:")
            for phrase in test_phrases:
                prediction = trainer.predict_sentiment(phrase)
                print(f"'{phrase}' -> {prediction['sentiment']} ({prediction['confidence']:.2f})")
                
            # Save the trained model
            print("\n💾 Saving trained model...")
            trainer.save_model("gaming_sentiment_model.pkl")
            print("✅ Model saved as gaming_sentiment_model.pkl")
            
            return trainer
            
        except Exception as e:
            print(f"❌ Training error: {e}")
            return None
    else:
        print("❌ Not enough diverse labels for training")
        return None

if __name__ == "__main__":
    trained_model = train_gaming_model()

#!/usr/bin/env python3

import sys
sys.path.append('.')
from esports_analytics.services.ml.sentiment_trainer import GamingSentimentTrainer, train_on_gaming_dataset
import pandas as pd

def test_trainer():
    print("🎮 Testing Gaming Sentiment Trainer...")
    
    # Initialize trainer
    trainer = GamingSentimentTrainer()
    print("✅ Trainer loaded successfully!")
    
    # Test texts with gaming language
    test_texts = [
        "That was such a clutch play! POG",
        "This team is trash, they should uninstall", 
        "Good game everyone, nice match",
        "kys noob you suck at this game",
        "ez clap that was lit! 200 IQ play"
    ]
    
    print("\n🏷️  Testing auto-labeling:")
    labels = trainer.auto_label_data(test_texts)
    
    for text, label in zip(test_texts, labels):
        print(f"'{text}' -> {label}")
    
    print("\n🤖 Testing with small gaming dataset...")
    
    # Try to load a small dataset
    try:
        dataset_path = "gaming/small/gaming_100mb.csv"
        print(f"Training on: {dataset_path}")
        
        # Use the training function with a small sample
        trained_trainer = train_on_gaming_dataset(dataset_path, sample_size=1000)
        
        print("🎯 Testing trained model predictions:")
        for text in test_texts:
            prediction = trained_trainer.predict_sentiment(text)
            print(f"'{text}' -> {prediction}")
            
    except Exception as e:
        print(f"❌ Error with dataset training: {e}")
        print("Testing basic functionality instead...")
        
        # Test basic training with our test data
        try:
            print("\n🔧 Training on test examples...")
            results = trainer.train_custom_model(test_texts, labels)
            print("✅ Training completed!")
            
            print("\n🎯 Testing predictions:")
            for text in test_texts:
                prediction = trainer.predict_sentiment(text)
                print(f"'{text}' -> {prediction}")
                
        except Exception as e2:
            print(f"❌ Error with basic training: {e2}")
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    test_trainer()

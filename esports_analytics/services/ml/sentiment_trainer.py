"""
Advanced Gaming Sentiment Analysis Trainer

This module creates a custom sentiment analysis model specifically trained
on gaming/esports data to eliminate false neutral classifications.
"""

import pandas as pd
import numpy as np
import re
import pickle
import os
from typing import Dict, List, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
import logging

logger = logging.getLogger(__name__)

class GamingSentimentTrainer:
    """Trains custom sentiment models on gaming data."""
    
    def __init__(self):
        self.models = {}
        self.vectorizers = {}
        self.gaming_keywords = self._load_gaming_keywords()
        
    def _load_gaming_keywords(self) -> Dict[str, List[str]]:
        """Load gaming-specific keyword dictionaries."""
        return {
            'positive': [
                # General positive
                'amazing', 'awesome', 'incredible', 'fantastic', 'perfect', 'excellent',
                'beautiful', 'brilliant', 'outstanding', 'wonderful', 'great', 'good',
                'nice', 'cool', 'epic', 'legendary',
                
                # Gaming positive
                'clutch', 'pog', 'pogchamp', 'poggers', 'pog!', 'hype', 'hyped',
                'lit', 'fire', 'sick', 'insane', 'nutty', 'cracked', 'crisp',
                'clean', 'smooth', 'beast', 'goat', 'pro', 'skill', 'skilled',
                'carry', 'carried', 'mvp', 'ace', 'pentakill', 'quadra',
                'triple', 'double', 'first blood', 'dominating', 'godlike',
                'rampage', 'unstoppable', 'flawless', 'perfect game',
                
                # Expressions
                'gg', 'gj', 'wp', 'well played', 'good job', 'nice play',
                'great play', 'amazing play', 'incredible play', 'insane play',
                'love this', 'love it', 'so good', 'too good', 'best ever',
                'on fire', 'killing it', 'crushing it'
            ],
            
            'negative': [
                # General negative
                'terrible', 'awful', 'horrible', 'disgusting', 'pathetic', 'useless',
                'worthless', 'disappointing', 'frustrating', 'annoying', 'boring',
                'bad', 'worst', 'hate', 'stupid', 'dumb', 'ridiculous',
                
                # Gaming negative
                'noob', 'newb', 'scrub', 'trash', 'garbage', 'bot', 'bronze',
                'hardstuck', 'boosted', 'carried', 'lucky', 'rng', 'bs',
                'bullshit', 'broken', 'op', 'overpowered', 'unfair', 'cheap',
                'cheese', 'cheesy', 'spam', 'spamming', 'camping', 'camper',
                'tryhard', 'sweaty', 'meta slave', 'tier whore',
                
                # Frustration
                'tilted', 'tilting', 'tilt', 'rage', 'raging', 'mad', 'angry',
                'pissed', 'salty', 'salt', 'toxic', 'grief', 'griefing',
                'throwing', 'throw', 'feed', 'feeding', 'int', 'inting',
                'afk', 'quit', 'ff', 'surrender', 'forfeit',
                
                # Tech issues
                'lag', 'lagging', 'laggy', 'ping', 'fps', 'frame', 'stutter',
                'disconnect', 'dc', 'crash', 'bug', 'glitch', 'exploit'
            ],
            
            'toxic': [
                # Direct insults
                'idiot', 'moron', 'retard', 'retarded', 'stupid', 'dumb',
                'braindead', 'brain dead', 'monkey', 'ape', 'dog', 'animal',
                
                # Profanity
                'fuck', 'fucking', 'shit', 'damn', 'hell', 'ass', 'bitch',
                'bastard', 'crap', 'piss', 'cock', 'dick',
                
                # Extreme toxic
                'kill yourself', 'kys', 'neck yourself', 'rope', 'hang yourself',
                'die', 'cancer', 'aids', 'autistic', 'autism', 'gay', 'fag',
                'faggot', 'homo', 'lesbian', 'trans', 'nigger', 'nigga',
                
                # Threats
                'kill you', 'murder you', 'find you', 'come for you',
                'destroy you', 'end you', 'ruin you',
                
                # Gaming toxic
                'uninstall', 'delete game', 'quit gaming', 'never play again',
                'should quit', 'waste of space', 'shouldn\'t exist',
                'get good', 'skill issue', 'git gud', 'learn to play'
            ]
        }
    
    def auto_label_data(self, texts: List[str]) -> List[str]:
        """Automatically label texts based on gaming keywords."""
        labels = []
        
        for text in texts:
            text_lower = text.lower()
            
            # Count keyword matches
            toxic_score = sum(1 for word in self.gaming_keywords['toxic'] 
                            if word in text_lower)
            negative_score = sum(1 for word in self.gaming_keywords['negative'] 
                               if word in text_lower)
            positive_score = sum(1 for word in self.gaming_keywords['positive'] 
                               if word in text_lower)
            
            # Apply gaming-specific rules
            if toxic_score > 0:
                labels.append('toxic')
            elif positive_score > negative_score and positive_score > 0:
                labels.append('positive')
            elif negative_score > positive_score and negative_score > 0:
                labels.append('negative')
            else:
                # Advanced pattern matching for edge cases
                if self._detect_positive_patterns(text_lower):
                    labels.append('positive')
                elif self._detect_negative_patterns(text_lower):
                    labels.append('negative')
                else:
                    labels.append('neutral')
        
        return labels
    
    def _detect_positive_patterns(self, text: str) -> bool:
        """Detect positive patterns that keywords might miss."""
        positive_patterns = [
            r'\b(so|too|very|really|extremely)\s+(good|great|amazing|awesome)\b',
            r'\b(love|loving|loved)\s+(this|it|that|the)\b',
            r'\b(best|greatest)\s+\w+\s+(ever|today)\b',
            r'\b(well\s+played|good\s+job|nice\s+work|great\s+game)\b',
            r'\b\w+\s+(is|was)\s+(fire|lit|sick|insane|amazing)\b',
            r'\b(pogchamp|pog|hype|clutch|epic)\b',
            r'[!]{2,}',  # Multiple exclamation marks often indicate excitement
        ]
        
        return any(re.search(pattern, text) for pattern in positive_patterns)
    
    def _detect_negative_patterns(self, text: str) -> bool:
        """Detect negative patterns that keywords might miss."""
        negative_patterns = [
            r'\b(so|too|very|really|extremely)\s+(bad|terrible|awful|boring)\b',
            r'\b(hate|hating|hated)\s+(this|it|that|the)\b',
            r'\b(worst|terrible)\s+\w+\s+(ever|today)\b',
            r'\bwhat\s+(a|an)\s+\w+\s+(noob|scrub|idiot)\b',
            r'\b(skill\s+issue|get\s+good|git\s+gud)\b',
            r'\bcan\'t\s+(believe|stand)\b',
            r'\bwhy\s+(is|are|do|does)\s+\w+\s+(so|such)\s+(bad|terrible)\b',
        ]
        
        return any(re.search(pattern, text) for pattern in negative_patterns)
    
    def preprocess_text(self, text: str) -> str:
        """Advanced text preprocessing for gaming content."""
        # Convert to lowercase
        text = text.lower()
        
        # Handle gaming-specific abbreviations
        replacements = {
            'gg': 'good game',
            'wp': 'well played',
            'gj': 'good job',
            'ff': 'forfeit',
            'kys': 'kill yourself',
            'pog': 'pogchamp',
            'lol': 'laugh out loud',
            'lmao': 'laugh my ass off',
            'wtf': 'what the fuck',
            'omg': 'oh my god',
            'tbh': 'to be honest',
            'imo': 'in my opinion',
            'rn': 'right now',
            'ngl': 'not gonna lie',
        }
        
        for abbrev, full in replacements.items():
            text = re.sub(r'\b' + abbrev + r'\b', full, text)
        
        # Remove excessive punctuation but keep some for emotion
        text = re.sub(r'[!]{3,}', '!!', text)
        text = re.sub(r'[?]{3,}', '??', text)
        text = re.sub(r'[.]{3,}', '...', text)
        
        # Handle repeated characters (e.g., "sooooo good" -> "so good")
        text = re.sub(r'(.)\1{2,}', r'\1\1', text)
        
        return text
    
    def train_custom_model(self, texts: List[str], labels: List[str] = None) -> Dict[str, Any]:
        """Train a custom sentiment model on gaming data."""
        
        # Auto-label if no labels provided
        if labels is None:
            print("Auto-labeling data based on gaming keywords...")
            labels = self.auto_label_data(texts)
        
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Create feature pipeline
        vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),  # Include phrases
            min_df=2,
            max_df=0.95,
            stop_words='english'
        )
        
        # Prepare data
        X = vectorizer.fit_transform(processed_texts)
        y = np.array(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train multiple models
        models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100, 
                max_depth=20, 
                random_state=42,
                class_weight='balanced'
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            ),
            'logistic_regression': LogisticRegression(
                max_iter=1000,
                random_state=42,
                class_weight='balanced'
            )
        }
        
        best_model = None
        best_score = 0
        results = {}
        
        print("Training models...")
        for name, model in models.items():
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate
            score = model.score(X_test, y_test)
            cv_scores = cross_val_score(model, X_train, y_train, cv=5)
            
            results[name] = {
                'model': model,
                'test_score': score,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
            
            print(f"{name}: {score:.3f} (CV: {cv_scores.mean():.3f} ± {cv_scores.std():.3f})")
            
            if score > best_score:
                best_score = score
                best_model = model
        
        # Store best model and vectorizer
        self.models['sentiment'] = best_model
        self.vectorizers['sentiment'] = vectorizer
        
        # Generate detailed report
        y_pred = best_model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        return {
            'model': best_model,
            'vectorizer': vectorizer,
            'test_score': best_score,
            'classification_report': report,
            'label_distribution': pd.Series(y).value_counts().to_dict()
        }
    
    def predict_sentiment(self, text: str) -> Dict[str, Any]:
        """Predict sentiment using the trained model."""
        if 'sentiment' not in self.models:
            raise ValueError("Model not trained. Call train_custom_model first.")
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Vectorize
        X = self.vectorizers['sentiment'].transform([processed_text])
        
        # Predict
        prediction = self.models['sentiment'].predict(X)[0]
        probabilities = self.models['sentiment'].predict_proba(X)[0]
        
        # Get class names
        classes = self.models['sentiment'].classes_
        prob_dict = {cls: prob for cls, prob in zip(classes, probabilities)}
        
        return {
            'prediction': prediction,
            'probabilities': prob_dict,
            'confidence': max(probabilities)
        }
    
    def save_model(self, filepath: str):
        """Save the trained model and vectorizer."""
        model_data = {
            'models': self.models,
            'vectorizers': self.vectorizers,
            'gaming_keywords': self.gaming_keywords
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model and vectorizer."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.models = model_data['models']
        self.vectorizers = model_data['vectorizers']
        self.gaming_keywords = model_data['gaming_keywords']
        
        print(f"Model loaded from {filepath}")

def train_on_gaming_dataset(dataset_path: str, sample_size: int = 50000) -> GamingSentimentTrainer:
    """Train on gaming dataset with smart sampling."""
    trainer = GamingSentimentTrainer()
    
    print(f"Loading gaming dataset from {dataset_path}...")
    
    try:
        # Load dataset (handle large files)
        if dataset_path.endswith('.csv'):
            # Sample data for training
            df = pd.read_csv(dataset_path, nrows=sample_size)
        else:
            raise ValueError("Unsupported file format")
        
        # Extract text column (adjust based on your dataset structure)
        if 'text' in df.columns:
            texts = df['text'].dropna().astype(str).tolist()
        elif 'message' in df.columns:
            texts = df['message'].dropna().astype(str).tolist()
        elif 'content' in df.columns:
            texts = df['content'].dropna().astype(str).tolist()
        else:
            # Use first text-like column
            text_cols = [col for col in df.columns if df[col].dtype == 'object']
            if text_cols:
                texts = df[text_cols[0]].dropna().astype(str).tolist()
            else:
                raise ValueError("No text column found in dataset")
        
        print(f"Training on {len(texts)} messages...")
        
        # Train model
        results = trainer.train_custom_model(texts)
        
        print(f"Training complete! Best model score: {results['test_score']:.3f}")
        print(f"Label distribution: {results['label_distribution']}")
        
        return trainer
        
    except Exception as e:
        print(f"Error training on dataset: {e}")
        raise

if __name__ == "__main__":
    # Example usage
    trainer = GamingSentimentTrainer()
    
    # Test with sample data
    sample_texts = [
        "That was an amazing clutch play!",
        "This game is so boring and terrible",
        "You're trash, uninstall the game",
        "GG everyone, well played",
        "I'm so tilted by this lag"
    ]
    
    results = trainer.train_custom_model(sample_texts)
    print("Training results:", results)

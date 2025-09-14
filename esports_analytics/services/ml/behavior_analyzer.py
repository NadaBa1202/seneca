"""Behavioral & Emotional Intelligence Service

Advanced analysis of user behavior and emotional patterns:
- Emotion tracking over time
- User interaction patterns
- Community behavior analysis
- Toxic behavior detection
- Cultural sensitivity analysis
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    user_id: str
    emotion_history: List[Dict[str, float]]
    interaction_patterns: Dict[str, float]
    toxicity_score: float
    engagement_score: float
    languages: List[str]
    activity_hours: Dict[int, float]
    topics: Dict[str, float]

@dataclass
class CommunitySnapshot:
    timestamp: datetime
    emotion_distribution: Dict[str, float]
    active_users: int
    toxicity_level: float
    engagement_level: float
    dominant_topics: List[str]
    language_distribution: Dict[str, float]
    user_clusters: Dict[str, List[str]]

class BehaviorAnalyzer:
    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.community_snapshots: List[CommunitySnapshot] = []
        self.interaction_graph = defaultdict(lambda: defaultdict(float))
        
    def update_user_profile(self, 
                          user_id: str, 
                          message: Dict[str, Any],
                          timestamp: datetime):
        """Update user profile with new message data."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                emotion_history=[],
                interaction_patterns={},
                toxicity_score=0.0,
                engagement_score=0.0,
                languages=[],
                activity_hours={},
                topics={}
            )
            
        profile = self.user_profiles[user_id]
        
        # Update emotion history
        if 'analysis' in message:
            profile.emotion_history.append(message['analysis'].emotions)
            
            # Keep last 100 emotions
            if len(profile.emotion_history) > 100:
                profile.emotion_history = profile.emotion_history[-100:]
                
        # Update activity hours
        hour = timestamp.hour
        profile.activity_hours[hour] = profile.activity_hours.get(hour, 0) + 1
        
        # Update language usage
        if 'language' in message:
            if message['language'] not in profile.languages:
                profile.languages.append(message['language'])
                
        # Update toxicity score with exponential moving average
        if 'analysis' in message:
            alpha = 0.1  # Smoothing factor
            new_toxicity = message['analysis'].toxicity
            profile.toxicity_score = (alpha * new_toxicity + 
                                    (1 - alpha) * profile.toxicity_score)
                                    
        # Update engagement score
        profile.engagement_score = self.calculate_engagement(profile)
        
    def update_interaction_graph(self, 
                               source_user: str, 
                               target_user: str, 
                               interaction_type: str,
                               weight: float = 1.0):
        """Update user interaction graph."""
        self.interaction_graph[source_user][target_user] += weight
        
    def create_community_snapshot(self, timestamp: datetime) -> CommunitySnapshot:
        """Create a snapshot of current community state."""
        active_users = [user for user, profile in self.user_profiles.items()
                       if self.is_recently_active(profile, timestamp)]
                       
        # Calculate emotion distribution
        emotions = defaultdict(list)
        for user in active_users:
            profile = self.user_profiles[user]
            if profile.emotion_history:
                latest_emotions = profile.emotion_history[-1]
                for emotion, score in latest_emotions.items():
                    emotions[emotion].append(score)
                    
        emotion_dist = {
            emotion: np.mean(scores)
            for emotion, scores in emotions.items()
        }
        
        # Calculate language distribution
        all_languages = []
        for user in active_users:
            all_languages.extend(self.user_profiles[user].languages)
            
        language_dist = {}
        if all_languages:
            lang_series = pd.Series(all_languages)
            language_dist = lang_series.value_counts(normalize=True).to_dict()
            
        # Cluster users based on behavior
        user_clusters = self.cluster_users(active_users)
        
        # Create snapshot
        snapshot = CommunitySnapshot(
            timestamp=timestamp,
            emotion_distribution=emotion_dist,
            active_users=len(active_users),
            toxicity_level=self.calculate_community_toxicity(active_users),
            engagement_level=self.calculate_community_engagement(active_users),
            dominant_topics=self.get_dominant_topics(active_users),
            language_distribution=language_dist,
            user_clusters=user_clusters
        )
        
        self.community_snapshots.append(snapshot)
        return snapshot
        
    def calculate_engagement(self, profile: UserProfile) -> float:
        """Calculate user engagement score."""
        factors = []
        
        # Activity frequency
        activity_score = sum(profile.activity_hours.values()) / 24
        factors.append(min(1.0, activity_score))
        
        # Emotion intensity
        if profile.emotion_history:
            emotion_intensity = np.mean([max(emotions.values()) 
                                      for emotions in profile.emotion_history])
            factors.append(emotion_intensity)
        
        # Language variety
        language_score = min(1.0, len(profile.languages) / 3)
        factors.append(language_score)
        
        return np.mean(factors) if factors else 0.0
        
    def cluster_users(self, active_users: List[str]) -> Dict[str, List[str]]:
        """Cluster users based on behavior patterns."""
        if not active_users:
            return {}
            
        # Create feature vectors for users
        features = []
        for user in active_users:
            profile = self.user_profiles[user]
            feature_vector = [
                profile.toxicity_score,
                profile.engagement_score,
                len(profile.languages),
                len(profile.activity_hours),
                # Add more features as needed
            ]
            features.append(feature_vector)
            
        # Perform clustering
        n_clusters = min(3, len(active_users))
        kmeans = KMeans(n_clusters=n_clusters)
        labels = kmeans.fit_predict(features)
        
        # Group users by cluster
        clusters = defaultdict(list)
        for user, label in zip(active_users, labels):
            clusters[f"cluster_{label}"].append(user)
            
        return dict(clusters)
        
    @staticmethod
    def is_recently_active(profile: UserProfile, 
                          current_time: datetime,
                          window: timedelta = timedelta(hours=1)) -> bool:
        """Check if user was active recently."""
        if not profile.activity_hours:
            return False
            
        recent_hour = current_time.hour
        return recent_hour in profile.activity_hours
        
    def calculate_community_toxicity(self, active_users: List[str]) -> float:
        """Calculate overall community toxicity level."""
        if not active_users:
            return 0.0
            
        toxicity_scores = [self.user_profiles[user].toxicity_score 
                          for user in active_users]
        return np.mean(toxicity_scores)
        
    def calculate_community_engagement(self, active_users: List[str]) -> float:
        """Calculate overall community engagement level."""
        if not active_users:
            return 0.0
            
        engagement_scores = [self.user_profiles[user].engagement_score 
                           for user in active_users]
        return np.mean(engagement_scores)
        
    def get_dominant_topics(self, active_users: List[str]) -> List[str]:
        """Identify dominant topics in the community."""
        # Implement topic detection logic
        return []  # Placeholder

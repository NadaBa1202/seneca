"""
Configuration management for the League of Legends Companion App.

This module handles all application configuration including environment variables,
API keys, model settings, and feature flags.
"""

import os
from pathlib import Path
from typing import Optional, List
try:
    from pydantic import BaseSettings, Field, validator
except ImportError:
    # Fallback for older pydantic versions or missing pydantic
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    def Field(default=None, env=None):
        return default
    
    def validator(field_name):
        def decorator(func):
            return func
        return decorator

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class RiotAPIConfig(BaseSettings):
    """Configuration for Riot Games API."""
    
    def __init__(self):
        self.api_key = os.getenv("RIOT_API_KEY", "RGAPI-demo-key-for-testing")
        self.base_url = os.getenv("RIOT_BASE_URL", "https://na1.api.riotgames.com")
        self.rate_limit_requests_per_second = int(os.getenv("RIOT_RATE_LIMIT_REQUESTS_PER_SECOND", "20"))
        self.rate_limit_requests_per_minute = int(os.getenv("RIOT_RATE_LIMIT_REQUESTS_PER_MINUTE", "100"))
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))


class CacheConfig:
    """Configuration for caching systems."""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_password = os.getenv("REDIS_PASSWORD")
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_cache_ttl = int(os.getenv("REDIS_CACHE_TTL", "3600"))
        self.api_cache_duration = int(os.getenv("API_CACHE_DURATION", "300"))


class DataConfig:
    """Configuration for data paths and sources."""
    
    def __init__(self):
        self.dragontail_data_path = Path(os.getenv("DRAGONTAIL_DATA_PATH", "../../15.18.1"))
        self.model_cache_dir = Path(os.getenv("MODEL_CACHE_DIR", "./models"))
        self.app_cache_dir = Path(os.getenv("APP_CACHE_DIR", "./cache"))
        self.huggingface_cache_dir = Path(os.getenv("HUGGINGFACE_CACHE_DIR", "./models/huggingface"))
        
        # Ensure paths exist
        for path in [self.model_cache_dir, self.app_cache_dir, self.huggingface_cache_dir]:
            path.mkdir(parents=True, exist_ok=True)


class MLConfig:
    """Configuration for machine learning models."""
    
    def __init__(self):
        self.model_download_timeout = int(os.getenv("MODEL_DOWNLOAD_TIMEOUT", "300"))
        self.use_gpu = os.getenv("USE_GPU", "False").lower() == "true"
        self.max_sequence_length = int(os.getenv("MAX_SEQUENCE_LENGTH", "512"))
        self.batch_size = int(os.getenv("BATCH_SIZE", "16"))
        
        # Model names for different tasks
        self.qa_model_name = os.getenv("QA_MODEL_NAME", "deepset/roberta-base-squad2")
        self.summarization_model_name = os.getenv("SUMMARIZATION_MODEL_NAME", "facebook/bart-large-cnn")
        self.sentiment_model_name = os.getenv("SENTIMENT_MODEL_NAME", "cardiffnlp/twitter-roberta-base-sentiment-latest")
        
        # Validate GPU availability
        if self.use_gpu:
            try:
                import torch
                if not torch.cuda.is_available():
                    print("Warning: GPU requested but not available, falling back to CPU")
                    self.use_gpu = False
            except ImportError:
                print("Warning: PyTorch not available, falling back to CPU")
                self.use_gpu = False


class StreamlitConfig:
    """Configuration for Streamlit application."""
    
    def __init__(self):
        self.port = int(os.getenv("STREAMLIT_PORT", "8501"))
        self.host = os.getenv("STREAMLIT_HOST", "localhost")
        self.auto_reload = os.getenv("STREAMLIT_AUTO_RELOAD", "True").lower() == "true"
        self.page_title = os.getenv("PAGE_TITLE", "LoL Companion App")
        self.page_icon = os.getenv("PAGE_ICON", "⚔️")


class FeatureFlags:
    """Feature flags for enabling/disabling functionality."""
    
    def __init__(self):
        self.enable_pro_matches = os.getenv("ENABLE_PRO_MATCHES", "True").lower() == "true"
        self.enable_sentiment_analysis = os.getenv("ENABLE_SENTIMENT_ANALYSIS", "True").lower() == "true"
        self.enable_real_time_updates = os.getenv("ENABLE_REAL_TIME_UPDATES", "True").lower() == "true"
        self.enable_chatbot = os.getenv("ENABLE_CHATBOT", "True").lower() == "true"
        self.enable_live_match_tracking = os.getenv("ENABLE_LIVE_MATCH_TRACKING", "True").lower() == "true"


class LoggingConfig:
    """Configuration for application logging."""
    
    def __init__(self):
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        log_file_path = os.getenv("LOG_FILE", "./logs/app.log")
        self.log_file = Path(log_file_path) if log_file_path else None
        self.log_rotation_size = os.getenv("LOG_ROTATION_SIZE", "10MB")
        self.log_retention_days = int(os.getenv("LOG_RETENTION_DAYS", "30"))
        
        # Ensure log directory exists
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)


class ExternalServicesConfig:
    """Configuration for external services integration."""
    
    def __init__(self):
        self.twitch_client_id = os.getenv("TWITCH_CLIENT_ID")
        self.twitch_client_secret = os.getenv("TWITCH_CLIENT_SECRET")
        self.discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")


class AppConfig:
    """Main application configuration."""
    
    def __init__(self):
        self.app_name = os.getenv("APP_NAME", "LoL Companion App")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        
        # Sub-configurations
        self.riot_api = RiotAPIConfig()
        self.cache = CacheConfig()
        self.data = DataConfig()
        self.ml = MLConfig()
        self.streamlit = StreamlitConfig()
        self.features = FeatureFlags()
        self.logging = LoggingConfig()
        self.external = ExternalServicesConfig()


# Global configuration instance
config = AppConfig()


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config


def validate_config() -> List[str]:
    """
    Validate the configuration and return a list of warnings/errors.
    
    Returns:
        List of configuration issues found.
    """
    issues = []
    
    # Check if required paths exist
    if not config.data.dragontail_data_path.exists():
        issues.append(f"Dragontail data path does not exist: {config.data.dragontail_data_path}")
    
    # Check API key
    if not config.riot_api.api_key or config.riot_api.api_key == "your_riot_api_key_here":
        issues.append("Valid Riot API key is required")
    
    # Check GPU availability if requested
    if config.ml.use_gpu:
        try:
            import torch
            if not torch.cuda.is_available():
                issues.append("GPU requested but not available")
        except ImportError:
            issues.append("PyTorch not available for GPU support")
    
    return issues


if __name__ == "__main__":
    # Test configuration loading
    print("Configuration loaded successfully!")
    print(f"App: {config.app_name} v{config.app_version}")
    print(f"Debug mode: {config.debug}")
    print(f"Dragontail path: {config.data.dragontail_data_path}")
    
    # Check for issues
    issues = validate_config()
    if issues:
        print("\nConfiguration issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nConfiguration is valid!")

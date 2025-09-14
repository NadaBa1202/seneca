"""Real-time Chat Ingestion System

Async WebSocket connections with message queuing and auto-scaling
for high-throughput chat processing.
"""

from .websocket_client import WebSocketChatClient
from .message_queue import MessageQueue
from .chat_processor import ChatProcessor
from .twitch_integration import TwitchChatIntegration
from .discord_integration import DiscordChatIntegration
from .youtube_integration import YouTubeChatIntegration

__all__ = [
    'WebSocketChatClient',
    'MessageQueue', 
    'ChatProcessor',
    'TwitchChatIntegration',
    'DiscordChatIntegration',
    'YouTubeChatIntegration'
]

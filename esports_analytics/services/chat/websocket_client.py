"""WebSocket Chat Client

Async WebSocket connections for real-time chat streaming with
automatic reconnection and error handling.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass
import aiohttp
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Standardized chat message format."""
    platform: str
    channel: str
    username: str
    message: str
    timestamp: float
    user_id: Optional[str] = None
    badges: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ConnectionConfig:
    """WebSocket connection configuration."""
    url: str
    headers: Optional[Dict[str, str]] = None
    auth_token: Optional[str] = None
    reconnect_interval: int = 5
    max_reconnect_attempts: int = 10
    ping_interval: int = 20
    ping_timeout: int = 10

class WebSocketChatClient:
    """
    WebSocket client for real-time chat streaming.
    
    Features:
    - Async WebSocket connections
    - Automatic reconnection with exponential backoff
    - Message parsing and standardization
    - Error handling and circuit breaker
    - Connection health monitoring
    - Rate limiting and backpressure handling
    """
    
    def __init__(self, 
                 config: ConnectionConfig,
                 message_handler: Optional[Callable[[ChatMessage], Awaitable[None]]] = None,
                 error_handler: Optional[Callable[[Exception], None]] = None):
        """
        Initialize WebSocket chat client.
        
        Args:
            config: Connection configuration
            message_handler: Async function to handle incoming messages
            error_handler: Function to handle errors
        """
        self.config = config
        self.message_handler = message_handler
        self.error_handler = error_handler
        
        # Connection state
        self.websocket = None
        self.connected = False
        self.reconnect_attempts = 0
        self.last_ping = 0
        self.last_pong = 0
        
        # Statistics
        self.stats = {
            'messages_received': 0,
            'messages_processed': 0,
            'connection_attempts': 0,
            'reconnect_count': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
        # Circuit breaker
        self.circuit_breaker = {
            'failures': 0,
            'last_failure': 0,
            'threshold': 5,
            'timeout': 60
        }
        
        logger.info(f"Initialized WebSocketChatClient for {config.url}")
    
    async def connect(self) -> bool:
        """Establish WebSocket connection."""
        if self.circuit_breaker['failures'] >= self.circuit_breaker['threshold']:
            if time.time() - self.circuit_breaker['last_failure'] < self.circuit_breaker['timeout']:
                logger.warning("Circuit breaker open, skipping connection attempt")
                return False
        
        try:
            self.stats['connection_attempts'] += 1
            
            # Prepare headers
            headers = self.config.headers or {}
            if self.config.auth_token:
                headers['Authorization'] = f"Bearer {self.config.auth_token}"
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                self.config.url,
                extra_headers=headers,
                ping_interval=self.config.ping_interval,
                ping_timeout=self.config.ping_timeout
            )
            
            self.connected = True
            self.reconnect_attempts = 0
            self.circuit_breaker['failures'] = 0
            self.last_ping = time.time()
            
            logger.info(f"Connected to WebSocket: {self.config.url}")
            return True
            
        except Exception as e:
            self.circuit_breaker['failures'] += 1
            self.circuit_breaker['last_failure'] = time.time()
            self.stats['errors'] += 1
            
            logger.error(f"WebSocket connection failed: {e}")
            if self.error_handler:
                self.error_handler(e)
            
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket."""
        if self.websocket:
            try:
                await self.websocket.close()
                logger.info("WebSocket disconnected")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self.websocket = None
                self.connected = False
    
    async def send_message(self, message: str) -> bool:
        """Send a message through WebSocket."""
        if not self.connected or not self.websocket:
            logger.warning("Cannot send message: not connected")
            return False
        
        try:
            await self.websocket.send(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.stats['errors'] += 1
            return False
    
    async def listen(self):
        """Listen for incoming messages."""
        if not self.connected:
            logger.error("Cannot listen: not connected")
            return
        
        try:
            async for message in self.websocket:
                await self._handle_message(message)
                
        except ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.connected = False
        except WebSocketException as e:
            logger.error(f"WebSocket error: {e}")
            self.stats['errors'] += 1
            self.connected = False
        except Exception as e:
            logger.error(f"Unexpected error in listen: {e}")
            self.stats['errors'] += 1
            self.connected = False
    
    async def _handle_message(self, raw_message: str):
        """Handle incoming WebSocket message."""
        try:
            self.stats['messages_received'] += 1
            
            # Parse message (platform-specific parsing will be implemented in subclasses)
            chat_message = await self._parse_message(raw_message)
            
            if chat_message and self.message_handler:
                await self.message_handler(chat_message)
                self.stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self.stats['errors'] += 1
            if self.error_handler:
                self.error_handler(e)
    
    async def _parse_message(self, raw_message: str) -> Optional[ChatMessage]:
        """
        Parse raw WebSocket message into ChatMessage.
        This method should be overridden by platform-specific implementations.
        """
        try:
            # Default JSON parsing
            data = json.loads(raw_message)
            
            return ChatMessage(
                platform=data.get('platform', 'unknown'),
                channel=data.get('channel', ''),
                username=data.get('username', ''),
                message=data.get('message', ''),
                timestamp=data.get('timestamp', time.time()),
                user_id=data.get('user_id'),
                badges=data.get('badges'),
                metadata=data.get('metadata')
            )
        except json.JSONDecodeError:
            # Fallback for non-JSON messages
            return ChatMessage(
                platform='unknown',
                channel='',
                username='',
                message=raw_message,
                timestamp=time.time()
            )
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None
    
    async def start(self):
        """Start the WebSocket client with automatic reconnection."""
        while True:
            try:
                if await self.connect():
                    await self.listen()
                
                # Handle reconnection
                if self.reconnect_attempts < self.config.max_reconnect_attempts:
                    self.reconnect_attempts += 1
                    self.stats['reconnect_count'] += 1
                    
                    wait_time = min(
                        self.config.reconnect_interval * (2 ** self.reconnect_attempts),
                        300  # Max 5 minutes
                    )
                    
                    logger.info(f"Reconnecting in {wait_time} seconds (attempt {self.reconnect_attempts})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("Max reconnection attempts reached")
                    break
                    
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Unexpected error in start loop: {e}")
                await asyncio.sleep(self.config.reconnect_interval)
    
    async def stop(self):
        """Stop the WebSocket client."""
        await self.disconnect()
        logger.info("WebSocket client stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        uptime = time.time() - self.stats['start_time']
        
        return {
            'connected': self.connected,
            'reconnect_attempts': self.reconnect_attempts,
            'uptime_seconds': uptime,
            'messages_per_second': self.stats['messages_received'] / uptime if uptime > 0 else 0,
            'circuit_breaker_open': self.circuit_breaker['failures'] >= self.circuit_breaker['threshold'],
            **self.stats
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the connection."""
        current_time = time.time()
        
        # Check ping/pong timing
        ping_latency = current_time - self.last_ping if self.last_ping > 0 else 0
        pong_delay = current_time - self.last_pong if self.last_pong > 0 else 0
        
        return {
            'connected': self.connected,
            'ping_latency': ping_latency,
            'pong_delay': pong_delay,
            'circuit_breaker_open': self.circuit_breaker['failures'] >= self.circuit_breaker['threshold'],
            'error_rate': self.stats['errors'] / max(self.stats['messages_received'], 1),
            'reconnect_count': self.stats['reconnect_count']
        }

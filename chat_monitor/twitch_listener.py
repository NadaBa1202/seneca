"""Asynchronous Twitch chat listener using twitchio.

Responsibilities:
- Authenticate with Twitch using client ID/secret to fetch an OAuth token.
- Connect to specified channel's IRC chat.
- Listen for PRIVMSG events and push messages into an asyncio.Queue.
- Provide reconnect logic with exponential backoff.

Environment Variables (recommended):
- TWITCH_CLIENT_ID
- TWITCH_CLIENT_SECRET
- TWITCH_CHANNEL  (channel name without #)

Usage:
    queue = asyncio.Queue()
    listener = TwitchChatListener(queue, client_id, client_secret, channel)
    await listener.start()
"""
from __future__ import annotations
import asyncio
import os
import time
import logging
from typing import Optional
import aiohttp
from twitchio.ext import commands

logger = logging.getLogger(__name__)

TOKEN_URL = "https://id.twitch.tv/oauth2/token"

class OAuthToken:
    def __init__(self, access_token: str, expires_in: int):
        self.access_token = access_token
        self.expiry = time.time() + expires_in - 30  # refresh 30s early

    @property
    def expired(self) -> bool:
        return time.time() >= self.expiry

async def fetch_app_access_token(client_id: str, client_secret: str) -> OAuthToken:
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "chat:read chat:edit",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(TOKEN_URL, data=data, timeout=30) as resp:
            resp.raise_for_status()
            js = await resp.json()
            return OAuthToken(js["access_token"], js["expires_in"])

class TwitchChatListener(commands.Bot):
    def __init__(
        self,
        message_queue: asyncio.Queue,
        client_id: str,
        client_secret: str,
        channel: str,
        initial_backoff: float = 2.0,
        max_backoff: float = 60.0,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._channel_name = channel.lstrip('#')
        self._token: Optional[OAuthToken] = None
        self._message_queue = message_queue
        self._initial_backoff = initial_backoff
        self._max_backoff = max_backoff
        self._ready_event = asyncio.Event()
        # Dummy token initially; will be refreshed before connect
        super().__init__(
            token="invalid",  # placeholder
            prefix="!",
            initial_channels=[self._channel_name],
        )

    async def ensure_token(self):
        if self._token is None or self._token.expired:
            self._token = await fetch_app_access_token(self._client_id, self._client_secret)
            # monkey patch token attribute used by twitchio
            self._http.token = self._token.access_token
            logger.info("Obtained new Twitch app token")

    async def event_ready(self):  # type: ignore
        logger.info(f"Connected to Twitch chat as {self.nick}")
        self._ready_event.set()

    async def event_message(self, message):  # type: ignore
        # Avoid bot's own messages
        if message.echo:
            return
        payload = {
            "user": message.author.name,
            "text": message.content,
            "timestamp": time.time(),
        }
        try:
            self._message_queue.put_nowait(payload)
        except asyncio.QueueFull:
            logger.warning("Message queue full; dropping message")

    async def connect_and_run(self):
        backoff = self._initial_backoff
        while True:
            try:
                await self.ensure_token()
                await self._ws._connect()  # internal connect
                await self._ready_event.wait()
                backoff = self._initial_backoff
                # Run the websocket until it closes
                await self._ws._listen()
            except Exception as e:  # noqa
                logger.exception("Twitch listener error: %s", e)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, self._max_backoff)
                self._ready_event.clear()
            finally:
                # Force token refresh next loop if near expiry
                if self._token and self._token.expired:
                    self._token = None

    async def start_background(self):
        asyncio.create_task(self.connect_and_run(), name="twitch-listener")

# Convenience factory
async def build_and_start_listener(queue: asyncio.Queue) -> TwitchChatListener:
    cid = os.getenv("TWITCH_CLIENT_ID", "")
    secret = os.getenv("TWITCH_CLIENT_SECRET", "")
    channel = os.getenv("TWITCH_CHANNEL", "")
    if not all([cid, secret, channel]):
        raise RuntimeError("Missing one of TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, TWITCH_CHANNEL env vars")
    listener = TwitchChatListener(queue, cid, secret, channel)
    await listener.start_background()
    return listener

"""Background task pulling raw Twitch messages -> NLP analysis -> processed queue."""
from __future__ import annotations
import asyncio
from typing import Any, Dict
from .nlp import analyze_message, load_models
from .models import ChatAnalysis

class MessageProcessor:
    def __init__(self, raw_queue: asyncio.Queue, processed_queue: asyncio.Queue):
        self.raw_queue = raw_queue
        self.processed_queue = processed_queue
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    async def start(self):
        await load_models()
        self._task = asyncio.create_task(self._run(), name="message-processor")

    async def stop(self):
        self._stop_event.set()
        if self._task:
            await self._task

    async def _run(self):
        while not self._stop_event.is_set():
            try:
                raw: Dict[str, Any] = await self.raw_queue.get()
            except asyncio.CancelledError:
                break
            text = raw.get("text", "")
            try:
                analysis = await analyze_message(text)
                record = ChatAnalysis(
                    user=raw.get("user", "unknown"),
                    text=text,
                    timestamp=raw.get("timestamp"),
                    sentiment=analysis["sentiment"],
                    compound=analysis["compound"],
                    pos=analysis["pos"],
                    neu=analysis["neu"],
                    neg=analysis["neg"],
                    toxicity_scores=analysis["toxicity_scores"],
                    is_toxic=analysis["is_toxic"],
                )
                try:
                    self.processed_queue.put_nowait(record)
                except asyncio.QueueFull:
                    # drop if full
                    pass
            except Exception:
                # Could log here
                continue

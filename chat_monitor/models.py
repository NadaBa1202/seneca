from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict
import time

class ChatAnalysis(BaseModel):
    user: str
    text: str
    timestamp: float = Field(default_factory=lambda: time.time())
    sentiment: str
    compound: float
    pos: float
    neu: float
    neg: float
    toxicity_scores: Dict[str, float]
    is_toxic: bool

    def csv_row(self):
        base = {
            "user": self.user,
            "text": self.text,
            "timestamp": self.timestamp,
            "sentiment": self.sentiment,
            "compound": self.compound,
            "pos": self.pos,
            "neu": self.neu,
            "neg": self.neg,
            "is_toxic": self.is_toxic,
        }
        base.update({f"tox_{k}": v for k, v in self.toxicity_scores.items()})
        return base

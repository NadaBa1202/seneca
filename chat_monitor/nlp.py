"""NLP processing utilities: sentiment (VADER) + toxicity (Detoxify).
Separates heavy model loading with caching helpers.
"""
from __future__ import annotations
import asyncio
from typing import Dict, Any
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from detoxify import Detoxify

_vader: SentimentIntensityAnalyzer | None = None
_detox: Detoxify | None = None
_detox_model_type: str | None = None
_lock = asyncio.Lock()

VALID_DETOX_MODELS = [
    "original-small",
    "unbiased-small",
    "original",
    "unbiased",
    "multilingual",
]

async def load_models() -> None:
    global _vader, _detox, _detox_model_type
    async with _lock:
        if _vader is None:
            nltk.download("vader_lexicon", quiet=True)
            _vader = SentimentIntensityAnalyzer()
        if _detox is None:
            last_err: Exception | None = None
            for mt in VALID_DETOX_MODELS:
                try:
                    _detox = Detoxify(model_type=mt)
                    _detox_model_type = mt
                    break
                except Exception as e:  # noqa
                    last_err = e
            if _detox is None:
                # Create dummy model
                class Dummy:
                    model_type = "dummy"
                    _error = str(last_err)
                    def predict(self, text):
                        dims = ["toxicity", "severe_toxicity", "insult", "identity_attack", "threat", "obscene"]
                        if isinstance(text, str):
                            return {d: 0.0 for d in dims}
                        else:
                            return {d: [0.0 for _ in text] for d in dims}
                _detox = Dummy()  # type: ignore
                _detox_model_type = "dummy"

async def analyze_message(text: str) -> Dict[str, Any]:
    if _vader is None or _detox is None:
        await load_models()
    assert _vader is not None and _detox is not None
    scores = _vader.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        sentiment = "positive"
    elif compound <= -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    tox_scores = _detox.predict([text])
    toxic_dims = ["toxicity", "severe_toxicity", "insult", "identity_attack", "threat", "obscene"]
    is_toxic = any(tox_scores.get(dim, [0.0])[0] >= 0.5 for dim in toxic_dims if dim in tox_scores)
    return {
        "sentiment": sentiment,
        "compound": compound,
        "pos": scores["pos"],
        "neu": scores["neu"],
        "neg": scores["neg"],
        "toxicity_scores": {d: tox_scores.get(d, [0.0])[0] for d in toxic_dims},
        "is_toxic": is_toxic,
        "detox_model": _detox_model_type,
    }

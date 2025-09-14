"""
NLP components for League of Legends Companion App.

This module provides AI-powered natural language processing capabilities including
question answering, summarization, sentiment analysis, and match event explanation.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from pathlib import Path
import torch
from transformers import (
    AutoTokenizer, AutoModelForQuestionAnswering, AutoModelForSequenceClassification,
    AutoModelForSeq2SeqLM, BertTokenizer, BertForQuestionAnswering,
    RobertaTokenizer, RobertaForSequenceClassification,
    T5Tokenizer, T5ForConditionalGeneration, pipeline
)
import numpy as np
from functools import lru_cache
import json

from ..config import get_config
from ..models import QuestionAnswerPair, MatchSummary, SentimentAnalysis, MatchEvent, Champion
from ..data.dragontail import get_dragontail_manager

logger = logging.getLogger(__name__)
config = get_config()


class ModelManager:
    """Manages loading and caching of transformer models."""
    
    def __init__(self):
        self.device = "cuda" if config.ml.use_gpu and torch.cuda.is_available() else "cpu"
        self.cache_dir = config.data.huggingface_cache_dir
        self.models: Dict[str, Any] = {}
        self.tokenizers: Dict[str, Any] = {}
        
        logger.info(f"ModelManager initialized with device: {self.device}")
    
    async def load_model(self, model_name: str, task: str) -> Tuple[Any, Any]:
        """
        Load a model and tokenizer for a specific task.
        
        Args:
            model_name: HuggingFace model name
            task: Task type (qa, sentiment, summarization)
            
        Returns:
            Tuple of (model, tokenizer)
        """
        cache_key = f"{model_name}_{task}"
        
        if cache_key in self.models:
            return self.models[cache_key], self.tokenizers[cache_key]
        
        logger.info(f"Loading model {model_name} for task {task}")
        
        try:
            if task == "qa":
                tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=self.cache_dir)
                model = AutoModelForQuestionAnswering.from_pretrained(model_name, cache_dir=self.cache_dir)
            elif task == "sentiment":
                tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=self.cache_dir)
                model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=self.cache_dir)
            elif task == "summarization":
                tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=self.cache_dir)
                model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=self.cache_dir)
            else:
                raise ValueError(f"Unsupported task: {task}")
            
            model.to(self.device)
            model.eval()
            
            self.models[cache_key] = model
            self.tokenizers[cache_key] = tokenizer
            
            logger.info(f"Successfully loaded {model_name}")
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise


class QuestionAnsweringEngine:
    """
    Question answering engine for League of Legends queries.
    
    Uses fine-tuned BERT/RoBERTa models to answer questions about champions,
    items, strategies, and game mechanics.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.dragontail = get_dragontail_manager()
        self._context_cache: Dict[str, str] = {}
        
    async def answer_question(
        self, 
        question: str, 
        context: Optional[str] = None,
        confidence_threshold: float = 0.5
    ) -> QuestionAnswerPair:
        """
        Answer a question about League of Legends.
        
        Args:
            question: The question to answer
            context: Optional context for the question
            confidence_threshold: Minimum confidence for answers
            
        Returns:
            QuestionAnswerPair with answer and confidence
        """
        try:
            # Get context if not provided
            if context is None:
                context = await self._get_context_for_question(question)
            
            # Load Q&A model
            model, tokenizer = await self.model_manager.load_model(config.ml.qa_model_name, "qa")
            
            # Tokenize input
            inputs = tokenizer(
                question, 
                context,
                return_tensors="pt",
                max_length=config.ml.max_sequence_length,
                truncation=True,
                padding=True
            ).to(self.model_manager.device)
            
            # Get model predictions
            with torch.no_grad():
                outputs = model(**inputs)
                start_logits = outputs.start_logits
                end_logits = outputs.end_logits
                
                # Get the most likely answer span
                start_idx = torch.argmax(start_logits)
                end_idx = torch.argmax(end_logits)
                
                # Calculate confidence
                start_prob = torch.softmax(start_logits, dim=-1).max().item()
                end_prob = torch.softmax(end_logits, dim=-1).max().item()
                confidence = (start_prob + end_prob) / 2
                
                # Extract answer
                if start_idx <= end_idx and confidence >= confidence_threshold:
                    answer_tokens = inputs["input_ids"][0][start_idx:end_idx+1]
                    answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)
                else:
                    answer = "I'm not confident enough to answer that question."
                    confidence = 0.0
            
            return QuestionAnswerPair(
                question=question,
                answer=answer,
                confidence=confidence,
                context=context[:500] + "..." if len(context) > 500 else context,
                sources=["Dragontail Data", "Champion Information"]
            )
            
        except Exception as e:
            logger.error(f"Error in question answering: {e}")
            return QuestionAnswerPair(
                question=question,
                answer="Sorry, I encountered an error while trying to answer your question.",
                confidence=0.0,
                context=context
            )
    
    async def _get_context_for_question(self, question: str) -> str:
        """
        Get relevant context for a question by searching game data.
        
        Args:
            question: The question to find context for
            
        Returns:
            Relevant context string
        """
        question_lower = question.lower()
        context_parts = []
        
        # Check if question is about a specific champion
        champions = await self.dragontail.load_champions()
        for champion_name, champion in champions.items():
            if champion_name.lower() in question_lower or champion.name.lower() in question_lower:
                context_parts.append(self._champion_to_context(champion))
                break
        
        # Check if question is about items
        if any(word in question_lower for word in ["item", "build", "equipment"]):
            items = await self.dragontail.search_items(question)
            for item in items[:3]:  # Limit to top 3 items
                context_parts.append(f"{item.name}: {item.description}")
        
        # Add general game knowledge if no specific context found
        if not context_parts:
            context_parts.append(self._get_general_game_context())
        
        return " ".join(context_parts)
    
    def _champion_to_context(self, champion: Champion) -> str:
        """Convert champion data to context string."""
        context = f"{champion.name}, {champion.title}. {champion.blurb} "
        context += f"Role: {', '.join(champion.tags)}. "
        
        # Add ability information
        for spell in champion.spells:
            context += f"{spell.name}: {spell.description} "
        
        # Add passive
        context += f"Passive - {champion.passive.name}: {champion.passive.description} "
        
        # Add tips
        if champion.ally_tips:
            context += f"Tips: {' '.join(champion.ally_tips[:2])} "
        
        return context
    
    def _get_general_game_context(self) -> str:
        """Get general League of Legends game context."""
        return """
        League of Legends is a multiplayer online battle arena (MOBA) game.
        Players control champions with unique abilities and work in teams to destroy the enemy Nexus.
        The game features items, runes, summoner spells, and various game modes.
        Champions have different roles: ADC (Attack Damage Carry), Support, Mid, Top, and Jungle.
        """


class SummarizationEngine:
    """
    Summarization engine for match events and game analysis.
    
    Uses T5/BART models to generate concise summaries of matches,
    key events, and strategic explanations.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
    
    async def summarize_match(
        self,
        match_events: List[MatchEvent],
        participants: List[Any],
        max_length: int = 150
    ) -> MatchSummary:
        """
        Generate a summary of a match based on events and participants.
        
        Args:
            match_events: List of match events
            participants: List of match participants
            max_length: Maximum summary length
            
        Returns:
            MatchSummary object
        """
        try:
            # Create text description of the match
            match_text = self._events_to_text(match_events, participants)
            
            # Load summarization model
            model, tokenizer = await self.model_manager.load_model(
                config.ml.summarization_model_name, 
                "summarization"
            )
            
            # Generate summary
            inputs = tokenizer(
                f"summarize: {match_text}",
                return_tensors="pt",
                max_length=config.ml.max_sequence_length,
                truncation=True
            ).to(self.model_manager.device)
            
            with torch.no_grad():
                summary_ids = model.generate(
                    inputs["input_ids"],
                    max_length=max_length,
                    min_length=30,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True
                )
            
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            # Extract key events
            key_events = self._extract_key_events(match_events)
            
            return MatchSummary(
                match_id="",  # Would be set by caller
                summary=summary,
                key_events=key_events,
                turning_points=self._identify_turning_points(match_events)
            )
            
        except Exception as e:
            logger.error(f"Error in match summarization: {e}")
            return MatchSummary(
                match_id="",
                summary="Unable to generate match summary due to an error.",
                key_events=[]
            )
    
    def _events_to_text(self, events: List[MatchEvent], participants: List[Any]) -> str:
        """Convert match events to descriptive text."""
        text_parts = []
        
        for event in events[:20]:  # Limit to first 20 events for context
            timestamp_min = event.timestamp // 60000  # Convert to minutes
            
            if event.event_type == "CHAMPION_KILL":
                text_parts.append(f"At {timestamp_min} minutes, a champion was killed.")
            elif event.event_type == "DRAGON_KILL":
                text_parts.append(f"At {timestamp_min} minutes, dragon was taken.")
            elif event.event_type == "BARON_KILL":
                text_parts.append(f"At {timestamp_min} minutes, Baron was secured.")
            elif event.event_type == "BUILDING_KILL":
                text_parts.append(f"At {timestamp_min} minutes, a structure was destroyed.")
        
        return " ".join(text_parts)
    
    def _extract_key_events(self, events: List[MatchEvent]) -> List[str]:
        """Extract the most important events from a match."""
        key_events = []
        
        for event in events:
            if event.event_type in ["FIRST_BLOOD", "BARON_KILL", "DRAGON_KILL", "ACE"]:
                timestamp_min = event.timestamp // 60000
                key_events.append(f"{event.event_type.replace('_', ' ').title()} at {timestamp_min}:00")
        
        return key_events[:10]  # Return top 10 key events
    
    def _identify_turning_points(self, events: List[MatchEvent]) -> List[Dict[str, Any]]:
        """Identify major turning points in the match."""
        turning_points = []
        
        # Simple heuristic: Baron kills and Aces are major turning points
        for event in events:
            if event.event_type in ["BARON_KILL", "ACE"]:
                turning_points.append({
                    "timestamp": event.timestamp,
                    "event": event.event_type,
                    "impact": "high"
                })
        
        return turning_points


class SentimentAnalysisEngine:
    """
    Sentiment analysis engine for chat and social media content.
    
    Analyzes sentiment of Twitch chat, social media posts, and community content
    related to matches and players.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
    
    async def analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """
        Analyze sentiment of given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentAnalysis object with sentiment and confidence
        """
        try:
            # Load sentiment model
            model, tokenizer = await self.model_manager.load_model(
                config.ml.sentiment_model_name,
                "sentiment"
            )
            
            # Tokenize input
            inputs = tokenizer(
                text,
                return_tensors="pt",
                max_length=config.ml.max_sequence_length,
                truncation=True,
                padding=True
            ).to(self.model_manager.device)
            
            # Get predictions
            with torch.no_grad():
                outputs = model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
                # Get sentiment label and confidence
                predicted_class = torch.argmax(predictions, dim=-1).item()
                confidence = predictions.max().item()
                
                # Map class to sentiment (assuming standard 3-class sentiment)
                sentiment_map = {0: "negative", 1: "neutral", 2: "positive"}
                sentiment = sentiment_map.get(predicted_class, "neutral")
            
            return SentimentAnalysis(
                text=text,
                sentiment=sentiment,
                confidence=confidence,
                emotions={}  # Could be expanded with emotion detection
            )
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return SentimentAnalysis(
                text=text,
                sentiment="neutral",
                confidence=0.0
            )
    
    async def analyze_chat_stream(self, messages: List[str]) -> Dict[str, Any]:
        """
        Analyze sentiment of multiple chat messages.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Aggregated sentiment analysis
        """
        sentiments = []
        
        for message in messages:
            sentiment = await self.analyze_sentiment(message)
            sentiments.append(sentiment)
        
        # Aggregate results
        positive_count = sum(1 for s in sentiments if s.sentiment == "positive")
        negative_count = sum(1 for s in sentiments if s.sentiment == "negative")
        neutral_count = sum(1 for s in sentiments if s.sentiment == "neutral")
        
        total = len(sentiments)
        
        return {
            "total_messages": total,
            "positive_percentage": positive_count / total * 100 if total > 0 else 0,
            "negative_percentage": negative_count / total * 100 if total > 0 else 0,
            "neutral_percentage": neutral_count / total * 100 if total > 0 else 0,
            "overall_sentiment": max(
                [("positive", positive_count), ("negative", negative_count), ("neutral", neutral_count)],
                key=lambda x: x[1]
            )[0],
            "individual_analyses": sentiments
        }


class NLPPipeline:
    """
    Main NLP pipeline that coordinates all NLP components.
    
    Provides a unified interface for all natural language processing
    capabilities in the application.
    """
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.qa_engine = QuestionAnsweringEngine(self.model_manager)
        self.summarization_engine = SummarizationEngine(self.model_manager)
        self.sentiment_engine = SentimentAnalysisEngine(self.model_manager)
        
        logger.info("NLP Pipeline initialized")
    
    async def initialize(self):
        """Initialize all models and components."""
        logger.info("Initializing NLP Pipeline...")
        
        # Preload commonly used models
        await asyncio.gather(
            self.model_manager.load_model(config.ml.qa_model_name, "qa"),
            self.model_manager.load_model(config.ml.sentiment_model_name, "sentiment"),
            return_exceptions=True
        )
        
        logger.info("NLP Pipeline initialization complete")
    
    async def process_user_question(self, question: str, context: Optional[str] = None) -> QuestionAnswerPair:
        """Process a user question and return an answer."""
        return await self.qa_engine.answer_question(question, context)
    
    async def generate_match_summary(
        self, 
        match_events: List[MatchEvent], 
        participants: List[Any]
    ) -> MatchSummary:
        """Generate a summary of a match."""
        return await self.summarization_engine.summarize_match(match_events, participants)
    
    async def analyze_text_sentiment(self, text: str) -> SentimentAnalysis:
        """Analyze sentiment of text."""
        return await self.sentiment_engine.analyze_sentiment(text)
    
    async def process_chat_stream(self, messages: List[str]) -> Dict[str, Any]:
        """Process and analyze a stream of chat messages."""
        return await self.sentiment_engine.analyze_chat_stream(messages)


# Global NLP pipeline instance
_nlp_pipeline: Optional[NLPPipeline] = None


async def get_nlp_pipeline() -> NLPPipeline:
    """Get the global NLP pipeline instance."""
    global _nlp_pipeline
    if _nlp_pipeline is None:
        _nlp_pipeline = NLPPipeline()
        await _nlp_pipeline.initialize()
    return _nlp_pipeline


# Utility functions for LoL-specific NLP tasks
async def explain_champion_ability(champion_name: str, ability_name: str) -> str:
    """
    Generate an explanation of a champion ability.
    
    Args:
        champion_name: Name of the champion
        ability_name: Name of the ability
        
    Returns:
        Human-readable explanation of the ability
    """
    dragontail = get_dragontail_manager()
    champion = await dragontail.get_champion_by_name(champion_name)
    
    if not champion:
        return f"Champion '{champion_name}' not found."
    
    # Find the ability
    ability = None
    if ability_name.lower() == "passive":
        ability = champion.passive
        return f"{champion.name}'s passive '{ability.name}': {ability.description}"
    else:
        for spell in champion.spells:
            if spell.name.lower() == ability_name.lower() or spell.id.lower() == ability_name.lower():
                ability = spell
                break
    
    if not ability:
        return f"Ability '{ability_name}' not found for {champion_name}."
    
    explanation = f"{champion.name}'s {ability.name}: {ability.description}"
    if hasattr(ability, 'cooldown') and ability.cooldown:
        explanation += f" Cooldown: {ability.cooldown[0]}-{ability.cooldown[-1]} seconds."
    
    return explanation


async def get_champion_tips(champion_name: str, tip_type: str = "both") -> Dict[str, List[str]]:
    """
    Get playing tips for a champion.
    
    Args:
        champion_name: Name of the champion
        tip_type: 'ally', 'enemy', or 'both'
        
    Returns:
        Dictionary with ally and/or enemy tips
    """
    dragontail = get_dragontail_manager()
    champion = await dragontail.get_champion_by_name(champion_name)
    
    if not champion:
        return {"error": [f"Champion '{champion_name}' not found."]}
    
    tips = {}
    if tip_type in ["ally", "both"]:
        tips["ally_tips"] = champion.ally_tips
    if tip_type in ["enemy", "both"]:
        tips["enemy_tips"] = champion.enemy_tips
    
    return tips


if __name__ == "__main__":
    async def main():
        # Test the NLP pipeline
        pipeline = await get_nlp_pipeline()
        
        # Test question answering
        qa_result = await pipeline.process_user_question("What does Aatrox's passive do?")
        print(f"Q&A Result: {qa_result.answer} (confidence: {qa_result.confidence:.2f})")
        
        # Test sentiment analysis
        sentiment_result = await pipeline.analyze_text_sentiment("This match is amazing!")
        print(f"Sentiment: {sentiment_result.sentiment} (confidence: {sentiment_result.confidence:.2f})")
        
        # Test champion explanation
        ability_explanation = await explain_champion_ability("Aatrox", "passive")
        print(f"Ability explanation: {ability_explanation}")
    
    asyncio.run(main())

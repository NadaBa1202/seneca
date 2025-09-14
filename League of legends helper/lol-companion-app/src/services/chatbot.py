"""
Advanced chatbot service for League of Legends companion app.

This module provides an intelligent chatbot that can answer questions about
champions, items, strategies, match analysis, and provide personalized advice
using NLP models and game data integration.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
import re

from ..config import get_config
from ..models import Champion, Item, QuestionAnswerPair, MatchEvent
from ..data.dragontail import get_dragontail_manager
from ..nlp import get_nlp_pipeline
from ..services.analytics import get_match_analyzer
from ..services.event_detection import get_event_service

logger = logging.getLogger(__name__)
config = get_config()


class QueryType(Enum):
    """Types of user queries."""
    CHAMPION_INFO = "champion_info"
    ITEM_BUILD = "item_build"
    STRATEGY = "strategy"
    MATCH_ANALYSIS = "match_analysis"
    COUNTERPICK = "counterpick"
    META_QUESTION = "meta_question"
    GENERAL_HELP = "general_help"
    UNKNOWN = "unknown"


class ContextType(Enum):
    """Types of conversation context."""
    CHAMPION_DISCUSSION = "champion_discussion"
    BUILD_DISCUSSION = "build_discussion"
    MATCH_DISCUSSION = "match_discussion"
    GENERAL_CHAT = "general_chat"


@dataclass
class ChatContext:
    """Context for ongoing conversation."""
    context_type: ContextType
    current_champion: Optional[str] = None
    current_role: Optional[str] = None
    current_match: Optional[str] = None
    recent_topics: List[str] = None
    user_preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.recent_topics is None:
            self.recent_topics = []
        if self.user_preferences is None:
            self.user_preferences = {}


@dataclass
class ChatResponse:
    """Response from the chatbot."""
    message: str
    confidence: float
    query_type: QueryType
    context: ChatContext
    suggestions: List[str]
    related_info: Dict[str, Any]
    follow_up_questions: List[str]


class QueryClassifier:
    """Classifies user queries into different types."""
    
    def __init__(self):
        self.dragontail = get_dragontail_manager()
        
        # Keywords for different query types
        self.champion_keywords = [
            "champion", "champ", "hero", "character", "abilities", "skills",
            "passive", "q", "w", "e", "r", "ultimate", "combo"
        ]
        
        self.item_keywords = [
            "item", "items", "build", "builds", "equipment", "gear",
            "core", "situational", "recommended", "optimal"
        ]
        
        self.strategy_keywords = [
            "strategy", "tactics", "tips", "advice", "how to", "guide",
            "playstyle", "positioning", "macro", "micro"
        ]
        
        self.match_keywords = [
            "match", "game", "analysis", "performance", "stats",
            "kda", "damage", "teamfight", "objective"
        ]
        
        self.counter_keywords = [
            "counter", "counters", "weak against", "strong against",
            "bad matchup", "good matchup", "beats", "loses to"
        ]
        
        self.meta_keywords = [
            "meta", "tier list", "op", "broken", "nerfed", "buffed",
            "current", "patch", "strongest", "weakest"
        ]
    
    async def classify_query(self, query: str, context: ChatContext) -> QueryType:
        """
        Classify a user query into a specific type.
        
        Args:
            query: User's question/query
            context: Current conversation context
            
        Returns:
            QueryType enum value
        """
        query_lower = query.lower()
        
        # Check for champion-related queries
        if any(keyword in query_lower for keyword in self.champion_keywords):
            return QueryType.CHAMPION_INFO
        
        # Check for item/build queries
        if any(keyword in query_lower for keyword in self.item_keywords):
            return QueryType.ITEM_BUILD
        
        # Check for strategy queries
        if any(keyword in query_lower for keyword in self.strategy_keywords):
            return QueryType.STRATEGY
        
        # Check for match analysis queries
        if any(keyword in query_lower for keyword in self.match_keywords):
            return QueryType.MATCH_ANALYSIS
        
        # Check for counterpick queries
        if any(keyword in query_lower for keyword in self.counter_keywords):
            return QueryType.COUNTERPICK
        
        # Check for meta queries
        if any(keyword in query_lower for keyword in self.meta_keywords):
            return QueryType.META_QUESTION
        
        return QueryType.UNKNOWN


class ChampionQueryHandler:
    """Handles champion-related queries."""
    
    def __init__(self):
        self.dragontail = get_dragontail_manager()
        self.nlp = None
    
    async def initialize(self):
        """Initialize the handler."""
        self.nlp = await get_nlp_pipeline()
    
    async def handle_query(self, query: str, context: ChatContext) -> ChatResponse:
        """Handle champion-related queries."""
        # Extract champion name from query
        champion_name = self._extract_champion_name(query)
        
        if not champion_name:
            return ChatResponse(
                message="I'd be happy to help with champion information! Could you specify which champion you're asking about?",
                confidence=0.0,
                query_type=QueryType.CHAMPION_INFO,
                context=context,
                suggestions=["Popular champions: Aatrox", "Jinx", "Thresh", "Yasuo", "Ahri"],
                related_info={},
                follow_up_questions=["Which champion would you like to know about?"]
            )
        
        # Get champion data
        champion = await self.dragontail.get_champion_by_name(champion_name)
        
        if not champion:
            return ChatResponse(
                message=f"I couldn't find information about '{champion_name}'. Could you check the spelling?",
                confidence=0.0,
                query_type=QueryType.CHAMPION_INFO,
                context=context,
                suggestions=["Try searching for: Aatrox", "Jinx", "Thresh", "Yasuo", "Ahri"],
                related_info={},
                follow_up_questions=["Which champion were you looking for?"]
            )
        
        # Generate response based on query type
        if "ability" in query.lower() or "skill" in query.lower():
            return await self._handle_ability_query(champion, query, context)
        elif "build" in query.lower() or "item" in query.lower():
            return await self._handle_build_query(champion, query, context)
        elif "tip" in query.lower() or "advice" in query.lower():
            return await self._handle_tips_query(champion, query, context)
        else:
            return await self._handle_general_champion_query(champion, query, context)
    
    def _extract_champion_name(self, query: str) -> Optional[str]:
        """Extract champion name from query."""
        # Load champions for name matching
        champions = asyncio.run(self.dragontail.load_champions())
        champion_names = list(champions.keys())
        
        query_lower = query.lower()
        
        # Direct name match
        for name in champion_names:
            if name.lower() in query_lower:
                return name
        
        # Check for common aliases
        aliases = {
            "k6": "Kha'Zix",
            "kha": "Kha'Zix",
            "khazix": "Kha'Zix",
            "yi": "Master Yi",
            "master": "Master Yi",
            "trynd": "Tryndamere",
            "trynda": "Tryndamere",
            "kat": "Katarina",
            "kata": "Katarina",
            "ez": "Ezreal",
            "ezreal": "Ezreal"
        }
        
        for alias, full_name in aliases.items():
            if alias in query_lower:
                return full_name
        
        return None
    
    async def _handle_ability_query(self, champion: Champion, query: str, context: ChatContext) -> ChatResponse:
        """Handle ability-specific queries."""
        query_lower = query.lower()
        
        # Check for specific ability
        ability_info = ""
        if "passive" in query_lower:
            ability_info = f"**{champion.passive.name}**: {champion.passive.description}"
        elif "q" in query_lower and len(query_lower) <= 10:  # Avoid matching "question"
            if champion.spells:
                ability_info = f"**{champion.spells[0].name}**: {champion.spells[0].description}"
        elif "w" in query_lower:
            if len(champion.spells) > 1:
                ability_info = f"**{champion.spells[1].name}**: {champion.spells[1].description}"
        elif "e" in query_lower:
            if len(champion.spells) > 2:
                ability_info = f"**{champion.spells[2].name}**: {champion.spells[2].description}"
        elif "r" in query_lower or "ultimate" in query_lower:
            if len(champion.spells) > 3:
                ability_info = f"**{champion.spells[3].name}**: {champion.spells[3].description}"
        
        if ability_info:
            message = f"Here's information about {champion.name}'s ability:\n\n{ability_info}"
            suggestions = [f"{champion.name} tips", f"{champion.name} build", f"{champion.name} counters"]
        else:
            # Show all abilities
            abilities_text = f"**{champion.passive.name}** (Passive): {champion.passive.description}\n\n"
            for i, spell in enumerate(champion.spells):
                abilities_text += f"**{spell.name}**: {spell.description}\n\n"
            
            message = f"Here are all of {champion.name}'s abilities:\n\n{abilities_text}"
            suggestions = [f"{champion.name} tips", f"{champion.name} build", f"{champion.name} counters"]
        
        return ChatResponse(
            message=message,
            confidence=0.9,
            query_type=QueryType.CHAMPION_INFO,
            context=ChatContext(
                context_type=ContextType.CHAMPION_DISCUSSION,
                current_champion=champion.name,
                recent_topics=[champion.name, "abilities"]
            ),
            suggestions=suggestions,
            related_info={"champion": champion.name, "abilities": len(champion.spells)},
            follow_up_questions=[
                f"What are some tips for playing {champion.name}?",
                f"What items should I build on {champion.name}?",
                f"Who counters {champion.name}?"
            ]
        )
    
    async def _handle_build_query(self, champion: Champion, query: str, context: ChatContext) -> ChatResponse:
        """Handle build-related queries."""
        # This would integrate with item recommendation system
        message = f"Here are some recommended builds for {champion.name}:\n\n"
        message += "**Core Items:**\n"
        message += "• Item recommendations would be generated based on champion stats and role\n\n"
        message += "**Situational Items:**\n"
        message += "• Adapt your build based on enemy team composition\n\n"
        message += "**Tips:**\n"
        message += "• Consider your team's needs and enemy threats\n"
        message += "• Build defensively if behind, offensively if ahead"
        
        return ChatResponse(
            message=message,
            confidence=0.8,
            query_type=QueryType.ITEM_BUILD,
            context=ChatContext(
                context_type=ContextType.BUILD_DISCUSSION,
                current_champion=champion.name,
                recent_topics=[champion.name, "build"]
            ),
            suggestions=[f"{champion.name} abilities", f"{champion.name} tips", f"{champion.name} counters"],
            related_info={"champion": champion.name, "role": champion.tags[0] if champion.tags else "Unknown"},
            follow_up_questions=[
                f"What are {champion.name}'s core abilities?",
                f"How should I play {champion.name} in teamfights?",
                f"What runes work well with {champion.name}?"
            ]
        )
    
    async def _handle_tips_query(self, champion: Champion, query: str, context: ChatContext) -> ChatResponse:
        """Handle tips and advice queries."""
        tips_text = f"Here are some tips for playing {champion.name}:\n\n"
        
        if champion.ally_tips:
            tips_text += "**Playing as {champion.name}:**\n"
            for tip in champion.ally_tips[:3]:  # Show top 3 tips
                tips_text += f"• {tip}\n"
            tips_text += "\n"
        
        if champion.enemy_tips:
            tips_text += "**Playing against {champion.name}:**\n"
            for tip in champion.enemy_tips[:3]:  # Show top 3 tips
                tips_text += f"• {tip}\n"
        
        return ChatResponse(
            message=tips_text,
            confidence=0.9,
            query_type=QueryType.STRATEGY,
            context=ChatContext(
                context_type=ContextType.CHAMPION_DISCUSSION,
                current_champion=champion.name,
                recent_topics=[champion.name, "tips"]
            ),
            suggestions=[f"{champion.name} build", f"{champion.name} abilities", f"{champion.name} counters"],
            related_info={"champion": champion.name, "tips_count": len(champion.ally_tips) + len(champion.enemy_tips)},
            follow_up_questions=[
                f"What items should I build on {champion.name}?",
                f"How do I counter {champion.name}?",
                f"What are {champion.name}'s key abilities?"
            ]
        )
    
    async def _handle_general_champion_query(self, champion: Champion, query: str, context: ChatContext) -> ChatResponse:
        """Handle general champion information queries."""
        message = f"**{champion.name} - {champion.title}**\n\n"
        message += f"{champion.blurb}\n\n"
        message += f"**Role:** {', '.join(champion.tags)}\n"
        message += f"**Resource:** {champion.partype}\n\n"
        message += f"**Passive:** {champion.passive.name}\n"
        message += f"{champion.passive.description}\n\n"
        message += "Would you like to know more about their abilities, builds, or tips?"
        
        return ChatResponse(
            message=message,
            confidence=0.9,
            query_type=QueryType.CHAMPION_INFO,
            context=ChatContext(
                context_type=ContextType.CHAMPION_DISCUSSION,
                current_champion=champion.name,
                recent_topics=[champion.name]
            ),
            suggestions=[f"{champion.name} abilities", f"{champion.name} build", f"{champion.name} tips"],
            related_info={"champion": champion.name, "role": champion.tags[0] if champion.tags else "Unknown"},
            follow_up_questions=[
                f"What are {champion.name}'s abilities?",
                f"What items should I build on {champion.name}?",
                f"How do I play {champion.name} effectively?"
            ]
        )


class StrategyQueryHandler:
    """Handles strategy and gameplay queries."""
    
    def __init__(self):
        self.nlp = None
    
    async def initialize(self):
        """Initialize the handler."""
        self.nlp = await get_nlp_pipeline()
    
    async def handle_query(self, query: str, context: ChatContext) -> ChatResponse:
        """Handle strategy-related queries."""
        query_lower = query.lower()
        
        if "macro" in query_lower:
            return self._handle_macro_query(query, context)
        elif "micro" in query_lower:
            return self._handle_micro_query(query, context)
        elif "teamfight" in query_lower:
            return self._handle_teamfight_query(query, context)
        elif "positioning" in query_lower:
            return self._handle_positioning_query(query, context)
        else:
            return self._handle_general_strategy_query(query, context)
    
    def _handle_macro_query(self, query: str, context: ChatContext) -> ChatResponse:
        """Handle macro strategy queries."""
        message = "**Macro Strategy Tips:**\n\n"
        message += "• **Map Control**: Ward key areas and control vision\n"
        message += "• **Objective Priority**: Focus on dragons, Baron, and towers\n"
        message += "• **Wave Management**: Control minion waves to create pressure\n"
        message += "• **Team Coordination**: Communicate with your team\n"
        message += "• **Resource Management**: Manage gold and experience efficiently"
        
        return ChatResponse(
            message=message,
            confidence=0.8,
            query_type=QueryType.STRATEGY,
            context=context,
            suggestions=["Micro mechanics", "Teamfight positioning", "Objective control"],
            related_info={"strategy_type": "macro"},
            follow_up_questions=[
                "How do I improve my micro mechanics?",
                "What's the best way to control objectives?",
                "How should I manage waves in different lanes?"
            ]
        )
    
    def _handle_micro_query(self, query: str, context: ChatContext) -> ChatResponse:
        """Handle micro mechanics queries."""
        message = "**Micro Mechanics Tips:**\n\n"
        message += "• **Last Hitting**: Practice CSing to maximize gold income\n"
        message += "• **Trading**: Learn when to trade damage with opponents\n"
        message += "• **Skill Shots**: Practice aiming and predicting movement\n"
        message += "• **Combo Execution**: Master champion ability combinations\n"
        message += "• **Kiting**: Learn to attack while moving"
        
        return ChatResponse(
            message=message,
            confidence=0.8,
            query_type=QueryType.STRATEGY,
            context=context,
            suggestions=["Macro strategy", "Champion combos", "Trading patterns"],
            related_info={"strategy_type": "micro"},
            follow_up_questions=[
                "How do I improve my macro game?",
                "What are some advanced trading techniques?",
                "How can I practice my mechanics?"
            ]
        )
    
    def _handle_teamfight_query(self, query: str, context: ChatContext) -> ChatResponse:
        """Handle teamfight strategy queries."""
        message = "**Teamfight Strategy:**\n\n"
        message += "• **Positioning**: Stay in safe positions relative to your role\n"
        message += "• **Target Priority**: Focus high-value targets first\n"
        message += "• **Cooldown Management**: Track important enemy abilities\n"
        message += "• **Engage Timing**: Wait for good opportunities to start fights\n"
        message += "• **Disengage**: Know when to back off from bad fights"
        
        return ChatResponse(
            message=message,
            confidence=0.8,
            query_type=QueryType.STRATEGY,
            context=context,
            suggestions=["Positioning tips", "Engage timing", "Target selection"],
            related_info={"strategy_type": "teamfight"},
            follow_up_questions=[
                "How do I position as different roles?",
                "When should I engage in teamfights?",
                "How do I prioritize targets?"
            ]
        )
    
    def _handle_positioning_query(self, query: str, context: ChatContext) -> ChatResponse:
        """Handle positioning queries."""
        message = "**Positioning Tips by Role:**\n\n"
        message += "• **ADC**: Stay behind tanks, focus on safe damage\n"
        message += "• **Support**: Protect carries, control vision\n"
        message += "• **Mid**: Look for picks, control flanks\n"
        message += "• **Top**: Frontline or split push based on champion\n"
        message += "• **Jungle**: Control objectives, provide pressure"
        
        return ChatResponse(
            message=message,
            confidence=0.8,
            query_type=QueryType.STRATEGY,
            context=context,
            suggestions=["Role-specific tips", "Teamfight positioning", "Map awareness"],
            related_info={"strategy_type": "positioning"},
            follow_up_questions=[
                "How do I position as ADC?",
                "What's the best positioning for supports?",
                "How do I improve my map awareness?"
            ]
        )
    
    def _handle_general_strategy_query(self, query: str, context: ChatContext) -> ChatResponse:
        """Handle general strategy queries."""
        message = "**General Strategy Tips:**\n\n"
        message += "• **Learn Your Role**: Master your champion's strengths\n"
        message += "• **Map Awareness**: Always know where enemies are\n"
        message += "• **Objective Focus**: Prioritize dragons, Baron, and towers\n"
        message += "• **Communication**: Coordinate with your team\n"
        message += "• **Adaptation**: Adjust strategy based on game state"
        
        return ChatResponse(
            message=message,
            confidence=0.7,
            query_type=QueryType.STRATEGY,
            context=context,
            suggestions=["Macro strategy", "Micro mechanics", "Champion guides"],
            related_info={"strategy_type": "general"},
            follow_up_questions=[
                "How do I improve my macro game?",
                "What are the best micro mechanics to practice?",
                "How do I communicate effectively with my team?"
            ]
        )


class LoLChatbot:
    """Main chatbot class that coordinates all query handlers."""
    
    def __init__(self):
        self.query_classifier = QueryClassifier()
        self.champion_handler = ChampionQueryHandler()
        self.strategy_handler = StrategyQueryHandler()
        self.nlp = None
        self.dragontail = None
        
        # Conversation history
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_context = ChatContext(context_type=ContextType.GENERAL_CHAT)
    
    async def initialize(self):
        """Initialize the chatbot."""
        self.nlp = await get_nlp_pipeline()
        self.dragontail = get_dragontail_manager()
        
        await self.champion_handler.initialize()
        await self.strategy_handler.initialize()
        
        logger.info("LoL Chatbot initialized")
    
    async def process_message(self, message: str, user_id: str = "default") -> ChatResponse:
        """
        Process a user message and generate a response.
        
        Args:
            message: User's message
            user_id: Unique user identifier
            
        Returns:
            ChatResponse object
        """
        # Update conversation history
        self.conversation_history.append({
            "timestamp": datetime.now(),
            "user_id": user_id,
            "message": message,
            "context": self.current_context
        })
        
        # Classify the query
        query_type = await self.query_classifier.classify_query(message, self.current_context)
        
        # Route to appropriate handler
        if query_type == QueryType.CHAMPION_INFO:
            response = await self.champion_handler.handle_query(message, self.current_context)
        elif query_type == QueryType.STRATEGY:
            response = await self.strategy_handler.handle_query(message, self.current_context)
        elif query_type == QueryType.ITEM_BUILD:
            response = await self._handle_item_build_query(message)
        elif query_type == QueryType.META_QUESTION:
            response = await self._handle_meta_query(message)
        elif query_type == QueryType.COUNTERPICK:
            response = await self._handle_counter_query(message)
        else:
            response = await self._handle_general_query(message)
        
        # Update context based on response
        self.current_context = response.context
        
        # Add to conversation history
        self.conversation_history.append({
            "timestamp": datetime.now(),
            "user_id": "bot",
            "message": response.message,
            "context": response.context
        })
        
        return response
    
    async def _handle_item_build_query(self, message: str) -> ChatResponse:
        """Handle item build queries."""
        message_text = "I can help you with item builds! Here are some general build principles:\n\n"
        message_text += "• **Core Items**: Build items that synergize with your champion\n"
        message_text += "• **Situational Items**: Adapt based on enemy team composition\n"
        message_text += "• **Power Spikes**: Understand when your champion is strongest\n"
        message_text += "• **Defensive Options**: Build resistances against enemy damage types\n\n"
        message_text += "Which champion are you looking for build advice on?"
        
        return ChatResponse(
            message=message_text,
            confidence=0.7,
            query_type=QueryType.ITEM_BUILD,
            context=self.current_context,
            suggestions=["Popular champions", "Role-specific builds", "Meta builds"],
            related_info={"query_type": "item_build"},
            follow_up_questions=[
                "What are the best ADC builds?",
                "How do I build tank items?",
                "What are situational items?"
            ]
        )
    
    async def _handle_meta_query(self, message: str) -> ChatResponse:
        """Handle meta-related queries."""
        message_text = "**Current Meta Overview:**\n\n"
        message_text += "• **Strong Picks**: Champions performing well in current patch\n"
        message_text += "• **Team Compositions**: Popular team strategies\n"
        message_text += "• **Objective Priority**: Current focus on dragons, Baron, etc.\n"
        message_text += "• **Item Changes**: Recent item updates and their impact\n\n"
        message_text += "Would you like to know about specific roles or champions?"
        
        return ChatResponse(
            message=message_text,
            confidence=0.8,
            query_type=QueryType.META_QUESTION,
            context=self.current_context,
            suggestions=["Tier lists", "Patch notes", "Pro play meta"],
            related_info={"query_type": "meta"},
            follow_up_questions=[
                "What are the strongest champions right now?",
                "How has the meta changed recently?",
                "What's popular in pro play?"
            ]
        )
    
    async def _handle_counter_query(self, message: str) -> ChatResponse:
        """Handle counterpick queries."""
        message_text = "I can help you with counterpicks! Here's how to think about matchups:\n\n"
        message_text += "• **Champion Counters**: Some champions naturally counter others\n"
        message_text += "• **Playstyle Counters**: Aggressive vs defensive playstyles\n"
        message_text += "• **Item Counters**: Building against specific threats\n"
        message_text += "• **Team Composition**: Countering enemy team strategies\n\n"
        message_text += "Which champion are you looking to counter or get countered by?"
        
        return ChatResponse(
            message=message_text,
            confidence=0.7,
            query_type=QueryType.COUNTERPICK,
            context=self.current_context,
            suggestions=["Champion matchups", "Counter items", "Team counters"],
            related_info={"query_type": "counterpick"},
            follow_up_questions=[
                "Who counters Yasuo?",
                "How do I counter assassins?",
                "What counters tank compositions?"
            ]
        )
    
    async def _handle_general_query(self, message: str) -> ChatResponse:
        """Handle general queries."""
        # Try to use NLP pipeline for general questions
        if self.nlp:
            try:
                nlp_response = await self.nlp.process_user_question(message)
                if nlp_response.confidence > 0.5:
                    return ChatResponse(
                        message=nlp_response.answer,
                        confidence=nlp_response.confidence,
                        query_type=QueryType.UNKNOWN,
                        context=self.current_context,
                        suggestions=["Champion info", "Strategy tips", "Item builds"],
                        related_info={"source": "nlp"},
                        follow_up_questions=[
                            "Tell me about a champion",
                            "Give me strategy advice",
                            "Help me with builds"
                        ]
                    )
            except Exception as e:
                logger.error(f"NLP processing failed: {e}")
        
        # Fallback response
        message_text = "I'm here to help with League of Legends! I can assist you with:\n\n"
        message_text += "• **Champion Information**: Abilities, tips, and strategies\n"
        message_text += "• **Item Builds**: Recommended items and builds\n"
        message_text += "• **Strategy Advice**: Macro, micro, and positioning tips\n"
        message_text += "• **Counterpicks**: Matchup advice and counters\n"
        message_text += "• **Meta Information**: Current meta and tier lists\n\n"
        message_text += "What would you like to know about?"
        
        return ChatResponse(
            message=message_text,
            confidence=0.6,
            query_type=QueryType.GENERAL_HELP,
            context=self.current_context,
            suggestions=["Champion guides", "Strategy tips", "Build recommendations"],
            related_info={"query_type": "general"},
            follow_up_questions=[
                "Tell me about Yasuo",
                "How do I improve my macro game?",
                "What are the best ADC builds?"
            ]
        )
    
    def get_conversation_history(self, user_id: str = "default", limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for a user."""
        user_messages = [
            msg for msg in self.conversation_history 
            if msg["user_id"] == user_id or msg["user_id"] == "bot"
        ]
        return user_messages[-limit:] if limit > 0 else user_messages
    
    def clear_conversation_history(self, user_id: str = "default"):
        """Clear conversation history for a user."""
        self.conversation_history = [
            msg for msg in self.conversation_history 
            if msg["user_id"] != user_id
        ]
        self.current_context = ChatContext(context_type=ContextType.GENERAL_CHAT)


# Global chatbot instance
_chatbot: Optional[LoLChatbot] = None


async def get_chatbot() -> LoLChatbot:
    """Get the global chatbot instance."""
    global _chatbot
    if _chatbot is None:
        _chatbot = LoLChatbot()
        await _chatbot.initialize()
    return _chatbot


# Utility functions
async def ask_chatbot(question: str, user_id: str = "default") -> str:
    """Simple function to ask the chatbot a question."""
    chatbot = await get_chatbot()
    response = await chatbot.process_message(question, user_id)
    return response.message


async def get_chatbot_suggestions(context: ChatContext) -> List[str]:
    """Get contextual suggestions from the chatbot."""
    suggestions = []
    
    if context.current_champion:
        suggestions.extend([
            f"{context.current_champion} abilities",
            f"{context.current_champion} build",
            f"{context.current_champion} tips"
        ])
    
    if context.context_type == ContextType.BUILD_DISCUSSION:
        suggestions.extend(["Item recommendations", "Situational items", "Build order"])
    
    if context.context_type == ContextType.CHAMPION_DISCUSSION:
        suggestions.extend(["Champion counters", "Similar champions", "Role guides"])
    
    return suggestions[:5]  # Limit to 5 suggestions


if __name__ == "__main__":
    async def main():
        # Test the chatbot
        chatbot = await get_chatbot()
        
        # Test different types of queries
        test_queries = [
            "Tell me about Yasuo",
            "What items should I build on Jinx?",
            "How do I improve my macro game?",
            "Who counters Aatrox?",
            "What's the current meta?"
        ]
        
        for query in test_queries:
            print(f"\nUser: {query}")
            response = await chatbot.process_message(query)
            print(f"Bot: {response.message}")
            print(f"Confidence: {response.confidence:.2f}")
            print(f"Type: {response.query_type.value}")
    
    asyncio.run(main())

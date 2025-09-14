"""Fan Q&A Chatbot Page

Interactive FAQ system using semantic search.
Features:
- Natural language question answering
- Semantic similarity search
- Team/player/game information
- Match schedule lookup
"""
from __future__ import annotations

import os
import sys

# Add the parent directory to Python path to resolve module imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any

def render_chatbot_page():
    """Render the fan Q&A chatbot page."""
    st.title("❓ Fan Q&A")
    
    with st.sidebar:
        st.header("Chatbot Settings")
        
        st.subheader("Knowledge Base")
        kb_source = st.radio(
            "Choose source",
            options=["Live API", "Local DB", "Demo Data"],
            index=2
        )
        
        st.subheader("Response Style")
        response_style = st.select_slider(
            "Style",
            options=["Concise", "Balanced", "Detailed"],
            value="Balanced"
        )
        
        st.subheader("Features")
        enable_context = st.checkbox("Use chat context", value=True)
        show_confidence = st.checkbox("Show confidence", value=False)
        auto_suggest = st.checkbox("Auto-suggest questions", value=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    if "kb" not in st.session_state:
        load_demo_knowledge_base()
    
    # Chat interface
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Auto-suggest questions
    if auto_suggest and not st.session_state.messages:
        with st.expander("Suggested Questions"):
            for q in get_suggested_questions():
                if st.button(q):
                    process_user_input(q)
    
    # Chat input
    if prompt := st.chat_input("Ask a question about esports..."):
        process_user_input(prompt)

def load_demo_knowledge_base():
    """Load sample knowledge base for demonstration."""
    st.session_state.kb = {
        "teams": [
            {
                "name": "Cloud9",
                "game": "League of Legends",
                "region": "NA",
                "achievements": ["LCS Champions 2021", "Worlds Quarter-finalist 2021"],
                "current_roster": ["Fudge", "Blaber", "Jojopyun", "Berserker", "Vulcan"]
            },
            {
                "name": "Fnatic",
                "game": "League of Legends",
                "region": "EU",
                "achievements": ["Worlds Champions S1", "LEC Champions 2018"],
                "current_roster": ["Oscarinin", "Razork", "Humanoid", "Noah", "Trymbi"]
            }
        ],
        "tournaments": [
            {
                "name": "LCS Spring 2025",
                "game": "League of Legends",
                "start_date": "2025-01-20",
                "end_date": "2025-04-10",
                "prize_pool": "$200,000",
                "format": "Double Round Robin + Playoffs"
            }
        ],
        "rules": [
            {
                "game": "League of Legends",
                "category": "Tournament",
                "rule": "Each team must have 5 starting players and at least 1 substitute",
                "explanation": "This ensures teams can continue playing if a player is unable to participate"
            }
        ],
        "schedules": [
            {
                "match_id": "LCS2025-W1D1-1",
                "team1": "Cloud9",
                "team2": "TSM",
                "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                "time": "17:00",
                "tournament": "LCS Spring 2025"
            }
        ]
    }

def get_suggested_questions() -> List[str]:
    """Get a list of suggested starter questions."""
    return [
        "When is the next Cloud9 match?",
        "What are the LCS tournament rules?",
        "Who are the current Fnatic players?",
        "How many teams are in LCS 2025?",
        "What was Cloud9's best Worlds performance?"
    ]

def process_user_input(prompt: str):
    """Process user question and generate response."""
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate response
    response = generate_response(prompt)
    
    # Add response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})

def generate_response(prompt: str) -> str:
    """Generate chatbot response using knowledge base."""
    prompt_lower = prompt.lower()
    
    # Team information
    for team in st.session_state.kb["teams"]:
        if team["name"].lower() in prompt_lower:
            if "roster" in prompt_lower or "players" in prompt_lower:
                return f"{team['name']}'s current roster: {', '.join(team['roster'])}"
            if "achievement" in prompt_lower or "win" in prompt_lower:
                return f"{team['name']}'s achievements: {', '.join(team['achievements'])}"
            return f"{team['name']} is a {team['region']} {team['game']} team. Current roster: {', '.join(team['current_roster'])}"
    
    # Schedule information
    if "next" in prompt_lower and "match" in prompt_lower:
        future_matches = [
            m for m in st.session_state.kb["schedules"]
            if datetime.strptime(m["date"], "%Y-%m-%d") > datetime.now()
        ]
        if future_matches:
            match = future_matches[0]
            return f"Next match: {match['team1']} vs {match['team2']} on {match['date']} at {match['time']}"
    
    # Tournament rules
    if "rule" in prompt_lower:
        rules = st.session_state.kb["rules"]
        if rules:
            return f"Tournament rule: {rules[0]['rule']}\n\nExplanation: {rules[0]['explanation']}"
    
    # Default response
    return "I'm not sure about that. Try asking about specific teams, upcoming matches, or tournament rules!"

def semantic_search(query: str, kb: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Perform semantic search on knowledge base (placeholder)."""
    # TODO: Implement proper semantic search using sentence-transformers
    return []

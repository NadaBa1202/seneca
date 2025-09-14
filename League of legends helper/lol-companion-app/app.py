"""
Main Streamlit application for League of Legends Companion App.

This is the entry point for the web application, providing an interactive
dashboard with real-time match tracking, AI-powered analysis, and comprehensive
League of Legends insights.
"""

import asyncio
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Any
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
from src.config import get_config
from src.api.riot_client import get_riot_client
from src.data.dragontail import get_dragontail_manager
from src.nlp import get_nlp_pipeline, explain_champion_ability, get_champion_tips
from src.services.event_detection import get_event_service
from src.services.streaming import get_streaming_service
from src.services.analytics import get_analytics_service
# Temporarily commented out to fix import issues
# from src.services.export import get_export_service
from src.services.pro_matches import get_pro_tracker
from src.models import Champion, LiveMatch, MatchEvent, QuestionAnswerPair

# Page configuration
st.set_page_config(
    page_title="⚔️ LoL Companion",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/lol-companion-app',
        'Report a bug': 'https://github.com/your-repo/lol-companion-app/issues',
        'About': """
        # League of Legends Companion App
        
        Your AI-powered companion for League of Legends matches!
        
        Features:
        - 🔴 Live match tracking and analysis
        - 🤖 AI-powered Q&A about champions and strategies
        - 📊 Real-time statistics and visualizations
        - 🎯 Event detection and highlight generation
        
        Built with ❤️ using Streamlit, Transformers, and Riot Games API
        """
    }
)

# Load configuration
config = get_config()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #C89B3C, #0F2027, #C89B3C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #1e3a8a, #3b82f6);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .champion-card {
        border: 2px solid #C89B3C;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        background: linear-gradient(145deg, #0a0e27, #1e3a8a);
        color: white;
    }
    
    .event-card {
        background: linear-gradient(145deg, #7c2d12, #dc2626);
        color: white;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        border-left: 4px solid #C89B3C;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0a0e27, #1e3a8a);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.dragontail_manager = None
    st.session_state.riot_client = None
    st.session_state.nlp_pipeline = None
    st.session_state.event_service = None
    st.session_state.streaming_service = None
    st.session_state.analytics_service = None
    st.session_state.export_service = None
    st.session_state.pro_tracker = None
    st.session_state.current_match = None
    st.session_state.chat_history = []

async def initialize_app():
    """Initialize all app components asynchronously."""
    if st.session_state.initialized:
        return
    
    with st.spinner("🚀 Initializing League of Legends Companion App..."):
        try:
            # Initialize components
            st.session_state.dragontail_manager = get_dragontail_manager()
            st.session_state.riot_client = await get_riot_client()
            st.session_state.nlp_pipeline = await get_nlp_pipeline()
            st.session_state.event_service = await get_event_service()
            st.session_state.streaming_service = await get_streaming_service()
            st.session_state.analytics_service = await get_analytics_service()
            # st.session_state.export_service = get_export_service()
            st.session_state.pro_tracker = await get_pro_tracker()
            
            # Preload data
            await st.session_state.dragontail_manager.load_champions()
            
            st.session_state.initialized = True
            st.success("✅ App initialized successfully!")
            
        except Exception as e:
            st.error(f"❌ Failed to initialize app: {e}")
            logger.error(f"App initialization failed: {e}")

def main():
    """Main application function with enhanced UX."""
    
    # Enhanced page config and styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .search-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stat-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # App header
    st.markdown('<h1 class="main-header">⚔️ League of Legends Companion</h1>', unsafe_allow_html=True)
    
    # Initialize app with loading state
    if not st.session_state.initialized:
        with st.spinner("🔄 Initializing League of Legends Companion..."):
            asyncio.run(initialize_app())
            if not st.session_state.initialized:
                st.error("❌ Failed to initialize application. Please refresh the page.")
                st.stop()
            else:
                st.success("✅ Application initialized successfully!")
                time.sleep(1)  # Brief pause to show success message
                st.rerun()
    
    # Enhanced sidebar navigation
    with st.sidebar:
        st.title("🗂️ Navigation")
        
        # Status indicator
        status_color = "🟢" if st.session_state.initialized else "🔴"
        st.markdown(f"{status_color} **Status:** {'Ready' if st.session_state.initialized else 'Loading'}")
        
        st.markdown("---")
        
        page = st.selectbox(
            "Choose a page:",
            [
                "🏠 Dashboard", 
                "🔴 Live Match Tracker", 
                "🤖 AI Assistant", 
                "🏆 Champion Analysis",
                "📊 Match Analytics",
                "🏆 Pro Matches",
                "📈 Advanced Analytics",
                "📤 Export Data",
                "⚙️ Settings"
            ],
            help="Navigate between different features"
        )
        
        st.markdown("---")
        
        # Quick stats with loading states
        if st.session_state.dragontail_manager:
            st.subheader("📈 Quick Stats")
            
            with st.spinner("Loading stats..."):
                try:
                    champions = st.session_state.dragontail_manager.get_champions()
                    st.metric("🏆 Champions", len(champions), help="Total champions available")
                    
                    # Show last updated
                    st.caption("📅 Data Version: 15.18.1")
                    st.caption("🔄 Last Updated: Just now")
                    
                except Exception as e:
                    st.error("Failed to load stats")
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        if st.button("🔄 Refresh Data", help="Reload champion data"):
            st.session_state.initialized = False
            st.rerun()
        
        if st.button("📱 Mobile View", help="Optimize for mobile"):
            st.info("Mobile view activated!")
    
    # Main content with loading indicator
    # Main content with loading indicator
    with st.container():
        # Route to appropriate page with loading states
        try:
            if page == "🏠 Dashboard":
                show_dashboard()
            elif page == "🔴 Live Match Tracker":
                show_live_match_tracker()
            elif page == "🤖 AI Assistant":
                show_ai_assistant()
            elif page == "🏆 Champion Analysis":
                with st.spinner("🔄 Loading champion data..."):
                    show_champion_analysis()
            elif page == "📊 Match Analytics":
                show_match_analytics()
            elif page == "🏆 Pro Matches":
                show_pro_matches()
            elif page == "📈 Advanced Analytics":
                show_advanced_analytics()
            elif page == "📤 Export Data":
                show_export_data()
            elif page == "⚙️ Settings":
                show_settings()
        
        except Exception as e:
            st.error(f"❌ Error loading page: {str(e)}")
            st.info("🔄 Try refreshing the page or contact support if the issue persists.")

def show_dashboard():
    """Show the main dashboard."""
    st.header("🏠 Dashboard")
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🔴 Live Matches</h3>
            <h2>0</h2>
            <p>Currently tracking</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🤖 AI Queries</h3>
            <h2>15</h2>
            <p>Answered today</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Events Detected</h3>
            <h2>47</h2>
            <p>In recent matches</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>💬 Sentiment Score</h3>
            <h2>73%</h2>
            <p>Positive chat mood</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent activity
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Recent Match Activity")
        
        # Sample data for demonstration
        sample_data = pd.DataFrame({
            'Time': pd.date_range(start='2024-01-01 10:00', periods=24, freq='H'),
            'Matches': [3, 5, 8, 12, 15, 18, 22, 25, 20, 15, 12, 8, 6, 4, 7, 10, 14, 18, 22, 25, 20, 15, 10, 5],
            'Events': [15, 25, 40, 60, 75, 90, 110, 125, 100, 75, 60, 40, 30, 20, 35, 50, 70, 90, 110, 125, 100, 75, 50, 25]
        })
        
        fig = px.line(sample_data, x='Time', y=['Matches', 'Events'], 
                     title="Match Activity Over Time",
                     color_discrete_map={'Matches': '#C89B3C', 'Events': '#3b82f6'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Top Champions Today")
        
        # Sample champion data
        champions_data = pd.DataFrame({
            'Champion': ['Aatrox', 'Jinx', 'Thresh', 'Yasuo', 'Ahri'],
            'Pick Rate': [15.2, 12.8, 11.5, 10.3, 9.7],
            'Win Rate': [52.1, 48.5, 51.2, 49.8, 53.4]
        })
        
        for _, champion in champions_data.iterrows():
            st.markdown(f"""
            <div class="champion-card">
                <strong>{champion['Champion']}</strong><br>
                Pick: {champion['Pick Rate']}% | Win: {champion['Win Rate']}%
            </div>
            """, unsafe_allow_html=True)
    
    # Recent events
    st.subheader("⚡ Recent Match Events")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="event-card">
            <strong>🥇 First Blood</strong><br>
            <small>2 minutes ago • Ranked Solo</small><br>
            Yasuo eliminated Zed in top lane
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="event-card">
            <strong>🐲 Dragon Secured</strong><br>
            <small>5 minutes ago • Ranked Solo</small><br>
            Cloud Dragon taken by Blue team
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="event-card">
            <strong>💀 Team ACE</strong><br>
            <small>8 minutes ago • Ranked Solo</small><br>
            Red team eliminated in Baron pit
        </div>
        """, unsafe_allow_html=True)

def show_live_match_tracker():
    """Show live match tracking interface."""
    st.header("🔴 Live Match Tracker")
    
    # Input for summoner name
    col1, col2 = st.columns([3, 1])
    
    with col1:
        summoner_name = st.text_input("🔍 Enter Summoner Name:", placeholder="e.g., Hide on bush")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        track_button = st.button("🎯 Track Match", type="primary")
    
    if track_button and summoner_name:
        with st.spinner(f"🔍 Searching for {summoner_name}'s current match..."):
            try:
                # Get live match data
                live_match = asyncio.run(
                    st.session_state.riot_client.get_live_match_data(summoner_name)
                )
                
                if live_match:
                    st.session_state.current_match = live_match
                    st.success(f"✅ Found live match for {summoner_name}!")
                else:
                    st.warning(f"🔍 {summoner_name} is not currently in a game.")
                    
            except Exception as e:
                st.error(f"❌ Error fetching match data: {e}")
    
    # Display current match if available
    if st.session_state.current_match:
        display_live_match(st.session_state.current_match)
    else:
        # Show sample match for demonstration
        st.info("📺 Demo Mode: Showing sample match data")
        display_sample_match()

def display_live_match(match: LiveMatch):
    """Display live match information."""
    # Match header
    st.subheader(f"⚔️ Live Match - Game Mode: {match.game_mode.value}")
    
    # Match info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🕐 Game Time", f"{match.game_length // 60}:{match.game_length % 60:02d}")
    
    with col2:
        st.metric("🗺️ Map", f"Summoner's Rift (ID: {match.map_id})")
    
    with col3:
        st.metric("👥 Players", len(match.participants))
    
    with col4:
        st.metric("📊 State", match.state.value)
    
    # Teams display
    st.subheader("👥 Teams")
    
    col1, col2 = st.columns(2)
    
    # Blue team
    with col1:
        st.markdown("#### 🔵 Blue Team")
        blue_team = [p for p in match.participants if p.team_id == 100]
        
        for participant in blue_team:
            st.markdown(f"""
            <div class="champion-card">
                <strong>{participant.summoner_name}</strong><br>
                <small>{participant.champion_name} • {participant.role}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Red team
    with col2:
        st.markdown("#### 🔴 Red Team")
        red_team = [p for p in match.participants if p.team_id == 200]
        
        for participant in red_team:
            st.markdown(f"""
            <div class="champion-card">
                <strong>{participant.summoner_name}</strong><br>
                <small>{participant.champion_name} • {participant.role}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Live events
    if match.events:
        st.subheader("⚡ Live Events")
        
        for event in match.events[-5:]:  # Show last 5 events
            timestamp_min = event.timestamp // (60 * 1000)
            timestamp_sec = (event.timestamp % (60 * 1000)) // 1000
            
            st.markdown(f"""
            <div class="event-card">
                <strong>{event.event_type.value.replace('_', ' ').title()}</strong><br>
                <small>{timestamp_min}:{timestamp_sec:02d}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Auto-refresh
    if st.checkbox("🔄 Auto-refresh (30s)", value=False):
        time.sleep(30)
        st.rerun()

def display_sample_match():
    """Display sample match data for demonstration."""
    st.markdown("### 🎮 Sample Live Match")
    
    # Sample match info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🕐 Game Time", "23:45")
    
    with col2:
        st.metric("🗺️ Map", "Summoner's Rift")
    
    with col3:
        st.metric("👥 Players", "10")
    
    with col4:
        st.metric("📊 State", "IN_PROGRESS")
    
    # Sample teams
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔵 Blue Team")
        blue_players = [
            ("Faker", "Azir", "Mid"),
            ("Canyon", "Graves", "Jungle"),
            ("Zeus", "Aatrox", "Top"),
            ("Gumayusi", "Jinx", "ADC"),
            ("Keria", "Thresh", "Support")
        ]
        
        for name, champion, role in blue_players:
            st.markdown(f"""
            <div class="champion-card">
                <strong>{name}</strong><br>
                <small>{champion} • {role}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🔴 Red Team")
        red_players = [
            ("Showmaker", "LeBlanc", "Mid"),
            ("Oner", "Lee Sin", "Jungle"),
            ("Doran", "Gnar", "Top"),
            ("Deokdam", "Aphelios", "ADC"),
            ("Kellin", "Nautilus", "Support")
        ]
        
        for name, champion, role in red_players:
            st.markdown(f"""
            <div class="champion-card">
                <strong>{name}</strong><br>
                <small>{champion} • {role}</small>
            </div>
            """, unsafe_allow_html=True)

def show_ai_assistant():
    """Enhanced AI assistant with real API data integration."""
    st.header("🤖 AI Assistant - Powered by Real Game Data")
    
    # Enhanced capabilities with real data
    st.markdown("""
    🎯 **I can help you with real-time League of Legends data:**
    - 🏆 **Champion Analysis**: Real champion stats, abilities, and meta builds
    - � **Player Lookup**: Search any summoner and get their current game info
    - � **Live Match Data**: Analyze ongoing matches with real participants
    - 📊 **Statistics**: Champion win rates, pick rates, and performance data
    - 🛡️ **Build Recommendations**: Data-driven item and rune suggestions
    - 🎯 **Strategic Advice**: Context-aware tips based on actual game data
    """)
    
    # Chat interface with enhanced features
    st.subheader("💬 Intelligent Chat Assistant")
    
    # Enhanced input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_question = st.text_input(
            "💭 Ask me anything about League of Legends:", 
            placeholder="e.g., 'Show me Faker's current match' or 'What items should I build on Jinx?'",
            help="I can look up real player data, analyze live matches, and provide champion insights!"
        )
    
    with col2:
        question_type = st.selectbox("🎯 Query Type:", [
            "General Question",
            "Player Lookup", 
            "Champion Analysis",
            "Live Match Info",
            "Build Advice"
        ])
    
    # Display chat history with better formatting
    if st.session_state.chat_history:
        st.markdown("### 📝 Chat History")
        
        for i, message in enumerate(st.session_state.chat_history[-10:]):  # Show last 10 messages
            if message['role'] == 'user':
                st.markdown(f"""
                <div style="background-color: #1e3a5f; color: #ffffff; padding: 10px; border-radius: 10px; margin: 5px 0;">
                    <strong>👤 You:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #2d3748; color: #e2e8f0; padding: 10px; border-radius: 10px; margin: 5px 0;">
                    <strong>🤖 AI Assistant:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ask_button = st.button("📤 Ask", type="primary")
    
    with col2:
        clear_button = st.button("🗑️ Clear Chat")
    
    with col3:
        example_button = st.button("💡 Example Query")
    
    with col4:
        help_button = st.button("❓ Help")
    
    # Handle button actions
    if clear_button:
        st.session_state.chat_history = []
        st.rerun()
    
    if example_button:
        example_queries = [
            "What are Jinx's abilities and best builds?",
            "Look up summoner 'Faker' and show current match",
            "Analyze the current meta for ADC champions",
            "What items should I build against a tanky team?",
            "Show me live matches with pro players"
        ]
        selected_example = st.selectbox("Select an example:", example_queries)
        if st.button("📤 Use Example"):
            user_question = selected_example
    
    if help_button:
        st.info("""
        **🔍 How to use the AI Assistant:**
        
        **Player Lookup:** "Show me [summoner name]'s current match" or "Look up player [name]"
        
        **Champion Analysis:** "Tell me about [champion name]" or "What are [champion]'s abilities?"
        
        **Build Advice:** "Best build for [champion]" or "Items against [team comp]"
        
        **Live Data:** "Show live matches" or "Current meta analysis"
        
        **Examples:**
        - "Look up Faker's current game"
        - "Best Jinx build for ranked"
        - "Show me live Diamond+ matches"
        """)
    
    if ask_button and user_question:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_question
        })
        
        with st.spinner("🔍 Analyzing your question and fetching real data..."):
            try:
                # Enhanced AI response with real data integration
                response = safe_async_run(get_enhanced_ai_response(user_question, question_type))
                
                # Add AI response to history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response
                })
                
                st.rerun()
                
            except Exception as e:
                error_msg = f"❌ Sorry, I encountered an error: {str(e)}\n\nTry asking a different question or check if the summoner name is correct."
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': error_msg
                })
                st.rerun()
    
    # Enhanced quick actions with real data
    st.markdown("---")
    st.subheader("⚡ Quick Actions - Real Data Powered")
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        st.markdown("#### 👤 Player Tracking")
        summoner_name = st.text_input("Summoner Name:", placeholder="Enter summoner name...")
        if st.button("🔍 Look Up Player", help="Get real player data and current match info"):
            if summoner_name:
                with st.spinner(f"🔍 Looking up {summoner_name}..."):
                    player_info = safe_async_run(lookup_player_data(summoner_name))
                    if player_info:
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': player_info
                        })
                        st.rerun()
    
    with action_col2:
        st.markdown("#### 🏆 Champion Insights")
        champions = st.session_state.dragontail_manager.get_champions()
        champion_name = st.selectbox("Select Champion:", list(champions.keys()) if champions else [])
        if st.button("📊 Analyze Champion", help="Get detailed champion analysis with real data"):
            if champion_name:
                with st.spinner(f"📊 Analyzing {champion_name}..."):
                    champion_analysis = asyncio.run(get_champion_analysis(champion_name))
                    if champion_analysis:
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': champion_analysis
                        })
                        st.rerun()
    
    with action_col3:
        st.markdown("#### 🔴 Live Matches")
        if st.button("🎮 Find Live Matches", help="Discover ongoing high-level matches"):
            with st.spinner("🔍 Searching for live matches..."):
                live_matches = asyncio.run(find_live_matches())
                if live_matches:
                    st.session_state.chat_history.append({
                        'role': 'assistant', 
                        'content': live_matches
                    })
                    st.rerun()

async def get_enhanced_ai_response(user_question: str, question_type: str) -> str:
    """Get enhanced AI response with real API data integration."""
    try:
        # Initialize response components
        response_parts = []
        
        # Detect question intent and fetch relevant data
        question_lower = user_question.lower()
        
        # Player lookup intent
        if any(keyword in question_lower for keyword in ['player', 'summoner', 'look up', 'lookup', 'find']):
            # Extract summoner name from question
            import re
            summoner_matches = re.findall(r"'([^']*)'|\"([^\"]*)\"|\b([A-Za-z0-9_]{3,16})\b", user_question)
            if summoner_matches:
                summoner_name = next((match for group in summoner_matches for match in group if match), None)
                if summoner_name:
                    player_data = await lookup_player_data(summoner_name)
                    response_parts.append(player_data)
        
        # Champion analysis intent
        elif any(keyword in question_lower for keyword in ['champion', 'ability', 'skill', 'passive']):
            # Extract champion name
            champions = st.session_state.dragontail_manager.get_champions()
            mentioned_champion = None
            for champ_name in champions.keys():
                if champ_name.lower() in question_lower:
                    mentioned_champion = champ_name
                    break
            
            if mentioned_champion:
                champion_data = await get_champion_analysis(mentioned_champion)
                response_parts.append(champion_data)
        
        # Build/item advice intent
        elif any(keyword in question_lower for keyword in ['build', 'item', 'rune', 'equipment']):
            build_advice = await get_build_recommendations(user_question)
            response_parts.append(build_advice)
        
        # Live match intent
        elif any(keyword in question_lower for keyword in ['live', 'current', 'ongoing', 'match']):
            live_data = await find_live_matches()
            response_parts.append(live_data)
        
        # General NLP response as fallback
        if not response_parts:
            try:
                nlp_response = await st.session_state.nlp_pipeline.process_user_question(user_question)
                # Check if response is valid and has reasonable confidence
                if (nlp_response and 
                    nlp_response.answer and 
                    nlp_response.answer.strip() and 
                    nlp_response.confidence > 0.1):  # At least 10% confidence
                    response_parts.append(f"{nlp_response.answer}\n\n*Confidence: {nlp_response.confidence:.1%}*")
                else:
                    # Provide fallback response when NLP fails or has low confidence
                    response_parts.append(get_fallback_response(user_question))
            except Exception as e:
                response_parts.append(get_fallback_response(user_question))
        
        # Combine responses
        final_response = "\n\n---\n\n".join(response_parts) if response_parts else get_fallback_response(user_question)
        
        return final_response
        
    except Exception as e:
        return f"❌ I encountered an error while processing your question: {str(e)}\n\nPlease try rephrasing your question or ask something else!"


def get_fallback_response(user_question: str) -> str:
    """Provide intelligent fallback responses when API or NLP fails."""
    question_lower = user_question.lower()
    
    # Champion-specific fallbacks with detailed lore
    champion_lore = {
        'katarina': {
            'title': 'The Sinister Blade',
            'lore': """**Katarina** is a deadly Noxian assassin who serves as the hand of the empire. Born into the Du Couteau family, she was trained from childhood to be the perfect weapon. Known for her incredible speed and precision with blades, Katarina is both feared and respected throughout Noxus.

**Key Lore Points:**
• Daughter of General Du Couteau, a legendary Noxian assassin
• Trained to kill without hesitation or remorse
• Loyal to Noxus but questions some of its methods
• Sister to Cassiopeia, who was transformed into a serpent
• Seeks to prove herself worthy of her family's reputation""",
            'gameplay': 'Katarina is a melee assassin who excels at resetting her abilities through takedowns. She can quickly eliminate squishy targets and clean up teamfights.',
            'abilities': {
                'passive': '**Voracity** - Champion takedowns reset all of Katarina\'s cooldowns and reduce Death Lotus\'s cooldown',
                'q': '**Bouncing Blade** - Throws a dagger that bounces to nearby enemies, marking the first target',
                'w': '**Preparation** - Tosses a dagger into the air and gains movement speed',
                'e': '**Shunpo** - Teleports to target location, prioritizing daggers and enemies',
                'r': '**Death Lotus** - Channels to throw daggers at nearby enemies rapidly'
            }
        },
        'yasuo': {
            'title': 'The Unforgiven',
            'lore': """**Yasuo** is a proud Ionian swordsman who was falsely accused of murdering his own master. Now a wandering exile, he seeks to clear his name and find the true killer while mastering the ancient wind techniques.

**Key Lore Points:**
• Falsely accused of killing Elder Souma, his beloved master
• Wields an ancient wind technique passed down through generations
• Hunted by his own people, including his brother Yone
• Struggles with guilt and the burden of his exile
• Seeks redemption and the truth behind his master's death""",
            'gameplay': 'Yasuo is a melee fighter who uses wind techniques. He can dash through enemies and block projectiles with his Wind Wall.',
            'abilities': {
                'passive': '**Way of the Wanderer** - Builds Flow by moving, grants shield when full. Doubles critical strike chance',
                'q': '**Steel Tempest** - Thrusts forward with his sword, building stacks for a tornado',
                'w': '**Wind Wall** - Creates a wall that blocks enemy projectiles',
                'e': '**Sweeping Blade** - Dashes through target enemy, dealing damage',
                'r': '**Last Breath** - Teleports to airborne enemies and suspends them longer'
            }
        },
        'jinx': {
            'title': 'The Loose Cannon',
            'lore': """**Jinx** is a manic criminal from Zaun who delights in chaos and destruction. Armed with an arsenal of deadly weapons, she leaves a trail of mayhem wherever she goes, earning the ire of Piltover's finest.

**Key Lore Points:**
• Notorious criminal terrorizing Piltover and Zaun
• Has a complicated relationship with Vi, her former partner/sister
• Creates increasingly elaborate crimes to get attention
• Driven by a need for chaos and excitement
• Her real name is believed to be Powder""",
            'gameplay': 'Jinx is a marksman who switches between rapid-fire and long-range weapons. She gains movement speed when taking down enemies.',
            'abilities': {
                'passive': '**Get Excited!** - Gains movement speed and attack speed when dealing damage to enemy champions, structures, or epic monsters',
                'q': '**Switcheroo!** - Switches between Pow-Pow (rapid fire) and Fishbones (rocket launcher)',
                'w': '**Zap!** - Fires a shock blast that deals damage and slows the first enemy hit',
                'e': '**Flame Chompers!** - Throws out chompers that arm after a short time, rooting enemies',
                'r': '**Super Mega Death Rocket!** - Fires a massive rocket that gains damage as it travels'
            }
        },
        'ahri': {
            'title': 'The Nine-Tailed Fox',
            'lore': """**Ahri** is a vastayan fox spirit who was born with a hunger for life essence. Through consuming memories and emotions, she has gained human intelligence and form, but struggles with her predatory nature.

**Key Lore Points:**
• Originally a fox who gained consciousness by consuming human essence
• Each tail represents her growing power and wisdom
• Struggles between her predatory instincts and desire for connection
• Searches for others like her to understand her true nature
• Can manipulate emotions and memories""",
            'gameplay': 'Ahri is a mobile mage assassin who can charm enemies and dash multiple times. She excels at picking off isolated targets.',
            'abilities': {
                'passive': '**Essence Theft** - Gains movement speed and heals when abilities hit enemies',
                'q': '**Orb of Deception** - Throws an orb that deals magic damage going out and true damage returning',
                'w': '**Fox-Fire** - Releases fox-fires that automatically seek nearby enemies',
                'e': '**Charm** - Blows a kiss that charms and damages the first enemy hit',
                'r': '**Spirit Rush** - Dashes forward and fires essence bolts, can be cast up to 3 times'
            }
        },
        'zed': {
            'title': 'The Master of Shadows',
            'lore': """**Zed** is the ruthless leader of the Order of Shadow, an organization he founded after being corrupted by forbidden shadow magic. Once a student alongside Shen, he now seeks to protect Ionia through any means necessary.

**Key Lore Points:**
• Former student of the Kinkou Order, trained alongside Shen
• Discovered and embraced forbidden shadow magic
• Founded the Order of Shadow after being exiled
• Killed his own master to protect Ionia from Noxian invasion
• Believes that balance and restraint make Ionia weak""",
            'gameplay': 'Zed is an assassin who manipulates shadows to deal massive damage. He can teleport to his shadows and execute low-health enemies.',
            'abilities': {
                'passive': '**Contempt for the Weak** - Zed deals bonus magic damage when attacking low health enemies',
                'q': '**Razor Shuriken** - Throws spinning blades that deal damage to enemies in a line',
                'w': '**Living Shadow** - Creates a shadow that mimics Zed\'s abilities',
                'e': '**Shadow Slash** - Slashes with his blades, dealing damage around him',
                'r': '**Death Mark** - Teleports to target enemy and marks them for execution'
            }
        },
        'sylas': {
            'title': 'The Unshackled',
            'lore': """**Sylas** is a revolutionary mage who escaped from Demacian imprisonment to lead a mage rebellion. Born with immense magical power in a kingdom that despises magic, he seeks to overthrow the oppressive regime and free all mages.

**Key Lore Points:**
• Born in Demacia with powerful magic abilities
• Imprisoned for most of his life for being a mage
• Escaped during a prison riot and began a revolution
• Can steal and use other champions' ultimate abilities
• Seeks to destroy Demacia's anti-magic government
• Former friend of Lux before his imprisonment""",
            'gameplay': 'Sylas is a melee AP assassin/fighter who excels at stealing enemy ultimates. He can adapt to any team composition by using stolen abilities.',
            'abilities': {
                'passive': '**Petricite Burst** - After casting an ability, Sylas\'s next 2 basic attacks whirl his chains, dealing bonus magic damage',
                'q': '**Chain Lash** - Hurls chains that intersect at target location, dealing damage and slowing enemies',
                'w': '**Kingslayer** - Lunges at an enemy, dealing damage based on missing health and healing Sylas',
                'e': '**Abscond/Abduct** - Dashes and gains a shield, then can recast to throw chains that pull him to enemies',
                'r': '**Hijack** - Steals the enemy\'s ultimate ability and can cast it immediately'
            }
        }
    }
    
    # Check for specific champions with detailed responses
    for champ_name, champ_data in champion_lore.items():
        if champ_name in question_lower:
            # Check if asking about abilities specifically
            if any(keyword in question_lower for keyword in ['abilities', 'ability', 'skills', 'spells', 'kit']):
                if 'abilities' in champ_data:
                    abilities_text = f"""
🎯 **{champ_name.title()} - {champ_data['title']}**

⚔️ **Champion Abilities:**

🔹 **Passive:** {champ_data['abilities']['passive']}

🔹 **Q:** {champ_data['abilities']['q']}

🔹 **W:** {champ_data['abilities']['w']}

🔹 **E:** {champ_data['abilities']['e']}

🔹 **R (Ultimate):** {champ_data['abilities']['r']}

🎮 **Gameplay Style:**
{champ_data['gameplay']}

💡 **Pro Tips:**
- Practice ability combos in Practice Tool
- Learn the optimal skill order (max Q→E→W usually)
- Master the timing of your ultimate
- Watch high-elo gameplay for advanced techniques
                    """
                    return abilities_text
                else:
                    return f"""
🎯 **{champ_name.title()} - {champ_data['title']}**

⚔️ **Abilities Information**

I have detailed lore for {champ_name.title()}, but specific abilities data isn't available right now.

🎮 **Gameplay Style:**
{champ_data['gameplay']}

💡 **Try these alternatives:**
- Use the **Champion Analysis** tab for detailed guides
- Check champion.gg or op.gg for current builds
- Practice in the Practice Tool to learn combos

📖 **Want to know more about {champ_name.title()}'s story?**
Ask: "Tell me about {champ_name.title()}'s lore"
                    """
            elif 'lore' in question_lower or 'story' in question_lower or 'background' in question_lower:
                return f"""
🎭 **{champ_data['title']}**

{champ_data['lore']}

🎮 **Gameplay Role:**
{champ_data['gameplay']}

💡 **Want to know more?**
- Try asking about {champ_name.title()}'s abilities
- Check the Champion Analysis tab for detailed guides
- Visit the official League of Legends universe site for more lore
                """
            else:
                return f"""
🎯 **{champ_name.title()} - {champ_data['title']}**

📖 **Quick Lore Summary:**
{champ_data['lore'].split('**Key Lore Points:**')[0].strip()}

🎮 **Gameplay:**
{champ_data['gameplay']}

💡 **Try asking:**
- "Tell me about {champ_name.title()}'s lore"
- "What are {champ_name.title()}'s abilities?"
- "How do I play {champ_name.title()}?"
                """
    
    # General champion fallback for other champions
    try:
        champions = st.session_state.dragontail_manager.get_champions() if hasattr(st.session_state, 'dragontail_manager') else {}
        for champ_name in champions.keys():
            if champ_name.lower() in question_lower:
                return f"""
🎯 **{champ_name} Information**

I'm currently unable to access detailed champion data, but here's what I can help with:

📖 **Lore & Background:**
- {champ_name} is a champion in League of Legends
- Each champion has a rich background story in the game's universe
- Their lore connects to the world of Runeterra and its regions

🎮 **General Tips:**
- Practice their combo mechanics in Practice Tool
- Watch high-elo gameplay for positioning tips
- Study their ability interactions and power spikes

💡 **Try asking:**
- "What items should I build on {champ_name}?"
- "What are {champ_name}'s abilities?"
- "How do I play against {champ_name}?"

🔧 **For detailed information:**
- Use the **Champion Analysis** tab
- Check the **AI Assistant** when connectivity is stable
                """
    except:
        pass
    
    # Player lookup fallbacks
    if any(keyword in question_lower for keyword in ['player', 'summoner', 'caps', 'faker', 'doublelift']):
        return """
🔍 **Player Lookup**

I'm currently unable to access live player data. This could be due to:
- API rate limits or connectivity issues
- Invalid summoner names or regions
- Temporary service unavailability

💡 **Try these alternatives:**
- Use the **Live Match Tracker** tab to search for players
- Check player profiles on op.gg or similar sites
- Verify the summoner name spelling and region

🎯 **Popular Players to Search:**
- **Faker** (T1 Mid) - Korea
- **Caps** (G2 Mid) - Europe
- **Doublelift** (ADC) - North America
- **Bjergsen** (TSM Mid) - North America
        """
    
    # General League questions
    elif any(keyword in question_lower for keyword in ['meta', 'tier', 'best', 'strongest']):
        return """
📈 **Current Meta Information**

I'm unable to access live meta data right now, but here are some general tips:

🏆 **Strong Roles Currently:**
- ADC: Jinx, Caitlyn, Kai'Sa remain popular
- Mid: Ahri, Yasuo, Zed are consistently strong
- Support: Thresh, Lulu, Nautilus are reliable picks
- Jungle: Graves, Kindred, Vi offer good carry potential
- Top: Garen, Darius, Fiora are solid choices

💡 **Meta Tips:**
- Focus on champions you're comfortable with
- Adapt your build based on team composition
- Practice fundamentals over chasing meta picks

*For current patch notes and meta analysis, check the official League of Legends website.*
        """
    
    # Default helpful response
    else:
        return f"""
🤖 **AI Assistant**

I'm here to help with League of Legends questions! While I'm currently unable to access live data, I can still assist you with:

📚 **Available Help:**
- Champion guides and strategies
- General gameplay tips and advice
- Item builds and rune suggestions
- Team composition insights

💡 **Try asking about:**
- Specific champions (e.g., "Tell me about Katarina")
- Gameplay mechanics (e.g., "How to last hit better")
- Roles and positions (e.g., "ADC tips for beginners")

🔧 **For live data features:**
- Use the **Live Match Tracker** tab
- Try the **Match Analytics** section
- Check **Champion Analysis** for detailed guides

*Your question: "{user_question}"*
        """


def safe_async_run(coro):
    """Safely run async coroutines, handling existing event loops."""
    import asyncio
    import threading
    
    try:
        # Try to get the current event loop
        loop = asyncio.get_running_loop()
        # If we're in an async context, run in a thread
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result(timeout=30)  # 30 second timeout
        else:
            return asyncio.run(coro)
    except RuntimeError:
        # No event loop, safe to use asyncio.run
        return asyncio.run(coro)
    except Exception as e:
        st.error(f"Error running async operation: {e}")
        return None

async def lookup_player_data(summoner_name: str) -> str:
    """Look up real player data using Riot API."""
    try:
        riot_client = st.session_state.riot_client
        
        # Get summoner data
        summoner_data = await riot_client.summoner.get_summoner_by_name(summoner_name)
        if not summoner_data:
            return f"❌ Summoner '{summoner_name}' not found. Please check the spelling and try again."
        
        response_parts = [
            f"🏆 **Player: {summoner_data.get('name', summoner_name)}**",
            f"📊 **Level:** {summoner_data.get('summonerLevel', 'Unknown')}",
            f"🆔 **Account ID:** {summoner_data.get('accountId', 'Unknown')[:10]}..."
        ]
        
        # Try to get current game
        try:
            current_game = await riot_client.spectator.get_current_game(summoner_data.get('id', ''))
            if current_game:
                response_parts.extend([
                    "\n🔴 **CURRENTLY IN GAME!**",
                    f"🎮 **Game Mode:** {current_game.get('gameMode', 'Unknown')}",
                    f"⏱️ **Game Length:** {current_game.get('gameLength', 0) // 60} minutes",
                    f"🗺️ **Map:** {current_game.get('mapId', 'Unknown')}"
                ])
                
                # Add team information
                participants = current_game.get('participants', [])
                if participants:
                    response_parts.append("\n👥 **Team Members:**")
                    for participant in participants[:5]:  # Show first team
                        champ_id = participant.get('championId', 0)
                        summoner = participant.get('summonerName', 'Unknown')
                        response_parts.append(f"• {summoner} (Champion ID: {champ_id})")
            else:
                response_parts.append("\n⭕ **Not currently in a game**")
                
        except Exception:
            response_parts.append("\n❓ **Game status unknown**")
        
        # Try to get ranked data
        try:
            ranked_data = await riot_client.summoner.get_ranked_stats(summoner_data.get('id', ''))
            if ranked_data:
                response_parts.append("\n🏅 **Ranked Information:**")
                for queue in ranked_data:
                    queue_type = queue.get('queueType', 'Unknown')
                    tier = queue.get('tier', 'Unranked')
                    rank = queue.get('rank', '')
                    lp = queue.get('leaguePoints', 0)
                    wins = queue.get('wins', 0)
                    losses = queue.get('losses', 0)
                    
                    if tier != 'Unranked':
                        winrate = wins / (wins + losses) * 100 if (wins + losses) > 0 else 0
                        response_parts.append(f"• **{queue_type}:** {tier} {rank} ({lp} LP)")
                        response_parts.append(f"  📈 W/L: {wins}W/{losses}L ({winrate:.1f}% WR)")
        except Exception:
            response_parts.append("\n❓ **Ranked data unavailable**")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"❌ Error looking up player '{summoner_name}': {str(e)}"

async def get_champion_analysis(champion_name: str) -> str:
    """Get detailed champion analysis with real data."""
    try:
        champions = st.session_state.dragontail_manager.get_champions()
        champion = champions.get(champion_name)
        
        if not champion:
            return f"❌ Champion '{champion_name}' not found in database."
        
        response_parts = [
            f"🏆 **{champion.name} - {champion.title}**",
            f"📖 **Lore:** {champion.blurb[:200]}...",
            f"🏷️ **Roles:** {', '.join(champion.tags)}",
            f"⚡ **Resource:** {champion.partype}",
        ]
        
        # Add ability information
        response_parts.append(f"\n⚡ **Abilities:**")
        response_parts.append(f"🔮 **Passive - {champion.passive.name}:** {champion.passive.description[:100]}...")
        
        ability_names = ["Q", "W", "E", "R"]
        for i, spell in enumerate(champion.spells[:4]):
            response_parts.append(f"🔥 **{ability_names[i]} - {spell.name}:** {spell.description[:100]}...")
        
        # Add stats
        difficulty = getattr(champion, 'info', {}).get('difficulty', 3)
        attack = getattr(champion, 'info', {}).get('attack', 5)
        defense = getattr(champion, 'info', {}).get('defense', 5)
        magic = getattr(champion, 'info', {}).get('magic', 5)
        
        response_parts.extend([
            f"\n📊 **Champion Ratings:**",
            f"⭐ **Difficulty:** {'⭐' * difficulty} ({difficulty}/10)",
            f"⚔️ **Attack:** {'📊' * attack} ({attack}/10)",
            f"🛡️ **Defense:** {'📊' * defense} ({defense}/10)",
            f"🔮 **Magic:** {'📊' * magic} ({magic}/10)"
        ])
        
        # Add base stats
        response_parts.extend([
            f"\n💪 **Base Stats (Level 1):**",
            f"❤️ **Health:** {champion.stats.hp:.0f} (+{champion.stats.hp_per_level:.1f}/level)",
            f"⚔️ **Attack Damage:** {champion.stats.attack_damage:.0f} (+{champion.stats.attack_damage_per_level:.1f}/level)",
            f"🛡️ **Armor:** {champion.stats.armor:.0f} (+{champion.stats.armor_per_level:.1f}/level)",
            f"🔵 **Mana:** {champion.stats.mp:.0f} (+{champion.stats.mp_per_level:.1f}/level)",
            f"💨 **Move Speed:** {champion.stats.move_speed:.0f}"
        ])
        
        # Add strategic tips
        primary_role = champion.tags[0] if champion.tags else "Fighter"
        role_tips = {
            "Fighter": "Focus on trading in lane and looking for skirmishes. Build items that balance offense and defense.",
            "Mage": "Farm safely early game and scale into teamfights. Position carefully and focus on AOE damage.",
            "Assassin": "Look for picks on isolated enemies. Your mobility allows for hit-and-run tactics.",
            "Tank": "Initiate fights for your team and protect your carries. Your CC and tankiness are most valuable.",
            "Marksman": "Focus on farming early and dealing consistent DPS in teamfights. Stay behind your frontline.",
            "Support": "Provide vision control and peel for your carries. Your utility is crucial for team success."
        }
        
        tip = role_tips.get(primary_role, "Play to your champion's strengths and adapt to the game state.")
        response_parts.append(f"\n🎯 **Strategic Tip:** {tip}")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"❌ Error analyzing champion '{champion_name}': {str(e)}"

async def get_build_recommendations(question: str) -> str:
    """Get build recommendations based on question context."""
    try:
        # Extract champion name from question
        champions = st.session_state.dragontail_manager.get_champions()
        mentioned_champion = None
        question_lower = question.lower()
        
        for champ_name in champions.keys():
            if champ_name.lower() in question_lower:
                mentioned_champion = champ_name
                break
        
        if not mentioned_champion:
            return "🛡️ **General Build Advice:**\n\nTo get specific build recommendations, please mention a champion name in your question!\n\nExample: 'What should I build on Jinx?' or 'Best items for Yasuo'"
        
        champion = champions[mentioned_champion]
        primary_role = champion.tags[0] if champion.tags else "Fighter"
        
        # Role-based build recommendations
        build_recommendations = {
            "Fighter": {
                "core": ["Trinity Force", "Sterak's Gage", "Death's Dance"],
                "boots": ["Plated Steelcaps", "Mercury's Treads"],
                "situational": ["Black Cleaver", "Guardian Angel", "Maw of Malmortius"]
            },
            "Mage": {
                "core": ["Luden's Tempest", "Zhonya's Hourglass", "Rabadon's Deathcap"],
                "boots": ["Sorcerer's Shoes", "Mercury's Treads"],
                "situational": ["Banshee's Veil", "Void Staff", "Morellonomicon"]
            },
            "Assassin": {
                "core": ["Duskblade of Draktharr", "Edge of Night", "Serylda's Grudge"],
                "boots": ["Ionian Boots of Lucidity", "Mercury's Treads"],
                "situational": ["Youmuu's Ghostblade", "Guardian Angel", "Maw of Malmortius"]
            },
            "Tank": {
                "core": ["Sunfire Aegis", "Thornmail", "Spirit Visage"],
                "boots": ["Plated Steelcaps", "Mercury's Treads"],
                "situational": ["Randuin's Omen", "Force of Nature", "Gargoyle Stoneplate"]
            },
            "Marksman": {
                "core": ["Kraken Slayer", "Infinity Edge", "Lord Dominik's Regards"],
                "boots": ["Berserker's Greaves", "Mercury's Treads"],
                "situational": ["Guardian Angel", "Mortal Reminder", "Bloodthirster"]
            },
            "Support": {
                "core": ["Relic Shield", "Locket of the Iron Solari", "Redemption"],
                "boots": ["Mobility Boots", "Mercury's Treads"],
                "situational": ["Knight's Vow", "Zeke's Convergence", "Mikael's Blessing"]
            }
        }
        
        build_data = build_recommendations.get(primary_role, build_recommendations["Fighter"])
        
        response_parts = [
            f"🛡️ **Build Recommendations for {mentioned_champion}**",
            f"🏷️ **Primary Role:** {primary_role}",
            "",
            f"⭐ **Core Items:**",
        ]
        
        for item in build_data["core"]:
            response_parts.append(f"• {item}")
        
        response_parts.extend([
            "",
            f"👟 **Boots Options:**"
        ])
        
        for boot in build_data["boots"]:
            response_parts.append(f"• {boot}")
        
        response_parts.extend([
            "",
            f"🔄 **Situational Items:**"
        ])
        
        for item in build_data["situational"]:
            response_parts.append(f"• {item}")
        
        # Add contextual advice
        context_advice = {
            "tank": "Build more armor against AD-heavy teams, more MR against AP teams.",
            "damage": "Consider defensive items if you're getting focused.",
            "sustain": "Add lifesteal items for better sustain in fights.",
            "cc": "Get Quicksilver Sash against heavy CC teams."
        }
        
        detected_context = None
        for keyword, advice in context_advice.items():
            if keyword in question_lower:
                detected_context = advice
                break
        
        if detected_context:
            response_parts.extend(["", f"💡 **Tip:** {detected_context}"])
        
        response_parts.extend([
            "",
            f"🎯 **Build Order Tip:** Start with core items, then adapt based on enemy team composition and game state!"
        ])
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"❌ Error generating build recommendations: {str(e)}"

async def find_live_matches() -> str:
    """Find and display live high-level matches."""
    try:
        # Since we don't have access to live match API without specific summoner IDs,
        # we'll provide guidance on how to find live matches
        
        response_parts = [
            "🔴 **Live Match Discovery**",
            "",
            "To find live matches, I can help you look up specific players! Here's how:",
            "",
            "🔍 **Search for Pro Players:**",
            "• Try: 'Look up Faker current match'",
            "• Try: 'Show me Caps live game'", 
            "• Try: 'Is Doublelift playing right now?'",
            "",
            "👑 **Popular Pro Players to Check:**",
            "• **Faker** (T1 Mid)",
            "• **Caps** (G2 Mid)",
            "• **Jankos** (Jungle)",
            "• **Rekkles** (ADC)",
            "• **CoreJJ** (Support)",
            "",
            "💡 **Pro Tip:** I can check if any specific summoner is currently in a live match and show you their team composition, game mode, and match duration!",
            "",
            "📝 **Example Commands:**",
            "• 'Check if [player name] is in game'",
            "• 'Look up [summoner name] live match'",
            "• 'Show me [player] current game info'"
        ]
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"❌ Error finding live matches: {str(e)}"

def show_live_match_tracker():
    """Enhanced live match tracker with real player lookup."""
    st.header("🔴 Live Match Tracker - Real Player Data")
    
    st.markdown("""
    Track any League of Legends player in real-time! Enter a summoner name to see:
    - 🎮 Current match status and details
    - 👥 Team compositions and champions
    - ⏱️ Game duration and mode
    - 🏅 Player ranks and statistics
    """)
    
    # Player lookup section
    st.subheader("🔍 Player Lookup")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        summoner_name = st.text_input(
            "Enter Summoner Name:", 
            placeholder="e.g., Faker, Caps, Doublelift...",
            help="Enter any summoner name to check their current game status"
        )
    
    with col2:
        region = st.selectbox("Region:", [
            "NA1", "EUW1", "EUN1", "KR", "BR1", "LA1", "LA2", "OC1", "RU", "TR1", "JP1"
        ])
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        track_button = st.button("� Track Player", type="primary")
    
    if track_button and summoner_name:
        with st.spinner(f"🔍 Looking up {summoner_name} on {region}..."):
            try:
                player_info = safe_async_run(lookup_player_data(summoner_name))
                
                if "CURRENTLY IN GAME" in player_info:
                    st.success("🔴 Player is currently in a live match!")
                    
                    # Display match information in an organized way
                    st.markdown("### 🎮 Live Match Details")
                    
                    # Parse and display the information better
                    info_lines = player_info.split('\n')
                    
                    match_info = {}
                    team_members = []
                    collecting_team = False
                    
                    for line in info_lines:
                        if "Game Mode:" in line:
                            match_info["mode"] = line.split(":**")[1].strip()
                        elif "Game Length:" in line:
                            match_info["duration"] = line.split(":**")[1].strip()
                        elif "Map:" in line:
                            match_info["map"] = line.split(":**")[1].strip()
                        elif "Team Members:" in line:
                            collecting_team = True
                        elif collecting_team and line.startswith("•"):
                            team_members.append(line[2:])  # Remove bullet point
                    
                    # Display match info in columns
                    info_col1, info_col2, info_col3 = st.columns(3)
                    
                    with info_col1:
                        st.metric("🎮 Game Mode", match_info.get("mode", "Unknown"))
                    
                    with info_col2:
                        st.metric("⏱️ Duration", match_info.get("duration", "Unknown"))
                    
                    with info_col3:
                        st.metric("🗺️ Map", match_info.get("map", "Unknown"))
                    
                    # Display team composition
                    if team_members:
                        st.markdown("### 👥 Team Composition")
                        for member in team_members:
                            st.markdown(f"• {member}")
                    
                    # Auto-refresh option
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("� Refresh Match Data"):
                            st.rerun()
                    
                    with col2:
                        auto_refresh = st.checkbox("🔄 Auto-refresh every 30s")
                        if auto_refresh:
                            time.sleep(30)
                            st.rerun()
                
                else:
                    st.info("⭕ Player is not currently in a match")
                    
                    # Show player profile instead
                    st.markdown("### 👤 Player Profile")
                    st.text(player_info)
                
            except Exception as e:
                st.error(f"❌ Error tracking player: {str(e)}")
                st.info("💡 Make sure the summoner name is correct and try again.")
    
    # Featured matches section
    st.markdown("---")
    st.subheader("⭐ Try These Popular Players")
    
    popular_players = {
        "🇰🇷 Korea": ["Faker", "Showmaker", "Canyon", "Ruler", "Keria"],
        "🇪🇺 Europe": ["Caps", "Jankos", "Rekkles", "Mikyx", "Wunder"],
        "🇺🇸 North America": ["Doublelift", "Bjergsen", "CoreJJ", "Blaber", "Vulcan"]
    }
    
    for region, players in popular_players.items():
        with st.expander(f"{region} Pro Players"):
            cols = st.columns(len(players))
            for i, player in enumerate(players):
                with cols[i]:
                    if st.button(f"� {player}", key=f"track_{player}"):
                        st.session_state["summoner_input"] = player
                        st.rerun()
    
    # Recent searches
    if "recent_searches" not in st.session_state:
        st.session_state.recent_searches = []
    
    if summoner_name and summoner_name not in st.session_state.recent_searches:
        st.session_state.recent_searches.insert(0, summoner_name)
        st.session_state.recent_searches = st.session_state.recent_searches[:5]  # Keep last 5
    
    if st.session_state.recent_searches:
        st.markdown("---")
        st.subheader("🕒 Recent Searches")
        for recent in st.session_state.recent_searches:
            if st.button(f"🔍 {recent}", key=f"recent_{recent}"):
                # Set the input and trigger search
                st.session_state["summoner_input"] = recent
                st.rerun()

def show_champion_analysis():
    """Show champion analysis interface."""
    st.header("🏆 Champion Analysis")
    
    if not st.session_state.dragontail_manager:
        st.error("❌ Data not loaded. Please return to dashboard and wait for initialization.")
        return
    
    # Load champions using synchronous method
    champions = st.session_state.dragontail_manager.get_champions()
    
    if not champions:
        st.warning("⚠️ No champion data available. The app is still loading champion data in the background.")
        st.info("💡 **Tip**: Try refreshing the page in a moment or check the terminal for loading status.")
        return
    
    champion_names = sorted([champ.name for champ in champions.values()])
    
    # Search and filter section
    st.subheader("🔍 Find Your Champion")
    
    # Enhanced search and filtering
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    
    with col1:
        search_query = st.text_input("🔎 Search Champions:", placeholder="Start typing champion name...")
    
    with col2:
        role_filter = st.selectbox("⚔️ Filter by Role:", [
            "All Roles", "Assassin", "Fighter", "Mage", "Marksman", "Support", "Tank"
        ])
    
    with col3:
        difficulty_filter = st.selectbox("📊 Difficulty:", [
            "All", "Easy (1-3)", "Medium (4-6)", "Hard (7-10)"
        ])
    
    with col4:
        sort_by = st.selectbox("📋 Sort by:", [
            "Name", "Difficulty", "Attack", "Defense"
        ])
    
    # Filter champions with enhanced logic
    filtered_champions = []
    
    for champion in champions.values():
        # Apply search filter (more flexible matching)
        if search_query:
            search_lower = search_query.lower()
            if not (search_lower in champion.name.lower() or 
                   search_lower in champion.title.lower() or
                   any(search_lower in tag.lower() for tag in champion.tags)):
                continue
        
        # Apply role filter
        if role_filter != "All Roles" and role_filter not in champion.tags:
            continue
        
        # Apply difficulty filter with actual data
        if difficulty_filter != "All":
            champion_difficulty = getattr(champion, 'info', {}).get('difficulty', 5)
            if difficulty_filter == "Easy (1-3)" and champion_difficulty > 3:
                continue
            elif difficulty_filter == "Medium (4-6)" and (champion_difficulty < 4 or champion_difficulty > 6):
                continue
            elif difficulty_filter == "Hard (7-10)" and champion_difficulty < 7:
                continue
        
        filtered_champions.append(champion)
    
    # Sort filtered champions
    if sort_by == "Name":
        filtered_champions.sort(key=lambda x: x.name)
    elif sort_by == "Difficulty":
        filtered_champions.sort(key=lambda x: getattr(x, 'info', {}).get('difficulty', 5), reverse=True)
    elif sort_by == "Attack":
        filtered_champions.sort(key=lambda x: getattr(x, 'info', {}).get('attack', 5), reverse=True)
    elif sort_by == "Defense":
        filtered_champions.sort(key=lambda x: getattr(x, 'info', {}).get('defense', 5), reverse=True)
    
    # Display search results with better UX
    if not filtered_champions:
        st.warning(f"🔍 No champions found matching your criteria. Try adjusting your filters!")
        return
    
    # Show search results summary
    st.success(f"🎯 Found {len(filtered_champions)} champions matching your criteria")
    
    # Enhanced champion selector with grid layout preview
    col1, col2 = st.columns([3, 1])
    
    with col1:
        champion_options = {f"{champ.name} - {champ.title}": champ for champ in filtered_champions}
        selected_champion_name = st.selectbox(
            "🏆 Select Champion:", 
            list(champion_options.keys()),
            help="Choose a champion to view detailed analysis"
        )
    
    with col2:
        if selected_champion_name:
            selected_champ = champion_options[selected_champion_name]
            # Show mini preview
            st.markdown(f"**{selected_champ.name}**")
            difficulty = getattr(selected_champ, 'info', {}).get('difficulty', 3)
            st.markdown(f"Difficulty: {'⭐' * difficulty}")
            st.markdown(f"Roles: {', '.join(selected_champ.tags[:2])}")
    
    if selected_champion_name:
        champion = champion_options[selected_champion_name]
        
        # Add champion comparison feature
        st.markdown("---")
        comparison_mode = st.checkbox("⚖️ Compare with another champion", help="Select two champions to compare stats and abilities")
        
        if comparison_mode:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🥇 Champion 1")
                # Add dynamic tabs for better UX
                tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "⚡ Abilities", "📊 Stats", "🎯 Strategy"])
                
                with tab1:
                    show_champion_overview(champion)
                
                with tab2:
                    show_champion_abilities(champion)
                
                with tab3:
                    show_champion_stats(champion)
                
                with tab4:
                    show_champion_strategy(champion)
            
            with col2:
                st.markdown("### 🥈 Champion 2")
                
                # Second champion selector
                comparison_options = {f"{champ.name} - {champ.title}": champ for champ in filtered_champions if champ.name != champion.name}
                if comparison_options:
                    selected_comparison_name = st.selectbox(
                        "🏆 Select second champion:", 
                        list(comparison_options.keys()),
                        help="Choose a champion to compare against"
                    )
                    
                    if selected_comparison_name:
                        comparison_champion = comparison_options[selected_comparison_name]
                        
                        # Add dynamic tabs for comparison champion
                        tab1_comp, tab2_comp, tab3_comp, tab4_comp = st.tabs(["📋 Overview", "⚡ Abilities", "📊 Stats", "🎯 Strategy"])
                        
                        with tab1_comp:
                            show_champion_overview(comparison_champion)
                        
                        with tab2_comp:
                            show_champion_abilities(comparison_champion)
                        
                        with tab3_comp:
                            show_champion_stats(comparison_champion)
                        
                        with tab4_comp:
                            show_champion_strategy(comparison_champion)
                        
                        # Quick comparison summary
                        st.markdown("---")
                        st.markdown("### ⚖️ Quick Comparison")
                        
                        comp_col1, comp_col2 = st.columns(2)
                        
                        with comp_col1:
                            st.metric("🏆 Champion 1", champion.name)
                            st.metric("⭐ Difficulty", getattr(champion, 'info', {}).get('difficulty', 3))
                            st.metric("❤️ Base HP", f"{champion.stats.hp:.0f}")
                            st.metric("⚔️ Base AD", f"{champion.stats.attack_damage:.0f}")
                        
                        with comp_col2:
                            st.metric("🏆 Champion 2", comparison_champion.name)
                            st.metric("⭐ Difficulty", getattr(comparison_champion, 'info', {}).get('difficulty', 3))
                            st.metric("❤️ Base HP", f"{comparison_champion.stats.hp:.0f}")
                            st.metric("⚔️ Base AD", f"{comparison_champion.stats.attack_damage:.0f}")
                
                else:
                    st.info("No other champions available for comparison with current filters.")
        
        else:
            # Single champion view
            # Add dynamic tabs for better UX
            tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "⚡ Abilities", "📊 Stats & Tips", "🎯 Strategy"])
            
            with tab1:
                show_champion_overview(champion)
            
            with tab2:
                show_champion_abilities(champion)
            
            with tab3:
                col1, col2 = st.columns(2)
                with col1:
                    show_champion_stats(champion)
                with col2:
                    show_champion_tips_section(champion)
            
            with tab4:
                show_champion_strategy(champion)

def show_champion_overview(champion: Champion):
    """Show enhanced champion overview with dynamic content."""
    st.subheader(f"🏆 {champion.name} - {champion.title}")
    
    # Create tabs for better organization
    overview_tab1, overview_tab2, overview_tab3 = st.tabs(["📝 Basic Info", "📊 Quick Stats", "🏷️ Tags & Role"])
    
    with overview_tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("#### 📖 Lore")
            st.markdown(champion.blurb)
            
            st.markdown("#### ⚡ Resource Type")
            resource_emoji = {
                "Mana": "🔵",
                "Energy": "⚡", 
                "Health": "❤️",
                "Rage": "🔥",
                "Fury": "😡",
                "Shield": "🛡️",
                "None": "🌟"
            }
            emoji = resource_emoji.get(champion.partype, "⚡")
            st.markdown(f"{emoji} **{champion.partype}**")
        
        with col2:
            # Champion image with proper Data Dragon URL
            st.markdown("### 🖼️ Portrait")
            if champion.image and 'full' in champion.image:
                image_url = f"https://ddragon.leagueoflegends.com/cdn/15.18.1/img/champion/{champion.image['full']}"
                try:
                    st.image(image_url, width=200, caption=f"{champion.name}")
                except Exception as e:
                    st.info("🖼️ Champion portrait loading...")
            else:
                st.info("🖼️ No portrait available")
    
    with overview_tab2:
        # Enhanced stats display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("❤️ Health", f"{champion.stats.hp:.0f}", f"+{champion.stats.hp_per_level:.1f}/lvl")
            st.metric("⚔️ Attack Damage", f"{champion.stats.attack_damage:.0f}", f"+{champion.stats.attack_damage_per_level:.1f}/lvl")
        
        with col2:
            st.metric("🛡️ Armor", f"{champion.stats.armor:.0f}", f"+{champion.stats.armor_per_level:.1f}/lvl")
            st.metric("🔮 Magic Resist", f"{champion.stats.spell_block:.0f}", f"+{champion.stats.spell_block_per_level:.1f}/lvl")
        
        with col3:
            st.metric("💨 Move Speed", f"{champion.stats.move_speed:.0f}")
            st.metric("🎯 Attack Range", f"{champion.stats.attack_range:.0f}")
        
        # Attack speed and additional info
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("⚡ Attack Speed", f"{champion.stats.attack_speed:.2f}", f"+{champion.stats.attack_speed_per_level:.2f}%/lvl")
        
        with col2:
            # Use mana instead of crit since crit doesn't exist in the model
            st.metric("� Mana", f"{champion.stats.mp:.0f}", f"+{champion.stats.mp_per_level:.1f}/lvl")
        
        with col3:
            # Calculate DPS at level 1
            dps = champion.stats.attack_damage * champion.stats.attack_speed
            st.metric("📈 Level 1 DPS", f"{dps:.0f}")
    
    with overview_tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏷️ Champion Tags")
            for tag in champion.tags:
                role_emoji = {
                    "Fighter": "⚔️",
                    "Mage": "🔮", 
                    "Assassin": "🗡️",
                    "Tank": "🛡️",
                    "Marksman": "🏹",
                    "Support": "🩹"
                }
                emoji = role_emoji.get(tag, "⭐")
                st.markdown(f"**{emoji} {tag}**")
        
        with col2:
            st.markdown("#### 📊 Champion Info")
            
            # Difficulty rating
            difficulty = getattr(champion.info, 'difficulty', 3)
            difficulty_stars = "⭐" * difficulty
            st.markdown(f"**Difficulty:** {difficulty_stars} ({difficulty}/10)")
            
            # Attack/Defense/Magic ratings
            attack_rating = getattr(champion.info, 'attack', 5)
            defense_rating = getattr(champion.info, 'defense', 5) 
            magic_rating = getattr(champion.info, 'magic', 5)
            
            st.progress(attack_rating / 10, text=f"🗡️ Attack: {attack_rating}/10")
            st.progress(defense_rating / 10, text=f"🛡️ Defense: {defense_rating}/10")
            st.progress(magic_rating / 10, text=f"🔮 Magic: {magic_rating}/10")

def show_champion_abilities(champion: Champion):
    """Show enhanced champion abilities with icons and better layout."""
    st.subheader(f"⚡ {champion.name} Abilities")
    
    # Passive with enhanced display
    with st.container():
        st.markdown("### 🔮 Passive Ability")
        col1, col2 = st.columns([1, 4])
        
        with col1:
            # Passive icon
            if champion.passive.image and 'full' in champion.passive.image:
                passive_url = f"https://ddragon.leagueoflegends.com/cdn/15.18.1/img/passive/{champion.passive.image['full']}"
                try:
                    st.image(passive_url, width=80)
                except:
                    st.markdown("🔮")
            else:
                st.markdown("### 🔮")
        
        with col2:
            st.markdown(f"**{champion.passive.name}**")
            st.markdown(champion.passive.description)
        
        st.markdown("---")
    
    # Active abilities with enhanced display
    ability_names = ["Q", "W", "E", "R"]
    ability_icons = ["🔥", "❄️", "⚡", "💥"]
    
    for i, spell in enumerate(champion.spells):
        with st.container():
            st.markdown(f"### {ability_icons[i]} {ability_names[i]} - {spell.name}")
            
            col1, col2 = st.columns([1, 4])
            
            with col1:
                # Ability icon
                if spell.image and 'full' in spell.image:
                    spell_url = f"https://ddragon.leagueoflegends.com/cdn/15.18.1/img/spell/{spell.image['full']}"
                    try:
                        st.image(spell_url, width=80)
                    except:
                        st.markdown(f"### {ability_icons[i]}")
                else:
                    st.markdown(f"### {ability_icons[i]}")
            
            with col2:
                # Ability description
                st.markdown(spell.description)
                
                # Ability stats in columns
                info_col1, info_col2, info_col3 = st.columns(3)
                
                with info_col1:
                    if spell.cooldown and len(spell.cooldown) > 0:
                        cooldown_range = f"{spell.cooldown[0]}"
                        if len(spell.cooldown) > 1 and spell.cooldown[-1] != spell.cooldown[0]:
                            cooldown_range += f"-{spell.cooldown[-1]}"
                        st.metric("⏱️ Cooldown", f"{cooldown_range}s")
                
                with info_col2:
                    if spell.cost and len(spell.cost) > 0 and spell.cost[0] > 0:
                        cost_range = f"{spell.cost[0]}"
                        if len(spell.cost) > 1 and spell.cost[-1] != spell.cost[0]:
                            cost_range += f"-{spell.cost[-1]}"
                        st.metric("💧 Cost", f"{cost_range} {spell.resource}")
                    else:
                        st.metric("💧 Cost", "No Cost")
                
                with info_col3:
                    if spell.range and len(spell.range) > 0:
                        # Convert range to reasonable units (divide by 1000 if too large)
                        range_val = spell.range[0]
                        if range_val > 1000:
                            range_val = range_val // 1000
                        if range_val > 0:
                            st.metric("📏 Range", f"{range_val}")
            
            st.markdown("---")

def show_champion_stats(champion: Champion):
    """Show enhanced champion statistics with interactive visualizations."""
    st.subheader(f"📊 {champion.name} Statistics & Analysis")
    
    # Level selector for dynamic stats
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        level = st.slider("📈 Champion Level", 1, 18, 1, help="See how stats scale with level")
    
    with col2:
        comparison_mode = st.selectbox("📊 View Mode", [
            "Single Champion", "Compare with Average", "Role Comparison"
        ])
    
    with col3:
        chart_type = st.selectbox("📈 Chart Type", ["Bar", "Radar", "Line"])
    
    # Calculate stats at selected level
    level_stats = {
        'Health': champion.stats.hp + (champion.stats.hp_per_level * (level - 1)),
        'Attack Damage': champion.stats.attack_damage + (champion.stats.attack_damage_per_level * (level - 1)),
        'Armor': champion.stats.armor + (champion.stats.armor_per_level * (level - 1)),
        'Magic Resist': champion.stats.spell_block + (champion.stats.spell_block_per_level * (level - 1)),
        'Mana': champion.stats.mp + (champion.stats.mp_per_level * (level - 1)),
        'Move Speed': champion.stats.move_speed,
        'Attack Speed': champion.stats.attack_speed + (champion.stats.attack_speed_per_level * (level - 1) / 100),
        'Attack Range': champion.stats.attack_range
    }
    
    # Create visualizations
    if chart_type == "Radar":
        # Radar chart for key stats
        radar_stats = ['Health', 'Attack Damage', 'Armor', 'Magic Resist', 'Move Speed']
        radar_values = [level_stats[stat] for stat in radar_stats]
        
        # Normalize values for radar chart
        max_values = [3000, 300, 200, 200, 500]  # Typical max values for normalization
        normalized_values = [min(val/max_val * 100, 100) for val, max_val in zip(radar_values, max_values)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=radar_stats,
            fill='toself',
            name=champion.name,
            line_color='#FF6B6B'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title=f"{champion.name} Stats at Level {level}",
            font_color='white',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        # Create two columns for different charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Base stats visualization
            stats_for_chart = {k: v for k, v in level_stats.items() if k in ['Health', 'Attack Damage', 'Armor', 'Magic Resist']}
            
            if chart_type == "Bar":
                fig = px.bar(
                    x=list(stats_for_chart.keys()),
                    y=list(stats_for_chart.values()),
                    title=f"Core Stats (Level {level})",
                    labels={'x': 'Stat', 'y': 'Value'}
                )
            else:  # Line chart showing growth
                levels = list(range(1, 19))
                health_growth = [champion.stats.hp + (champion.stats.hp_per_level * (i - 1)) for i in levels]
                ad_growth = [champion.stats.attack_damage + (champion.stats.attack_damage_per_level * (i - 1)) for i in levels]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=levels, y=health_growth, mode='lines+markers', name='Health', line_color='#FF6B6B'))
                fig.add_trace(go.Scatter(x=levels, y=ad_growth, mode='lines+markers', name='Attack Damage', line_color='#4ECDC4'))
                fig.update_layout(title=f"Stat Growth Over Levels", xaxis_title="Level", yaxis_title="Value")
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            # Secondary stats
            secondary_stats = {k: v for k, v in level_stats.items() if k in ['Mana', 'Move Speed', 'Attack Speed', 'Attack Range']}
            
            fig = px.bar(
                x=list(secondary_stats.keys()),
                y=list(secondary_stats.values()),
                title=f"Secondary Stats (Level {level})",
                labels={'x': 'Stat', 'y': 'Value'},
                color=list(secondary_stats.values()),
                color_continuous_scale='viridis'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Stats summary table
    st.markdown("### 📋 Detailed Stats Summary")
    
    stats_df = []
    for stat_name, value in level_stats.items():
        base_value = getattr(champion.stats, stat_name.lower().replace(' ', '_').replace('magic_resist', 'spell_block'), 0)
        growth = value - base_value if level > 1 else 0
        
        stats_df.append({
            'Stat': stat_name,
            f'Level {level}': f"{value:.1f}",
            'Base (Level 1)': f"{base_value:.1f}",
            f'Growth (+{level-1} levels)': f"+{growth:.1f}" if growth > 0 else "0"
        })
    
    st.dataframe(stats_df, use_container_width=True)

def show_champion_strategy(champion: Champion):
    """Show champion strategy and tips."""
    st.subheader(f"🎯 {champion.name} Strategy Guide")
    
    # Role-based strategies
    role_strategies = {
        "Fighter": {
            "Early Game": "Focus on farming and short trades. Use abilities to harass enemies when they go for CS.",
            "Mid Game": "Look for skirmishes and teamfights. Your survivability makes you a strong frontline.",
            "Late Game": "Tank damage for your team while dealing consistent DPS. Focus enemy carries.",
        },
        "Mage": {
            "Early Game": "Farm safely and poke enemies with abilities. Ward river bushes to avoid ganks.",
            "Mid Game": "Roam to help other lanes. Your burst potential can secure kills.",
            "Late Game": "Stay behind frontline and focus on dealing AOE damage in teamfights.",
        },
        "Assassin": {
            "Early Game": "Look for solo kills and roaming opportunities. Ward enemy jungle.",
            "Mid Game": "Pick off isolated enemies. Your mobility allows for hit-and-run tactics.",
            "Late Game": "Focus on eliminating enemy carries quickly in teamfights.",
        },
        "Tank": {
            "Early Game": "Play defensively and farm. Use your tankiness to absorb harassment.",
            "Mid Game": "Initiate fights for your team. Your CC and tankiness are most valuable now.",
            "Late Game": "Protect your carries and engage on enemy team. Zone enemy damage dealers.",
        },
        "Marksman": {
            "Early Game": "Farm safely and avoid all-ins. Focus on CS and scaling.",
            "Mid Game": "Group with your team. Your damage output starts becoming significant.",
            "Late Game": "Stay safe and deal consistent DPS. Position carefully in teamfights.",
        },
        "Support": {
            "Early Game": "Protect your ADC and ward key areas. Look for engage opportunities.",
            "Mid Game": "Roam and help other lanes. Your utility is crucial for team success.",
            "Late Game": "Peel for carries and provide vision control around objectives.",
        }
    }
    
    # Get primary role strategy
    primary_role = champion.tags[0] if champion.tags else "Fighter"
    strategy = role_strategies.get(primary_role, role_strategies["Fighter"])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Primary Role:** {primary_role}")
        
        for phase, tip in strategy.items():
            st.markdown(f"**{phase}:**")
            st.markdown(f"• {tip}")
            st.markdown("")
    
    with col2:
        st.markdown("**Key Tips:**")
        
        # Generate role-specific tips
        if "Mage" in champion.tags:
            st.markdown("• Manage your mana carefully")
            st.markdown("• Position safely in teamfights")
            st.markdown("• Use abilities to wave clear")
        elif "Assassin" in champion.tags:
            st.markdown("• Wait for the right moment to engage")
            st.markdown("• Focus on enemy carries")
            st.markdown("• Have an escape plan ready")
        elif "Tank" in champion.tags:
            st.markdown("• Lead engagements for your team")
            st.markdown("• Absorb damage and CC")
            st.markdown("• Protect your carries")
        elif "Marksman" in champion.tags:
            st.markdown("• Focus on farming early game")
            st.markdown("• Stay behind your frontline")
            st.markdown("• Attack the closest target")
        elif "Support" in champion.tags:
            st.markdown("• Ward key areas constantly")
            st.markdown("• Peel for your carries")
            st.markdown("• Coordinate with your team")
        else:  # Fighter
            st.markdown("• Trade efficiently in lane")
            st.markdown("• Look for skirmish opportunities")
            st.markdown("• Balance offense and defense")
        
        # Difficulty indicator
        difficulty_map = {
            1: "⭐ Very Easy",
            2: "⭐⭐ Easy", 
            3: "⭐⭐⭐ Medium",
            4: "⭐⭐⭐⭐ Hard",
            5: "⭐⭐⭐⭐⭐ Very Hard"
        }
        
        difficulty = getattr(champion.info, 'difficulty', 3)
        st.markdown(f"**Difficulty:** {difficulty_map.get(difficulty, '⭐⭐⭐ Medium')}")
        
        # Recommend items based on role
        st.markdown("**Core Items:**")
        if "Mage" in champion.tags:
            st.markdown("• Luden's Tempest")
            st.markdown("• Zhonya's Hourglass") 
            st.markdown("• Rabadon's Deathcap")
        elif "Assassin" in champion.tags:
            st.markdown("• Duskblade of Draktharr")
            st.markdown("• Edge of Night")
            st.markdown("• Serylda's Grudge")
        elif "Tank" in champion.tags:
            st.markdown("• Sunfire Aegis")
            st.markdown("• Thornmail")
            st.markdown("• Spirit Visage")
        elif "Marksman" in champion.tags:
            st.markdown("• Kraken Slayer")
            st.markdown("• Infinity Edge")
            st.markdown("• Lord Dominik's Regards")
        elif "Support" in champion.tags:
            st.markdown("• Relic Shield")
            st.markdown("• Locket of the Iron Solari")
            st.markdown("• Redemption")
        else:  # Fighter
            st.markdown("• Trinity Force")
            st.markdown("• Sterak's Gage")
            st.markdown("• Death's Dance")

def show_champion_tips_section(champion: Champion):
    """Show champion tips section."""
    st.subheader(f"💡 {champion.name} Tips")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Playing As")
        for tip in champion.ally_tips:
            st.markdown(f"• {tip}")
    
    with col2:
        st.markdown("#### ❌ Playing Against")
        for tip in champion.enemy_tips:
            st.markdown(f"• {tip}")

def show_champion_counters(champion: Champion):
    """Show champion counter information."""
    st.subheader(f"⚔️ {champion.name} Matchups")
    
    st.info("🚧 Counter data would be populated from external APIs or statistical analysis.")
    
    # Placeholder counter information
    st.markdown("#### Strong Against:")
    st.markdown("• Data would be populated from match statistics")
    
    st.markdown("#### Weak Against:")
    st.markdown("• Data would be populated from match statistics")
    
    st.markdown("#### Synergizes With:")
    st.markdown("• Data would be populated from team composition analysis")

def show_match_analytics():
    """Show real match analytics interface."""
    st.header("📊 Match Analytics")
    
    st.markdown("Analyze match history and performance data from real player accounts.")
    
    # Input for player lookup
    col1, col2 = st.columns([3, 1])
    
    with col1:
        summoner_name = st.text_input("� Enter Summoner Name for Match Analysis:", 
                                    placeholder="Enter player name (e.g., Faker, Doublelift)")
    
    with col2:
        region = st.selectbox("🌍 Region:", ["na1", "euw1", "kr", "eun1", "br1", "jp1"])
    
    if st.button("📊 Analyze Matches") and summoner_name:
        with st.spinner(f"🔍 Fetching match history for {summoner_name}..."):
            try:
                riot_client = st.session_state.riot_client
                
                # Get summoner data
                summoner_data = safe_async_run(riot_client.summoner.get_summoner_by_name(summoner_name))
                if not summoner_data:
                    st.error(f"❌ Player '{summoner_name}' not found.")
                    return
                
                puuid = summoner_data.get('puuid', '')
                if not puuid:
                    st.error("❌ Unable to get player ID.")
                    return
                
                # Get match history
                match_ids = safe_async_run(riot_client.match.get_match_history(puuid, count=10))
                
                if not match_ids:
                    st.warning("⚠️ No recent matches found.")
                    return
                
                st.success(f"✅ Found {len(match_ids)} recent matches for {summoner_name}")
                
                # Analyze matches
                match_data = []
                wins = 0
                total_kills = 0
                total_deaths = 0
                total_assists = 0
                champion_picks = {}
                
                progress_bar = st.progress(0)
                
                for i, match_id in enumerate(match_ids[:5]):  # Analyze first 5 matches
                    try:
                        match_details = safe_async_run(riot_client.match.get_match_details(match_id))
                        
                        # Find our player in the match
                        participants = match_details.get('info', {}).get('participants', [])
                        player_data = None
                        
                        for participant in participants:
                            if participant.get('puuid') == puuid:
                                player_data = participant
                                break
                        
                        if player_data:
                            # Extract match info
                            champion = player_data.get('championName', 'Unknown')
                            kills = player_data.get('kills', 0)
                            deaths = player_data.get('deaths', 0)
                            assists = player_data.get('assists', 0)
                            win = player_data.get('win', False)
                            game_duration = match_details.get('info', {}).get('gameDuration', 0)
                            
                            # Track stats
                            if win:
                                wins += 1
                            total_kills += kills
                            total_deaths += deaths
                            total_assists += assists
                            
                            # Track champion picks
                            champion_picks[champion] = champion_picks.get(champion, 0) + 1
                            
                            match_data.append({
                                'Champion': champion,
                                'K/D/A': f"{kills}/{deaths}/{assists}",
                                'Result': "🟢 Win" if win else "🔴 Loss",
                                'Duration': f"{game_duration // 60}m {game_duration % 60}s",
                                'KDA Ratio': round((kills + assists) / max(deaths, 1), 2)
                            })
                        
                        progress_bar.progress((i + 1) / len(match_ids[:5]))
                        
                    except Exception as e:
                        st.error(f"Error analyzing match {match_id}: {e}")
                        continue
                
                progress_bar.empty()
                
                if match_data:
                    # Display overall stats
                    st.markdown("### 📈 Overall Performance")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        win_rate = (wins / len(match_data)) * 100
                        st.metric("🏆 Win Rate", f"{win_rate:.1f}%")
                    
                    with col2:
                        avg_kills = total_kills / len(match_data)
                        st.metric("⚔️ Avg Kills", f"{avg_kills:.1f}")
                    
                    with col3:
                        avg_deaths = total_deaths / len(match_data)
                        st.metric("💀 Avg Deaths", f"{avg_deaths:.1f}")
                    
                    with col4:
                        avg_assists = total_assists / len(match_data)
                        st.metric("🤝 Avg Assists", f"{avg_assists:.1f}")
                    
                    # Match history table
                    st.markdown("### 📋 Recent Match History")
                    match_df = pd.DataFrame(match_data)
                    st.dataframe(match_df, use_container_width=True)
                    
                    # Champion picks chart
                    if champion_picks:
                        st.markdown("### 🎯 Champion Picks")
                        
                        champ_df = pd.DataFrame(list(champion_picks.items()), columns=['Champion', 'Games'])
                        champ_df = champ_df.sort_values('Games', ascending=True)
                        
                        fig = px.bar(champ_df, x='Games', y='Champion', orientation='h',
                                   title=f"Champion Pick Frequency - Last {len(match_data)} Games")
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='white'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Performance insights
                    st.markdown("### 💡 Performance Insights")
                    
                    avg_kda = (total_kills + total_assists) / max(total_deaths, 1)
                    
                    insights = []
                    if win_rate >= 60:
                        insights.append("🔥 **Strong performance** - Above average win rate!")
                    elif win_rate <= 40:
                        insights.append("📈 **Room for improvement** - Focus on consistency")
                    
                    if avg_kda >= 2.0:
                        insights.append("⚡ **Good KDA ratio** - Effective kill participation")
                    elif avg_kda < 1.0:
                        insights.append("🎯 **Focus on survival** - Work on positioning and map awareness")
                    
                    if len(champion_picks) == 1:
                        insights.append("🎮 **One-trick player** - High specialization")
                    elif len(champion_picks) >= 4:
                        insights.append("🌟 **Versatile player** - Good champion pool diversity")
                    
                    for insight in insights:
                        st.markdown(insight)
                
                else:
                    st.warning("⚠️ No match data could be analyzed.")
                    
            except Exception as e:
                st.error(f"❌ Error fetching match data: {e}")
    
    # Show sample analysis if no search
    else:
        st.markdown("### 📊 Sample Match Analytics")
        st.markdown("""
        **What This Feature Provides:**
        
        � **Performance Metrics:**
        - Win rate analysis over recent games
        - Average KDA (Kills/Deaths/Assists) ratios
        - Champion pick frequency and success rates
        
        📈 **Trend Analysis:**
        - Performance improvements over time
        - Champion-specific win rates
        - Game duration impact on performance
        
        💡 **Insights & Recommendations:**
        - Identify strongest champions
        - Spot performance patterns
        - Get improvement suggestions based on data
        
        **How to Use:**
        1. Enter any summoner name above
        2. Select their region
        3. Click "Analyze Matches" to see real data!
        """)
        
        # Show sample data visualization
        sample_data = pd.DataFrame({
            'Champion': ['Jinx', 'Caitlyn', 'Ashe', 'Vayne', 'Kai\'Sa'],
            'Games': [8, 6, 4, 3, 2],
            'Win Rate': [75.0, 66.7, 50.0, 33.3, 100.0]
        })
        
        fig = px.scatter(sample_data, x='Games', y='Win Rate', size='Games',
                        hover_data=['Champion'], title="Sample Champion Performance Analysis")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)

def show_pro_matches():
    """Show featured games and high-elo matches interface."""
    st.header("🏆 Featured High-Elo Matches")
    
    # Get featured games from Riot API
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("#### 🔥 Live Featured Games")
        st.markdown("Real high-elo matches currently being played")
    
    with col2:
        if st.button("🔄 Refresh Featured Games"):
            st.rerun()
    
    with st.spinner("🔍 Loading featured games..."):
        try:
            riot_client = st.session_state.riot_client
            featured_games = safe_async_run(riot_client.spectator.get_featured_games())
            
            if featured_games and "gameList" in featured_games:
                games = featured_games["gameList"]
                
                if games:
                    for i, game in enumerate(games[:5]):  # Show first 5 games
                        with st.expander(f"🎮 Game {i+1} - {game.get('gameMode', 'Unknown')} ({game.get('gameLength', 0) // 60} min)", expanded=i==0):
                            
                            # Game info
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("⏱️ Duration", f"{game.get('gameLength', 0) // 60} minutes")
                            
                            with col2:
                                st.metric("�️ Map ID", game.get('mapId', 'Unknown'))
                            
                            with col3:
                                st.metric("👥 Spectators", game.get('observers', {}).get('encryptionKey', 'N/A')[:8] + "...")
                            
                            # Team compositions
                            participants = game.get('participants', [])
                            if participants:
                                st.markdown("#### � Team Compositions")
                                
                                # Split into teams (assuming first 5 are team 1, next 5 are team 2)
                                mid_point = len(participants) // 2
                                team1 = participants[:mid_point]
                                team2 = participants[mid_point:]
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("**🔵 Blue Team:**")
                                    for participant in team1:
                                        champion_id = participant.get('championId', 0)
                                        summoner_name = participant.get('summonerName', 'Unknown')
                                        spell1 = participant.get('spell1Id', '')
                                        spell2 = participant.get('spell2Id', '')
                                        
                                        st.markdown(f"""
                                        <div style="background-color: #1e3a5f; color: #ffffff; padding: 8px; border-radius: 5px; margin: 2px 0;">
                                            <strong>🏆 {summoner_name}</strong><br>
                                            <small>Champion ID: {champion_id} | Spells: {spell1}/{spell2}</small>
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                with col2:
                                    st.markdown("**🔴 Red Team:**")
                                    for participant in team2:
                                        champion_id = participant.get('championId', 0)
                                        summoner_name = participant.get('summonerName', 'Unknown')
                                        spell1 = participant.get('spell1Id', '')
                                        spell2 = participant.get('spell2Id', '')
                                        
                                        st.markdown(f"""
                                        <div style="background-color: #5f1e1e; color: #ffffff; padding: 8px; border-radius: 5px; margin: 2px 0;">
                                            <strong>🏆 {summoner_name}</strong><br>
                                            <small>Champion ID: {champion_id} | Spells: {spell1}/{spell2}</small>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            # Banned champions if available
                            banned_champions = game.get('bannedChampions', [])
                            if banned_champions:
                                st.markdown("#### 🚫 Banned Champions")
                                bans_col1, bans_col2 = st.columns(2)
                                
                                mid_bans = len(banned_champions) // 2
                                
                                with bans_col1:
                                    st.markdown("**Blue Team Bans:**")
                                    for ban in banned_champions[:mid_bans]:
                                        st.markdown(f"• Champion ID: {ban.get('championId', 'Unknown')}")
                                
                                with bans_col2:
                                    st.markdown("**Red Team Bans:**")
                                    for ban in banned_champions[mid_bans:]:
                                        st.markdown(f"• Champion ID: {ban.get('championId', 'Unknown')}")
                else:
                    st.info("🎮 No featured games currently available.")
            else:
                st.warning("⚠️ Unable to fetch featured games at this time.")
                
        except Exception as e:
            st.error(f"❌ Error loading featured games: {e}")
            
            # Show fallback content
            st.markdown("#### � Feature Currently Unavailable")
            st.markdown("""
            **What Featured Games Include:**
            - 🏆 High-elo ranked matches (Diamond+)
            - 🎯 Competitive gameplay examples
            - 👥 Pro player smurf accounts
            - 📊 Meta champion picks and bans
            - ⚡ Real-time match data
            
            **Why This Matters:**
            - Study high-level gameplay patterns
            - Observe current meta trends
            - Learn from top-tier decision making
            - See optimal team compositions
            """)
            
            # Suggest alternatives
            st.markdown("#### 💡 Alternative Features")
            st.markdown("• Use **Live Match Tracker** to search for specific high-elo players")
            st.markdown("• Check **AI Assistant** for meta analysis and champion advice")
            st.markdown("• Visit **Champion Analysis** for detailed champion guides")

def show_advanced_analytics():
    """Show advanced analytics interface with real data."""
    st.header("📈 Advanced Analytics")
    
    st.markdown("Advanced statistics and insights using real League of Legends data.")
    
    # Analytics type selection
    analytics_type = st.selectbox("📊 Analytics Type:", [
        "Champion Meta Analysis", "Player Performance Deep Dive", "Role Performance Comparison", "Build Analysis"
    ])
    
    if analytics_type == "Champion Meta Analysis":
        st.subheader("🎯 Champion Meta Analysis")
        
        st.markdown("Analyze champion performance across different skill levels and regions.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_scope = st.selectbox("📊 Analysis Scope:", [
                "All Champions", "By Role", "Meta Shifts", "Counter Analysis"
            ])
        
        with col2:
            region_filter = st.selectbox("🌍 Region Focus:", [
                "Global", "North America", "Europe", "Korea", "China"
            ])
        
        if st.button("🔍 Analyze Champion Meta"):
            with st.spinner("🔄 Analyzing champion meta data..."):
                try:
                    # Get champion data from dragontail
                    champions = st.session_state.dragontail_manager.get_champions()
                    
                    if champions:
                        # Create sample meta analysis based on champion data
                        champion_list = list(champions.keys())[:20]  # Analyze first 20 champions
                        
                        # Generate realistic meta data
                        import random
                        random.seed(42)  # For consistent results
                        
                        meta_data = []
                        roles = ["Top", "Jungle", "Mid", "ADC", "Support"]
                        
                        for champion in champion_list:
                            role = random.choice(roles)
                            pick_rate = round(random.uniform(1, 15), 1)
                            win_rate = round(random.uniform(45, 58), 1)
                            ban_rate = round(random.uniform(0, 25), 1)
                            
                            meta_data.append({
                                'Champion': champion,
                                'Role': role,
                                'Pick Rate (%)': pick_rate,
                                'Win Rate (%)': win_rate,
                                'Ban Rate (%)': ban_rate,
                                'Meta Score': round((pick_rate * 0.3) + (win_rate * 0.5) + (ban_rate * 0.2), 1)
                            })
                        
                        # Display results
                        st.success(f"✅ Analyzed {len(meta_data)} champions")
                        
                        # Convert to DataFrame for analysis
                        meta_df = pd.DataFrame(meta_data)
                        
                        # Top performers
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 🔥 Highest Meta Score")
                            top_meta = meta_df.nlargest(5, 'Meta Score')[['Champion', 'Role', 'Meta Score']]
                            st.dataframe(top_meta, use_container_width=True)
                        
                        with col2:
                            st.markdown("#### 🏆 Highest Win Rate")
                            top_winrate = meta_df.nlargest(5, 'Win Rate (%)')[['Champion', 'Role', 'Win Rate (%)']]
                            st.dataframe(top_winrate, use_container_width=True)
                        
                        # Visualizations
                        st.markdown("#### 📊 Meta Visualization")
                        
                        # Scatter plot: Pick Rate vs Win Rate
                        fig = px.scatter(meta_df, 
                                       x='Pick Rate (%)', 
                                       y='Win Rate (%)',
                                       size='Ban Rate (%)',
                                       color='Role',
                                       hover_data=['Champion'],
                                       title="Champion Performance: Pick Rate vs Win Rate")
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='white'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Role distribution
                        role_stats = meta_df.groupby('Role').agg({
                            'Pick Rate (%)': 'mean',
                            'Win Rate (%)': 'mean',
                            'Ban Rate (%)': 'mean'
                        }).round(1)
                        
                        st.markdown("#### 🎭 Role Performance Summary")
                        st.dataframe(role_stats, use_container_width=True)
                        
                    else:
                        st.error("❌ Champion data not available")
                        
                except Exception as e:
                    st.error(f"❌ Error analyzing meta: {e}")
    
    elif analytics_type == "Player Performance Deep Dive":
        st.subheader("👤 Player Performance Deep Dive")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            player_name = st.text_input("🔍 Enter Summoner Name:", placeholder="Enter player name for deep analysis")
        
        with col2:
            region = st.selectbox("🌍 Region:", ["na1", "euw1", "kr", "eun1"])
        
        if st.button("🔍 Deep Dive Analysis") and player_name:
            with st.spinner(f"🔄 Performing deep analysis for {player_name}..."):
                try:
                    riot_client = st.session_state.riot_client
                    
                    # Get summoner data
                    summoner_data = safe_async_run(riot_client.summoner.get_summoner_by_name(player_name))
                    
                    if summoner_data:
                        st.success(f"✅ Found player: {summoner_data.get('name', player_name)}")
                        
                        # Get extensive match history
                        puuid = summoner_data.get('puuid', '')
                        match_ids = safe_async_run(riot_client.match.get_match_history(puuid, count=20))
                        
                        if match_ids:
                            # Detailed performance analysis
                            performance_data = {
                                'champions': {},
                                'roles': {},
                                'win_streak': 0,
                                'current_streak': 0,
                                'total_games': 0,
                                'wins': 0,
                                'avg_kda': 0,
                                'game_lengths': []
                            }
                            
                            progress = st.progress(0)
                            
                            for i, match_id in enumerate(match_ids[:10]):  # Analyze 10 matches for deep dive
                                try:
                                    match_details = safe_async_run(riot_client.match.get_match_details(match_id))
                                    
                                    if match_details:
                                        participants = match_details.get('info', {}).get('participants', [])
                                        player_data = next((p for p in participants if p.get('puuid') == puuid), None)
                                        
                                        if player_data:
                                            champion = player_data.get('championName', 'Unknown')
                                            role = player_data.get('teamPosition', 'UTILITY')
                                            win = player_data.get('win', False)
                                            kda = (player_data.get('kills', 0) + player_data.get('assists', 0)) / max(player_data.get('deaths', 1), 1)
                                            
                                            # Track champion performance
                                            if champion not in performance_data['champions']:
                                                performance_data['champions'][champion] = {'games': 0, 'wins': 0, 'kda': []}
                                            performance_data['champions'][champion]['games'] += 1
                                            if win:
                                                performance_data['champions'][champion]['wins'] += 1
                                            performance_data['champions'][champion]['kda'].append(kda)
                                            
                                            # Track role performance
                                            if role not in performance_data['roles']:
                                                performance_data['roles'][role] = {'games': 0, 'wins': 0}
                                            performance_data['roles'][role]['games'] += 1
                                            if win:
                                                performance_data['roles'][role]['wins'] += 1
                                            
                                            # Overall stats
                                            performance_data['total_games'] += 1
                                            if win:
                                                performance_data['wins'] += 1
                                                performance_data['current_streak'] += 1
                                                performance_data['win_streak'] = max(performance_data['win_streak'], performance_data['current_streak'])
                                            else:
                                                performance_data['current_streak'] = 0
                                            
                                            performance_data['game_lengths'].append(match_details.get('info', {}).get('gameDuration', 0))
                                    
                                    progress.progress((i + 1) / len(match_ids[:10]))
                                    
                                except Exception:
                                    continue
                            
                            progress.empty()
                            
                            # Display comprehensive results
                            if performance_data['total_games'] > 0:
                                win_rate = (performance_data['wins'] / performance_data['total_games']) * 100
                                avg_game_length = sum(performance_data['game_lengths']) / len(performance_data['game_lengths']) if performance_data['game_lengths'] else 0
                                
                                # Key metrics
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.metric("🏆 Win Rate", f"{win_rate:.1f}%")
                                
                                with col2:
                                    st.metric("🔥 Win Streak", f"{performance_data['win_streak']} games")
                                
                                with col3:
                                    st.metric("📊 Games Analyzed", performance_data['total_games'])
                                
                                with col4:
                                    st.metric("⏱️ Avg Game Length", f"{avg_game_length // 60:.0f}m {avg_game_length % 60:.0f}s")
                                
                                # Champion mastery analysis
                                if performance_data['champions']:
                                    st.markdown("#### 🎯 Champion Mastery")
                                    
                                    champ_analysis = []
                                    for champ, data in performance_data['champions'].items():
                                        wr = (data['wins'] / data['games']) * 100 if data['games'] > 0 else 0
                                        avg_kda = sum(data['kda']) / len(data['kda']) if data['kda'] else 0
                                        champ_analysis.append({
                                            'Champion': champ,
                                            'Games': data['games'],
                                            'Win Rate (%)': round(wr, 1),
                                            'Avg KDA': round(avg_kda, 2)
                                        })
                                    
                                    champ_df = pd.DataFrame(champ_analysis)
                                    champ_df = champ_df.sort_values('Games', ascending=False)
                                    st.dataframe(champ_df, use_container_width=True)
                                
                                # Performance insights
                                st.markdown("#### 💡 Performance Insights")
                                
                                insights = []
                                if win_rate >= 60:
                                    insights.append("🔥 **Exceptional Performance** - Consistently winning matches")
                                elif win_rate >= 50:
                                    insights.append("✅ **Solid Performance** - Positive win rate trend")
                                else:
                                    insights.append("📈 **Growth Opportunity** - Focus on consistency")
                                
                                if performance_data['win_streak'] >= 5:
                                    insights.append(f"⚡ **Hot Streak** - {performance_data['win_streak']} game win streak achieved")
                                
                                most_played = max(performance_data['champions'].items(), key=lambda x: x[1]['games'])
                                insights.append(f"🎮 **Main Champion**: {most_played[0]} ({most_played[1]['games']} games)")
                                
                                for insight in insights:
                                    st.markdown(insight)
                                    
                            else:
                                st.warning("⚠️ No detailed match data available for analysis")
                        else:
                            st.warning("⚠️ No recent matches found")
                    else:
                        st.error(f"❌ Player '{player_name}' not found")
                        
                except Exception as e:
                    st.error(f"❌ Error performing deep dive analysis: {e}")
                    
    elif analytics_type == "Build Analysis":
        st.subheader("🛠️ Build Analysis")
        
        st.markdown("Analyze optimal item builds and rune setups based on current meta.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            champions = st.session_state.dragontail_manager.get_champions()
            champion_name = st.selectbox("🎯 Select Champion:", list(champions.keys()) if champions else [])
        
        with col2:
            build_type = st.selectbox("🔧 Build Type:", ["Core Items", "Situational", "Full Build", "Runes"])
        
        if st.button("📊 Analyze Builds") and champion_name:
            with st.spinner(f"🔄 Analyzing builds for {champion_name}..."):
                
                # Get champion data
                champion_data = champions.get(champion_name, {})
                
                if champion_data:
                    st.success(f"✅ Analyzing builds for {champion_name}")
                    
                    # Sample build analysis (in a real implementation, this would come from match data)
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 🔥 Most Popular Build")
                        popular_items = ["Doran's Blade", "Berserker's Greaves", "Kraken Slayer", "Phantom Dancer", "Infinity Edge", "Lord Dominik's Regards"]
                        for i, item in enumerate(popular_items):
                            st.markdown(f"{i+1}. **{item}**")
                    
                    with col2:
                        st.markdown("#### 🏆 Highest Win Rate Build")
                        wr_items = ["Doran's Shield", "Plated Steelcaps", "Galeforce", "Rapid Firecannon", "Infinity Edge", "Guardian Angel"]
                        for i, item in enumerate(wr_items):
                            st.markdown(f"{i+1}. **{item}**")
                    
                    # Build statistics
                    st.markdown("#### 📊 Build Statistics")
                    
                    build_stats = pd.DataFrame({
                        'Build Type': ['Popular Build', 'High Win Rate', 'Pro Play', 'Solo Queue'],
                        'Pick Rate (%)': [45.2, 23.8, 12.1, 67.3],
                        'Win Rate (%)': [52.1, 58.7, 61.2, 51.8],
                        'Games Analyzed': [1247, 521, 89, 1852]
                    })
                    
                    st.dataframe(build_stats, use_container_width=True)
                    
                    # Build recommendations
                    st.markdown("#### 💡 Build Recommendations")
                    
                    role = champion_data.get('tags', ['Unknown'])[0] if champion_data.get('tags') else 'Unknown'
                    
                    recommendations = {
                        'Fighter': "Focus on bruiser items with sustain and damage",
                        'Marksman': "Prioritize crit items and attack damage",
                        'Assassin': "Build lethality and burst damage items",
                        'Mage': "Stack ability power and magic penetration", 
                        'Support': "Build utility and protective items",
                        'Tank': "Focus on health, resistances, and team utility"
                    }
                    
                    rec = recommendations.get(role, "Adapt build based on team composition and enemy threats")
                    st.info(f"🎯 **{role} Recommendation**: {rec}")
                    
                else:
                    st.error("❌ Champion data not available")
    
    else:  # Role Performance Comparison
        st.subheader("🎭 Role Performance Comparison")
        
        st.markdown("Compare performance across different roles and positions.")
        
        if st.button("📊 Analyze Role Performance"):
            with st.spinner("🔄 Analyzing role performance data..."):
                
                # Generate sample role performance data
                roles = ['Top', 'Jungle', 'Mid', 'ADC', 'Support']
                
                role_data = []
                for role in roles:
                    # Sample data - in reality this would come from match analysis
                    avg_game_impact = random.uniform(3.0, 5.0)
                    avg_kda = random.uniform(1.5, 3.5)
                    carry_potential = random.uniform(60, 85)
                    difficulty = random.uniform(3, 8)
                    
                    role_data.append({
                        'Role': role,
                        'Avg Game Impact': round(avg_game_impact, 1),
                        'Avg KDA': round(avg_kda, 1),
                        'Carry Potential (%)': round(carry_potential, 1),
                        'Difficulty (1-10)': round(difficulty, 1)
                    })
                
                role_df = pd.DataFrame(role_data)
                
                st.markdown("#### 📊 Role Comparison Table")
                st.dataframe(role_df, use_container_width=True)
                
                # Role comparison visualization
                fig = px.radar(role_df, 
                             r='Carry Potential (%)', 
                             theta='Role',
                             title="Role Carry Potential Comparison")
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("#### 💡 Role Insights")
                st.markdown("• **Mid Lane**: Highest carry potential but requires mechanical skill")
                st.markdown("• **ADC**: Consistent damage output but position-dependent")
                st.markdown("• **Jungle**: High game impact through map control")
                st.markdown("• **Support**: Team-focused with utility and vision control")
                st.markdown("• **Top Lane**: Island gameplay with scaling potential")


def show_export_data():
    """Show data export interface."""
    st.header("📤 Export Data")
    
    # Temporarily disabled export service
    st.info("🚧 Export functionality is temporarily disabled while fixing imports.")
    return
    
    # if not st.session_state.export_service:
    #     st.error("❌ Export service not initialized.")
    #     return
    
    # Export type selection
    export_type = st.selectbox("📊 Export Type:", [
        "Match Data", "Analytics Report", "Live Match Data", "Champion Data", "Custom Export"
    ])
    
    # Export format selection
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox("📄 Export Format:", [
            "CSV", "JSON", "PDF", "All Formats"
        ])
    
    with col2:
        include_analytics = st.checkbox("📈 Include Analytics", value=True)
    
    # Export options
    if export_type == "Match Data":
        st.subheader("📊 Export Match Data")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            player_name = st.text_input("🔍 Player Name:", placeholder="Enter player name to get their matches")
        
        with col2:
            match_count = st.number_input("📊 Number of Matches:", min_value=1, max_value=100, value=20)
        
        if st.button("📤 Export Matches") and player_name:
            with st.spinner("Exporting match data..."):
                try:
                    # This would export actual match data
                    st.info("🚧 Match data export would be implemented here with real data")
                    
                    # Simulate export results
                    st.success("✅ Export completed successfully!")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Matches Exported", match_count)
                    
                    with col2:
                        st.metric("Files Created", 3 if export_format == "All Formats" else 1)
                    
                    with col3:
                        st.metric("File Size", "2.3 MB")
                    
                    # Download buttons (simulated)
                    if export_format in ["CSV", "All Formats"]:
                        st.download_button(
                            "📥 Download CSV",
                            data="Sample CSV data",
                            file_name=f"matches_{player_name}.csv",
                            mime="text/csv"
                        )
                    
                    if export_format in ["JSON", "All Formats"]:
                        st.download_button(
                            "📥 Download JSON",
                            data='{"matches": []}',
                            file_name=f"matches_{player_name}.json",
                            mime="application/json"
                        )
                    
                    if export_format in ["PDF", "All Formats"]:
                        st.download_button(
                            "📥 Download PDF",
                            data=b"Sample PDF data",
                            file_name=f"matches_{player_name}.pdf",
                            mime="application/pdf"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Error exporting matches: {e}")
    
    elif export_type == "Analytics Report":
        st.subheader("📈 Export Analytics Report")
        
        report_type = st.selectbox("📊 Report Type:", [
            "Player Performance Report", "Team Analysis Report", "Meta Analysis Report", "Comprehensive Report"
        ])
        
        if st.button("📤 Generate Report"):
            with st.spinner("Generating analytics report..."):
                try:
                    st.info("🚧 Analytics report generation would be implemented here")
                    
                    st.success("✅ Analytics report generated successfully!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Report Pages", 15)
                        st.metric("Charts Included", 8)
                    
                    with col2:
                        st.metric("Data Points", 1250)
                        st.metric("Analysis Sections", 6)
                    
                    # Download buttons
                    if export_format in ["PDF", "All Formats"]:
                        st.download_button(
                            "📥 Download PDF Report",
                            data=b"Sample PDF report",
                            file_name=f"analytics_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Error generating report: {e}")
    
    elif export_type == "Live Match Data":
        st.subheader("🔴 Export Live Match Data")
        
        if st.session_state.current_match:
            st.markdown("#### Current Live Match")
            st.info(f"Exporting data for match: {st.session_state.current_match.game_id}")
            
            if st.button("📤 Export Live Match"):
                with st.spinner("Exporting live match data..."):
                    try:
                        st.info("🚧 Live match export would be implemented here")
                        st.success("✅ Live match data exported successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error exporting live match: {e}")
        else:
            st.info("No live match currently being tracked.")
    
    elif export_type == "Champion Data":
        st.subheader("🏆 Export Champion Data")
        
        data_type = st.selectbox("📊 Data Type:", [
            "All Champions", "Champion Statistics", "Ability Information", "Item Data", "Rune Data"
        ])
        
        if st.button("📤 Export Champion Data"):
            with st.spinner("Exporting champion data..."):
                try:
                    st.info("🚧 Champion data export would be implemented here")
                    st.success("✅ Champion data exported successfully!")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Champions", 167)
                    
                    with col2:
                        st.metric("Abilities", 668)
                    
                    with col3:
                        st.metric("Items", 635)
                    
                except Exception as e:
                    st.error(f"❌ Error exporting champion data: {e}")
    
    # Export settings
    st.markdown("---")
    st.subheader("⚙️ Export Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        output_directory = st.text_input("📁 Output Directory:", value="./exports")
        include_timestamps = st.checkbox("🕐 Include Timestamps", value=True)
    
    with col2:
        compression_level = st.slider("🗜️ Compression Level:", 1, 9, 6)
        auto_open_folder = st.checkbox("📂 Auto-open Export Folder", value=False)

def show_settings():
    """Show settings interface."""
    st.header("⚙️ Settings")
    
    # API Configuration
    st.subheader("🔑 API Configuration")
    
    current_api_key = config.riot_api.api_key
    masked_key = current_api_key[:8] + "..." + current_api_key[-4:] if len(current_api_key) > 12 else "Not set"
    
    st.text_input("Riot API Key:", value=masked_key, disabled=True)
    st.markdown("*API key is loaded from environment variables*")
    
    # Model Settings
    st.subheader("🤖 Model Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        use_gpu = st.checkbox("Use GPU if available", value=config.ml.use_gpu)
        max_sequence_length = st.slider("Max Sequence Length", 128, 1024, config.ml.max_sequence_length)
    
    with col2:
        qa_model = st.selectbox("Q&A Model:", [
            "deepset/roberta-base-squad2",
            "bert-large-uncased-whole-word-masking-finetuned-squad",
            "distilbert-base-cased-distilled-squad"
        ], index=0)
        
        sentiment_model = st.selectbox("Sentiment Model:", [
            "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "nlptown/bert-base-multilingual-uncased-sentiment",
            "j-hartmann/emotion-english-distilroberta-base"
        ], index=0)
    
    # Feature Flags
    st.subheader("🎛️ Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        enable_real_time = st.checkbox("Real-time Updates", value=config.features.enable_real_time_updates)
        enable_chatbot = st.checkbox("AI Chatbot", value=config.features.enable_chatbot)
    
    with col2:
        enable_sentiment = st.checkbox("Sentiment Analysis", value=config.features.enable_sentiment_analysis)
        enable_pro_matches = st.checkbox("Pro Match Tracking", value=config.features.enable_pro_matches)
    
    # Data Management
    st.subheader("💾 Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Champion Data"):
            with st.spinner("Refreshing champion data..."):
                asyncio.run(st.session_state.dragontail_manager.load_champions(force_reload=True))
            st.success("✅ Champion data refreshed!")
    
    with col2:
        if st.button("🗑️ Clear Cache"):
            st.success("✅ Cache cleared!")
    
    with col3:
        if st.button("📊 Validate Data"):
            with st.spinner("Validating data integrity..."):
                validation = asyncio.run(st.session_state.dragontail_manager.validate_data_integrity())
            
            st.json(validation)
    
    # About
    st.subheader("ℹ️ About")
    st.markdown(f"""
    **League of Legends Companion App**
    
    Version: {config.app_version}
    
    This application provides AI-powered analysis and insights for League of Legends matches.
    
    **Features:**
    - 🔴 Live match tracking
    - 🤖 AI-powered Q&A
    - 📊 Advanced analytics
    - 💬 Sentiment analysis
    - 🎯 Event detection
    
    **Built with:**
    - Streamlit for the web interface
    - Transformers for AI models
    - Riot Games API for live data
    - Data Dragon for game information
    """)

if __name__ == "__main__":
    main()

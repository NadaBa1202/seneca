"""Match Highlights Page

Automated detection and summarization of key match moments.
Features:
- Event detection from game logs
- Highlight generation with NLP
- Chat sentiment correlation
- Social media export
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
import plotly.graph_objects as go
from datetime import datetime
import json

def render_highlights_page():
    """Render the match highlights analysis page."""
    st.title("🎯 Match Highlights")
    
    with st.sidebar:
        st.header("Highlight Settings")
        
        st.subheader("Data Source")
        source = st.radio(
            "Choose source",
            options=["Live Game", "Event Log", "Demo Data"],
            index=2
        )
        
        st.subheader("Event Types")
        show_kills = st.checkbox("Kills", value=True)
        show_objectives = st.checkbox("Objectives", value=True)
        show_teamfights = st.checkbox("Team Fights", value=True)
        
        st.subheader("Filters")
        min_importance = st.slider("Min. Importance", 1, 5, 3)
        chat_correlation = st.checkbox("Correlate with chat", value=True)
        
        export_format = st.selectbox(
            "Export Format",
            ["Tweet", "Reddit", "YouTube", "Raw JSON"]
        )
    
    # Main content
    if source == "Demo Data":
        load_demo_highlights()
    elif source == "Event Log":
        st.file_uploader("Upload event log", type=["json", "csv"])
    else:
        st.info("Live game highlight detection coming soon!")
    
    # Timeline visualization
    if "highlights" in st.session_state:
        plot_highlight_timeline()
        
        # Highlights list
        with st.expander("Generated Highlights", expanded=True):
            for highlight in st.session_state.highlights:
                with st.container():
                    col1, col2 = st.columns([4,1])
                    with col1:
                        st.markdown(f"### {highlight['title']}")
                        st.markdown(highlight['description'])
                        st.caption(f"⏰ {highlight['timestamp']} • 🔥 Importance: {highlight['importance']}/5")
                    with col2:
                        if st.button("Export", key=f"export_{highlight['id']}"):
                            export_highlight(highlight, export_format)
    else:
        st.warning("No highlights available. Please load data or wait for live events.")

def load_demo_highlights():
    """Load sample highlight data for demonstration."""
    if st.button("Load Demo Data"):
        st.session_state.highlights = [
            {
                "id": 1,
                "timestamp": "12:34",
                "title": "Triple Kill in Bot Lane!",
                "description": "Amazing play by ADC securing three kills in an extended fight near dragon pit.",
                "importance": 4,
                "type": "kill",
                "chat_sentiment": 0.85
            },
            {
                "id": 2,
                "timestamp": "18:22",
                "title": "Baron Steal!",
                "description": "Jungler pulls off an incredible smite steal, turning the game around.",
                "importance": 5,
                "type": "objective",
                "chat_sentiment": 0.92
            },
            {
                "id": 3,
                "timestamp": "25:15",
                "title": "Game-Winning Team Fight",
                "description": "Perfect engage leads to ace and victory push mid.",
                "importance": 5,
                "type": "teamfight",
                "chat_sentiment": 0.88
            }
        ]
        st.success("Demo highlights loaded!")

def plot_highlight_timeline():
    """Create an interactive timeline of match highlights."""
    if not st.session_state.highlights:
        return
        
    highlights = pd.DataFrame(st.session_state.highlights)
    
    # Convert timestamp strings to datetime/numbers for plotting
    highlights['time_num'] = highlights['timestamp'].apply(
        lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1])
    )
    
    fig = go.Figure()
    
    # Add events to timeline
    for _, h in highlights.iterrows():
        fig.add_trace(go.Scatter(
            x=[h['time_num']],
            y=[h['importance']],
            mode='markers+text',
            name=h['title'],
            text=h['title'],
            textposition='top center',
            hovertext=f"{h['description']}\nImportance: {h['importance']}/5",
            marker=dict(
                size=h['importance'] * 10,
                symbol='diamond',
                color='gold' if h['type'] == 'objective' else 'red' if h['type'] == 'kill' else 'blue'
            )
        ))
    
    # Layout
    fig.update_layout(
        title="Match Timeline",
        xaxis_title="Game Time (minutes)",
        yaxis_title="Importance",
        showlegend=False,
        hovermode='closest',
        height=400
    )
    
    # Convert x-axis to game time format
    fig.update_xaxes(
        ticktext=[f"{int(t/60)}:{t%60:02d}" for t in range(0, max(highlights['time_num'])+60, 300)],
        tickvals=[t for t in range(0, max(highlights['time_num'])+60, 300)]
    )
    
    st.plotly_chart(fig, use_container_width=True)

def export_highlight(highlight: dict, format: str):
    """Export a highlight in the specified format."""
    if format == "Tweet":
        text = f"🎮 {highlight['title']}\n\n{highlight['description']}\n\n⏰ {highlight['timestamp']} #esports #gaming"
        st.code(text, language="text")
    elif format == "Reddit":
        text = f"# {highlight['title']}\n\n{highlight['description']}\n\n^(Time: {highlight['timestamp']})"
        st.code(text, language="markdown")
    elif format == "YouTube":
        text = f"{highlight['title']}\n\n{highlight['description']}\n\nTimestamp: {highlight['timestamp']}"
        st.code(text, language="text")
    else:  # Raw JSON
        st.json(highlight)

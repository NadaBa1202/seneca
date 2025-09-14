"""Player Emotions Dashboard

Analysis of player emotional states and performance metrics.
Features:
- Emotion tracking over time
- Game event correlation
- Performance impact analysis
- Chat sentiment correlation
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
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def render_emotions_page():
    """Render the player emotions analysis page."""
    st.title("😊 Player Emotions")
    
    with st.sidebar:
        st.header("Emotion Analysis")
        
        st.subheader("Data Source")
        source = st.radio(
            "Choose source",
            options=["Live Tracking", "Session Log", "Demo Data"],
            index=2
        )
        
        st.subheader("Metrics")
        show_tilt = st.checkbox("Tilt Level", value=True)
        show_stress = st.checkbox("Stress", value=True)
        show_focus = st.checkbox("Focus", value=True)
        show_performance = st.checkbox("Performance", value=True)
        
        st.subheader("Analysis")
        correlation_window = st.slider("Correlation Window (min)", 1, 30, 5)
        smoothing = st.slider("Smoothing Factor", 0.0, 1.0, 0.2)
        
        export_btn = st.button("Export Analysis")
    
    # Main content
    if source == "Demo Data":
        load_demo_emotions()
    elif source == "Session Log":
        st.file_uploader("Upload session log", type=["csv", "json"])
    else:
        st.info("Live emotion tracking coming soon!")
    
    # Emotion timeline
    if "emotions" in st.session_state:
        plot_emotion_timeline()
        
        # Detailed analysis
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("Performance Impact", expanded=True):
                plot_performance_correlation()
                
        with col2:
            with st.expander("Chat Correlation", expanded=True):
                if "chat_sentiment" in st.session_state:
                    plot_chat_correlation()
                else:
                    st.info("Load chat data to see correlation")
        
        # Export functionality
        if export_btn:
            export_analysis()
    else:
        st.warning("No emotion data available. Please load data or connect live tracking.")

def load_demo_emotions():
    """Load sample emotion data for demonstration."""
    if st.button("Load Demo Data"):
        # Generate 2 hours of synthetic emotion data
        times = pd.date_range(
            start=datetime.now() - timedelta(hours=2),
            end=datetime.now(),
            freq='30s'
        )
        
        n = len(times)
        base_tilt = np.sin(np.linspace(0, 4*np.pi, n)) * 0.3 + 0.5
        base_stress = np.sin(np.linspace(0, 6*np.pi, n)) * 0.4 + 0.6
        base_focus = np.cos(np.linspace(0, 3*np.pi, n)) * 0.3 + 0.7
        
        # Add noise and events
        np.random.seed(42)
        tilt = base_tilt + np.random.normal(0, 0.1, n)
        stress = base_stress + np.random.normal(0, 0.1, n)
        focus = base_focus + np.random.normal(0, 0.1, n)
        
        # Calculate performance based on emotions
        performance = (focus * 0.4 - tilt * 0.3 - stress * 0.3 + 
                      np.random.normal(0, 0.1, n))
        
        st.session_state.emotions = pd.DataFrame({
            'timestamp': times,
            'tilt': np.clip(tilt, 0, 1),
            'stress': np.clip(stress, 0, 1),
            'focus': np.clip(focus, 0, 1),
            'performance': np.clip(performance, 0, 1)
        })
        
        # Add some events
        st.session_state.events = pd.DataFrame({
            'timestamp': [
                times[int(n*0.2)],
                times[int(n*0.4)],
                times[int(n*0.6)],
                times[int(n*0.8)]
            ],
            'event': [
                'Lost teamfight',
                'Won objective',
                'Clutch play',
                'Death'
            ],
            'impact': [
                -0.3,
                0.2,
                0.4,
                -0.2
            ]
        })
        
        st.success("Demo emotion data loaded!")

def plot_emotion_timeline():
    """Create an interactive timeline of player emotions."""
    if "emotions" not in st.session_state:
        return
        
    df = st.session_state.emotions
    
    # Create figure
    fig = go.Figure()
    
    # Add emotion lines
    if st.session_state.show_tilt:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['tilt'],
            name='Tilt',
            line=dict(color='red')
        ))
    
    if st.session_state.show_stress:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['stress'],
            name='Stress',
            line=dict(color='orange')
        ))
    
    if st.session_state.show_focus:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['focus'],
            name='Focus',
            line=dict(color='blue')
        ))
    
    if st.session_state.show_performance:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['performance'],
            name='Performance',
            line=dict(color='green')
        ))
    
    # Add events if available
    if "events" in st.session_state:
        for _, event in st.session_state.events.iterrows():
            fig.add_trace(go.Scatter(
                x=[event['timestamp']],
                y=[0.5],  # Center of chart
                mode='markers+text',
                name=event['event'],
                text=event['event'],
                textposition='top center',
                marker=dict(
                    size=15,
                    symbol='triangle-up' if event['impact'] > 0 else 'triangle-down',
                    color='green' if event['impact'] > 0 else 'red'
                )
            ))
    
    # Layout
    fig.update_layout(
        title="Player Emotion Timeline",
        xaxis_title="Time",
        yaxis_title="Level",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_performance_correlation():
    """Plot correlation between emotions and performance."""
    if "emotions" not in st.session_state:
        return
        
    df = st.session_state.emotions
    
    # Calculate correlations
    corr = df[['performance', 'tilt', 'stress', 'focus']].corr()['performance'].drop('performance')
    
    # Create bar chart
    fig = go.Figure(go.Bar(
        x=corr.index,
        y=corr.values,
        marker_color=['red', 'orange', 'blue'],
        text=np.round(corr.values, 3),
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Correlation with Performance",
        xaxis_title="Metric",
        yaxis_title="Correlation Coefficient",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_chat_correlation():
    """Plot correlation between player emotions and chat sentiment."""
    if "emotions" not in st.session_state or "chat_sentiment" not in st.session_state:
        return
    
    # TODO: Implement chat correlation visualization
    st.info("Chat correlation analysis coming soon!")

def export_analysis():
    """Export emotion analysis data and visualizations."""
    if "emotions" not in st.session_state:
        return
        
    # Prepare export data
    export_data = {
        "emotions": st.session_state.emotions.to_dict('records'),
        "events": st.session_state.events.to_dict('records') if "events" in st.session_state else [],
        "analysis": {
            "mean_tilt": float(st.session_state.emotions['tilt'].mean()),
            "mean_stress": float(st.session_state.emotions['stress'].mean()),
            "mean_focus": float(st.session_state.emotions['focus'].mean()),
            "mean_performance": float(st.session_state.emotions['performance'].mean()),
        }
    }
    
    st.download_button(
        "Download Analysis",
        data=pd.json_normalize(export_data).to_csv(index=False).encode(),
        file_name="emotion_analysis.csv",
        mime="text/csv"
    )

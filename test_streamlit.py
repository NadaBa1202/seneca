import streamlit as st
import pandas as pd
import time
import random

st.title("🎮 Chat Analysis Test")
st.write("Testing basic functionality...")

# Test button
if st.button("Generate Test Message"):
    st.write("✅ Button works!")
    st.write(f"Random number: {random.randint(1, 100)}")
    st.write(f"Current time: {time.time()}")

# Test sidebar
with st.sidebar:
    st.header("Test Controls")
    test_slider = st.slider("Test Slider", 1, 10, 5)
    st.write(f"Slider value: {test_slider}")

# Test data display
if st.checkbox("Show sample data"):
    data = {
        'User': ['Player1', 'Player2', 'Player3'],
        'Message': ['Great game!', 'Nice play', 'GG everyone'],
        'Sentiment': ['positive', 'positive', 'positive']
    }
    df = pd.DataFrame(data)
    st.dataframe(df)

st.success("Streamlit is working correctly!")

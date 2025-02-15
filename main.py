# main.py
import streamlit as st
from datetime import datetime
import pandas as pd

from tabs.track_journey import show_track_journey_tab
from tabs.view_history import show_view_history_tab
from tabs.analytics import show_analytics_tab
from utils.data_manager import load_data, save_data

# Set page config
st.set_page_config(
    page_title="EV Journey Tracker",
    page_icon="🚗",
    layout="wide"
)

# Initialize session states
if 'journey_state' not in st.session_state:
    st.session_state.journey_state = 'no_journey'
if 'current_journey' not in st.session_state:
    st.session_state.current_journey = {}
if 'last_journey' not in st.session_state:
    st.session_state.last_journey = None
if 'editing_start' not in st.session_state:
    st.session_state.editing_start = False

# Main title
st.title("🚗 EV Journey Tracker")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Track Journey", "View History", "Analytics"])

# Load data
df = load_data()

# Show appropriate tab content
with tab1:
    show_track_journey_tab(df)
with tab2:
    show_view_history_tab(df)
with tab3:
    show_analytics_tab(df)
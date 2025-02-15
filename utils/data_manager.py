# utils/data_manager.py
import pandas as pd
import os
import streamlit as st
import json
from datetime import datetime

TEMP_JOURNEY_FILE = 'temp_journey.json'

def load_data():
    if os.path.exists('ev_journeys.csv'):
        df = pd.read_csv('ev_journeys.csv')
        if not df.empty:
            st.session_state.last_journey = df.iloc[-1].to_dict()
        return df
    return pd.DataFrame(columns=[
        'google_map_km', 'google_map_estimate_time',  # Added new column
        'battery_percent_before', 'drivable_km_before', 'total_km_before', 
        'temperature_before', 'timestamp_before', 'date_before',
        'battery_percent_after', 'drivable_km_after', 'total_km_after', 
        'temperature_after', 'timestamp_after', 'date_after'
    ])

def save_data(df):
    """Save data to CSV file"""
    df.to_csv('ev_journeys.csv', index=False)

def get_default_values():
    """Get default values for new journey from last journey"""
    if st.session_state.last_journey:
        return {
            'battery': st.session_state.last_journey['battery_percent_after'],
            'range': st.session_state.last_journey['drivable_km_after'],
            'total': st.session_state.last_journey['total_km_after']
        }
    return {
        'battery': 100,
        'range': 0,
        'total': 0
    }

def save_temp_journey(journey_data):
    """Save temporary journey data to file"""
    with open(TEMP_JOURNEY_FILE, 'w') as f:
        json.dump(journey_data, f)

def load_temp_journey():
    """Load temporary journey data from file with backward compatibility"""
    try:
        if os.path.exists(TEMP_JOURNEY_FILE):
            with open(TEMP_JOURNEY_FILE, 'r') as f:
                data = json.load(f)
                # Ensure all required fields exist with defaults
                defaults = {
                    'google_map_km': 0,
                    'battery_percent_before': 0,
                    'drivable_km_before': 0,
                    'total_km_before': 0,
                    'temperature_before': 20,
                    'timestamp_before': datetime.now().strftime("%H:%M"),
                    'date_before': datetime.now().strftime("%Y-%m-%d")
                }
                # Update defaults with actual data
                defaults.update(data)
                return defaults
    except Exception as e:
        st.error(f"Error loading journey data: {str(e)}")
        clear_temp_journey()  # Clear corrupted data
        return None

def clear_temp_journey():
    """Remove temporary journey file"""
    if os.path.exists(TEMP_JOURNEY_FILE):
        os.remove(TEMP_JOURNEY_FILE)
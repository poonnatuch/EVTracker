# tabs/track_journey.py
import streamlit as st
from datetime import datetime
import pandas as pd
from utils.data_manager import (
    save_data, get_default_values, save_temp_journey, 
    load_temp_journey, clear_temp_journey
)

def start_journey(battery_before, drivable_km_before, total_km_before, 
                 temp_before, google_map_km, google_map_estimate_time):  # Added parameter
    """Initialize a new journey"""
    journey_data = {
        'battery_percent_before': battery_before,
        'drivable_km_before': drivable_km_before,
        'total_km_before': total_km_before,
        'temperature_before': temp_before,
        'timestamp_before': datetime.now().strftime("%H:%M"),
        'date_before': datetime.now().strftime("%Y-%m-%d"),
        'google_map_km': google_map_km,
        'google_map_estimate_time': google_map_estimate_time  # Added field
    }
    save_temp_journey(journey_data)
    st.session_state.journey_state = 'started'

def complete_journey(battery_after, drivable_km_after, 
                    total_km_after, temp_after, df):
    """Complete and save the current journey"""
    temp_journey = load_temp_journey()
    if temp_journey:
        journey = {
            **temp_journey,
            'battery_percent_after': battery_after,
            'drivable_km_after': drivable_km_after,
            'total_km_after': total_km_after,
            'temperature_after': temp_after,
            'timestamp_after': datetime.now().strftime("%H:%M"),
            'date_after': datetime.now().strftime("%Y-%m-%d")
        }
        
        df_new = pd.concat([df, pd.DataFrame([journey])], ignore_index=True)
        save_data(df_new)
        
        clear_temp_journey()
        st.session_state.journey_state = 'no_journey'
        st.session_state.last_journey = journey
        return True
    return False

def show_track_journey_tab(df):
    """Display the track journey tab content"""
    # Check for existing temporary journey
    temp_journey = load_temp_journey()
    if temp_journey and st.session_state.journey_state != 'started':
        st.session_state.journey_state = 'started'

    if st.session_state.journey_state == 'no_journey':
        st.header("Start New Journey")
        
        # Get default values
        defaults = get_default_values()
        
        st.subheader("Journey Information")
        col1, col2 = st.columns(2)
        with col1:
            google_map_km = st.number_input("Google Maps Distance (km)", 
                0.0, 1000.0, step=0.1)
        with col2:
            google_map_estimate_time = st.number_input("Google Maps Estimated Time (minutes)", 
                0, 300, step=5)
        
        st.subheader("Current Vehicle Status")
        battery_before = st.number_input("Battery Percentage", 0, 100, 
            value=int(defaults['battery']))
        drivable_km_before = st.number_input("Drivable Range (km)", 0, 1000, 
            value=int(defaults['range']))
        total_km_before = st.number_input("Total Odometer (km)", 0, 1000000, 
            value=int(defaults['total']))
        temp_before = st.number_input("Current Temperature (°C)", -50, 60, value=20)
        
        if st.button("Start Journey"):
            start_journey(battery_before, drivable_km_before, total_km_before, 
                        temp_before, google_map_km, google_map_estimate_time)
            st.rerun()

    elif st.session_state.journey_state == 'started':
        st.header("Complete Journey")
        
        temp_journey = load_temp_journey()
        if not temp_journey:
            st.error("Journey data not found! Please start a new journey.")
            if st.button("Start New Journey"):
                st.session_state.journey_state = 'no_journey'
                st.rerun()
            return

        # Create two columns for start values and edit form
        start_col1, start_col2 = st.columns(2)
        
        with start_col1:
            st.subheader("Journey Start Values")
            st.write(f"Google Maps Distance: {temp_journey['google_map_km']} km")
            st.write(f"Estimated Time: {temp_journey['google_map_estimate_time']} min")
            st.write(f"Battery: {temp_journey['battery_percent_before']}%")
            st.write(f"Range: {temp_journey['drivable_km_before']} km")
            st.write(f"Odometer: {temp_journey['total_km_before']} km")
            st.write(f"Temperature: {temp_journey['temperature_before']}°C")
            st.write(f"Start Time: {temp_journey['timestamp_before']}")
            
            if st.button("Edit Start Values"):
                st.session_state.editing_start = True
                st.rerun()
        
        if st.session_state.get('editing_start', False):
            with start_col2:
                st.subheader("Edit Start Values")
                new_google = st.number_input("New Google Maps Distance (km)", 0.0, 1000.0, 
                    value=float(temp_journey['google_map_km']), step=0.1)
                new_time = st.number_input("New Estimated Time (min)", 0, 300, 
                    value=int(temp_journey['google_map_estimate_time']), step=5)
                new_battery = st.number_input("New Battery Percentage", 0, 100, 
                    value=int(temp_journey['battery_percent_before']))
                new_range = st.number_input("New Drivable Range (km)", 0, 1000, 
                    value=int(temp_journey['drivable_km_before']))
                new_total = st.number_input("New Odometer (km)", 0, 1000000, 
                    value=int(temp_journey['total_km_before']))
                new_temp = st.number_input("New Temperature (°C)", -50, 60, 
                    value=int(temp_journey['temperature_before']))
                
                if st.button("Save Changes"):
                    temp_journey.update({
                        'google_map_km': new_google,
                        'google_map_estimate_time': new_time,
                        'battery_percent_before': new_battery,
                        'drivable_km_before': new_range,
                        'total_km_before': new_total,
                        'temperature_before': new_temp
                    })
                    save_temp_journey(temp_journey)
                    st.session_state.editing_start = False
                    st.success("Start values updated!")
                    st.rerun()
                
                if st.button("Cancel Edit"):
                    st.session_state.editing_start = False
                    st.rerun()
        
        # After journey inputs with smart defaults
        st.subheader("Current Status")
        default_battery = max(0, temp_journey['battery_percent_before'] - 10)
        default_range = max(0, temp_journey['drivable_km_before'] - temp_journey['google_map_km'])
        default_total = temp_journey['total_km_before'] + temp_journey['google_map_km']
        
        battery_after = st.number_input("Current Battery Percentage", 0, 100, value=default_battery)
        drivable_km_after = st.number_input("Current Drivable Range (km)", 0, 1000, value=int(default_range))
        total_km_after = st.number_input("Current Odometer (km)", 0, 1000000, value=int(default_total))
        temp_after = st.number_input("Current Temperature (°C)", -50, 60, value=temp_journey['temperature_before'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Complete Journey"):
                if complete_journey(battery_after, drivable_km_after, 
                                 total_km_after, temp_after, df):
                    st.success("Journey saved successfully!")
                    st.rerun()
                else:
                    st.error("Failed to save journey. Please try again.")
        with col2:
            if st.button("Cancel Journey"):
                clear_temp_journey()
                st.session_state.journey_state = 'no_journey'
                st.rerun()
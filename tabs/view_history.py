# tabs/view_history.py
import streamlit as st
from utils.data_manager import save_data
import pandas as pd

def show_view_history_tab(df):
    """Display the view history tab content with editing capabilities"""
    st.header("Journey History")
    
    if not df.empty:
        # Initialize session state for editing
        if 'editing_row' not in st.session_state:
            st.session_state.editing_row = None
        if 'edited_df' not in st.session_state:
            st.session_state.edited_df = df.copy()
            
        # Display data editing interface
        edited_df = st.data_editor(
            st.session_state.edited_df,
            key='journey_editor',
            num_rows="dynamic",
            column_config={
                "google_map_km": st.column_config.NumberColumn(
                    "Google Maps Distance (km)",
                    min_value=0.0,
                    max_value=1000.0,
                    format="%.1f km"
                ),
                "google_map_estimate_time": st.column_config.NumberColumn(
                    "Estimated Time (min)",
                    min_value=0,
                    max_value=300,
                    format="%d min"
                ),
                "battery_percent_before": st.column_config.NumberColumn(
                    "Starting Battery %",
                    min_value=0,
                    max_value=100,
                    format="%d%%"
                ),
                "battery_percent_after": st.column_config.NumberColumn(
                    "Ending Battery %",
                    min_value=0,
                    max_value=100,
                    format="%d%%"
                ),
                "drivable_km_before": st.column_config.NumberColumn(
                    "Starting Range (km)",
                    min_value=0,
                    format="%d km"
                ),
                "drivable_km_after": st.column_config.NumberColumn(
                    "Ending Range (km)",
                    min_value=0,
                    format="%d km"
                ),
                "total_km_before": st.column_config.NumberColumn(
                    "Starting Odometer",
                    min_value=0,
                    format="%d km"
                ),
                "total_km_after": st.column_config.NumberColumn(
                    "Ending Odometer",
                    min_value=0,
                    format="%d km"
                ),
                "temperature_before": st.column_config.NumberColumn(
                    "Starting Temp",
                    min_value=-50,
                    max_value=60,
                    format="%d°C"
                ),
                "temperature_after": st.column_config.NumberColumn(
                    "Ending Temp",
                    min_value=-50,
                    max_value=60,
                    format="%d°C"
                ),
                "timestamp_before": st.column_config.TextColumn(
                    "Start Time",
                    help="Time format: HH:MM"
                ),
                "timestamp_after": st.column_config.TextColumn(
                    "End Time",
                    help="Time format: HH:MM"
                ),
                "date_before": st.column_config.TextColumn(
                    "Start Date",
                    help="Date format: YYYY-MM-DD"
                ),
                "date_after": st.column_config.TextColumn(
                    "End Date",
                    help="Date format: YYYY-MM-DD"
                )
            },
            hide_index=True
        )
        
        # Save changes button
        if not edited_df.equals(df):
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("Save Changes"):
                    save_data(edited_df)
                    st.session_state.edited_df = edited_df
                    st.success("Changes saved successfully!")
                    st.rerun()
            with col2:
                if st.button("Discard Changes"):
                    st.session_state.edited_df = df.copy()
                    st.rerun()
        
        # Download button
        csv = edited_df.to_csv(index=False)
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name="ev_journeys.csv",
            mime="text/csv"
        )
    else:
        st.info("No journeys recorded yet.")

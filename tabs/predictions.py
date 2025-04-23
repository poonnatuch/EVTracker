# tabs/predictions.py
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path

# Path to the model files
MODELS_DIR = Path("machine_learning/weights")
TIME_MODEL_PATH = MODELS_DIR / "actual_time_drive_model.joblib"
BATTERY_MODEL_PATH = MODELS_DIR / "battery_usage_model.joblib"


def load_models():
    """Load the machine learning models"""
    try:
        time_model = joblib.load(TIME_MODEL_PATH)
        battery_model = joblib.load(BATTERY_MODEL_PATH)
        return time_model, battery_model
    except Exception as e:
        st.error(f"Error loading models: {str(e)}")
        return None, None


def predict_time(model, km, estimate_time):
    """Predict actual driving time based on distance and Google Maps estimated time"""
    try:
        # Convert inputs to the format expected by the model
        km = float(km)
        estimate_time = float(estimate_time)
        # Make prediction
        prediction = model.predict([[km, estimate_time]])[0]
        return prediction
    except Exception as e:
        st.error(f"Time prediction error: {str(e)}")
        return None


def predict_battery(model, km, estimate_time):
    """Predict battery usage based on distance and Google Maps estimated time"""
    try:
        # Convert inputs to the format expected by the model
        km = float(km)
        estimate_time = float(estimate_time)
        # Make prediction
        prediction = model.predict([[km, estimate_time]])[0]
        return prediction
    except Exception as e:
        st.error(f"Battery prediction error: {str(e)}")
        return None


def show_predictions_tab():
    """Display the predictions tab content"""
    st.header("Journey Predictions")

    # Load models
    time_model, battery_model = load_models()

    if time_model is None or battery_model is None:
        st.warning(
            "Could not load prediction models. Please check that the model files exist."
        )
        return

    # Display model information and description
    st.write(
        "This tab provides predictions based on machine learning models trained on your previous journey data."
    )

    # Create input form for journey parameters (used by both models)
    st.subheader("Journey Parameters")

    # Input form for both predictions
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            google_map_km = st.number_input(
                "Journey Distance (kilometers)",
                min_value=0.0,
                max_value=1000.0,
                value=50.0,
                step=5.0,
            )

        with col2:
            google_map_estimate_time = st.number_input(
                "Google Maps Estimated Time (minutes)",
                min_value=0.0,
                max_value=300.0,
                value=30.0,
                step=5.0,
            )

        submitted = st.form_submit_button("Generate Predictions")

    # Only make predictions if form is submitted
    if submitted:
        # Create columns for displaying prediction results
        result_col1, result_col2 = st.columns(2)

        with result_col1:
            st.subheader("Actual Drive Time Prediction")

            if time_model is not None:
                predicted_time = predict_time(
                    time_model, google_map_km, google_map_estimate_time
                )
                if predicted_time is not None:
                    st.metric(
                        "Predicted Actual Drive Time",
                        f"{predicted_time:.1f} minutes",
                        f"{predicted_time - google_map_estimate_time:+.1f} min vs Google",
                        help="Based on your driving patterns, this is how long the journey will likely take",
                    )

        with result_col2:
            st.subheader("Battery Usage Prediction")

            if battery_model is not None:
                predicted_battery = predict_battery(
                    battery_model, google_map_km, google_map_estimate_time
                )
                if predicted_battery is not None:
                    # Ensure prediction is between 0-100%
                    predicted_battery = min(max(predicted_battery, 0), 100)
                    st.metric(
                        "Predicted Battery Consumption",
                        f"{predicted_battery:.1f}%",
                        help="Based on your vehicle's performance, this is how much battery the journey will likely consume",
                    )

                    # Calculate the efficiency for reference
                    if predicted_battery > 0:
                        efficiency = google_map_km / predicted_battery
                        st.metric(
                            "Predicted Efficiency",
                            f"{efficiency:.2f} km/%",
                            help="Distance covered per percent of battery",
                        )

    # Additional information about the models
    st.subheader("About the Prediction Models")
    st.info(
        """
    These predictions are based on machine learning models trained on your previous journey data.
    Both models use the same inputs:
    - Google Maps distance (km)
    - Google Maps estimated time (minutes)
    
    Factors that may affect prediction accuracy:
    - Driving style and speed
    - Weather conditions
    - Traffic conditions
    - Vehicle load
    - Air conditioning/heating usage
    """
    )

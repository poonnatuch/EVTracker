# tabs/analytics.py
import streamlit as st
import pandas as pd
import numpy as np

def calculate_analytics_data(df):
    """Calculate all analytics metrics from the dataframe with focus on battery efficiency"""
    df = df.copy()
    
    # Basic distance and battery calculations
    df['actual_distance'] = df['total_km_after'] - df['total_km_before']
    df['battery_used'] = df['battery_percent_before'] - df['battery_percent_after']
    df['avg_temperature'] = (df['temperature_before'] + df['temperature_after']) / 2
    
    # Time and speed calculations - fixed by combining date and time
    df['start_datetime'] = pd.to_datetime(df['date_before'] + ' ' + df['timestamp_before'])
    df['end_datetime'] = pd.to_datetime(df['date_after'] + ' ' + df['timestamp_after'])
    df['actual_time'] = df['end_datetime'] - df['start_datetime']
    df['actual_time_minutes'] = df['actual_time'].dt.total_seconds() / 60
    df['time_difference'] = df['actual_time_minutes'] - df['google_map_estimate_time']
    df['time_accuracy'] = (df['google_map_estimate_time'] / df['actual_time_minutes']) * 100
    df['average_speed'] = df['actual_distance'] / (df['actual_time_minutes'] / 60)  # km/h
    
    # Filter valid data before calculating efficiency
    valid_data = df[
        (df['battery_used'] > 0) & 
        (df['actual_distance'] > 0) &
        (df['actual_time_minutes'] > 0)
    ].copy()
    
    if not valid_data.empty:
        # Battery efficiency metrics
        valid_data['km_per_battery'] = valid_data['actual_distance'] / valid_data['battery_used']
        valid_data['km_per_hour'] = valid_data['actual_distance'] / (valid_data['actual_time_minutes'] / 60)
        valid_data['battery_per_hour'] = valid_data['battery_used'] / (valid_data['actual_time_minutes'] / 60)
        
        # Categorize temperatures
        valid_data['temp_category'] = pd.cut(
            valid_data['avg_temperature'],
            bins=[-np.inf, 0, 10, 20, 30, np.inf],
            labels=['Below 0°C', '0-10°C', '10-20°C', '20-30°C', 'Above 30°C']
        )
        
        # Time efficiency categories - add safeguard for divide by zero
        valid_data['time_accuracy'] = np.where(
            valid_data['actual_time_minutes'] > 0,
            (valid_data['google_map_estimate_time'] / valid_data['actual_time_minutes']) * 100,
            100  # Default to 100% if time is zero
        )
        
        valid_data['time_efficiency'] = pd.cut(
            valid_data['time_accuracy'],
            bins=[0, 80, 90, 110, 120, np.inf],
            labels=['Very Slow', 'Slower', 'On Time', 'Faster', 'Very Fast']
        )
    
    return valid_data

def show_battery_overview(df):
    """Display key battery efficiency metrics"""
    st.subheader("Battery Efficiency Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_efficiency = df['km_per_battery'].mean()
        st.metric(
            "Average km per Battery %",
            f"{avg_efficiency:.2f} km/%",
            help="Average distance traveled per 1% battery consumption"
        )
    
    with col2:
        theoretical_range = avg_efficiency * 100
        st.metric(
            "Theoretical Full Range",
            f"{theoretical_range:.0f} km",
            help="Estimated range from 100% to 0% based on average efficiency"
        )
    
    with col3:
        efficiency_variation = df['km_per_battery'].std()
        st.metric(
            "Efficiency Variation",
            f"±{efficiency_variation:.2f} km/%",
            help="Standard deviation in efficiency (lower is more consistent)"
        )

def show_temperature_analysis(df):
    """Analyze and display temperature impact on battery efficiency"""
    st.subheader("Temperature Impact Analysis")
    
    # Temperature efficiency breakdown
    temp_efficiency = df.groupby('temp_category')['km_per_battery'].agg([
        ('avg_efficiency', 'mean'),
        ('min_efficiency', 'min'),
        ('max_efficiency', 'max'),
        ('journey_count', 'count')
    ]).reset_index()
    
    # Display temperature efficiency table
    st.write("Efficiency by Temperature Range")
    formatted_temp_df = pd.DataFrame({
        'Temperature Range': temp_efficiency['temp_category'],
        'Average km/%': temp_efficiency['avg_efficiency'].round(2),
        'Range (km/%)': temp_efficiency.apply(
            lambda x: f"{x['min_efficiency']:.2f} - {x['max_efficiency']:.2f}", axis=1
        ),
        'Sample Size': temp_efficiency['journey_count']
    })
    st.dataframe(formatted_temp_df, hide_index=True)
    
    # Temperature vs Efficiency scatter plot
    st.write("Temperature vs Battery Efficiency")
    temp_chart_data = pd.DataFrame({
        'Temperature (°C)': df['avg_temperature'],
        'Efficiency (km/%)': df['km_per_battery']
    })
    st.scatter_chart(data=temp_chart_data)

def show_efficiency_trends(df):
    """Display efficiency trends over time"""
    st.subheader("Efficiency Trends")
    
    # Prepare data for the time series
    trend_data = pd.DataFrame({
        'Date': pd.to_datetime(df['date_before']),
        'Efficiency (km/%)': df['km_per_battery']
    })
    
    # Group by date and calculate average efficiency
    daily_efficiency = (trend_data
        .groupby('Date')['Efficiency (km/%)']
        .mean()
        .reset_index()
        .sort_values('Date'))
    
    # Display the line chart
    st.line_chart(
        daily_efficiency.set_index('Date')
    )
    
    # Calculate trend statistics
    recent_efficiency = daily_efficiency.iloc[-1]['Efficiency (km/%)']
    avg_efficiency = daily_efficiency['Efficiency (km/%)'].mean()
    efficiency_change = ((recent_efficiency - avg_efficiency) / avg_efficiency) * 100
    
    # Display trend metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Most Recent Efficiency",
            f"{recent_efficiency:.2f} km/%",
            f"{efficiency_change:+.1f}% vs average",
            help="Latest recorded efficiency compared to historical average"
        )
    with col2:
        # Calculate efficiency trend (positive or negative)
        if len(daily_efficiency) > 1:
            first_half_avg = daily_efficiency['Efficiency (km/%)'].iloc[:len(daily_efficiency)//2].mean()
            second_half_avg = daily_efficiency['Efficiency (km/%)'].iloc[len(daily_efficiency)//2:].mean()
            trend_change = ((second_half_avg - first_half_avg) / first_half_avg) * 100
            st.metric(
                "Efficiency Trend",
                "Improving" if trend_change > 0 else "Declining",
                f"{trend_change:+.1f}% change",
                help="Trend based on comparison of first and second half of data"
            )

def show_battery_consumption_patterns(df):
    """Analyze battery consumption patterns"""
    st.subheader("Battery Consumption Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distance vs Battery Usage
        st.write("Distance vs Battery Consumption")
        consumption_data = pd.DataFrame({
            'Distance (km)': df['actual_distance'],
            'Battery Used (%)': df['battery_used']
        })
        st.scatter_chart(consumption_data)
        
        # Calculate and display correlation
        correlation = df['actual_distance'].corr(df['battery_used'])
        st.metric(
            "Distance-Battery Correlation",
            f"{correlation:.2f}",
            help="1.0 indicates perfect correlation between distance and battery usage"
        )
    
    with col2:
        # Battery efficiency distribution
        st.write("Battery Efficiency Distribution")
        efficiency_hist_data = pd.DataFrame({
            'Efficiency (km/%)': df['km_per_battery']
        })
        st.bar_chart(efficiency_hist_data)

def show_time_analysis(df):
    """Display time estimation accuracy analysis"""
    st.subheader("Time Estimation Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        avg_time_accuracy = df['time_accuracy'].mean()
        st.metric(
            "Average Route Accuracy",
            f"{avg_time_accuracy:.1f}%",
            help="How close actual distances match Google Maps estimates"
        )
    
    with col2:
        # Fixed: Use average_speed instead of time_efficiency categorical data
        avg_speed = df['average_speed'].mean()
        st.metric(
            "Average Speed",
            f"{avg_speed:.1f} km/h",
            help="Average travel speed"
        )
    
    # Add time estimation accuracy chart
    st.write("Time Estimation Accuracy Over Time")
    accuracy_data = pd.DataFrame({
        'Date': pd.to_datetime(df['date_before']),
        'Accuracy (%)': df['time_accuracy']
    })
    st.line_chart(accuracy_data.set_index('Date'))

def show_analytics_tab(df):
    """Display the analytics tab content with focus on battery efficiency"""
    st.header("Battery & Range Analytics")
    
    if not df.empty:
        # Calculate analytics data first
        analytics_df = calculate_analytics_data(df)
        
        if not analytics_df.empty:
            # Show all analysis sections
            show_battery_overview(analytics_df)
            show_efficiency_trends(analytics_df)
            show_temperature_analysis(analytics_df)
            show_time_analysis(analytics_df)
            show_battery_consumption_patterns(analytics_df)
        else:
            st.warning("No valid journey data available for analysis. Please ensure journeys are recorded with proper battery and distance measurements.")
    else:
        st.info("No journey data available for analytics yet.")
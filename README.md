# EV Journey Tracker 🚗

A Streamlit-based application for tracking and analyzing electric vehicle journeys, with a focus on battery efficiency and range analysis.

## Features

### Track Journeys
- Record start and end journey metrics including:
  - Battery percentage
  - Drivable range
  - Total odometer reading
  - Temperature
  - Google Maps estimated distance and time
- Smart defaults based on previous journey data
- Edit journey start values before completion
- Temporary journey storage to prevent data loss

### View History
- Complete journey history in an editable table format
- Data validation with min/max constraints
- Export data to CSV
- Edit or delete previous journey records
- Dynamic row addition and modification

### Analytics
- Comprehensive battery efficiency analysis:
  - Average kilometers per battery percentage
  - Theoretical full range estimation
  - Efficiency variation statistics
- Temperature impact analysis:
  - Efficiency breakdown by temperature ranges
  - Temperature vs efficiency visualization
- Efficiency trends:
  - Historical efficiency tracking
  - Trend analysis and comparison
- Battery consumption patterns:
  - Distance vs battery usage correlation
  - Efficiency distribution analysis
- Time estimation analysis:
  - Route accuracy metrics
  - Average speed calculations

### Predictions
- Machine learning-based predictions:
  - Actual driving time prediction based on Google Maps estimates
  - Battery consumption prediction for planned journeys
  - Efficiency calculations for planned routes
- Interactive prediction form with customizable parameters
- Detailed prediction insights and comparative metrics

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ev-journey-tracker.git
cd ev-journey-tracker
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
streamlit run main.py
```

2. Navigate through the four main tabs:
   - **Track Journey**: Record new journeys
   - **View History**: Review and edit past journeys
   - **Analytics**: Analyze journey data and efficiency metrics
   - **Predictions**: Get ML-based predictions for planned journeys

## Project Structure

```
ev-journey-tracker/
├── main.py                 # Application entry point
├── utils/
│   └── data_manager.py     # Data handling utilities
├── tabs/
│   ├── track_journey.py    # Journey tracking interface
│   ├── view_history.py     # History viewing and editing
│   ├── analytics.py        # Analytics and visualizations
│   └── predictions.py      # ML-based predictions
├── machine_learning/
│   └── weights/            # ML model files
│       ├── actual_time_drive_model.joblib
│       └── battery_usage_model.joblib
└── ev_journeys.csv         # Journey data storage
```

## Data Storage

The application stores journey data in a CSV file (`ev_journeys.csv`) with the following fields:
- `google_map_km`: Estimated journey distance from Google Maps
- `google_map_estimate_time`: Estimated journey time from Google Maps (minutes)
- `battery_percent_before/after`: Battery percentage at start/end
- `drivable_km_before/after`: Available range at start/end
- `total_km_before/after`: Odometer reading at start/end
- `temperature_before/after`: Temperature at start/end
- `timestamp_before/after`: Time at start/end
- `date_before/after`: Date at start/end

## Machine Learning Models

The application uses two pre-trained machine learning models:
- **Actual Drive Time Model**: Predicts the actual journey duration based on Google Maps distance and estimated time
- **Battery Usage Model**: Predicts the battery consumption for a planned journey

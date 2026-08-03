"""
Weather station data analysis script.

This script parses meteorological station CSV records, extracts the wind speed
and wind direction columns, and performs a vectorized conversion of the wind
direction from degrees to radians for subsequent physical computations.

:var weather_df: The parsed meteorological station dataset.
:type weather_df: pandas.DataFrame
:var wind_speed: Array of collected wind speed records.
:type wind_speed: numpy.ndarray
:var wind_direction: Array of wind direction records in degrees.
:type wind_direction: numpy.ndarray
:var wind_direction_rad: Array of wind direction records converted to radians.
:type wind_direction_rad: numpy.ndarray
"""

import pandas as pd  # Data analysis library
import numpy as np   # Numerical operations library

# Security/Sphinx Guard: Only execute the file loading if this script is run directly.
# This prevents FileNotFoundError crashes when Sphinx imports the module.
if __name__ == '__main__':
    # Load weather data from the CSV file
    weather_df = pd.read_csv('april2024_station_data.csv')

    # Convert columns to NumPy arrays for faster calculations
    wind_speed = weather_df['wind_speed'].to_numpy()
    wind_direction = weather_df['wind_direction'].to_numpy()

    # Convert wind direction from degrees to radians (needed for trigonometry)
    wind_direction_rad = np.deg2rad(wind_direction)
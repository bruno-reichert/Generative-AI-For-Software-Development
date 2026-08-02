import pandas as pd  # Data analysis library
import numpy as np   # Numerical operations library

# Load weather data from the CSV file
weather_df = pd.read_csv('april2024_station_data.csv')

# Convert columns to NumPy arrays for faster calculations
wind_speed = weather_df['wind_speed'].to_numpy()
wind_direction = weather_df['wind_direction'].to_numpy()

# Convert wind direction from degrees to radians (needed for trigonometry)
wind_direction_rad = np.deg2rad(wind_direction)
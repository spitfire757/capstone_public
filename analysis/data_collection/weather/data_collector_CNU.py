import os
import pandas as pd
from weather_api_hist import Wapi

# Function to append unique data to CSV
def append_unique_to_csv(new_data, file_path):
    if os.path.exists(file_path):
        # Load existing data
        existing_data = pd.read_csv(file_path)
        # Concatenate and drop duplicates based on the datetime column
        combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset="date")
        # Write the combined data back to the file
        combined_data.to_csv(file_path, mode='w', header=True, index=False)
    else:
        # If the file doesn't exist, create it with the new data
        new_data.to_csv(file_path, mode='w', header=True, index=False)

def collect_weather_data():
    # Define the location (latitude and longitude)
    lat, lon = 37.065974,-76.490285  # estimated 36.9804, -76.4297

    # Create an instance of the Wapi class and get historical data
    wapi_instance = Wapi()
    data = wapi_instance.get_hist_data(lat, lon)

    # File paths for the CSV files
    hourly_csv = "/home/bkelley/capstone/data_collection/weather/data/hourly_weather_data.csv"
    daily_csv = "/home/bkelley/capstone/data_collection/weather/data/daily_weather_data.csv"

    # Append unique hourly and daily data to the respective CSV files
    append_unique_to_csv(data.hourly_response, hourly_csv)
    append_unique_to_csv(data.daily_response, daily_csv)

    print(f"Data successfully collected and written to {hourly_csv} and {daily_csv}")

if __name__ == "__main__":
    collect_weather_data()


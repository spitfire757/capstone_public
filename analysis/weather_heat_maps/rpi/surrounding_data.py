#!/usr/bin/env python3

import sys
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from dataclasses import dataclass
from timezonefinder import TimezoneFinder
from datetime import datetime, timedelta
import pytz
import time 

# Location to save data files
data_loc = '/home/bkelley/main/data/'

class Wapi:
    def __init__(self, cache_location=".cache", expire_after=-1, retries=5, backoff_factor=0.2):
        # Set up session with cache and retry mechanism
        self.cache_session = requests_cache.CachedSession(cache_location, expire_after=expire_after)
        self.retry_session = retry(self.cache_session, retries=retries, backoff_factor=backoff_factor)
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)

    @dataclass
    class Responses:
        hourly_response: pd.DataFrame = None

    @staticmethod
    def get_timezone(lat, lon):
        # Create an instance of the TimezoneFinder
        lat, lon = float(lat), float(lon)
        tf = TimezoneFinder()
        # Get the timezone name based on lat and lon
        timezone_str = tf.timezone_at(lat=lat, lng=lon)
        if timezone_str is None:
            return "Timezone not found"
        # Load the timezone object
        timezone = pytz.timezone(timezone_str)
        # Get the current time in that timezone
        current_time = datetime.now(timezone)
        # Get the timezone abbreviation (3-letter designation)
        timezone_abbr = current_time.strftime('%Z')
        return f"Timezone: {timezone_str}, Abbreviation: {timezone_abbr}"

    def get_hist_data(self, lat, lon):
        # Define date range
        start_date = "2022-01-01"
        end_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation",
                       "rain", "weather_code", "surface_pressure", "cloud_cover",
                       "wind_speed_10m", "wind_speed_100m", "wind_direction_10m",
                       "wind_direction_100m"]
        }
        responses = self.openmeteo.weather_api(url, params=params)

        response = responses[0]
        print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation {response.Elevation()} m asl")
        print(Wapi.get_timezone(lat, lon))

        # Process hourly data
        hourly = response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
            "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
            "precipitation": hourly.Variables(2).ValuesAsNumpy(),
            "rain": hourly.Variables(3).ValuesAsNumpy(),
            "weather_code": hourly.Variables(4).ValuesAsNumpy(),
            "surface_pressure": hourly.Variables(5).ValuesAsNumpy(),
            "cloud_cover": hourly.Variables(6).ValuesAsNumpy(),
            "wind_speed_10m": hourly.Variables(7).ValuesAsNumpy(),
            "wind_speed_100m": hourly.Variables(8).ValuesAsNumpy(),
            "wind_direction_10m": hourly.Variables(9).ValuesAsNumpy(),
            "wind_direction_100m": hourly.Variables(10).ValuesAsNumpy(),
        }
        hourly_dataframe = pd.DataFrame(data=hourly_data)

        return self.Responses(hourly_response=hourly_dataframe)


def grab_data(latlon_list, user_ID):
    wapi_instance = Wapi()
    request_count = 0  # Initialize counter
    start_time = time.time()  # Track the start of a new minute

    for lat, lon in latlon_list:
        # Check if 60 seconds have passed and reset the counter
        elapsed_time = time.time() - start_time
        if elapsed_time >= 60:
            request_count = 0
            start_time = time.time()  # Reset the start time

        # Pause if close to the limit (500 requests to be safe)
        if request_count >= 500:
            # Calculate remaining time until the next minute mark
            time_to_wait = 60 - elapsed_time
            print(f"Approaching limit: waiting for {time_to_wait:.2f} seconds.")
            time.sleep(time_to_wait)
            request_count = 0  # Reset counter after waiting
            start_time = time.time()  # Restart timer

        # Fetch historical data
        try:
            data = wapi_instance.get_hist_data(lat, lon)
            
            # Save hourly data to CSV file
            hourly_file = f"{data_loc}{user_ID}_{lat}_{lon}_hourly.csv"
            data.hourly_response.to_csv(hourly_file, index=False)
            print(f"Data saved for {user_ID} at ({lat}, {lon})")

            # Increment request count
            request_count += 1

        except Exception as e:
            # Convert exception to string and check for the rate limit message
            error_message = str(e)
            print(f"API request error: {error_message}")
            
            # If the error is due to rate limiting, wait and retry
            if "Minutely API request limit exceeded" in error_message:
                print("Rate limit exceeded, waiting for 60 seconds before retrying.")
                time.sleep(60)
                request_count = 0  # Reset counter after waiting
                start_time = time.time()  # Restart timer
                continue  # Retry the current lat/lon after waiting

        # Short pause between requests
        time.sleep(0.6)  # Adjust as needed

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
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import os


# Location to save data files
data_loc = '/work/bkelley/large_data/weather/'

# Wapi class definition as before

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
        # Get timezone information
        lat, lon = float(lat), float(lon)
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=lat, lng=lon)
        if timezone_str is None:
            return "Timezone not found"
        timezone = pytz.timezone(timezone_str)
        current_time = datetime.now(timezone)
        timezone_abbr = current_time.strftime('%Z')
        return f"Timezone: {timezone_str}, Abbreviation: {timezone_abbr}"

    def get_hist_data(self, lat, lon):
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
        print(Wapi.get_timezone(lat, lon))

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



def grab_data(points_gdf, user_ID, overwrite=False):
    wapi_instance = Wapi()
    request_count = 0
    start_time = time.time()

    for index, row in points_gdf.iterrows():
        lat, lon = row['geometry'].y, row['geometry'].x

        # Check if 60 seconds have passed and reset the counter
        elapsed_time = time.time() - start_time
        if elapsed_time >= 60:
            request_count = 0
            start_time = time.time()

        # Handle rate limit
        if request_count >= 500:
            time_to_wait = 60 - elapsed_time
            print(f"Approaching limit: waiting for {time_to_wait:.2f} seconds.")
            time.sleep(time_to_wait)  # Wait for remaining time in the minute
            request_count = 0
            start_time = time.time()

        # Prepare the file path
        hourly_file = f"{data_loc}{user_ID}_{lat}_{lon}_hourly.csv"

        # Check if the file exists and whether to overwrite
        if not overwrite and os.path.exists(hourly_file):
            print(f"File already exists for ({lat}, {lon}). Skipping...")
            continue  # Skip to the next point

        try:
            # Fetch the data from the API
            data = wapi_instance.get_hist_data(lat, lon)
            
            # Save the data if the file doesn't exist or we want to overwrite
            data.hourly_response.to_csv(hourly_file, index=False)
            print(f"Data saved for {user_ID} at ({lat}, {lon})")

            # Update request count
            request_count += 1

        except Exception as e:
            error_message = str(e)
            print(f"API request error: {error_message}")
            if "Minutely API request limit exceeded" in error_message:
                print("Rate limit exceeded, waiting for 60 seconds before retrying.")
                time.sleep(60)
                request_count = 0
                start_time = time.time()
                continue  # Retry the same request

        time.sleep(0.6)  # Adjust to avoid hitting rate limits, if necessary
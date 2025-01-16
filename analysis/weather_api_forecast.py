#!/usr/bin/env python3
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

global lat, lon
lat, lon = 37.065974, -76.490285

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Open-Meteo API parameters
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": lat,
    "longitude": lon,
    "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation",
               "rain", "weather_code", "surface_pressure", "cloud_cover",
               "wind_speed_10m", "wind_speed_100m", "wind_direction_10m",
               "wind_direction_100m"],
    "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min",
              "precipitation_sum", "rain_sum", "wind_speed_10m_max",
              "wind_direction_10m_dominant"],
    "forecast_days": 15
}

# Send API request
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data
hourly = response.Hourly()

# Assign requested variables correctly to the corresponding values
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
hourly_rain = hourly.Variables(3).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(4).ValuesAsNumpy()
hourly_surface_pressure = hourly.Variables(5).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(6).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(7).ValuesAsNumpy()
hourly_wind_speed_100m = hourly.Variables(8).ValuesAsNumpy()
hourly_wind_direction_10m = hourly.Variables(9).ValuesAsNumpy()
hourly_wind_direction_100m = hourly.Variables(10).ValuesAsNumpy()

# Create a DataFrame for hourly data
hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ),
    "temperature_2m": hourly_temperature_2m,
    "relative_humidity_2m": hourly_relative_humidity_2m,
    "precipitation": hourly_precipitation,
    "rain": hourly_rain,
    "weather_code": hourly_weather_code,
    "surface_pressure": hourly_surface_pressure,
    "cloud_cover": hourly_cloud_cover,
    "wind_speed_10m": hourly_wind_speed_10m,
    "wind_speed_100m": hourly_wind_speed_100m,
    "wind_direction_10m": hourly_wind_direction_10m,
    "wind_direction_100m": hourly_wind_direction_100m
}

hourly_dataframe = pd.DataFrame(data=hourly_data)

# Process daily data
daily = response.Daily()

# Assign requested variables correctly to the corresponding values
daily_weather_code = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(3).ValuesAsNumpy()
daily_rain_sum = daily.Variables(4).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(5).ValuesAsNumpy()
daily_wind_direction_10m_dominant = daily.Variables(6).ValuesAsNumpy()

# Create a DataFrame for daily data
daily_data = {
    "date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(days=1),
        inclusive="left"
    ),
    "weather_code": daily_weather_code,
    "temperature_2m_max": daily_temperature_2m_max,
    "temperature_2m_min": daily_temperature_2m_min,
    "precipitation_sum": daily_precipitation_sum,
    "rain_sum": daily_rain_sum,
    "wind_speed_10m_max": daily_wind_speed_10m_max,
    "wind_direction_10m_dominant": daily_wind_direction_10m_dominant
}

daily_dataframe = pd.DataFrame(data=daily_data)
hourly_dataframe.to_csv('/home/bkelley/capstone/data_collection/weather/data/NOAA_forecast.csv')


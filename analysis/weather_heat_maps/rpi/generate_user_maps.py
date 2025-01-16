import os
import numpy as np
import openmeteo_requests
import requests_cache
import pandas as pd
import seaborn as sns
from retry_requests import retry
from PIL import Image
from scipy.interpolate import griddata
import geopandas as gpd
import argparse
import xgboost as xgb
from surrounding_data import grab_data
import time
import matplotlib.pyplot as plt

# Global variables
global cache_session, retry_session, openmeteo, url, data_loc
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)
url = "https://api.open-meteo.com/v1/forecast"
data_loc = '/home/bkelley/capstone/weather_heat_maps/data'


def grab_9_points(lat, lon):
    c = 1.25  # Degrees
    center = (lat, lon)
    tl = (lat + c, lon - c)  # Top-Left
    tr = (lat + c, lon + c)  # Top-Right
    bl = (lat - c, lon - c)  # Bottom-Left
    br = (lat - c, lon + c)  # Bottom-Right
    mt = (lat + c / 2, lon)       # Mid-Top
    mb = (lat - c / 2, lon)       # Mid-Bottom
    ml = (lat, lon - c / 2)       # Mid-Left
    mr = (lat, lon + c / 2)       # Mid-Right

    points = [center, tl, tr, bl, br, mt, mb, ml, mr]
    return points


def process_points(points, user_ID):
    """
    Ensure data availability for all points by fetching data if missing.
    """
    for lat_point, lon_point in points:
        file_path = f"{data_loc}/{user_ID}_{lat_point}_{lon_point}_hourly.csv"
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}. Fetching data using grab_data...")
            try:
                grab_data([(lat_point, lon_point)], user_ID)
            except Exception as e:
                print(f"Failed to fetch data for point ({lat_point}, {lon_point}): {e}")
                continue


def create_user_models(user_ID, lat, lon, filt):
    points = grab_9_points(lat, lon)
    process_points(points, user_ID)  # Ensure data is available
    
    features = [
        'relative_humidity_2m', 'precipitation', 'rain', 'weather_code', 'surface_pressure',
        'cloud_cover', 'wind_speed_10m', 'wind_speed_100m', 'wind_direction_10m',
        'wind_direction_100m', 'temperature_2m_K', 'surface_pressure_Pa', 'density', 'speed_of_sound'
    ]
    arr = []  # To store DataFrames for further processing
    
    for lat_point, lon_point in points:
        file_path = f"{data_loc}/{user_ID}_{lat_point}_{lon_point}_hourly.csv"
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            continue
        
        for col in features:
            if col not in df.columns:
                df[col] = 0
        
        arr.append(df)

        for feature in features:
            print(f"Training model for feature: {feature}")
            X = df.drop(columns=['date', feature], errors='ignore')
            X = pd.get_dummies(X, columns=['weather_code'], drop_first=True)
            y = df.get(feature, pd.Series(0))

            dtrain = xgb.DMatrix(X, label=y)
            params = {'objective': 'reg:squarederror', 'max_depth': 6, 'eta': 0.1, 'subsample': 0.8, 'colsample_bytree': 0.8}
            model = xgb.train(params, dtrain, num_boost_round=100)
            
            model_dir = "/home/bkelley/main/models"
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, f"xgb_{user_ID}_{lat_point}_{lon_point}_{feature}.model")
            model.save_model(model_path)
            print(f"Model saved: {model_path}")
    
    return arr, points


def plot_surface_pressure_heatmaps(arr, lat_lon_list, user_ID, output_dir, filt, center_lat_lon):
    os.makedirs(output_dir, exist_ok=True)
    world = gpd.read_file('/home/bkelley/capstone/weather_heat_maps/data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp')
    combined_df = pd.DataFrame()
    
    for df, (lat, lon) in zip(arr, lat_lon_list):
        df['latitude'] = lat
        df['longitude'] = lon
        combined_df = pd.concat([combined_df, df])
    
    combined_df['date'] = pd.to_datetime(combined_df['date'])
    combined_df['hour'] = combined_df['date'].dt.floor('h')
    
    for hour in combined_df['hour'].unique():
        hour_data = combined_df[combined_df['hour'] == hour]
        if hour_data.empty:
            continue
        grid_latitude, grid_longitude = np.meshgrid(
            np.linspace(hour_data['latitude'].min(), hour_data['latitude'].max(), 200),
            np.linspace(hour_data['longitude'].min(), hour_data['longitude'].max(), 200)
        )
        grid_surface_pressure = griddata(
            (hour_data['latitude'], hour_data['longitude']),
            hour_data[f'{filt}'],
            (grid_latitude, grid_longitude),
            method='cubic'
        )
        plt.figure(figsize=(12, 8))
        plt.pcolormesh(grid_longitude, grid_latitude, grid_surface_pressure, shading='auto', cmap='viridis')
        plt.colorbar(label=f'{filt} (hPa)')
        plt.title(f'{filt} for Hour: {hour.strftime("%Y-%m-%d %H:%M:%S")}')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        world.boundary.plot(ax=plt.gca(), color='black')
        output_file = os.path.join(output_dir, f'user_{user_ID}_{filt}_heatmap_{hour.strftime("%Y%m%d_%H")}.png')
        plt.savefig(output_file)
        plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map for a specific user location.")
    parser.add_argument("user_ID", type=str, help="The user ID")
    parser.add_argument("lat", type=float, help="The latitude of the user's location")
    parser.add_argument("lon", type=float, help="The longitude of the user's location")
    parser.add_argument("filt", type=str, help="The filter")
    args = parser.parse_args()

    user_ID = args.user_ID
    lat = args.lat
    lon = args.lon
    filt = args.filt

    start_time = time.time()
    arr, points = create_user_models(user_ID, lat, lon, filt)
    plot_surface_pressure_heatmaps(arr, points, user_ID, data_loc, filt, (lat, lon))
    create_gif_from_pngs(data_loc, f'{data_loc}/{user_ID}_{lat}_{lon}_{filt}.gif')
    end_time = time.time()

    print(f"The program took {end_time - start_time:.2f} seconds to run.")


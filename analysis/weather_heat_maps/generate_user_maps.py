import matplotlib.pyplot as plt
import numpy as np
import openmeteo_requests
import requests_cache
import pandas as pd
import seaborn as sns 
from retry_requests import retry
import os
from PIL import Image
from scipy.interpolate import griddata
import geopandas as gpd
import argparse
import xgboost as xgb
from surrounding_data import grab_data
import time

global cache_session, retry_session, openmeteo, url
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)
url = "https://api.open-meteo.com/v1/forecast"


def get_bound_area(lat, lon):
    # Create a square with lat, lon in the center (lat, lon) = (y, x) in Cartesian
    c = 0.5  # Degrees
    point_1 = (lat, lon)
    tl = (lat + c, lon - c)  # Top-Left
    tr = (lat + c, lon + c)  # Top-Right
    bl = (lat - c, lon - c)  # Bottom-Left
    br = (lat - c, lon + c)  # Bottom-Right
    # Create a list of the corner points
    points = [point_1, tl, tr, bl, br]
    # Extract latitudes and longitudes from the corner points
    latitudes, longitudes = zip(*points)
    # Create the plot
    plt.figure(figsize=(8, 6))
    plt.scatter(longitudes, latitudes, marker='o', color='blue')
    # Generate a grid of points within the bounding area
    # Define the number of points in each direction
    num_points = 1  # Reoslution (opitmal before backoff factor passed)
    lat_range = np.linspace(lat - c, lat + c, num_points)
    lon_range = np.linspace(lon - c, lon + c, num_points)
    # Create a dictionary to store the points
    point_dict = {}
    index = 0
    # Populate the dictionary with points
    for latitude in lat_range:
        for longitude in lon_range:
            point_dict[index] = (latitude, longitude)
            index += 1
    # Optional: Plot the grid of points

    for latitude in lat_range:
        for longitude in lon_range:
            plt.scatter(longitude, latitude, marker='x', color='orange', alpha=0.5)

    # Set plot labels and title

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Bounding Area with Grid Points')
    plt.grid()
    plt.axhline(0, color='gray', linewidth=0.5, linestyle='--')
    plt.axvline(0, color='gray', linewidth=0.5, linestyle='--')
    plt.xlim(lon - c - 0.1, lon + c + 0.1)
    plt.ylim(lat - c - 0.1, lat + c + 0.1)
    # Show the plot
    plt.show()
    return point_dict

def grab_4_points(lat, lon):
    # Create a square with lat, lon in the center (lat, lon) = (y, x) in Cartesian
    c = 0.5  # Degrees
    point_1 = (lat, lon)
    tl = (lat + c, lon - c)  # Top-Left
    tr = (lat + c, lon + c)  # Top-Right
    bl = (lat - c, lon - c)  # Bottom-Left
    br = (lat - c, lon + c)  # Bottom-Right
    # Create a list of the corner points
    points = [point_1, tl, tr, bl, br]
    # Extract latitudes and longitudes from the corner points
    latitudes, longitudes = zip(*points)
    # return dict(map(lambda x, y: (x, y), latitudes, longitudes))
    return points


def create_user_models(user_ID=str, lat=float, lon=float, filt=str):
    '''
    This function will generate 5 independent models, one for each bounding point and the center point.
    Each model will make hourly predictions for 15 days. The resulting data is saved to separate CSV files
    based on the user ID and coordinates.
    '''
    points = grab_4_points(lat, lon)
    
    print("Loading model...")
    xgb_model = xgb.Booster()
    xgb_model.load_model('/home/bkelley/capstone/xgb_model_pres_temp.json')
    
    print("Grabbing historical data for 5 points...")
    grab_data(points, user_ID)
    
    features = [
        'relative_humidity_2m', 'precipitation', 'rain', 
        'weather_code', 'surface_pressure', 'cloud_cover', 'wind_speed_10m',
        'wind_speed_100m', 'wind_direction_10m', 'wind_direction_100m', 
        'temperature_2m_K', 'surface_pressure_Pa', 'density', 'speed_of_sound'
    ]
    
    future_data_list = []  # To store future predictions for each point

    for lat_point, lon_point in points:        
        print(f'Preparing data for prediction at ({lat_point}, {lon_point})...')

        
        file_path = f"/home/bkelley/capstone/weather_heat_maps/data/{user_ID}_{lat_point}_{lon_point}_hourly.csv"
        
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            continue

        
        # Ensure required columns are present, add missing columns as zeros
        for col in features:
            if col not in df.columns:
                df[col] = 0

        X = df[features]
        X = pd.get_dummies(X, columns=['weather_code'], drop_first=True)
        
        # Align columns with the model’s expected feature names
        missing_cols = set(xgb_model.feature_names) - set(X.columns)
        for col in missing_cols:
            X[col] = 0
        
        X = X[xgb_model.feature_names]
        print(f'Predicting for point ({lat_point}, {lon_point})...')

        dtest = xgb.DMatrix(X)
        predictions = xgb_model.predict(dtest)

        
        df['predictions'] = predictions
        
        future_dates = pd.date_range(start=df['date'].max(), periods=15*24, freq='h')
        future_data = df.iloc[-24:].copy()
        future_data = pd.concat([future_data] * 15, ignore_index=True)
        future_data['date'] = future_dates
        
        X_future = future_data[features]
        X_future = pd.get_dummies(X_future, columns=['weather_code'], drop_first=True)
        
        missing_cols = set(X.columns) - set(X_future.columns)
        for col in missing_cols:
            X_future[col] = 0
        
        X_future = X_future[X.columns]
        
        dtest_future = xgb.DMatrix(X_future)
        future_predictions = xgb_model.predict(dtest_future)
        
        future_data['predictions'] = future_predictions
        # Filter out uneccessary data
        future_data['date'] = future_data['date'].dt.tz_localize(None)  # Remove timezone
        future_data = future_data[future_data['date'] >= pd.Timestamp('today').normalize()]
        future_data = future_data[['date', f'{filt}']]
        future_data_list.append(future_data)
    # returns 
    # furture_data_list :  list of dataframes which correspond to 5 points in order and each df 
    #     contains the date of prediction and prediction value for specified filter param
    # points : All 5 points
    return future_data_list, points
 
def create_heat_maps(user_ID, lat, lon):
    '''
    Once the 5 df's files have been created it will then plot the data as an array, then bi-cubicly interpotlate 
    the data as ind. pngs for each hour (these heatmaps will be hourly only). Then it will create a GIF based on all 
    the heatmaps, delete the old heatmaps to save space, then  it will save the gifs under a user_ID dir with
    unique (user_ID agian) names. That way when a user requests the data it can easily be dispaled using some 
    php on the SkySynth website
    '''
    return 0 


def create_gif_from_pngs(source_dir, output_gif_path, duration=150):
    """
    Combine all PNG images in a directory into a GIF.

    Parameters:
    - source_dir (str): Path to the directory containing PNG images.
    - output_gif_path (str): Path where the output GIF will be saved.
    - duration (int): Duration for each frame in milliseconds.
    """
    from PIL import Image  # Import here to avoid dependency issues

    # List all PNG files in the directory
    png_files = [f for f in os.listdir(source_dir) if f.endswith('.png')]
    png_files.sort()  # Sort files if needed (e.g., by name)

    # Create a list to hold the images
    images = []

    for file in png_files:
        image_path = os.path.join(source_dir, file)
        # Open image and append it to the list
        images.append(Image.open(image_path))

    # Save as GIF
    if images:
        images[0].save(output_gif_path, save_all=True, append_images=images[1:], duration=duration, loop=0)



if __name__ == "__main__":
    start_time = time.time()
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate a map for a specific user location.")
    
    # Add arguments for user ID, latitude, and longitude
    parser.add_argument("user_ID", type=str, help="The user ID")
    parser.add_argument("lat", type=float, help="The latitude of the user's location")
    parser.add_argument("lon", type=float, help="The longitude of the user's location")
    parser.add_argument("filt", type=str, help="The filter")

    # Parse arguments
    args = parser.parse_args()

    # assing args to variables
    user_ID = args.user_ID
    lat = args.lat
    lon = args.lon
    filt = args.filt
    arr, points = create_user_models(user_ID, lat, lon, filt)
    end_time = time.time()
    print(f"The program took {end_time - start_time:.2f} seconds to run.")
    # DEBUG : 
    #print(arr[0])
    # User_ID, lat, and lon are all accounted for ind. users now and can be executed via shell
    # point_dict = get_bound_area(lat, lon)  # for bounding area of user input lat, lon
    # points = grab_4_points(lat, lon) 
    



from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from scipy.interpolate import griddata
import xgboost as xgb
from PIL import Image
import geopandas as gpd  # Import GeoPandas

def predict_and_plot(user_ID, parameter, arr, lat_lon_list, output_dir, lat, lon):
    os.makedirs(output_dir, exist_ok=True)

    # Load world shapefile for plotting boundaries (replace with correct path if needed)
    world = gpd.read_file('main/data/ne_10m_admin_2_counties/ne_10m_admin_2_counties.shp')  # Adjust this path

    # Calculate the bounding box for the region based on lat_lon_list
    latitudes = [lat_point for lat_point, _ in lat_lon_list]
    longitudes = [lon_point for _, lon_point in lat_lon_list]
    
    min_lat = min(latitudes)
    max_lat = max(latitudes)
    min_lon = min(longitudes)
    max_lon = max(longitudes)

    # Create a date range for the next 5 days (hourly)
    # 3 days is only accuracy valid. AHHHH 
    start_date = datetime.now()
    future_dates = [start_date + timedelta(hours=i) for i in range(3 * 24)]

    print("Generating predictions...")
    heatmap_files = []

    for future_date in future_dates:
        combined_data = []

        for df, (lat_point, lon_point) in zip(arr, lat_lon_list):
            # Create a row with the necessary features for prediction
            row = {
                'latitude': lat_point,
                'longitude': lon_point,
                'date': future_date,
                'hour': future_date.hour,
            }

            # Ensure the data changes as time progresses
            for col in df.columns:
                if col not in ['date', parameter]:
                    # Use the current time step data for the feature
                    row[col] = df[col].iloc[future_date.hour] if col in df.columns else 0

            combined_data.append(row)

        future_df = pd.DataFrame(combined_data)

        # Prepare data for model prediction
        X_future = future_df.drop(columns=['date', parameter], errors='ignore')

        # One-hot encode weather_code if present
        if 'weather_code' in X_future.columns:
            X_future = pd.get_dummies(X_future, columns=['weather_code'], drop_first=True)

        # Load the trained model for the parameter
        model_dir = "/Users/brendankelley/Desktop/All/NEW_FINAL_OFFSITE/school_2024_2025/main/models"
        model_path = os.path.join(model_dir, f"xgb_{user_ID}_{lat}_{lon}_{parameter}.json")

        if not os.path.exists(model_path):
            print(f"Model file not found: {model_path}")
            continue

        model = xgb.Booster()
        model.load_model(model_path)

        # Align future data with model's feature names
        trained_features = model.feature_names
        for feature in trained_features:
            if feature not in X_future.columns:
                X_future[feature] = 0  # Add missing features as zero

        X_future = X_future[trained_features]  # Match order of features
        dfuture = xgb.DMatrix(X_future)
        predictions = model.predict(dfuture)

        # Add predictions to the DataFrame
        future_df[parameter] = predictions

        # Create a heatmap for the prediction
        grid_latitude, grid_longitude = np.meshgrid(
            np.linspace(future_df['latitude'].min(), future_df['latitude'].max(), 200),
            np.linspace(future_df['longitude'].min(), future_df['longitude'].max(), 200)
        )
        grid_values = griddata(
            (future_df['latitude'], future_df['longitude']),
            future_df[parameter],
            (grid_latitude, grid_longitude),
            method='cubic'
        )

        # Calculate the dimensions based on the golden ratio
        height = 8  # You can choose any height
        width = height * 1.618  # Golden ratio width

        # Plot the heatmap with golden ratio dimensions
        plt.figure(figsize=(width, height))

        # Use aspect="auto" to allow for non-square but proportional size
        plt.pcolormesh(grid_longitude, grid_latitude, grid_values, shading='auto', cmap='viridis')
        plt.colorbar(label=f'{parameter}')
        plt.title(f'{parameter} Prediction for {future_date.strftime("%Y-%m-%d %H:%M:%S")}')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')

        # Plot world boundaries on top of the heatmap (but restrict it to the bounding box)
        world.boundary.plot(ax=plt.gca(), color='black', linewidth=1)

        # Adjust the limits based on the bounding box
        plt.xlim(min_lon, max_lon)
        plt.ylim(min_lat, max_lat)

        # Adjust the aspect ratio to avoid white space
        plt.gca().set_aspect('auto', adjustable='box')

        # Save the plot
        output_file = os.path.join(output_dir, f'{user_ID}_{parameter}_{future_date.strftime("%Y%m%d_%H")}.png')
        plt.savefig(output_file)
        plt.close()
        heatmap_files.append(output_file)

    # Create a GIF from the heatmap files
    print("Creating GIF...")
    gif_path = os.path.join(output_dir, f'{user_ID}_{parameter}_forecast.gif')
    images = [Image.open(file) for file in heatmap_files]
    images[0].save(
        gif_path, save_all=True, append_images=images[1:], duration=200, loop=0
    )

    # Remove individual heatmap files to save space
    for file in heatmap_files:
        os.remove(file)

    print(f"GIF saved: {gif_path}")
    return gif_path

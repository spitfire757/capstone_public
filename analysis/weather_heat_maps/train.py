import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from surrounding_map_data import grab_data
import warnings
import xgboost as xgb
import joblib  # Import joblib for saving and loading models
import os
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import mean_squared_error
from multiprocessing import Pool
import pandas as pd
from glob import glob 
from datetime import datetime, timedelta


global data_loc
data_loc = '/work/bkelley/large_data/weather/hist_data'
other_loc = '/work/bkelley/large_data/weather'
random_seed = 42


def grab_evenly_spaced_us_points(n_points=100):
    # Southwest corner (min latitude, min longitude)
    min_lat = 24.396308
    min_lon = -125.0
    # Northeast corner (max latitude, max longitude)
    max_lat = 49.384358
    max_lon = -66.93457
    # Create evenly spaced latitudes and longitudes
    latitudes = np.linspace(min_lat, max_lat, int(np.sqrt(n_points)))
    longitudes = np.linspace(min_lon, max_lon, int(np.sqrt(n_points)))
    # Generate the grid of points (lat, lon)
    points = []
    for lat in latitudes:
        for lon in longitudes:
            points.append((lat, lon))
    # Convert points to GeoDataFrame
    geometry = [Point(lon, lat) for lat, lon in points]  # Point expects (x, y) = (lon, lat)
    points_gdf = gpd.GeoDataFrame(geometry=geometry, crs="EPSG:4326")  # WGS84 coordinate system
    # Load the world map (No filtering by 'NAME' for United States)
    world = gpd.read_file('/home/bkelley/capstone/weather_heat_maps/data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp')
    # Plot the map
    plt = False
    if plt == True:    
        fig, ax = plt.subplots(figsize=(10, 6))
        world.plot(ax=ax, color='lightgrey', edgecolor='black')  # Plot world boundary
        # Plot points
        points_gdf.plot(ax=ax, color='red', marker='o', markersize=50)
        # Set the axis limits to the bounding box of the United States
        ax.set_xlim(min_lon-1, max_lon+1)
        ax.set_ylim(min_lat-1, max_lat+1)
        # Set equal aspect ratio to avoid distortion
        ax.set_aspect('equal', adjustable='datalim')
        plt.title('Evenly Spaced Points Inside the United States')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.show()
    return points_gdf


def grab_data_for_training(latlon_list, user_ID):
    # Directory to save CSVs
    data_loc = '/work/bkelley/large_data/weather/data'
    # Extract lat, lon from GeoDataFrame points_gdf
    # Run the data grabbing function for each lat/lon point
    grab_data(latlon_list, user_ID)
    # Ensure the data is saved with the lat/lon as the filename
    for lat, lon in latlon_list:
        # Ensure the filename is unique and uses lat lon as filename
        lat_lon_filename = f"{data_loc}{user_ID}_{lat}_{lon}_hourly.csv"
        # Check if the CSV is generated and save the data
        if os.path.exists(lat_lon_filename):
            print(f"Data successfully saved for coordinates ({lat}, {lon}) at {lat_lon_filename}")
        else:
            print(f"Failed to save data for coordinates ({lat}, {lon})")
    return 0


# Function to list all CSV files in the data directory
def get_csv_files():
    return [os.path.join(data_loc, f) for f in os.listdir(data_loc) if f.endswith('.csv')]


# Function to train the model on a single CSV file
def train_model(csv_file):
    # Load data
    data = pd.read_csv(csv_file)
    
    # Extract feature columns (excluding target columns like 'temperature_2m', 'weather_code', 'date')
    x = data.drop(['temperature_2m', 'weather_code', 'date'], axis=1)
    
    # Get the list of all target columns (the columns to predict)
    target_columns = [col for col in x.columns if col != 'temperature_2m']  # Excluding 'temperature_2m' as an example
    
    for target in target_columns:
        # print(f"Training model for {target}...")

        y = data[[target]]  # Set the current column as the target
        
        # Convert categorical columns to 'category' type
        cats = x.select_dtypes(exclude=np.number).columns.tolist()
        for col in cats:
            x[col] = x[col].astype('category')

        # Split the data into training and testing sets (75%/25%)
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=random_seed)

        # Create DMatrix objects for XGBoost
        dtrain_reg = xgb.DMatrix(x_train, y_train, enable_categorical=True)
        dtest_reg = xgb.DMatrix(x_test, y_test, enable_categorical=True)

        # Define hyperparameters for XGBoost (GPU usage)
        params = {
            "objective": "reg:squarederror",
            "tree_method": "hist",  # Use GPU for training
            "eval_metric": "rmse",
            "device": "cuda"
        }
        n = 1_000
        evals = [(dtrain_reg, "train"), (dtest_reg, "validation")]

        # Train the model with early stopping
        model = xgb.train(
            params=params,
            dtrain=dtrain_reg,
            num_boost_round=n,
            evals=evals,
            verbose_eval=100,
            early_stopping_rounds=250
        )
        
        # print(f'Model training completed for {target}')
        
        # Save the trained model with lat/lon information from the filename
        lat_lon = "_".join(os.path.basename(csv_file).split('_')[1:3])  # Extracts latitude and longitude
        model_filename = f'{other_loc}/models/{lat_lon}_{target}_xgb_model.json'
        
        # Save the model
        model.save_model(model_filename)
        print(f'Model saved to {model_filename}.')

        # Evaluate the model performance
        preds = model.predict(dtest_reg)
        rmse = mean_squared_error(y_test, preds, squared=False)
        print(f"RMSE for model {lat_lon}_{target}: {rmse:.3f}")

        # Perform 5-fold cross-validation
        print("Performing cross validation") 
        kf = KFold(n_splits=5, shuffle=True, random_state=random_seed)
        results = []
        for train_idx, val_idx in kf.split(x_train):
            x_train_cv, x_val_cv = x_train.iloc[train_idx], x_train.iloc[val_idx]
            y_train_cv, y_val_cv = y_train.iloc[train_idx], y_train.iloc[val_idx]
            
            dtrain_cv = xgb.DMatrix(x_train_cv, y_train_cv, enable_categorical=True)
            dval_cv = xgb.DMatrix(x_val_cv, y_val_cv, enable_categorical=True)
            
            model_cv = xgb.train(params, dtrain_cv, num_boost_round=n, evals=[(dval_cv, "validation")], verbose_eval=False)
            cv_preds = model_cv.predict(dval_cv)
            cv_rmse = mean_squared_error(y_val_cv, cv_preds, squared=False)
            results.append(cv_rmse)
        
        avg_rmse = np.mean(results)
        print(f"Average RMSE from 5-fold CV for {lat_lon}_{target}: {avg_rmse:.3f}")


# Function to train models
def train_models():
    # Get list of CSV files
    csv_files = get_csv_files()

    # Train models in parallel using multiprocessing
    with Pool(processes=225) as pool:  # Use 128 processes (or more if you have more CPUs)
        pool.map(train_model, csv_files)


def predict(user_id):
    model_dir = '/work/bkelley/large_data/weather/models'
    data_dir = '/work/bkelley/large_data/weather/hist_data'
    prediction_dir = '/work/bkelley/large_data/weather/predictions'

    # Loop through each model file in the model directory
    for model_file in os.listdir(model_dir):
        if model_file.endswith('_xgb_model.json'):
            # Extract lat, lon from the model filename
            lat, lon = model_file.split('_')[:2]
            
            # Load the corresponding hourly data file
            hourly_file = os.path.join(data_dir, f"{user_id}_{lat}_{lon}_hourly.csv")
            if os.path.exists(hourly_file):
                # Read the hourly data CSV file
                hourly_data = pd.read_csv(hourly_file)

                # Check if necessary columns are present in the data
                required_columns = [
                    'temperature_2m', 'relative_humidity_2m', 'precipitation', 'rain', 'weather_code',
                    'surface_pressure', 'cloud_cover', 'wind_speed_10m', 'wind_speed_100m', 
                    'wind_direction_10m', 'wind_direction_100m'
                ]
                if not all(col in hourly_data.columns for col in required_columns):
                    print(f"Missing columns in {hourly_file}, skipping this file.")
                    continue
                
                # Select the most recent data (e.g., last 24 hours)
                input_data = hourly_data.tail(24).copy()  # Use last 24 hours

                # Remove 'temperature_2m' and 'weather_code' if they were not in the training data
                input_data = input_data.drop(columns=['temperature_2m', 'weather_code'], errors='ignore')

                # Load the model
                model_path = os.path.join(model_dir, model_file)
                
                if os.path.exists(model_path):
                    model = xgb.XGBRegressor()
                    try:
                        model.load_model(model_path)
                    except Exception as e:
                        print(f"Error loading model {model_file}: {e}")
                        continue  # Skip to the next model if loading fails
                else:
                    print(f"Model file not found: {model_path}")
                    continue  # Skip to the next model if file doesn't exist

                # Prepare input data for prediction (drop non-numeric or unnecessary columns)
                features = input_data.drop(columns=['date'], errors='ignore')  # Drop 'date' if present

                # Create a dictionary to hold predictions for each weather variable
                predicted_data_dict = {
                    'date': pd.date_range(datetime.now(), periods=24, freq='H')
                }

                # Loop through each weather feature and predict
                weather_columns = [
                    'temperature_2m', 'relative_humidity_2m', 'precipitation', 'rain', 
                    'surface_pressure', 'cloud_cover', 'wind_speed_10m', 'wind_speed_100m', 
                    'wind_direction_10m', 'wind_direction_100m'
                ]

                for col in weather_columns:
                    # Generate predictions for the current weather feature
                    predictions = model.predict(features)

                    # Add the predictions to the dictionary
                    predicted_data_dict[f'predicted_{col}'] = predictions

                # Create the final DataFrame with predictions
                predicted_data = pd.DataFrame(predicted_data_dict)

                # Save the predictions to a CSV file in the prediction directory
                output_file = os.path.join(prediction_dir, f"{user_id}_{lat}_{lon}_predictions.csv")
                predicted_data.to_csv(output_file, index=False)
                print(f"Predictions saved for {user_id} at ({lat}, {lon})")
            else:
                print(f"Data file for {lat}, {lon} not found: {hourly_file}")



if __name__ =="__main__":
    warnings.filterwarnings("ignore")
    # points_gdf = grab_evenly_spaced_us_points()
    # grab_data_for_training(points_gdf, 123)
    train_models()
    # predict(123)



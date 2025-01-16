import pandas as pd
import os

def remove_duplicates_hourly(file_path):
    # Load the hourly data
    hourly_data = pd.read_csv(file_path)
    
    # Convert the 'date' column to datetime
    hourly_data['date'] = pd.to_datetime(hourly_data['date'])
    
    # Sort by date
    hourly_data.sort_values(by='date', inplace=True)
    
    # Remove duplicates based on the 'date' column
    hourly_data = hourly_data.drop_duplicates(subset='date', keep='first')
    
    # Save the cleaned data back to CSV
    cleaned_file_path = '/home/bkelley/capstone/data_collection/weather/data/cleaned_hourly_weather_data.csv'
    hourly_data.to_csv(cleaned_file_path, index=False)
    print(f"Cleaned hourly weather data saved as '{cleaned_file_path}'")

    # Remove the old file
    os.remove(file_path)
    print(f"Old hourly weather data file '{file_path}' removed.")

def remove_duplicates_daily(file_path):
    # Load the daily data
    daily_data = pd.read_csv(file_path)
    
    # Convert the 'date' column to datetime
    daily_data['date'] = pd.to_datetime(daily_data['date'])
    
    # Sort by date
    daily_data.sort_values(by='date', inplace=True)
    
    # Remove duplicates based on the 'date' column
    daily_data = daily_data.drop_duplicates(subset='date', keep='first')
    
    # Save the cleaned data back to CSV
    cleaned_file_path = '/home/bkelley/capstone/data_collection/weather/data/cleaned_daily_weather_data.csv'
    daily_data.to_csv(cleaned_file_path, index=False)
    print(f"Cleaned daily weather data saved as '{cleaned_file_path}'")

    # Remove the old file
    os.remove(file_path)
    print(f"Old daily weather data file '{file_path}' removed.")

if __name__ == "__main__":
    remove_duplicates_hourly('/home/bkelley/capstone/data_collection/weather/data/hourly_weather_data.csv')
    remove_duplicates_daily('/home/bkelley/capstone/data_collection/weather/data/daily_weather_data.csv')


#!/bin/bash

# Define the target directory
TARGET_DIR="/home/bkelley/capstone/weather_heat_maps/data"

# Find and delete all non-directory files with a .gif extension in the specified directory
find "$TARGET_DIR" -type f -name "*.png" -exec rm -f {} +
find "$TARGET_DIR" -type f -name "*.csv" -exec rm -f {} +


echo "All .png / .csv files in $TARGET_DIR have been deleted."


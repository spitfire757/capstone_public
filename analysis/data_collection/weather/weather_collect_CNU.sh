#!/bin/bash

# Define log file path
LOG_FILE="/home/bkelley/capstone/data_collection/weather/log.txt"

# Get current date and time
CURRENT_DATE=$(date +"%Y-%m-%d %H:%M:%S")

# Run the data collector script
echo "Running data_collector_CNU.py..."
python3 data_collector_CNU.py

# Check if the first script ran successfully
if [ $? -eq 0 ]; then
    echo "data_collector_CNU.py completed successfully."

    # Run the data filter script
    echo "Running data_filter_CNU.py..."
    python3 data_filter_CNU.py

    # Check if the second script ran successfully
    if [ $? -eq 0 ]; then
        echo "data_filter_CNU.py completed successfully."

        # Get sizes of cleaned CSV files
        CLEANED_DAILY_SIZE=$(stat -c%s "/home/bkelley/capstone/data_collection/weather/data/cleaned_daily_weather_data.csv")
        CLEANED_HOURLY_SIZE=$(stat -c%s "/home/bkelley/capstone/data_collection/weather/data/cleaned_hourly_weather_data.csv")

        # Log the successful run details
        echo "$CURRENT_DATE - Script ran successfully. Daily CSV size: $CLEANED_DAILY_SIZE bytes, Hourly CSV size: $CLEANED_HOURLY_SIZE bytes" >> "$LOG_FILE"

        # Execute create_temp_avg.ipynb using nbconvert
        echo "Running create_temp_avg.ipynb..."
        jupyter nbconvert --to notebook --execute /home/bkelley/capstone/data_collection/weather/create_temp_avg.ipynb --inplace

        if [ $? -eq 0 ]; then
            echo "create_temp_avg.ipynb completed successfully."
            echo "$CURRENT_DATE - create_temp_avg.ipynb completed successfully." >> "$LOG_FILE"
        else
            echo "Error: create_temp_avg.ipynb failed."
            echo "$CURRENT_DATE - create_temp_avg.ipynb failed." >> "$LOG_FILE"
        fi
    else
        echo "Error: data_filter_CNU.py failed."
        echo "$CURRENT_DATE - data_filter_CNU.py failed." >> "$LOG_FILE"
    fi
else
    echo "Error: data_collector_CNU.py failed."
    echo "$CURRENT_DATE - data_collector_CNU.py failed." >> "$LOG_FILE"
fi

#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 4 ]; then
	  echo "Usage: $0 <user_id> <lat> <lon> <var>"
	    echo "Example: $0 1 10 10 temp"
	      exit 1
fi

# Input arguments
USER_ID="$1"
LAT="$2"
LON="$3"
VAR="$4"

# Variables
LOCAL_DIR="main/data"  
REMOTE_USER="ubuntu"
REMOTE_HOST="1.1.1.1"
REMOTE_KEY="for_server/CAPSTONE.pem"
REMOTE_DIR="/var/www/html/user_maps"
FILE_TO_TRANSFER="${USER_ID}_${VAR}_forecast.gif"
# 473036448_surface_pressure_forecast.gif
# Check if the file exists locally
if [ ! -f "$LOCAL_DIR/$FILE_TO_TRANSFER" ]; then
	  echo "File $FILE_TO_TRANSFER does not exist in $LOCAL_DIR. Exiting."
	    exit 1
fi

# Perform the SCP transfer
echo "Starting file transfer for $FILE_TO_TRANSFER to $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR..."
sudo scp -i "$REMOTE_KEY" "$LOCAL_DIR/$FILE_TO_TRANSFER" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"

# Check the result of the SCP command
if [ $? -eq 0 ]; then
	  echo "File transfer completed successfully."
  else
	    echo "File transfer failed."
	      exit 1
fi


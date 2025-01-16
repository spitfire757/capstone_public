#!/bin/bash
# check if the correct number of arguments are provided
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <user_ID> <lat> <lon> <filt>"
        exit 1
        fi

        # Assign the arguments to variables
        user_ID=$1
        lat=$2
        lon=$3
        filt=$4

        # Execute the Python script with the provided arguments
        python3 generate_user_maps.py "$user_ID" "$lat" "$lon" "$filt"

        # Run the cleanup script after the Python script completes
        ./refresh_data.sh

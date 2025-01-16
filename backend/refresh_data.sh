#!/bin/bash

TARGET_DIR="/home/bkelley/main/data"

find "$TARGET_DIR" -type f -name "*.png" -exec rm -f {} +
find "$TARGET_DIR" -type f -name "*.csv" -exec rm -f {} +

echo "All .png / .csv files in $TARGET_DIR have been deleted."


import os
import json
import pdal
import matplotlib.pyplot as plt
import geopandas as gpd
from pyproj import Transformer
import numpy as np
import rasterio


# Global variables for square size and output directory
square_size = 0.05  # size in Degrees per band
output_dir = 'main/data'


def generate_heatmap(user_ID, lat, lon, square_size, output_dir):
    """
    Generates a heatmap around the given latitude and longitude using the PDAL pipeline
    and saves a geospatial plot for the user.

    Args:
        user_ID (str): Unique identifier for the user.
        lat (float): Latitude of the center point.
        lon (float): Longitude of the center point.
        square_size (float): Size of the square in degrees (side length).
        output_dir (str): Directory to save the generated files.

    Returns:
        dict: Paths to the saved LAZ and geospatial plot files.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Calculate the bounds of the square based on the midpoint
    lat_min = lat - (square_size / 2)
    lat_max = lat + (square_size / 2)
    lon_min = lon - (square_size / 2)
    lon_max = lon + (square_size / 2)

    print("Square Bounds based on midpoint:")
    print(f"Top Left (Lat, Lon): ({lat_max}, {lon_min})")
    print(f"Bottom Right (Lat, Lon): ({lat_min}, {lon_max})")

    # Step 2: Transform the latitude/longitude bounds to EPSG:3857 (Web Mercator)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x_min, y_min = transformer.transform(lon_min, lat_min)
    x_max, y_max = transformer.transform(lon_max, lat_max)

    # Step 3: Define the PDAL pipeline JSON with the transformed bounds
    laz_file = os.path.join(output_dir, f"{user_ID}_{lat}_{lat}.laz")
    pipeline_json = {
        "pipeline": [
            {
                "type": "readers.ept",
                "filename": "http://usgs-lidar-public.s3.amazonaws.com/USGS_LPC_VA_Sandy_2014_LAS_2015/ept.json",
                "bounds": f"([{x_min}, {x_max}], [{y_min}, {y_max}])"
            },
            {
                "type": "writers.las",
                "filename": laz_file
            }
        ]
    }

    # Step 4: Run the PDAL pipeline
    pipeline = json.dumps(pipeline_json)
    p = pdal.Pipeline(pipeline)
    p.execute()

    print(f"LAZ file created: {laz_file}")

    # Step 5: Load the LAS/LAZ data and extract information for plotting
    # We'll load the generated LAZ file and extract the elevation values
    with rasterio.open(laz_file) as src:
        # Read the point cloud data (we're only interested in the elevation for the heatmap)
        point_cloud_data = src.read(1)  # Read the first band (usually elevation data)
        transform = src.transform

    # Convert the point cloud data into a 2D grid (to create a heatmap)
    grid_data = point_cloud_data.reshape((int(np.sqrt(len(point_cloud_data))), -1))

    # Step 6: Generate the heatmap plot
    plt.figure(figsize=(12, 8))
    plt.imshow(grid_data, cmap='terrain', extent=(lon_min, lon_max, lat_min, lat_max))
    plt.colorbar(label='Elevation (meters)')
    plt.title(f'Heatmap for User {user_ID}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Step 7: Save the heatmap plot
    geospatial_plot_file = os.path.join(output_dir, f"{user_ID}_geospatial_plot.png")
    plt.savefig(geospatial_plot_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Geospatial heatmap saved: {geospatial_plot_file}")

    return {"laz_file": laz_file, "geospatial_plot_file": geospatial_plot_file}


if __name__ == "__main__":
   # Test data: Define user ID and latitude/longitude for a point of interest
   user_ID = "test_user_01"
   lat = 37.53400769401545  # Example latitude (Browns Island)
   lon = -77.44275569915773  # Example longitude (Browns Island)
   
   # Call the generate_heatmap function
   result = generate_heatmap(user_ID, lat, lon, square_size, output_dir)
   
   # Print out the paths to the generated files
   print("Generated Files:")
   print(f"LAZ File: {result['laz_file']}")
   print(f"Geospatial Plot: {result['geospatial_plot_file']}")


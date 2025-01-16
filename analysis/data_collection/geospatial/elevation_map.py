#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import laspy
import lazrs  # Ensure lazrs is installed and imported correctly
import plotly.express as px
import plotly.io as pio
import matplotlib.pyplot as plt

# Set the file paths
global PATH, LOC, HEATMAP_PATH, SCATTER_PNG_PATH, SCATTER_HTML_PATH
PATH = '/home/bkelley/capstone/data_collection/geospatial/USGS-3DEP/EPT/U_USGS-3DEP_PC_20241002.1732_1.laz'
LOC = '/work/bkelley/large_data/geospatial'
HEATMAP_PATH = f'{LOC}/plots/test_heatmap.png'
SCATTER_HTML_PATH = f'{LOC}/plots/test_scatter3d.html'
SCATTER_PNG_PATH = f'{LOC}/plots/test_scatter3d.png'

# Create the directory if it doesn't exist
os.makedirs(os.path.dirname(HEATMAP_PATH), exist_ok=True)

def plot_laz():
    # Read the .laz file
    laz_file = PATH
    las = laspy.read(laz_file)  # Do not need to pass the backend explicitly

    # Extract the X, Y, Z coordinates
    x = las.X * las.header.scale[0] + las.header.offset[0]
    y = las.Y * las.header.scale[1] + las.header.offset[1]
    z = las.Z * las.header.scale[2] + las.header.offset[2]

    # Downsample for the scatter plot only
    scatter_downsample_factor = 84  # Adjust the downsampling factor as needed
    x_scatter = x[::scatter_downsample_factor]
    y_scatter = y[::scatter_downsample_factor]
    z_scatter = z[::scatter_downsample_factor]

    # Create 2D histogram for the heatmap (no downsampling)
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=100)  # Adjust bins for resolution

    # Create a figure for the heatmap
    fig, ax = plt.subplots(figsize=(10, 7))

    # Create the heatmap using imshow
    im = ax.imshow(heatmap.T, origin='lower', cmap='viridis', 
                   extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], 
                   aspect='auto')

    # Set plot labels and title
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    plt.title("LiDAR Point Cloud Heatmap")
    plt.colorbar(im, ax=ax, label='Count')

    # Save the heatmap to a file
    plt.savefig(HEATMAP_PATH)
    plt.close()  # Close the figure to free memory

    # Create a 3D scatter plot using Plotly
    scatter_fig = px.scatter_3d(
        x=x_scatter,
        y=y_scatter,
        z=z_scatter,
        color=z_scatter,  # Optional: color by Z values
        labels={'x': 'Longitude (degrees)', 'y': 'Latitude (degrees)', 'z': 'Elevation (meters)'},
        title='LiDAR Point Cloud 3D Scatter Plot',
        size_max=2,  # Set maximum size for points
        opacity=0.9  # Set the opacity for better visibility
    )

    # Update the layout for better visualization
    scatter_fig.update_traces(marker=dict(size=1))  # Adjust dot size here
    scatter_fig.update_layout(
        scene=dict(
            xaxis_title='Longitude (degrees)',
            yaxis_title='Latitude (degrees)',
            zaxis_title='Elevation (meters)',
            camera=dict(
                eye=dict(x=-0.5, y=-1.5, z=1.5)  # Adjust camera angle for better view
            )
        ),
        width=1000,  # Set width of the plot
        height=800,  # Set height of the plot
    )

    # Save the interactive scatter plot as an HTML file
    pio.write_html(scatter_fig, SCATTER_HTML_PATH)

    # Save the scatter plot as a PNG file
    pio.write_image(scatter_fig, SCATTER_PNG_PATH)  # Save as PNG

if __name__ == "__main__":
    plot_laz()

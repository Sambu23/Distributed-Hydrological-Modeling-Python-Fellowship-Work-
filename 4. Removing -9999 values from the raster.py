# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 15:49:56 2024

@author: Dell
"""

import rasterio
import numpy as np
import os
import glob

# Directory paths
input_raster_dir = r"D:\Nepal\Narayani DEM\input values\2004_2014\Eawag Research\Distributed model\Using python\4. Simulated runoff xy defined"
output_raster_dir = r"D:\Nepal\Narayani DEM\input values\2004_2014\Eawag Research\Distributed model\Using python\5. Clipped simulated runoff"

# Function to check file accessibility
def check_file_accessibility(file_path, check_write=False):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Read permission denied for the file {file_path}.")
    if check_write and not os.access(os.path.dirname(file_path), os.W_OK):
        raise PermissionError(f"Write permission denied for the directory {os.path.dirname(file_path)}.")

# Check input and output directories
check_file_accessibility(input_raster_dir)
check_file_accessibility(output_raster_dir, check_write=True)

# Get all raster files in the input directory
input_raster_files = glob.glob(os.path.join(input_raster_dir, '*.tif'))

# Process each raster file
for input_raster_path in input_raster_files:
    with rasterio.open(input_raster_path) as src:
        # Read the input raster data
        input_image = src.read(1)
        
        # Replace nodata values (-9999) with np.nan
        input_image[input_image == -9999] = np.nan
        
        # Update metadata to reflect changes
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": src.height,
            "width": src.width,
            "transform": src.transform,
            "crs": src.crs,
            "nodata": np.nan
        })

        # Define output path
        output_raster_path = os.path.join(output_raster_dir, os.path.basename(input_raster_path))

        # Write the cleaned raster to disk
        with rasterio.open(output_raster_path, "w", **out_meta) as dest:
            dest.write(input_image, 1)

print("Processing complete.")

import os
import netCDF4 as nc
import numpy as np
import rasterio
import geopandas as gpd
from rasterio.mask import mask

# Define the input folder containing the NetCDF files and the shapefile location
input_folder = r"Your input folder containig NetCDF"

# Shapefile location
shapefile_path = r"path\Your desired shapefile to extract from NetCDF.shp"

# Define the output folder and create it if it doesn’t exist
output_folder = os.path.join(input_folder, "Outputs")
os.makedirs(output_folder, exist_ok=True)

# Load the shapefile using Geopandas
shapefile = gpd.read_file(shapefile_path)

# Loop through all NetCDF files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".nc"):
        netcdf_file = os.path.join(input_folder, filename)

        # Define temporary and output file paths for each NetCDF file
        temp_raster_file = os.path.join(output_folder, f'temp_{filename}.tif')
        output_file = os.path.join(output_folder, f'{os.path.splitext(filename)[0]}_clipped.tif')

        # Open the NetCDF file
        dataset = nc.Dataset(netcdf_file)

        # Extract the latitude, longitude, and the variable (e.g., soil moisture 'sm')
        latitudes = dataset.variables['lat'][:]
        longitudes = dataset.variables['lon'][:]
        soil_moisture = dataset.variables['sm'][:]  # Modify 'sm' to the correct variable

        # Get the first time step of soil moisture data
        sm_data = soil_moisture[0, :, :]  # Modify if you need other time steps

        # Open the rasterio dataset and save to temporary file
        transform = rasterio.transform.from_bounds(longitudes.min(), latitudes.min(), longitudes.max(), latitudes.max(), sm_data.shape[1], sm_data.shape[0])
        crs = 'EPSG:4326'  # Assuming lat/lon in WGS84, adjust if needed

        # Write the soil moisture data to a temporary GeoTIFF file
        with rasterio.open(
            temp_raster_file, 'w', driver='GTiff', height=sm_data.shape[0], width=sm_data.shape[1],
            count=1, dtype=sm_data.dtype, crs=crs, transform=transform
        ) as temp_dst:
            temp_dst.write(sm_data, 1)

        # Re-open the saved GeoTIFF file for masking
        with rasterio.open(temp_raster_file) as src:
            # Clip the raster using the shapefile
            clipped_image, clipped_transform = mask(src, shapes=shapefile.geometry, crop=True)

            # Save the clipped raster to a new GeoTIFF file
            with rasterio.open(
                output_file, 'w', driver='GTiff', height=clipped_image.shape[1], width=clipped_image.shape[2],
                count=1, dtype=clipped_image.dtype, crs=src.crs, transform=clipped_transform
            ) as dst:
                dst.write(clipped_image[0], 1)  # Saving the clipped soil moisture data

        # Close the NetCDF file
        dataset.close()

        # Delete the temporary raster file (optional)
        os.remove(temp_raster_file)

        print(f"Processed and saved clipped raster for: {filename}")

print(f"All NetCDF files in {input_folder} have been processed and saved in {output_folder}.")

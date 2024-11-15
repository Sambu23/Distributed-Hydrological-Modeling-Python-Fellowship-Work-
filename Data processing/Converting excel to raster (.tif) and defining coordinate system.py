import pandas as pd
import numpy as np
import os
import rasterio
from rasterio.transform import from_origin

# Load the Excel file
file_path = "Your folder path/Simulated_Runoff.xlsx"
df = pd.read_excel(file_path, index_col=0)

# Set grid dimensions
ncols = 32
nrows = 25
numtotal = nrows * ncols

# Intermediate output directory
intermediate_output_dir = "Your intemediate output folder/3. Simulated runoff"
os.makedirs(intermediate_output_dir, exist_ok=True)

# Final output directory
final_output_dir = "Your output folder/4. Simulated runoff xy defined"
os.makedirs(final_output_dir, exist_ok=True)

# Pixel size
pixel_size = 9286.694243

# Function to convert each row in the DataFrame to a raster
def create_raster_from_row(row, output_path, nrows=nrows, ncols=ncols):
    # Reshape the data to match the grid
    data = row.values.reshape((nrows, ncols))

    # Replace very low values and -inf with np.nan (no data)S
    data[data < -1e10] = np.nan
    data[data == -np.inf] = np.nan

    # Replace np.nan with a specific no-data value, e.g., -9999
    no_data_value = -9999
    data = np.nan_to_num(data, nan=no_data_value)

    # Define transform based on the pixel size and origin (you may need to adjust the origin)
    transform = from_origin(0, 0, pixel_size, pixel_size)  # Placeholder origin values

    # Define CRS for WGS 1984 UTM Zone 44N
    crs = 'EPSG:32644'

    # Check if the file already exists and delete it if necessary
    if os.path.exists(output_path):
        os.remove(output_path)

    # Create a new raster file
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=nrows,
        width=ncols,
        count=1,
        dtype='float32',
        crs=crs,
        transform=transform,
        nodata=no_data_value
    ) as dst:
        dst.write(data, 1)

# Iterate over each row (time step) in the DataFrame and create an intermediate raster
for idx, row in df.iterrows():
    # Replace colons and spaces in the date format
    safe_date = str(idx).replace(":", "-").replace(" ", "_")
    output_path = os.path.join(intermediate_output_dir, f"Svec_WR_{safe_date}.tif")
    create_raster_from_row(row, output_path)

print("Intermediate rasters created successfully.")

# Read reference raster
reference_raster_path = "Your folder path of raster/Your_tiff_file.tif"
with rasterio.open(reference_raster_path) as ref_raster:
    ref_transform = ref_raster.transform
    ref_crs = ref_raster.crs
    ref_shape = ref_raster.shape

# Function to update the coordinates of rasters
def update_raster_coordinates(input_path, output_path, ref_transform, ref_crs, ref_shape):
    with rasterio.open(input_path) as src:
        data = src.read(1)

    # Ensure the input raster has the same shape as the reference raster
    if data.shape != ref_shape:
        raise ValueError(f"Shape mismatch: {input_path} shape {data.shape} != reference shape {ref_shape}")

    # Check if the file already exists and delete it if necessary
    if os.path.exists(output_path):
        os.remove(output_path)

    # Write the data with the new transform and CRS
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=ref_shape[0],
        width=ref_shape[1],
        count=1,
        dtype=data.dtype,
        crs=ref_crs,
        transform=ref_transform,
    ) as dst:
        dst.write(data, 1)

# Process each intermediate raster and update its coordinates
for filename in os.listdir(intermediate_output_dir):
    if filename.endswith(".tif"):
        input_path = os.path.join(intermediate_output_dir, filename)
        output_path = os.path.join(final_output_dir, filename)
        update_raster_coordinates(input_path, output_path, ref_transform, ref_crs, ref_shape)

print("Final rasters with updated coordinates created successfully.")

import pandas as pd
import numpy as np
import time
import tqdm
from pathlib import Path

# Import your model function
from modFunctions import model_01

# Function to calculate Nash-Sutcliffe efficiency coefficient
def NSfun(Qobs, Qsim):
    mx = np.isfinite(Qobs)
    NSnum = sum((Qobs[mx] - Qsim[mx])**2)
    NSden = sum((Qobs[mx] - Qobs[mx].mean())**2)
    NS = 1 - NSnum / NSden
    return NS

# Load the Excel files
path_lst = "./Data/1.LST value of raster by python 2004_2013.xlsx"
path_pet = "./Data/1.PET value of raster by python 2004_2013.xlsx"
path_precip = "./Data/1.Precipitation value of raster from 2004 to 2013.xlsx"

lst_df = pd.read_excel(path_lst, index_col=0)
pet_df = pd.read_excel(path_pet, index_col=0)
precip_df = pd.read_excel(path_precip, index_col=0)

# Convert DataFrames to nullable Float64 type
lst_df = lst_df.astype('Float64')
pet_df = pet_df.astype('Float64')
precip_df = precip_df.astype('Float64')

# Define filtering criteria
lst_min = -50  # Minimum threshold for LST
lst_max = 50   # Maximum threshold for LST
pet_precip_min = 0  # Minimum threshold for PET and Precipitation
pet_precip_max = 2000  # Maximum threshold for PET and Precipitation

# Apply filtering criteria to replace out-of-bounds values with pd.NA
lst_df = lst_df.applymap(lambda x: x if lst_min <= x <= lst_max else pd.NA)
pet_df = pet_df.applymap(lambda x: x if pet_precip_min <= x <= pet_precip_max else pd.NA)
precip_df = precip_df.applymap(lambda x: x if pet_precip_min <= x <= pet_precip_max else pd.NA)


# Verify if the input data have the same shape
print("LST data shape:", lst_df.shape)
print("PET data shape:", pet_df.shape)
print("Precipitation data shape:", precip_df.shape)

# Define model parameters
cE = 0.3#0.3  # Evaporation multiplication factor
Kmlt_WR = 0.3#0.05#0.003  # Degree day factor
Smax_UR = 1000  # Capacity root zone (mm) #without parameter adjustment
K_UR = 0.3 # Root zone parameter (mm/d)
theta = [Kmlt_WR, Smax_UR, K_UR]
delT = 1  # Time step (days)
SiniFrac_UR = 0.3  # Initial condition root zone as fraction of Smax
Sini_WR = 0.0
Sini_UR = SiniFrac_UR
Sini = [Sini_WR, Sini_UR]

# Initialize arrays to store results
num_rows, num_cols = lst_df.shape
simulated_runoff = np.full((num_rows, num_cols), np.nan, dtype=np.float32)
Svec_WR = np.full((num_rows, num_cols), np.nan, dtype=np.float32)
Svec_UR = np.full((num_rows, num_cols), np.nan, dtype=np.float32)


# Run model for each pixel
start_time = time.time()
for col in tqdm.tqdm(lst_df.columns):
    P = precip_df[col].values
    Epot = pet_df[col].values * cE
    Tc = lst_df[col].values
    
    # Run the hydrological model only if the column doesn't contain any NA values
    if not pd.isna(P).any() and not pd.isna(Epot).any() and not pd.isna(Tc).any():
        Qsim, Eact, Svec_WR_col, Svec_UR_col = model_01(Sini, P, Epot, Tc, theta, delT)
    
        # Check if the output length matches the expected length
        if len(Qsim) == num_rows:
            simulated_runoff[:, lst_df.columns.get_loc(col)] = Qsim
            Svec_WR[:, lst_df.columns.get_loc(col)] = Svec_WR_col
            Svec_UR[:, lst_df.columns.get_loc(col)] = Svec_UR_col
        else:
            print(f"Column {col} has a mismatch in dimensions. Expected {num_rows}, but got {len(Qsim)}")
    else:
        print(f"Skipping column {col} due to invalid data.")

print("Time taken to run the model for all pixels:", time.time() - start_time)

# Create DataFrames for the results
simulated_runoff_df = pd.DataFrame(simulated_runoff, index=lst_df.index, columns=lst_df.columns)
Svec_WR_df = pd.DataFrame(Svec_WR, index=lst_df.index, columns=lst_df.columns)
Svec_UR_df = pd.DataFrame(Svec_UR, index=lst_df.index, columns=lst_df.columns)

# Save the results to Excel files with NaN correctly represented
Path("./Output/").mkdir(parents=True, exist_ok=True)
output_path_runoff = "./Output/Simulated_Runoff.xlsx"
output_path_Svec_WR = "./Output/Svec_WR.xlsx"
output_path_Svec_UR = "./Output/Svec_UR.xlsx"

simulated_runoff_df.to_excel(output_path_runoff, na_rep=np.nan)
Svec_WR_df.to_excel(output_path_Svec_WR, na_rep=np.nan)
Svec_UR_df.to_excel(output_path_Svec_UR, na_rep=np.nan)

print(f"Results saved to {output_path_runoff}, {output_path_Svec_WR}, and {output_path_Svec_UR}")

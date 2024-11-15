import pandas as pd

# Load the Excel file from Sheet2
input_file_path = r"path\1. example excel file.xlsx" #your discharge data file (daily)
df = pd.read_excel(input_file_path, sheet_name='404', parse_dates=['Date'])

# Add a 'Month' column to group by month later
df['Month'] = df['Date'].dt.to_period('M')

# Calculate the monthly sum of daily volumes (m³)
monthly_volume = df.groupby('Month')['Volume of P404'].sum()

# Convert monthly volume to m³/s
# There are 86400 seconds in a day
monthly_discharge_m3s = monthly_volume / (monthly_volume.index.to_timestamp().days_in_month * 86400)

# Convert m³/s to mm
catchment_area_km2 = 5638
catchment_area_m2 = catchment_area_km2 * 1e6
monthly_discharge_mm = (monthly_discharge_m3s * 1e3 * monthly_volume.index.to_timestamp().days_in_month) / catchment_area_m2

# Prepare the results in a DataFrame
result_df = pd.DataFrame({
    'Month': monthly_volume.index.astype(str),
    'Monthly Volume (m³)': monthly_volume.values,
    'Monthly Discharge (m³/s)': monthly_discharge_m3s.values,
    'Monthly Discharge (mm)': monthly_discharge_mm.values
})

# Export the results to a new Excel file
output_file_path = r"path\Output_excelfile.xlsx"
result_df.to_excel(output_file_path, index=False)

print(f"Results saved to {output_file_path}")

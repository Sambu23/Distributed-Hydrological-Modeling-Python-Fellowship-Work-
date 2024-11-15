import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Load the Excel file containing simulated runoff data
file_path = "./Your Output folder of 2nd step/Simulated_Runoff.xlsx"
df = pd.read_excel(file_path)

# Columns corresponding to the pixel data (up to the 801st column, which is named '799')
pixel_columns = df.columns[1:801]  # Adjusted to sum up to column '799', excluding the date column
numeric_pixel_columns = df[pixel_columns].select_dtypes(include=['number']).columns

# Sum of individual row (sum of each date), ignoring negative values and values above the threshold
df['Simulated_Sum_mm'] = df[numeric_pixel_columns].apply(
    lambda row: row[(row > 0)].sum(), axis=1
)

# Convert from mm to meters
df['Simulated_Sum_m'] = df['Simulated_Sum_mm'] / 1000

# Multiply by the area of the pixel in square meters to get the volume
pixel_area = 86242689.1643136
df['Simulated_Volume_m3'] = df['Simulated_Sum_m'] * pixel_area

total_area = 3.6598e+10  # Replace this with your actual area in sq. m
df['Simulated_Streamflow_mm'] = df['Simulated_Volume_m3'] / total_area * 1000  # Convert to mm

# Load the observed volume data from the Excel file
observed_file_path = "./Your Data Folder/2. Volume_m3_observed_flow.xlsx" #this excel is an external data
observed_df = pd.read_excel(observed_file_path)

# Ensure 'Date' is properly formatted in both dataframes
df['Date'] = pd.to_datetime(df['Date'])
observed_df['Date'] = pd.to_datetime(observed_df['Date'])

# Merge the simulated data with the observed volume data
df_merged = pd.merge(df, observed_df, on='Date', how='left')

# Calculate the Nash-Sutcliffe Efficiency coefficient
def NSfun(Qobs, Qsim):
    mx = np.isfinite(Qobs)
    NSnum = sum((Qobs[mx] - Qsim[mx])**2)
    NSden = sum((Qobs[mx] - Qobs[mx].mean())**2)
    NS = 1 - NSnum / NSden
    return NS

# Calculate NSE for the observed and simulated data
nse_value = NSfun(df_merged['Observed (mm/month)'].values, df_merged['Simulated_Streamflow_mm'].values)

# Calculate R-squared
def calculate_r_squared(Qobs, Qsim):
    correlation_matrix = np.corrcoef(Qobs, Qsim)
    correlation_xy = correlation_matrix[0, 1]
    r_squared = correlation_xy**2
    return r_squared

# Calculate R-squared for the observed and simulated data
r_squared_value = calculate_r_squared(df_merged['Observed (mm/month)'].values, df_merged['Simulated_Streamflow_mm'].values)

def calculate_correlation(Qobs, Qsim):
    correlation_matrix = np.corrcoef(Qobs, Qsim)
    correlation_xy = correlation_matrix[0, 1]
    return correlation_xy

# Calculate the correlation for observed and simulated data
correlation_value = calculate_correlation(df_merged['Observed (mm/month)'].values, df_merged['Simulated_Streamflow_mm'].values)


# Plotting the graph
plt.figure(figsize=(12, 6))
plt.plot(df_merged['Date'], df_merged['Observed (mm/month)'], color='blue', label='Observed')
plt.plot(df_merged['Date'], df_merged['Simulated_Streamflow_mm'], color='red', label='Simulated')


# Formatting the x-axis to show dates at appropriate intervals
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_minor_locator(mdates.MonthLocator(bymonth=(1, 7)))  # Show January and July for better clarity
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# Adding labels and title
plt.xlabel('')
plt.ylabel('Streamflow (mm/month)')
plt.title('Observed vs Simulated Runoff')

# Display the NSE and R-squared values on the plot
plt.text(0.27, 0.95, f'NS={nse_value:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
plt.text(0.27, 0.90, f'R²={r_squared_value:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
plt.text(0.27, 0.85, f'Corr={correlation_value:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')

# Ensure the legend is displayed
plt.legend()

# Rotating the date labels for better readability
plt.gcf().autofmt_xdate()

# Display the plot
plt.grid(False)
plt.show()

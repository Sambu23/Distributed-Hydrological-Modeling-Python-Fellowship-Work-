Hydrological Modeling Repository

Overview:
This repository contains Python codes developed during my research fellowship for distributed hydrological modeling. The codes handle various aspects of hydrological data processing, simulation, and analysis, with a specific focus on rainfall-runoff processes, snow and soil reservoir modeling, and raster-based analysis.

Repository Structure

Main Codes:

These Python scripts perform the core functions of distributed hydrological modeling:

- Hydrological_Model_with_Snow_and_Soil_Reservoirs.py:
      -Implements a hydrological model with explicit formulations for snow and soil reservoirs.
      -Outputs include:
        Simulated runoff
        Snow reservoir storage (Svec_WR)
        Unsaturated zone storage (Svec_UR)
        Actual evapotranspiration (EactVec)

- Combine_PET_Precip_LST_and_Runoff_Modeling.py:
      - Combines input Excel files for Potential Evapotranspiration (PET), Precipitation (P), and Land Surface Temperature (LST).
      - Runs a hydrological modeling function to generate outputs like simulated runoff and rasterized pixel-wise data.
  
- Sum_Raster_Pixels_to_Volume_and_Plot_Observed_Runoff.py:
      - Aggregates raster pixel data to calculate total runoff volume.
      - Plots modeled versus observed runoff for validation.

Outputs:
Review the generated outputs (e.g., raster files, Excel files, and plots) in the designated output directories.

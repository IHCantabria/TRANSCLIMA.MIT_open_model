import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
import random
import xarray as xr
import re
import os
import sys
# Get the parent folder of the current script
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
import namelist
from postprocessing import utils


# Initialize iteration and parameters for the simulation
src_directory = namelist.src_directory
N = 1  # number of iterations (can be implemented for different runs to have standard deviation)
nyear = 2000  # The number of years to simulate or consider
number_of_simulations = 1 # Number of TCrisks files  


nIB = namelist.end_year - namelist.start_year + 1  # This calculates the number of years from 1980 to 2021

folder_name =src_directory+ '/postprocessing/List_of_Cities.xlsx'  # Define the folder name 

# Load city data
df = pd.read_excel(folder_name, header=0, keep_default_na=False)
latitudes = df['LATITUDE']
longitudes = df['LONGITUDE']
basins = df['BASIN']
names = df['NAME']
capitals = df['CITY']

radius = 111  # search radius in km
#Please check the definition of wind speed! If it's 1-minute sustained wind, use the following: 
wind_items=[20, 25, 30, 33, 35, 40, 42, 45, 50, 55, 58, 60, 65, 70, 75, 80, 85]

#In STORM, the wind speeds are 10-min average, so the Saffir-Simpson category thresholds need to be converted from 1-min to 10-min: 
#wind_items =[20, 25, 29, 30, 35, 37.6, 40, 43.4, 45, 50, 51.1, 55, 60, 61.6, 65, 70, 75]

pathOut=namelist.base_directory + '/'+namelist.exp_name+'/'
basin=namelist.basin_name

IB_Storms_Per_Year0_NA = namelist.mu_tc_per_year 

name_file_tracks='tracks_'+basin+'_'+namelist.exp_prefix+'_'+str(namelist.start_year)+'01_'+str(namelist.end_year)+str(namelist.end_month)+'e'

period=str(namelist.start_year)+'01_'+str(namelist.end_year)+str(namelist.end_month)
results_by_city = {}  # dictionary to hold per-city DataFrames

pathTCrisks0=r'C:\Users\oderizi\Documents\GitHub\IH-MIT_open_model\tropical_cyclone_risk-main\data\era5\test/'


for iteration in range(N):
    print(f"--- Iteration {iteration} ---")
    wind_dict = {i: [] for i in range(len(latitudes))}

    print(basin)
    data, Estimated_Years_TCrisks = utils.random_dataframes_TCrisks(name_file_tracks,
        pathTCrisks0, IB_Storms_Per_Year0_NA, nyear, basin, number_of_simulations
    )
    # Extract needed columns: time, lat, lon, wind
    time, lat, lon, wind = (
        data[data.columns[5]],
        data[data.columns[3]],
        data[data.columns[2]],
        data[data.columns[4]],
    )

    del data

    indices = [i for i, x in enumerate(time) if x == 0]
    indices.append(len(time))
    i = 0

    # Loop over all tropical cyclones
    while i < len(indices) - 1:
        start = indices[i]
        end = indices[i + 1]

        latslice = lat[start:end].values
        lonslice = lon[start:end].values
        windslice = wind[start:end].values

        for l in range(len(latitudes)):  # For every city
            if basins[l] == basin:
                lat_loc = latitudes[l]
                lon_loc = longitudes[l]
                wind_loc = []
                if lon_loc < 0.0:
                    lon_loc += 360

                for j in range(len(latslice)):
                    # Calculate distance between TC track point and city
                    distance = utils.haversine(lonslice[j], latslice[j], lon_loc, lat_loc)
                    if distance <= radius:
                        wind_loc.append(windslice[j])

                if len(wind_loc) > 0 and np.max(wind_loc) >= 17.0:
                    wind_dict[l].append(np.max(wind_loc))  # Store max wind for the TC
        i += 1

# After processing all storms, compute return periods for each city
for i in range(len(wind_dict)):
    city = capitals[i]
    if len(wind_dict[i]) == 0:
        continue

    df_temp = pd.DataFrame({'Wind': wind_dict[i]})
    df_temp['Ranked'] = df_temp['Wind'].rank(ascending=0)
    df_temp = df_temp.sort_values(by=['Ranked'])
    ranklist = df_temp['Ranked'].tolist()
    windlist = df_temp['Wind'].tolist()

    rpwindlist = []
    for m in range(len(ranklist)):
        weibull = ranklist[m] / (len(ranklist) + 1.0)  # Weibull plotting position formula
        r = weibull * (len(ranklist) / nyear)  # Exceedance rate per year
        rpwindlist.append(1.0 / r)  # Return period in years

    rpwindlist = rpwindlist[::-1]
    windlist = windlist[::-1]

    RP_values = []
    for w in wind_items:
        rp_int = np.interp(w, windlist, rpwindlist)
        RP_values.append(rp_int)

    # Store results in global dictionary, create DataFrame if new city
    if city not in results_by_city:
        df_init = pd.DataFrame({'Wind_speed': wind_items})
        results_by_city[city] = df_init

    results_by_city[city][f'RP_{iteration}'] = RP_values



# After processing all storms, compute return periods for each city
for i in range(len(wind_dict)):
    city = capitals[i]
    if len(wind_dict[i]) == 0:
        continue

    df_temp = pd.DataFrame({'Wind': wind_dict[i]})
    df_temp['Ranked'] = df_temp['Wind'].rank(ascending=0)
    df_temp = df_temp.sort_values(by=['Ranked'])
    ranklist = df_temp['Ranked'].tolist()
    windlist = df_temp['Wind'].tolist()

    rpwindlist = []
    for m in range(len(ranklist)):
        weibull = ranklist[m] / (len(ranklist) + 1.0)  # Weibull plotting position formula
        r = weibull * (len(ranklist) / nyear)  # Exceedance rate per year
        rpwindlist.append(1.0 / r)  # Return period in years

    rpwindlist = rpwindlist[::-1]
    windlist = windlist[::-1]

    RP_values = []
    for w in wind_items:
        rp_int = np.interp(w, windlist, rpwindlist)
        RP_values.append(rp_int)

    # Store results in global dictionary, create DataFrame if new city
    if city not in results_by_city:
        df_init = pd.DataFrame({'Wind_speed': wind_items})
        results_by_city[city] = df_init

    results_by_city[city][f'RP_{iteration}'] = RP_values


pathOut=pathTCrisks0+'return_period/'
os.makedirs(pathOut, exist_ok=True)

# Save results: one CSV per city with columns: Wind_speed, RP_0, RP_1, ..., RP_{N-1}
for city, df_result in results_by_city.items():
    safe_city = re.sub(r'\W+', '_', city)
    df_result.to_csv(pathOut+ city + '_' + period + '.csv', index=False)



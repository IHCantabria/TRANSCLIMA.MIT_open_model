
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
import matplotlib.pyplot as plt
import random
import xarray as xr
import re

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)

    Parameters
    ----------
    lon1,lat1 : coordinates location 1
    lon2,lat2 : coordinates location 2

    Returns
    -------
    distance in km.

    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def import_storm_data(basin, pathSTORM):
    """
    Import and process storm data from multiple files.

    Parameters
    ----------
    basin : str
        The basin ID (e.g., 'ATL' for Atlantic).
    pathSTORM : str
        The path to the directory containing the storm data files.

    Returns
    -------
    list
        A list of pandas DataFrames, each containing storm data from a file.
    """

    # Define an empty list to store dataframes
    dataframes = []

    # Loop through the 2 data files (from 0 to 1)
    for i in range(2):
        # Construct the file path dynamically
        file_path = f'{pathSTORM}STORM_DATA_IBTRACS_{str(basin)}_1000_YEARS_{i}.txt'
        
        # Read the data file
        data = np.loadtxt(file_path, delimiter=',')
        
        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Unique identifier for each storm
        df[2] = df[2].astype(int)
        df[2] = df[2].apply(lambda x: f"{i}_{x}")
        
        # Apply the incrementing logic
        incrementing_array = np.cumsum(np.r_[0, np.diff(df[0]) != 0])
        df[0] = incrementing_array

        df = df.rename(columns={0: 'season', 1: 'month', 2: 'sid',3: 'iso_time', 4: 'Basin_ID', 5: 'Latitude',
                        6: 'Longitude', 7: 'wmo_pres', 8: 'wmo_wind', 9: 'Radius', 10: 'usa_sshs', 11: 'landfall', 12: 'Dist2land'})  
        
        # Append the dataframe to the list
        dataframes.append(df)

    return dataframes




def import_TCrisks_data(file_path,basin, pathTCrisks, number_of_simulations):
    """
    Import and process TCrisks data from a NetCDF file (only specific variables) and put them in the same format as STORM output data.


    Parameters
    ----------
    basin : str
        The basin ID (e.g., 'NA' for Northern Atlantic).
    pathTCrisks : str
        The path to the directory containing the TCrisks data files.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing selected TCrisks data from the file.
    """
    
    dataframes = []

    for sim_index in range (number_of_simulations):

        # Construct the file path dynamically
        file_name = file_path + f"{sim_index:1d}.nc"

        # Open the NetCDF file and load only the required variables
        ds = xr.open_dataset(pathTCrisks+file_name, use_cftime=True)

        # Extract relevant variables
        tc_years = ds['tc_years'].values
        lon_trks = ds['lon_trks'].values
        lat_trks = ds['lat_trks'].values
        vmax_trks = ds['vmax_trks'].values
        time_trks=ds['time'].values
        tc_month = ds['tc_month'].values

        # Flatten and build the output table
        extracted_data = {
            'tc_years': [],
            'sid': [],
            'lon': [],
            'lat': [],
            'vmax': [],
            'time': [],
            'month': []
        }

        for i in range(len(tc_years)):
            for j in range(len(lon_trks[i])):
                if np.isnan(lon_trks[i][j]) and np.all(np.isnan(lon_trks[i][j:])):
                    break 

                extracted_data['tc_years'].append(tc_years[i])
                extracted_data['sid'].append(f"{sim_index}_{i}")
                extracted_data['lon'].append(lon_trks[i][j])
                extracted_data['lat'].append(lat_trks[i][j])
                extracted_data['vmax'].append(vmax_trks[i][j]*0.88) # convert to 10-min sustained wind to compare with STORM
                extracted_data['time'].append(time_trks[j])
                extracted_data['month'].append(tc_month[i])
        # Convert to DataFrame
        df = pd.DataFrame(extracted_data)

        # Append the dataframe to the list
        dataframes.append(df)

    return dataframes



def random_dataframes_STORM(pathSTORM0,IB_Storms_Per_Year0,nSTORM,basin,number_of_simulation):
    """
    Select random storm data from multiple files and calculate the estimated number of years for storms.

    Parameters
    ----------
    pathSTORM0 : str
        The path to the directory containing the storm data files.
    IB_Storms_Per_Year0 : float
        The average number of storms per year.
    nSTORM : int
        The number of random storm samples to select.
    basin : str
        The basin ID (e.g., 'ATL' for Atlantic).

    Returns
    -------
    tuple
        A tuple containing:
        - DataFrame with random storm data.
        - Estimated number of years for storms.
    """
    
    dataframes_0 = import_storm_data(basin, pathSTORM0)

    random_combinations = [(random.randint(0, number_of_simulation-1), random.randint(0, 1000)) for _ in range(nSTORM)]

    df_all_0=pd.DataFrame() 

    for idx, (num1, num2) in enumerate(random_combinations, start=1):
        
        df_0 = dataframes_0[num1]  
        df_0=df_0[df_0['season']==num2]   
        df_all_0 = pd.concat([df_all_0, df_0], ignore_index=True)  

    storm_counts_0 = df_all_0.groupby('season')['sid'].nunique().reset_index() 
    total_storms_0 = storm_counts_0['sid'].sum() 
    Estimated_Years_STORMS0=total_storms_0/IB_Storms_Per_Year0
    print('Estimated_Years_STORMS0',Estimated_Years_STORMS0)
 
    return df_all_0,Estimated_Years_STORMS0


def random_dataframes_TCrisks(file_path,pathTCrisks0,IB_TCs_Per_Year0,nTC,basin,number_of_simulation):
    """
    Select random TCrisks data from multiple files and calculate the estimated number of years for TCs.

    Parameters
    ----------
    pathTCrisks0 : str
        The path to the directory containing the TCrisks data files.
    IB_TCs_Per_Year0 : float
        The average number of TCs per year.
    nTC : int
        The number of random TCrisks samples to select.
    basin : str
        The basin ID (e.g., 'NA' for Northern Atlantic).

    Returns
    -------
    tuple
        A tuple containing:
        - DataFrame with random TCrisks data.
        - Estimated number of years for TCs.
    """

    dataframe_0 = import_TCrisks_data(file_path,basin, pathTCrisks0,number_of_simulation)
    
    random_combinations = [(random.randint(0, number_of_simulation-1), random.randint(1980, 2021)) for _ in range(nTC)]
    
    df_all_0=pd.DataFrame()

    for idx, (num1,num2) in enumerate(random_combinations, start=1):
        df_0 = dataframe_0[num1]  
        df_0=df_0[df_0['tc_years']==num2]
        df_all_0 = pd.concat([df_all_0, df_0], ignore_index=True) 

    TC_counts_0 = df_all_0.groupby('tc_years')['sid'].nunique().reset_index() 
    total_TCs_0 = TC_counts_0['sid'].sum()  
    Estimated_Years_TCS0=total_TCs_0/IB_TCs_Per_Year0  

    print(f"Estimated number of years for TCs: {Estimated_Years_TCS0}") 

    return df_all_0,Estimated_Years_TCS0



def rp_climatology(nIB,period, pathOut0, city):
    import numpy as np
    import pandas as pd

    df0 = pd.read_csv(pathOut0 + city + '_' + period + '.csv')  

    rp_columns = [f'RP_{i}' for i in range(10)]

    treshold = nIB 

    for col in rp_columns:
        if col in df0.columns:
            df0.loc[df0[col] > treshold, col] = np.nan

    df = df0.copy()

    df['RPmean'] = df.iloc[:, 2:].mean(axis=1) 
    df['RPstd'] = df.iloc[:, 2:].std(axis=1) 

    df['RPb0'] = df['RPmean'] - df['RPstd']
    df['RPb1'] = df['RPmean'] + df['RPstd']

    df.loc[df['RPb0'] < 0, 'RPb0'] = np.nan
    df.loc[df['RPb1'] < 0, 'RPb1'] = np.nan

    return df



def plot_return_wind(df1, df2,city, country, pathOut, city_number):

    # 10 min 
    # wind_items = [20, 29, 37.6, 43.4, 51.1, 61.6]
    wind_items = [18, 33, 43, 50, 58, 70]
    cat = ['TS', 'cat 1', 'cat 2', 'cat 3', 'cat 4', 'cat 5']

    fig, ax = plt.subplots(figsize=(3, 3))

    ax.plot(df1['RPmean'], df1['Wind_speed'], color='green', linestyle='-', linewidth=1, markersize=5, label='MIT-OM 1980-2021')
    ax.fill_betweenx(df1['Wind_speed'], df1['RPb0'], df1['RPb1'], color='green', alpha=0.1)


    ax.set_yticks(wind_items)
    ax.set_yticklabels(cat)
    ax.set_ylim(20, 80)

    ax.set_xlabel('Return period (years)')
    ax.set_ylabel('Category')

    ax.legend(loc='best')

    ax.set_xlim(0, 1000)
    ax.set_xscale('log')
    ax.grid(True, linestyle='--', alpha=0.7)

    ax2 = ax.twinx()
    ax2.set_yticks(wind_items)
    ax2.set_yticklabels(wind_items)
    ax2.set_ylabel('Wind speed (m/s)')
    ax2.set_ylim(20, 80)
    ax.set_xlim(0, 1000)
    ax.set_title(r"$\bf{" + str(city_number+1) + "}$" + " : " + city + " (" + country + ")")

    plt.savefig(pathOut + city + '_' + country + '_' + str(city_number + 1) + '.png', format='png', dpi=600, bbox_inches='tight')
    plt.show()
    plt.close('all')

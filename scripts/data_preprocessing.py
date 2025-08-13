#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: oderizi@unican.es
"""

import xarray as xr
import numpy as np
import pandas as pd
import glob 
import os
import re
import shutil


"""
Change the name of variable in a dataset.
"""

def ds_change_variable_name (ds):
    if 'date' in ds:
        # Convert the 'date' coordinate from int64 to numpy datetime64
        date_values = ds['date'].values  # Get the date values as numpy array
        
        # Convert int64 to string, then to the format 'YYYY-MM-DD'
        date_as_strings = date_values.astype(str)  # Convert to string
        
        proper_times = pd.to_datetime(ds['date'].values.astype(str), format='%Y%m%d')
        ds.assign_coords(time=proper_times)
        ds['date'] = proper_times
        ds = ds.rename({'date':'time'})  
        
        
    if 'valid_time' in ds:
        ds = ds.rename({'valid_time':'time'})     
    return ds

"""
Delete files in a folder
"""

def delete_files_borra (fns,pattern):
    for file_path in fns:
        if re.search(pattern, file_path):
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
                continue


def delete_files(fns, pattern):
    for file_path in fns:
        if re.search(pattern, file_path):
            try:
                # Si es un .nc, intentar abrir/cerrar para liberar el lock
                if file_path.endswith(".nc"):
                    try:
                        with xr.open_dataset(file_path) as ds:
                            pass  # se cierra automáticamente
                    except Exception as e:
                        print(f"No se pudo abrir/cerrar {file_path}: {e}")

                os.remove(file_path)
                print(f"Deleted: {file_path}")

            except PermissionError:
                print(f"No se pudo borrar (en uso): {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

"""
Create a copy of a folder
"""
def copy_folder (source_folder,destination_folder):
    # Check if the source folder exists
    if os.path.exists(source_folder):
        try:
            # Copy the folder and its contents
            shutil.copytree(source_folder, destination_folder)
            print(f"Folder copied from {source_folder} to {destination_folder}")
        except Exception as e:
            print(f"Error copying folder: {e}")
    else:
        print(f"The source folder '{source_folder}' does not exist.")
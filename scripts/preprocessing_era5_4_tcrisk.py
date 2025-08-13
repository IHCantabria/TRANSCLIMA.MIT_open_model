import data_preprocessing_io as data_pre
import os
import glob
import xarray as xr
from pathlib import Path
import tempfile
import shutil

#change date to time and format #######################################################################
base_directory = os.path.join(os.getcwd(), 'data')
input_directory=os.path.join(base_directory, 'era5')
output_directory=os.path.join(base_directory, 'era5')
os.makedirs(output_directory, exist_ok=True)
exp_prefix = 'era5'

# Use glob to find all .nc files matching the pattern recursively ##############################################
fns = glob.glob(f'{input_directory}/**/*{exp_prefix}*.nc', recursive=True)

for i in range(len(fns)):
    with xr.open_dataset(fns[i]) as ds:
    
        ds1=data_pre.ds_change_variable_name (ds)
        ds1.to_netcdf(fns[i]+'_test')
    
print('####################################################')
print('#name of variable changed')

#delete origin files #######################################################################
#fns = glob.glob(f'{base_directory}/**/*{exp_prefix}*.nc', recursive=True)
pattern = r"\d{4}\.nc$"
data_pre.delete_files (fns,pattern)

print('####################################################')
print(' origin files deleted')

# Copy and rename origin files #############################################################################################
print('Genereting a copy of the *.nc_text and converting to .nc extension')

fns_test = glob.glob(f'{base_directory}/**/*{exp_prefix}*.nc_test', recursive=True)
for file_path in fns_test:
    new_filename = file_path[:-5]
    # Guardar usando archivo temporal para evitar problemas de bloqueo
    with xr.open_dataset(file_path) as ds:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".nc")
        temp_file.close()
        ds.to_netcdf(temp_file.name)
    
    shutil.move(temp_file.name, new_filename)  # mover temporal a destino



""" for file_path in fns:
    new_filename = file_path[:-5]

    # Usar archivo temporal para evitar conflicto de escritura
    with xr.open_dataset(file_path) as ds:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".nc")
        temp_file.close()
        ds.to_netcdf(temp_file.name)

    shutil.move(temp_file.name, new_filename) """
    
print('####################################################')
print('Done')

# Delete _test files #############################################################################################
pattern_test = r"_test$"
data_pre.delete_files (fns_test,pattern_test)
print('####################################################')
print('Delete origin files')


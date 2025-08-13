from global_land_mask import globe
import numpy as np
from util import basins
import xarray as xr
import os

"""
Generates land masks across basins from the global_land_mask module.
Saves output in the "land" folder in master directory.
"""

def generate_land_masks(iteration):
    print(f'Generating land masks for iteration {iteration}...')
    
    output_dir = f'land_{iteration}'
    os.makedirs(output_dir, exist_ok=True)

    fns = ['land.nc', 'NA.nc', 'EP.nc', 'NI.nc', 'SI.nc',
           'AU.nc', 'SP.nc', 'WP.nc', 'GL.nc']
    fn_exists = [os.path.exists(f"{output_dir}/{fn}") for fn in fns]
    if all(fn_exists):
        print(f"All files already exist for iteration {iteration}. Skipping generation.")
        return

    # Generate global land mask
    lat = np.linspace(-90, 90, 721)
    lon = np.linspace(-180, 180, 1441)[:-1]
    lon_grid, lat_grid = np.meshgrid(lon, lat)
    globe_land_mask = globe.is_land(lat_grid, lon_grid)

    # Change to 0-360 coordinates for easier global mask.
    b_GL = basins.TC_Basin('GL')
    lon_GL, land_GL = b_GL.transform_lon_r(lon, globe_land_mask)
    lat_GL = lat
    lon_GL_grid, lat_GL_grid = np.meshgrid(lon_GL, lat_GL)

    land = xr.DataArray(data=land_GL, dims=["lat", "lon"],
                        coords=dict(lon=lon, lat=lat))
    ds_land = xr.Dataset(data_vars=dict(land=land))
    ds_land.to_netcdf(f'{output_dir}/land.nc')

    # Atlantic
    lat_box_NA = [0, 9, 10, 14, 18]
    lon_box_NA = np.array([285, 278, 276, 271, 262])
    NA_mask = (lon_GL_grid >= 255) & (lon_GL_grid <= 360) & (lat_GL_grid >= 0) & (lat_GL_grid <= 60)
    NA_box_mask = np.full(NA_mask.shape, False)
    for i in range(len(lat_box_NA)):
        box_mask = (lat_GL_grid >= lat_box_NA[i]) & (lon_GL_grid >= lon_box_NA[i]) & (~land_GL)
        NA_box_mask[box_mask] = True
    NA_mask = xr.DataArray(data=NA_mask & NA_box_mask, dims=["lat", "lon"],
                           coords=dict(lon=lon_GL, lat=lat_GL))
    xr.Dataset(data_vars=dict(basin=NA_mask)).to_netcdf(f'{output_dir}/NA.nc')

    # Eastern Pacific
    lat_box_EP = [7.5, 8.8, 9, 10, 15, 18, 60]
    lon_box_EP = [295, 282, 277, 276.5, 276, 271, 262]
    EP_mask = (lon_GL_grid >= 180) & (lon_GL_grid <= 290) & (lat_GL_grid >= 0) & (lat_GL_grid <= 60)
    EP_box_mask = np.full(EP_mask.shape, False)
    for i in range(len(lon_box_EP)):
        box_mask = (lat_GL_grid <= lat_box_EP[i]) & (lon_GL_grid <= lon_box_EP[i]) & (~land_GL)
        EP_box_mask[box_mask] = True
    EP_mask = xr.DataArray(data=EP_mask & EP_box_mask, dims=["lat", "lon"],
                           coords=dict(lon=lon_GL, lat=lat_GL))
    xr.Dataset(data_vars=dict(basin=EP_mask)).to_netcdf(f'{output_dir}/EP.nc')

    # Western Pacific
    WP_mask = (lon_GL_grid >= 100) & (lon_GL_grid <= 180) & (lat_GL_grid >= 0) & (lat_GL_grid <= 60)
    WP_mask = xr.DataArray(data=WP_mask & (~land_GL), dims=["lat", "lon"],
                           coords=dict(lon=lon_GL, lat=lat_GL))
    xr.Dataset(data_vars=dict(basin=WP_mask)).to_netcdf(f'{output_dir}/WP.nc')

    # North Indian
    NI_mask = (lon_GL_grid >= 30) & (lon_GL_grid <= 100) & (lat_GL_grid >= 0) & (lat_GL_grid <= 49)
    NI_mask = xr.DataArray(data=NI_mask & (~land_GL), dims=["lat", "lon"],
                           coords=dict(lon=lon_GL, lat=lat_GL))
    xr.Dataset(data_vars=dict(basin=NI_mask)).to_netcdf(f'{output_dir}/NI.nc')

    # South Indian
    SI_mask = (lon_GL_grid >= 10) & (lon_GL_grid <= 100) & (lat_GL_grid >= -45) & (lat_GL_grid <= 0)
    SI_mask = xr.DataArray(data=SI_mask & (~land_GL), dims=["lat", "lon"],
                           coords=dict(lon=lon_GL, lat=lat_GL))
    xr.Dataset(data_vars=dict(basin=SI_mask)).to_netcdf(f'{output_dir}/SI.nc')

    # Australia
    AU_mask = (lon_GL_grid >= 100) & (lon_GL_grid <= 170) & (lat_GL_grid >= -45) & (lat_GL_grid <= 0)
    AU_mask = xr.DataArray(data=AU_mask & (~land_GL), dims=["lat", "lon"],
                           coords=dict(lon=lon_GL, lat=lat_GL))
    xr.Dataset(data_vars=dict(basin=AU_mask)).to_netcdf(f'{output_dir}/AU.nc')

    # South Pacific
    SP_mask = (lon_GL_grid >= 170) & (lon_GL_grid <= 260) & (lat_GL_grid >= -45) & (lat_GL_grid <= 0)
    SP_mask = xr.DataArray(data=SP_mask & (~land_GL), dims=["lat", "lon"],
                           coords=dict(lon=lon_GL, lat=lat_GL))
    xr.Dataset(data_vars=dict(basin=SP_mask)).to_netcdf(f'{output_dir}/SP.nc')

    # Global
    GL_mask = ~land_GL
    GL_mask[np.abs(lat_GL_grid) > 50] = 0
    GL_mask = xr.DataArray(data=GL_mask, dims=["lat", "lon"],
                           coords=dict(lon=lon_GL, lat=lat_GL))
    xr.Dataset(data_vars=dict(basin=GL_mask)).to_netcdf(f'{output_dir}/GL.nc')
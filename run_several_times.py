# -*- coding: utf-8 -*-

import os
import shutil
import importlib
import sys
import numpy as np
import random
from scripts import generate_land_masks
from util import compute

def Poisson(mu):
    """Sample the number of TC formations in a given year for the basin."""
    poisson_samples = np.random.poisson(mu, 10000)
    return int(random.choice(poisson_samples))

if __name__ == '__main__':
    sim_index = int(sys.argv[1])

    # === Step 1: Dynamically import the corresponding namelist ===
    namelist_name = f"namelist"
    namelist = importlib.import_module(namelist_name)
    print('namelist = ', namelist_name)

    basin_name = namelist.basin_name
    mu = namelist.mu_tc_per_year

    # === Step 2: Sample the number of TCs for each year ===
    n_years = namelist.end_year - namelist.start_year + 1
    n_TC_per_year = [Poisson(mu) for _ in range(n_years)]
    print('n_TC_per_year =', n_TC_per_year)

    # === Step 3: Set up output directory and copy namelist ===
    f_base = f"{namelist.output_directory}/{namelist.exp_name}_{basin_name}_{sim_index:02d}/"
    os.makedirs(f_base, exist_ok=True)
    print('Saving model output to', f_base)

    shutil.copyfile(f'./{namelist_name}.py', f'{f_base}/namelist.py')

    # === Step 4: Run downscaling steps ===
    generate_land_masks.generate_land_masks(sim_index)
    compute.compute_downscaling_inputs()

    print('Running downscaling for basin', basin_name)
    compute.run_downscaling(basin_name, n_TC_per_year, sim_index, namelist)

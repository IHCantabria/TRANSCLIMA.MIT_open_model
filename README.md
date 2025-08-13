# Modified MIT open model


## Description
This repository contains a **modified version** of the [TCrisk](https://github.com/linjonathan/tropical_cyclone_risk) model.  
While the **core algorithm** remains the same, this version includes:
- **Parallel execution support** for faster simulations.
- **Preprocessing scripts** for streamlined input preparation.
- **Postprocessing utilities** for results analysis and visualization.

It is designed to work efficiently with **ERA5 reanalysis datasets** and GCMs.

---

## Folder structure
```
├── data/                 
├── examples/                  
├── intensity/                 
├── land/              
├── postprocessing/               
├── scripts/                
├── thermo/                 
├── track/                
├── util/                  
├── wind/                 
├── environment.yml           # Conda environment definition
├── run.py                    # Main execution script
├── namelist                 # Example model configurations
└── README.md
```

---

## Installation

```bash
# Create environment
conda env create -f environment.yml
conda activate tc_risk

# Install ERA5 download API
pip install cdsapi

# Configure CDS API credentials
# (Instructions: https://cds.climate.copernicus.eu/api-how-to)
# Save your credentials as ~/.cdsapirc
```

## Installation on the Cluster

```bash
ml Python/3.10.8-GCCcore-12.2.0
python -m venv Risk
source Risk/bin/activate
pip install -r requirements.txt

# Configure CDS API credentials
# (Instructions: https://cds.climate.copernicus.eu/api-how-to)
# Save your credentials as ~/.cdsapirc
```

---

## Quick start example in local for ERA5 
```bash
conda activate tc_risk
python scripts/download_era5.py
python scripts/data_preprocessing.py
python run_several_times.py
python postprocessing/return_period.py
```
After running, you’ll find output files in the `data/test/` directory, including tracks and return period plots.

## Quick start example in cluster for ERA5
To be completed

## Quick start example in local for GCMs
To be completed

## Quick start example in cluster for GCMs
To be completed


---

## Authors
- @SimonTRAISNEL and @itxasoOderiz – Development and modifications  
- **Original TCrisk** – [https://github.com/linjonathan/tropical_cyclone_risk]

---

## License
To be completed

---




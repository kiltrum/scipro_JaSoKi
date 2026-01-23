''' fixtures used in tests '''

from datetime import datetime

import pytest
import xarray as xr
import numpy as np
import pandas as pd
from era5vis import cfg

@pytest.fixture
def retrieve_param_level_from_ds():

    # retrieve variable name and level from the dataset to make sure 
    # that we don't call the function with bad arguments
    with xr.open_dataset(cfg.datafile) as ds:
        param = [variable for variable in ds.variables if
                 ('pressure_level' in ds[variable].dims) and ('longitude' in ds[variable].dims)][0]
        level = ds.pressure_level.to_numpy()[0].astype(int)

    return param, level


@pytest.fixture
def retrieve_param_level_time_from_ds():

    # retrieve variable name, level, and time from the dataset to make sure 
    # that we don't call the function with bad arguments
    with xr.open_dataset(cfg.datafile) as ds:
        param = [variable for variable in ds.variables if
                 ('pressure_level' in ds[variable].dims) and ('longitude' in ds[variable].dims)][0]
        level = ds.pressure_level.to_numpy()[0].astype(int)
        time = ds.valid_time.to_numpy()[0].astype(
               'datetime64[ms]').astype(datetime).strftime('%Y%m%d%H%M')

    return param, level, time

#Creating a minimal ERA5-like NetCDF file for testing plotting functions
@pytest.fixture
def era5_test_file(tmp_path):
    """
    Minimal ERA5-like NetCDF file for plotting tests.

    Covers:
    - Plot_map_anomaly
    - plot_sounding
    """
    valid_time = pd.to_datetime(["2020-01-01"])
    pressure_level = xr.DataArray(
    np.array([1000, 850, 700, 500], dtype=float),
    dims=("pressure_level",),
    attrs={"units": "hPa"},
    )
    latitude = np.linspace(45, 55, 5)
    longitude = np.linspace(5, 15, 5)

    shape = (1, len(pressure_level), len(latitude), len(longitude))

    # -------------------------
    # Helper to create variables
    # -------------------------
    def make_var(name, data, units, long_name):
        return xr.DataArray(
            data,
            dims=("valid_time", "pressure_level", "latitude", "longitude"),
            coords={
                "valid_time": valid_time,
                "pressure_level": pressure_level,
                "latitude": latitude,
                "longitude": longitude,
            },
            attrs={
                "units": units,
                "long_name": long_name,
            },
            name=name,
        )

    # -------------------------
    # Dataset
    # -------------------------
    ds = xr.Dataset(
        {
            # required for both plots
            "t": make_var(
                "t",
                273 + 15 * np.random.rand(*shape),
                "K",
                "Temperature",
            ),
            "z": make_var(
                "z",
                50000 + 1000 * np.random.rand(*shape),
                "m2 s-2",
                "Geopotential",
            ),

            # required for sounding
            "q": make_var(
                "q",
                1e-3 * np.random.rand(*shape),
                "kg/kg",
                "Specific humidity",
            ),
            "u": make_var(
                "u",
                10 * np.random.randn(*shape),
                "m/s",
                "Zonal wind",
            ),
            "v": make_var(
                "v",
                10 * np.random.randn(*shape),
                "m/s",
                "Meridional wind",
            ),
        }
    )

    # -------------------------
    # Write temporary NetCDF
    # -------------------------
    fpath = tmp_path / "era5_test.nc"
    ds.to_netcdf(fpath)

    return fpath


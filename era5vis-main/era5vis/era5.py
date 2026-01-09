"""Functions interacting with the ERA5 dataset. """

import sys
from pathlib import Path

import xarray as xr

from era5vis import cfg


def check_data_availability(param, level=None, time=None, time_ind=None):
    """function code to check if variable, model level, and time stamp are 
    in the data file and if not raise an exception."""

    if not Path(cfg.datafile).exists():
        print("The specified data file does not exist. Please set a valid path in cfg.py.")
        sys.exit()

    with xr.open_dataset(cfg.datafile) as ds:
        # Check if parameter exists in dataset
        if param not in ds.variables:
            raise ValueError(f"Parameter '{param}' not found in dataset. "
                           f"Available parameters: {list(ds.data_vars)}")
        
        # Check if level exists 
        if level is not None:
            if 'pressure_level' not in ds.dims:
                raise ValueError(f"Dataset does not have 'pressure_level' dimension")
            if level not in ds.pressure_level.values:
                raise ValueError(f"Pressure level {level} hPa not found in dataset. "
                               f"Available levels: {ds.pressure_level.values}")
        
        # Check if time exists (if provided as string)
        if time is not None:
            try:
                ds.sel(valid_time=time)
            except (KeyError, ValueError):
                raise ValueError(f"Time '{time}' not found in dataset. "
                               f"Available time range: {ds.valid_time.values[0]} to {ds.valid_time.values[-1]}")
        
        # Check if time index exists (if provided as integer)
        if time_ind is not None:
            if not isinstance(time_ind, int):
                raise TypeError(f"time_ind must be an integer, got {type(time_ind)}")
            if time_ind < 0 or time_ind >= len(ds.valid_time):
                raise ValueError(f"Time index {time_ind} out of range. "
                               f"Valid range: 0 to {len(ds.valid_time) - 1}")


def horiz_cross_section(param, lvl, time):
    """Extract a horizontal cross section from the ERA5 data.
    
    Parameters
    ----------
    param: str
        ERA5 variable
    lvl : integer
        model pressure level (hPa)
    time : str or integer
        time string or time index

    Returns
    -------
    da: xarray.DataArray
        2D DataArray of param
    """

    if not Path(cfg.datafile).exists():
        print("The specified data file does not exist. Please set a valid path in cfg.py.")
        sys.exit()

    # use either sel or sel depending on the type of time (index or date format)
    with xr.open_dataset(cfg.datafile).load() as ds:
        if isinstance(time, str):
            da = ds[param].sel(pressure_level=lvl).sel(valid_time=time)
        elif isinstance(time, int):
            da = ds[param].sel(pressure_level=lvl).isel(valid_time=time)
        else:
            raise TypeError('time must be a time format string or integer')

    return da

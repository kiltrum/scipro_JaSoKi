import xarray as xr
import numpy as np

def add_wind_speed_dir(ds: xr.Dataset, u_name="u", v_name="v"):

    """
    Add wind speed (wspd) and meteorological wind direction (wdir) to a Dataset.

    Wind speed is computed as sqrt(u² + v²).
    Wind direction is the direction the wind is coming FROM
    (0° = north, 90° = east).
    """
    u = ds[u_name]
    v = ds[v_name]

    wspd = np.hypot(u, v)  # sqrt(u**2 + v**2)

    # meteorological direction wind is coming FROM
    wdir = (np.degrees(np.arctan2(-u, -v)) + 360.0) % 360.0

    wspd = wspd.assign_attrs(
        long_name="Wind speed",
        units=getattr(u, "units", "m s-1"),
    )
    wdir = wdir.assign_attrs(
        long_name="Wind direction (from)",
        units="degrees",
        convention="meteorological (0=from North, 90=from East)",
    )

    return ds.assign(wspd=wspd, wdir=wdir)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import os
from datetime import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.ticker as mticker
from metpy.plots import SkewT
from metpy.units import pandas_dataframe_to_unit_arrays, units
import metpy.calc as mpcalc
from metpy.calc import potential_temperature
from metpy.calc import precipitable_water

def plot_sounding(pathfile, lat_pt, lon_pt):
    ds = xr.open_dataset(pathfile)
    ds = ds.metpy.parse_cf()
    date=ds.valid_time.dt.strftime("%B %Y").item()
    ds = ds.squeeze()
    profile = ds.sel(
        latitude=lat_pt,
        longitude=lon_pt,
        method="nearest"
    )


    p = profile['pressure_level'].metpy.unit_array
    T = profile['t'].metpy.unit_array
    q = profile['q'].metpy.unit_array
    u = profile['u'].metpy.unit_array
    v = profile['v'].metpy.unit_array
    #Calculate dew point temperature from specific humidity
    Td = mpcalc.dewpoint_from_specific_humidity(p, T, q)

    # Change default to be better for skew-T (optional)
    fig = plt.figure(figsize=(9, 9))

    # Initiate the skew-T plot type from MetPy class loaded earlier
    skew = SkewT(fig, rotation=45)

    # Plot the data using normal plotting functions, in this case using
    # log scaling in Y, as dictated by the typical meteorological plot
    skew.plot(p, T, 'r')
    skew.plot(p, Td, 'g')
    skew.plot_barbs(p, u, v, y_clip_radius=0.03)
    #skew.plot_barbs(p[::3], u[::3], v[::3], y_clip_radius=0.03)
    # Add the relevant special lines to plot throughout the figure
    skew.plot_dry_adiabats(t0=np.arange(233, 533, 10) * units.K,
                        alpha=0.25, color='orangered')
    skew.plot_moist_adiabats(t0=np.arange(233, 400, 5) * units.K,
                            alpha=0.25, color='tab:green')
    skew.plot_mixing_lines(pressure=np.arange(1000, 99, -20) * units.hPa,
                        linestyle='dotted', color='tab:blue')
    #skew.shade_cape(pressure=p,t=T,t_parcel=)
    # Add some descriptive titles
    plt.title(f'Sounding at location {lat_pt}°,{lon_pt}° from {date}')
    fname = (
    f"ERA5_sounding_"
    f"{lon_pt},{lat_pt}"
    f"{date}.png"
    )
    
    outdir = "PNG"

    if not os.path.isdir(outdir):
        os.makedirs(outdir)
        print(f"Created output directory: {outdir}")
    else:
        print(f"Output directory already exists: {outdir}")
    outpath = os.path.join(outdir, fname)
    plt.savefig(outpath, dpi=300, bbox_inches="tight")
    print(f"Plot saved to: {outpath}")
    plt.show()
    return fname
    

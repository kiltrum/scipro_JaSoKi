import profile
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
    #ds = ds.squeeze()
    #profile = ds.sel(
    #    latitude=lat_pt,
    #    longitude=lon_pt,
        
    #    method="nearest"
    #)
    profile = ds.sel(latitude=lat_pt, longitude=lon_pt, method="nearest").squeeze()
    profile = profile.sortby('pressure_level', ascending=False)


    p = profile['pressure_level'].metpy.unit_array.to(units.hPa)
    T = profile['t'].metpy.unit_array.to(units.K)
    q = profile['q'].metpy.unit_array.to('kg/kg')
    u = profile['u'].metpy.unit_array
    v = profile['v'].metpy.unit_array

    #Calculate dew point temperature from specific humidity
    Td = mpcalc.dewpoint_from_specific_humidity(p, T, q)

    # Change default to be better for skew-T (optional)
    fig = plt.figure(figsize=(9, 9))

    # Initiate the skew-T plot type from MetPy class loaded earlier
   
    skew = SkewT(fig, rotation=45)
    skew.ax.set_ylim(p.max().m, p.min().m)
    skew.ax.set_xlim(-40, 40)
    # Plot the data using normal plotting functions, in this case using
    # log scaling in Y, as dictated by the typical meteorological plot
    skew.plot(p, T, 'r')
    skew.plot(p, Td, 'g')
    skew.plot_barbs(p, u, v, y_clip_radius=0.03)
    
    # Add the relevant special lines to plot throughout the figure

    skew.plot_dry_adiabats(alpha=0.25, color='orangered')
    skew.plot_moist_adiabats(alpha=0.25, color='tab:green')

    # MIXING-RATIO
    skew.plot_mixing_lines(
        pressure=np.arange(p.max().m, p.min().m, -20) * units.hPa,
        linestyle='dotted',
        color='tab:blue',
        linewidth=1
    )
    # Add some descriptive titles
    plt.title(f'Sounding at location {lat_pt}°,{lon_pt}° from {date}')

    safe_date = date.replace(" ", "_").replace(",", "")
    safe_loc = f"{lon_pt}_{lat_pt}"

    fname = (
        f"ERA5_sounding_"
        f"{safe_loc}_"
        f"{safe_date}.png"
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


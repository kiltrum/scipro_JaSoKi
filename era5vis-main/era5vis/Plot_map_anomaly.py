#era5vis/Plot_map_anomaly.py
#Simon Porrmann, 2026
'''
Plot for a 2D map of ERA5 (mean month) anomaly data for a given parameter and pressure level.

What it does:
----------
- Loads ERA5 data from a NetCDF file.
- Computes the anomaly against a climatology dataset.
- Plots the anomaly on a map with coastlines and gridlines.
- Overlays contour lines of geopotential height.
- Marks a specific location (sounding point) and crosscesction lines.

-saves the plot as a PNG file in a designated directory.
'''


import matplotlib.pyplot as plt  
import numpy as np  
import os
from pytest import param
from pathlib import Path
import xarray as xr
import cartopy  
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

#FIXED VARIABLES


def Plot_map_anomaly(pathfile,param,pressure_level,lat_pt,lon_pt):
    range = [-55,35,35,90]
    DATA_DIR = Path(__file__).parent / "data"
    clim_path = DATA_DIR / "model_clim.nc"
    clim_monthly = xr.open_dataset(clim_path)

    ds = xr.open_dataset(pathfile)
    #Get the parameter and Month information
    long_name = ds[param].attrs.get("long_name", param)
    units = ds[param].attrs.get("units", "")
    month = ds.valid_time.dt.month.item()
    date=ds.valid_time.dt.strftime("%B %Y").item()
    #Calculate anomaly
    anomaly = ds - clim_monthly.sel(month=month)
    #Create Map
    fig = plt.figure(figsize=(9,9))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(range)  
    ax.coastlines()
    #Create the contour plot include some map features
    lon = anomaly['longitude']
    lat = anomaly['latitude']
    im = ax.contourf(lon,lat,anomaly[param].sel(pressure_level=pressure_level).isel(valid_time=0),transform=ccrs.PlateCarree())
    cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.05)
    cbar.set_label(f"{long_name} [{units}]", fontsize=12)
    gl = ax.gridlines(draw_labels=True, crs=ccrs.PlateCarree(),
                    linewidth=1, color='gray', alpha=0.5, linestyle='--')
      
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 10}
    gl.ylabel_style = {'size': 10}

    #Insert Sounding location and crossplot lines
    ax.plot(lon_pt, lat_pt, marker='o', color='red', markersize=8,
            transform=ccrs.PlateCarree(), label="sounding")
    ax.axhline(lat_pt, color='red', linestyle='-', linewidth=1)
    ax.axvline(lon_pt, color='red', linestyle='-', linewidth=1)
    
    #extract z for same level and time step
    z_level = ds['z'].sel(pressure_level=pressure_level).isel(valid_time=0)
    g=9.81
    z_dam = z_level / (g * 10)
    # Contours
    cs = ax.contour(lon, lat, z_dam, colors='black', linewidths=1, transform=ccrs.PlateCarree())

    # Labels for the contours
    ax.clabel(cs, inline=True, fontsize=10, fmt="%d dam")  # fmt kann angepasst werden

    plt.title(f"ERA5 {long_name} anomaly for {date} at {pressure_level} hPa", fontsize=14)

    # make filename-safe date string
    safe_date = date.replace(" ", "_").replace(",", "")

    fname = (
        f"ERA5_{param}_"
        f"{pressure_level}hPa_"
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


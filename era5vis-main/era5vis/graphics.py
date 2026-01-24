""" contains plot functions """

from __future__ import annotations


import calendar
import os
from datetime import datetime
from pathlib import Path


import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import xarray as xr

# local imports
from . import helpers_crosssection as ch


def plot_horiz_cross_section(da, filepath=None):
    ''' plot horizontal cross-section

    Parameters
    ----------
    da : xarray.DataArray
        horizontal cross section
    filepath : str
        plot is saved to filepath if provided
    '''

    # set up a single set of axes
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_position([0.1, 0.1, 0.7, 0.85])
    ax.set_xlabel(r'Longitude ($^{\circ}$)')
    ax.set_ylabel(r'Latitude ($^{\circ}$)')
    time = da.valid_time.to_numpy().astype('datetime64[ms]').astype(datetime)
    ax.set_title(f'{da.long_name} at {da.pressure_level.to_numpy()} '
                 + f'{da.pressure_level.units} ({time:%d %b %Y %H:%M})', fontsize=12
                )

    cf = ax.contourf(da, levels=20)
    # add colorbar in separate axes
    cax = fig.add_axes([0.83, 0.1, 0.02, 0.85])
    plt.colorbar(cf, cax=cax)
    cax.set_ylabel(f'({da.units})')

    if filepath is not None:
        fig.savefig(filepath)
        plt.close()

    return fig




#### Crossection for the HTML ERA5 visualizer


# Jakob Werkgarner, 2026


"""
Simple cross-section plots for ERA5-style pressure level data.

"""
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(__file__).parent / "data"

CLIMFILE_DEFAULT = DATA_DIR / "model_clim.nc"
TERRAIN_FILE_DEFAULT = DATA_DIR / "model_topo_pressure.nc"



def plot_crosssection(
    casefile,
    lat,
    lon,
    var,
    *,
    climfile=CLIMFILE_DEFAULT,
    field="anomaly",
    terrainfile=TERRAIN_FILE_DEFAULT,
    savepath=None,
):
    """
    Main function.

    Parameters
    ----------
    var : str
        Variable name (parsed from terminal input)
    lat, lon : float
        Location for the cross-sections
    casefile : str
        Case dataset
    climfile : str
        Monthly climatology (default: 1991–2020 climatology)
    field : str
        "anomaly" (default), "case", or "clim".
    terrainfile : str or None
        If given: adds a terrain line + white mask.
    savepath : str or None
        If given: saves the plot and closes the figure.
    """
    if field not in ("anomaly", "case", "clim"):
        raise ValueError("field must be one of: 'anomaly', 'case', 'clim'.")
    

    ################
    # Define Constants
    ################


    # --- constants / defaults ---
    G0 = 9.80665  # m/s²

    LEVEL_DIM = "pressure_level"
    LAT_DIM = "latitude"
    LON_DIM = "longitude"
    MONTH_DIM = "month"
    GEO_VAR = "z"

    U_VAR = "u"
    V_VAR = "v"

    CLIM_REF_PERIOD = "1991–2020"

    NLEVELS_FILL = 21
    NLEVELS_GEO = 12

    QUIVER_X_SKIP = 5
    QUIVER_Y_SKIP = 1
    QUIVER_SCALE = 5.0



    # --- read casefile ---
    with xr.open_dataset(casefile) as ds_case:
        ds_case2 = ch.drop_time(ds_case)
        case_month, case_year = ch.get_case_month_year(ds_case)

    month_short = calendar.month_abbr[case_month]
    month_year_text = f"{month_short} {case_year}"

    # --- read clim for that month ---
    with xr.open_dataset(climfile) as ds_clim_all:
        ds_clim = ds_clim_all.sel({MONTH_DIM: case_month}, drop=True)

    # Use CASE grid as reference (API subset area) so extent fits
    ref = ds_case2[var]
    ds_clim_on_case = ds_clim.reindex_like(ref, method="nearest")

    if GEO_VAR not in ds_clim_on_case:
        raise KeyError(f"'{GEO_VAR}' missing from climatology file (needed for background).")

    if field in ("case", "anomaly") and var not in ds_case2:
        raise KeyError(f"'{var}' not found in case file.")
    if field in ("clim", "anomaly") and var not in ds_clim:
        raise KeyError(f"'{var}' not found in climatology file (needed for field='{field}').")

    # --- background (climatological geopotential height) ---
    z_bg = ds_clim_on_case[GEO_VAR] / G0
    z_lat = ch.to_2d(z_bg.sel({LAT_DIM: lat}, method="nearest"))
    z_lon = ch.to_2d(z_bg.sel({LON_DIM: lon}, method="nearest"))

    pretty_name = ch.pretty_var_name(var, ds_case2, ds_clim_on_case)
    units = ds_clim[var].attrs.get("units", "")

    # wspd special-case
    effective_field = "case" if (field == "anomaly" and var == "wspd") else field

    if effective_field == "case":
        fld = ds_case2[var]
        mode_text = "CASE"
    elif effective_field == "clim":
        fld = ds_clim_on_case[var]
        mode_text = "CLIM"
    else:
        fld = ds_case2[var] - ds_clim_on_case[var]
        mode_text = "ANOMALY"

    # --- color scaling ---
    if mode_text == "ANOMALY":
        vmax = float(max(abs(fld.min()), abs(fld.max())))
        norm = Normalize(-vmax, vmax)
        cmap = "coolwarm"
    else:
        vmax = float(fld.max())
        norm = Normalize(0.0, vmax)
        cmap = "Blues" if var == "wspd" else "viridis"

    # --- extract 2D sections ---
    fld_lat_sel = fld.sel({LAT_DIM: lat}, method="nearest")
    fld_lon_sel = fld.sel({LON_DIM: lon}, method="nearest")

    fld_lat = ch.to_2d(fld_lat_sel)
    fld_lon = ch.to_2d(fld_lon_sel)

    lat_used = float(fld_lat_sel[LAT_DIM].values)
    lon_used = float(fld_lon_sel[LON_DIM].values)

    # --- arrows (only for wspd; always from CASE) ---
    u = v = None
    if var == "wspd":
        for needed in (U_VAR, V_VAR):
            if needed not in ds_case2:
                raise KeyError(f"Case file missing '{needed}' required for wind arrows (wspd).")
        u = ds_case2[U_VAR]
        v = ds_case2[V_VAR]

    # --- terrain lines (optional) ---
    terr_we = terr_sn = None
    if terrainfile is not None:
        terr_we, terr_sn = ch.load_terrain_lines(terrainfile, lat_used, lon_used)

    # --- title ---
    when_text = month_year_text if mode_text in ("CASE", "ANOMALY") else month_short
    ref_text = f"Model climate {CLIM_REF_PERIOD}" if mode_text != "CASE" else ""
    title_line = " • ".join([p for p in [mode_text, when_text, ref_text, pretty_name] if p])
    cb_label = f"{pretty_name} [{units}]"

    fig, axes = plt.subplots(2, 1, figsize=(10.5, 9.2), constrained_layout=True)
    fig.suptitle(title_line, x=0.01, ha="left")

    ch.plot_panel_we(axes[0], fld_lat, z_lat, lon_used, lat_used, norm, cmap, cb_label, u, terr_we)
    ch.plot_panel_sn(axes[1], fld_lon, z_lon, lat_used, lon_used, norm, cmap, cb_label, v, terr_sn)

    outdir = "tmp_png"
    os.makedirs(outdir, exist_ok=True)
    fname = "ERA5_crosssection.png"
    outpath = savepath or os.path.join(outdir, fname)

    fig.savefig(outpath, dpi=180, bbox_inches="tight")
    #plt.show()
    plt.close(fig)

    print(f"Plot saved to: {outpath}")
    return os.path.basename(outpath)

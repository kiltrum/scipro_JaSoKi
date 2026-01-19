# era5vis/crosssection.py
"""
Simple cross-section plots for ERA5-style pressure level data.

What it does
------------
- Recives and reads the case file (Donwloaded from the API)
- Reads monthly model climatology file
- Plots two cross-sections through a point (lat/lon):
    1) W–E at fixed latitude  (x = longitude, y = pressure)
    2) S–N at fixed longitude (x = latitude,  y = pressure)

modes
---------------------
field="anomaly" (default)

field="case"
    plots values of case file (shows the background climatology)

field="clim"
    plots the climatological mean for the case month

Background
----------
Climatological geopotential height (z/g0) as light grey shading + contours.

Wind arrows (only when var == "wspd")
-------------------------------------
IMPORTANT: W IS NOT USED.
- W–E panel: arrows are horizontal only (u, 0)
- S–N panel: arrows are horizontal only (v, 0)

Terrain mask
------------
Terrain file contains a variable called "p_sfc" which is the surface pressure (hPa).
"""

from __future__ import annotations

import calendar
import os
from pathlib import Path

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize


# --- constants / defaults (kept simple) ---
G0 = 9.80665

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


# FILEPATHS
ROOT = Path(__file__).resolve().parents[1]   # .../era5vis-main
DATA = ROOT / "data"
DATA_DIR = Path(__file__).parent / "data"
CLIMFILE_DEFAULT = DATA_DIR / "model_clim.nc"
#CLIMFILE_DEFAULT = DATA / "model_clim.nc"
TERRAIN_FILE_DEFAULT = DATA_DIR / "model_topo_pressure.nc"

# terrain is already in pressure coords (hPa)
TERRAIN_VAR = "p_sfc"


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
        Monthly climatology
    field : str
        "anomaly" (default), "case", or "clim".
    terrainfile : str or None
        If given: adds a terrain line + white mask.
    savepath : str or None
        If given: saves the plot and closes the figure.
    """

    # Check input field (guard clause)
    if field not in ("anomaly", "case", "clim"):
        raise ValueError("field must be one of: 'anomaly', 'case', 'clim'.")

    # read casefile
    with xr.open_dataset(casefile) as ds_case:
        ds_case2 = drop_time(ds_case)

        # month/year from case time
        case_month, case_year = get_case_month_year(ds_case)

    month_short = calendar.month_abbr[case_month]
    month_year_text = f"{month_short} {case_year}"

    # read clim for that month (drop month dim)
    with xr.open_dataset(climfile) as ds_clim_all:
        ds_clim = ds_clim_all.sel({MONTH_DIM: case_month}, drop=True)

    # Use CASE grid as reference (API subset area)
    ref = ds_case2[var]

    # Put climatology variables onto the CASE grid (lat/lon/pressure_level)
    ds_clim_on_case = ds_clim.reindex_like(ref, method="nearest")

    # all data is now loaded and prepared now make sure that data is available
    # make sure that gph (z) is in the file for the background
    if GEO_VAR not in ds_clim_on_case:
        raise KeyError(...)

    # basic checks
    if field in ("case", "anomaly") and var not in ds_case2:
        raise KeyError(f"'{var}' not found in case file.")
    if field in ("clim", "anomaly") and var not in ds_clim:
        raise KeyError(f"'{var}' not found in climatology file (needed for field='{field}').")

    # peprae background (clim geopotential height) (basically hydrostatic for a month)
    z_bg = ds_clim_on_case[GEO_VAR] / G0
    z_lat = to_2d(z_bg.sel({LAT_DIM: lat}, method="nearest"))
    z_lon = to_2d(z_bg.sel({LON_DIM: lon}, method="nearest"))

    # nice name
    pretty_name = pretty_var_name(var, ds_case2, ds_clim_on_case)

    # units (just try case first, otherwise clim)
    units = ds_case2[var].attrs.get("units", "") if var in ds_case2 else ds_clim[var].attrs.get("units", "")

    # what field to actually plot (wspd special case)
    effective_field = "case" if (field == "anomaly" and var == "wspd") else field

    if effective_field == "case":
        fld = ds_case2[var]
        mode_text = "CASE"
    elif effective_field == "clim":
        fld = ds_clim_on_case[var]
        mode_text = "CLIM"
    else:
        # Calculate anomaly like in Plot_map_anomaly:
        # anomaly = case - clim(month), but force clim onto the case grid

        # put climatology onto the case coordinates (uses case lon/lat/levels)
        fld = ds_case2[var] - ds_clim_on_case[var]
        mode_text = "ANOMALY"

    # color scaling
    # make sure that the color scales around 0 for the anomaly
    if mode_text == "ANOMALY":
        vmax = float(max(abs(fld.min()), abs(fld.max())))
        norm = Normalize(-vmax, vmax)
        cmap = "coolwarm"
    else:
        vmax = float(fld.max())
        norm = Normalize(0.0, vmax)
        cmap = "Blues" if var == "wspd" else "viridis"

    # extract 2D sections
    fld_lat_sel = fld.sel({LAT_DIM: lat}, method="nearest")
    fld_lon_sel = fld.sel({LON_DIM: lon}, method="nearest")

    fld_lat = to_2d(fld_lat_sel)
    fld_lon = to_2d(fld_lon_sel)

    # just make sure the actually used lat/lon values are saved somewhere when gridpoint is not selected directly
    lat_used = float(fld_lat_sel[LAT_DIM].values)
    lon_used = float(fld_lon_sel[LON_DIM].values)

    # arrows (only for wspd; always from CASE)
    # NOTE: W is not used. Arrows are horizontal only.
    u = v = None
    if var == "wspd":
        for needed in (U_VAR, V_VAR):
            if needed not in ds_case2:
                raise KeyError(f"Case file missing '{needed}' required for wind arrows (wspd).")
        u = ds_case2[U_VAR]
        v = ds_case2[V_VAR]

    # terrain lines (optional)
    terr_we = terr_sn = None
    if terrainfile is not None:
        terr_we, terr_sn = load_terrain_lines(terrainfile, lat_used, lon_used)

    # title: requested format
    when_text = month_year_text if mode_text in ("CASE", "ANOMALY") else month_short
    ref_text = f"Model climate {CLIM_REF_PERIOD}" if mode_text != "CASE" else ""
    title_line = " • ".join([p for p in [mode_text, when_text, ref_text, pretty_name] if p])

    cb_label = f"{pretty_name} [{units}]" if units else pretty_name

    fig, axes = plt.subplots(2, 1, figsize=(10.5, 9.2), constrained_layout=True)
    fig.suptitle(title_line, x=0.01, ha="left")

    plot_panel_we(axes[0], fld_lat, z_lat, lon_used, lat_used, norm, cmap, cb_label, u, terr_we)
    plot_panel_sn(axes[1], fld_lon, z_lon, lat_used, lon_used, norm, cmap, cb_label, v, terr_sn)

    # output path (either custom or default)
    outdir = "PNG"
    os.makedirs(outdir, exist_ok=True)

    safe_date = month_year_text.replace(" ", "_")
    fname = f"ERA5_crosssection_{var}_{safe_date}.png"
    outpath = savepath or os.path.join(outdir, fname)

    fig.savefig(outpath, dpi=180, bbox_inches="tight")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {outpath}")

    

    return os.path.basename(outpath)


# -------------------------
# helpers (candidates to move into helpers.py)
# -------------------------
def drop_time(ds):
    """Drop time dimension (valid_time)"""
    if "valid_time" in ds.dims:
        return ds.isel(valid_time=0).squeeze(drop=True)
    return ds


def get_case_month_year(ds_case):
    """Return (month, year) from valid_time coordinate."""
    if "valid_time" not in ds_case.coords:
        raise KeyError("Case dataset has no 'valid_time' coordinate.")
    t = ds_case["valid_time"]
    t0 = t.values[0] if t.size > 0 else t.values
    dt = xr.DataArray(t0).dt
    return int(dt.month.values), int(dt.year.values)


def pretty_var_name(var, ds_case2, ds_clim):
    """Try long_name from case. Fallback: var."""
    return ds_case2[var].attrs.get("long_name", var) if var in ds_case2 else str(var)


def to_2d(da):
    """Make sure contourf gets a 2D array (drop singleton dims like expver/number)."""
    out = da.squeeze(drop=True)
    while out.ndim > 2:
        out = out.isel({out.dims[0]: 0}).squeeze(drop=True)
    return out


def add_background(ax, x, y, z2d):
    ax.contourf(x, y, z2d, levels=NLEVELS_GEO, cmap="Greys", alpha=0.18)
    ax.contour(x, y, z2d, levels=NLEVELS_GEO, colors="#667085", linewidths=0.6, alpha=0.65)


def add_colorbar(fig, ax, mappable, label):
    cb = fig.colorbar(mappable, ax=ax, pad=0.02, shrink=0.98)
    cb.set_label(label)


def add_quiver(ax, xdim, horiz):
    """
    Add wind arrows.

    IMPORTANT: W is not used.
    - Uses only horiz (=u or v).
    - Vertical component is set to zero for plotting.
    """
    hq = horiz.isel(
        {
            xdim: slice(None, None, QUIVER_X_SKIP),
            LEVEL_DIM: slice(None, None, QUIVER_Y_SKIP),
        }
    )

    X, Y = xr.broadcast(hq[xdim], hq[LEVEL_DIM])
    U = hq.values
    V = np.zeros_like(U)

    ax.quiver(
        X.values,
        Y.values,
        U,
        V,
        angles="xy",
        scale_units="xy",
        scale=QUIVER_SCALE,
        width=0.0035,
        headwidth=4.8,
        headlength=6.2,
        headaxislength=5.5,
        alpha=0.9,
    )


def load_terrain_lines(terrainfile, lat_used, lon_used):
    """Load terrain already in pressure (hPa) and return two 1D lines."""
    with xr.open_dataset(terrainfile) as ds_terr:
        ds_terr2 = drop_time(ds_terr)
        if TERRAIN_VAR not in ds_terr2:
            raise KeyError(f"Terrain file does not contain variable '{TERRAIN_VAR}'.")
        p_sfc = ds_terr2[TERRAIN_VAR]
        terr_we_p = to_2d(p_sfc.sel({LAT_DIM: lat_used}, method="nearest"))
        terr_sn_p = to_2d(p_sfc.sel({LON_DIM: lon_used}, method="nearest"))
    return terr_we_p, terr_sn_p


def mask_terrain_white(ax, x1d, p_sfc_hpa):
    """Fill below the terrain with white."""
    ymin, ymax = ax.get_ylim()
    pmax = max(ymin, ymax)  # bottom (largest pressure)
    ax.fill_between(x1d.values, p_sfc_hpa.values, pmax, color="white", zorder=10)


def plot_panel_we(ax, fld2d, z2d, lon_used, lat_used, norm, cmap, cb_label, u, terrain_line):
    """Plot W–E panel"""
    x = fld2d[LON_DIM]
    y = fld2d[LEVEL_DIM]

    add_background(ax, x, y, z2d)
    cf = ax.contourf(x, y, fld2d, levels=NLEVELS_FILL, cmap=cmap, norm=norm)

    # horizontal arrows only
    if u is not None:
        u2 = to_2d(u.sel({LAT_DIM: lat_used}, method="nearest"))
        add_quiver(ax, LON_DIM, u2)

    ax.invert_yaxis()

    if terrain_line is not None:
        # terrain_line may be on a larger lon grid than the API subset -> put it onto x
        terrain_on_x = terrain_line.reindex({x.dims[0]: x}, method="nearest")
        mask_terrain_white(ax, x, terrain_on_x)

    ax.plot(x.values, terrain_on_x.values, color="k", linewidth=1.3, zorder=11)
    ax.axvline(lon_used, color="k", linestyle=":", linewidth=1.1, alpha=0.7)
    ax.set_title(f"W–E at {LAT_DIM}≈{lat_used:.2f}")
    ax.set_xlabel(LON_DIM)
    ax.set_ylabel(LEVEL_DIM)
    add_colorbar(ax.figure, ax, cf, cb_label)


def plot_panel_sn(ax, fld2d, z2d, lat_used, lon_used, norm, cmap, cb_label, v, terrain_line):
    """Plot S–N panel"""
    x = fld2d[LAT_DIM]
    y = fld2d[LEVEL_DIM]

    add_background(ax, x, y, z2d)
    cf = ax.contourf(x, y, fld2d, levels=NLEVELS_FILL, cmap=cmap, norm=norm)

    # horizontal arrows only
    if v is not None:
        v2 = to_2d(v.sel({LON_DIM: lon_used}, method="nearest"))
        add_quiver(ax, LAT_DIM, v2)

    ax.invert_yaxis()

    if terrain_line is not None:
        terrain_on_x = terrain_line.reindex({x.dims[0]: x}, method="nearest")
        mask_terrain_white(ax, x, terrain_on_x)
        ax.plot(x.values, terrain_on_x.values, color="k", linewidth=1.3, zorder=11)


    ax.axvline(lat_used, color="k", linestyle=":", linewidth=1.1, alpha=0.7)
    ax.set_title(f"S–N at {LON_DIM}≈{lon_used:.2f}")
    ax.set_xlabel(LAT_DIM)
    ax.set_ylabel(LEVEL_DIM)
    add_colorbar(ax.figure, ax, cf, cb_label)
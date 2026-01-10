# era5vis/crosssection.py
"""
Simple cross-section plots for ERA5-style pressure level data.

What it does
------------
- Reads a CASE file (usually one timestep with 'valid_time' or 'time')
- Reads a monthly climatology file (dimension 'month' = 1..12)
- Plots two cross-sections through a point (lat/lon):
    1) W–E at fixed latitude  (x = longitude, y = pressure)
    2) S–N at fixed longitude (x = latitude,  y = pressure)

Shading modes (field)
---------------------
field="anomaly" (default)
    case - climatology(month)
    Exception: for "wspd" we plot CASE wspd (more intuitive than anomaly)
field="case"
    plots the case field
field="clim"
    plots the climatological mean for the case month

Background
----------
Climatological geopotential height (z/g0) as light grey shading + contours.

Wind arrows (only when var == "wspd")
-------------------------------------
- W–E panel: arrows are (u, w)
- S–N panel: arrows are (v, w)
w is ERA5 vertical velocity in pressure coordinates (Pa/s).
We convert to hPa/s (divide by 100) and multiply by W_EXAG so it is visible.

Terrain mask
------------
Terrain file contains a variable called "z" which you said is terrain height (m).
We convert that height to an approximate surface pressure using a standard
atmosphere formula, then:
- draw a black terrain line
- fill everything below it with white (so it looks like the ground)
"""

from __future__ import annotations

import calendar
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
W_VAR = "w"

CLIM_REF_PERIOD = "1991–2020"

NLEVELS_FILL = 21
NLEVELS_GEO = 12

QUIVER_X_SKIP = 5
QUIVER_Y_SKIP = 1
QUIVER_SCALE = 5.0
W_EXAG = 1000.0

TERRAIN_FILE_DEFAULT = "era5vis-main/data/model_terrain/elevaation.nc"
TERRAIN_VAR = "z"


def plot_crosssection(var, lat, lon, *, casefile, climfile, field="anomaly",
                      terrainfile=TERRAIN_FILE_DEFAULT, savepath=None):
    """
    Main function.

    Parameters
    ----------
    var : str
        Variable name (e.g. "t", "q", "wspd").
    lat, lon : float
        Location for the cross-sections (nearest grid point is used).
    casefile : str
        Case dataset (usually one timestep).
    climfile : str
        Monthly climatology (month=1..12).
    field : str
        "anomaly" (default), "case", or "clim".
    terrainfile : str or None
        If given: adds a terrain line + white mask.
    savepath : str or None
        If given: saves the plot and closes the figure.
    """
    if field not in ("anomaly", "case", "clim"):
        raise ValueError("field must be one of: 'anomaly', 'case', 'clim'.")

    ds_case = xr.open_dataset(casefile)
    ds_case2 = drop_time(ds_case)

    # month/year from case time
    case_month, case_year = get_case_month_year(ds_case)
    month_short = calendar.month_abbr[case_month]
    month_year_text = f"{month_short} {case_year}"

    # read clim for that month
    ds_clim_all = xr.open_dataset(climfile)
    ds_clim = ds_clim_all.sel({MONTH_DIM: case_month}).squeeze(drop=True)

    if GEO_VAR not in ds_clim:
        raise KeyError(f"'{GEO_VAR}' must exist in climatology file for the background.")

    # basic checks
    if field in ("case", "anomaly") and var not in ds_case2:
        raise KeyError(f"'{var}' not found in case file.")
    if field in ("clim", "anomaly") and var not in ds_clim:
        raise KeyError(f"'{var}' not found in climatology file (needed for field='{field}').")

    # background (clim geopotential height)
    z_bg = ds_clim[GEO_VAR] / G0
    z_lat = to_2d(z_bg.sel({LAT_DIM: lat}, method="nearest"))
    z_lon = to_2d(z_bg.sel({LON_DIM: lon}, method="nearest"))

    # nice name
    pretty_name = pretty_var_name(var, ds_case2, ds_clim)

    # units (just try case first, otherwise clim)
    units = ""
    if var in ds_case2:
        units = ds_case2[var].attrs.get("units", "")
    elif var in ds_clim:
        units = ds_clim[var].attrs.get("units", "")

    # what field to actually plot (wspd special case)
    effective_field = field
    if field == "anomaly" and var == "wspd":
        effective_field = "case"

    if effective_field == "case":
        fld = ds_case2[var]
        mode_text = "CASE"
    elif effective_field == "clim":
        fld = ds_clim[var]
        mode_text = "CLIM"
    else:
        case_a, clim_a = xr.align(ds_case2[[var]], ds_clim[[var]], join="exact")
        fld = case_a[var] - clim_a[var]
        mode_text = "ANOMALY"

    # color scaling
    if mode_text == "ANOMALY":
        vmax = float(max(abs(fld.min()), abs(fld.max())))
        norm = Normalize(-vmax, vmax)
        cmap = "coolwarm"
    else:
        vmax = float(fld.max())
        norm = Normalize(0.0, vmax)
        cmap = "Blues" if var == "wspd" else "viridis"

    # extract 2D sections
    fld_lat = to_2d(fld.sel({LAT_DIM: lat}, method="nearest"))
    fld_lon = to_2d(fld.sel({LON_DIM: lon}, method="nearest"))

    lat_used = float(fld.sel({LAT_DIM: lat}, method="nearest")[LAT_DIM].values)
    lon_used = float(fld.sel({LON_DIM: lon}, method="nearest")[LON_DIM].values)

    # arrows (only for wspd; always from CASE)
    u = v = w = None
    if var == "wspd":
        for needed in (U_VAR, V_VAR, W_VAR):
            if needed not in ds_case2:
                raise KeyError(f"Case file missing '{needed}' required for wind arrows (wspd).")
        u = ds_case2[U_VAR]
        v = ds_case2[V_VAR]
        w = ds_case2[W_VAR]

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

    plot_panel_we(axes[0], fld_lat, z_lat, lon_used, lat_used, norm, cmap, cb_label, u, w, terr_we)
    plot_panel_sn(axes[1], fld_lon, z_lon, lat_used, lon_used, norm, cmap, cb_label, v, w, terr_sn)

    if savepath is not None:
        fig.savefig(savepath, dpi=180)
        plt.close(fig)

    ds_case.close()
    ds_clim_all.close()
    return fig


# -------------------------
# helpers (no underscores)
# -------------------------

def drop_time(ds):
    """Drop time dimension (valid_time or time) if present."""
    if "valid_time" in ds.dims:
        return ds.isel(valid_time=0).squeeze(drop=True)
    if "time" in ds.dims:
        return ds.isel(time=0).squeeze(drop=True)
    return ds


def get_case_month_year(ds_case):
    """Return (month, year) from valid_time or time coordinate."""
    if "valid_time" in ds_case.coords:
        t = ds_case["valid_time"]
    elif "time" in ds_case.coords:
        t = ds_case["time"]
    else:
        raise KeyError("Case dataset has no 'valid_time' or 'time' coordinate.")
    t0 = t.values[0] if t.size > 0 else t.values
    dt = xr.DataArray(t0).dt
    return int(dt.month.values), int(dt.year.values)


def pretty_var_name(var, ds_case2, ds_clim):
    """Try to build: 'var – long_name'. Fallback: just var."""
    long_name = ""
    if var in ds_case2:
        long_name = ds_case2[var].attrs.get("long_name") or ds_case2[var].attrs.get("standard_name") or ""
    if (not long_name) and (var in ds_clim):
        long_name = ds_clim[var].attrs.get("long_name") or ds_clim[var].attrs.get("standard_name") or ""
    return f"{var} – {long_name}" if long_name else var


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


def add_quiver(ax, xdim, horiz, vert):
    """Add wind arrows from horiz (=u or v) and vert (=w)."""
    hq = horiz.isel({xdim: slice(None, None, QUIVER_X_SKIP),
                    LEVEL_DIM: slice(None, None, QUIVER_Y_SKIP)})
    vq = vert.isel({xdim: slice(None, None, QUIVER_X_SKIP),
                    LEVEL_DIM: slice(None, None, QUIVER_Y_SKIP)})

    X, Y = xr.broadcast(hq[xdim], hq[LEVEL_DIM])
    U = hq.values
    V = (vq / 100.0 * W_EXAG).values  # Pa/s -> hPa/s and exaggerate

    ax.quiver(
        X.values, Y.values, U, V,
        angles="xy", scale_units="xy", scale=QUIVER_SCALE,
        width=0.0035, headwidth=4.8, headlength=6.2, headaxislength=5.5, alpha=0.9,
    )


def height_to_pressure_hpa(z_m):
    """
    Convert height (m) to approximate pressure (hPa) using standard atmosphere.
    Only used for the terrain mask in pressure coordinates.
    """
    T0 = 288.15
    L = 0.0065
    g = 9.80665
    M = 0.0289644
    R = 8.3144598
    p0 = 100000.0  # Pa

    z = np.maximum(z_m, 0.0)
    exponent = (g * M) / (R * L)
    p_pa = p0 * (1.0 - (L * z / T0)) ** exponent
    return p_pa / 100.0  # hPa


def load_terrain_lines(terrainfile, lat_used, lon_used):
    """
    Load terrain and return two 1D lines in pressure (hPa):
      - W–E: p_sfc(lon) at fixed latitude
      - S–N: p_sfc(lat) at fixed longitude
    """
    ds_terr = xr.open_dataset(terrainfile)
    ds_terr2 = drop_time(ds_terr)

    if TERRAIN_VAR not in ds_terr2:
        ds_terr.close()
        raise KeyError(f"Terrain file does not contain variable '{TERRAIN_VAR}'.")

    terr_m = ds_terr2[TERRAIN_VAR]

    terr_we_m = to_2d(terr_m.sel({LAT_DIM: lat_used}, method="nearest"))
    terr_sn_m = to_2d(terr_m.sel({LON_DIM: lon_used}, method="nearest"))

    terr_we_p = xr.DataArray(
        height_to_pressure_hpa(terr_we_m.values),
        coords={LON_DIM: terr_we_m[LON_DIM]},
        dims=(LON_DIM,),
    )
    terr_sn_p = xr.DataArray(
        height_to_pressure_hpa(terr_sn_m.values),
        coords={LAT_DIM: terr_sn_m[LAT_DIM]},
        dims=(LAT_DIM,),
    )

    ds_terr.close()
    return terr_we_p, terr_sn_p


def mask_terrain_white(ax, x1d, p_sfc_hpa):
    """Fill below the terrain with white (ground mask)."""
    ymin, ymax = ax.get_ylim()
    pmax = max(ymin, ymax)  # bottom (largest pressure)
    ax.fill_between(x1d.values, p_sfc_hpa.values, pmax, color="white", zorder=10)


def plot_panel_we(ax, fld2d, z2d, lon_used, lat_used, norm, cmap, cb_label, u, w, terrain_line):
    x = fld2d[LON_DIM]
    y = fld2d[LEVEL_DIM]

    add_background(ax, x, y, z2d)
    cf = ax.contourf(x, y, fld2d, levels=NLEVELS_FILL, cmap=cmap, norm=norm)

    if u is not None and w is not None:
        u2 = to_2d(u.sel({LAT_DIM: lat_used}, method="nearest"))
        w2 = to_2d(w.sel({LAT_DIM: lat_used}, method="nearest"))
        add_quiver(ax, LON_DIM, u2, w2)

    ax.invert_yaxis()

    if terrain_line is not None:
        mask_terrain_white(ax, x, terrain_line)
        ax.plot(terrain_line[LON_DIM], terrain_line.values, color="k", linewidth=1.3, zorder=11)

    ax.axvline(lon_used, color="k", linestyle=":", linewidth=1.1, alpha=0.7)
    ax.set_title(f"W–E at {LAT_DIM}≈{lat_used:.2f}")
    ax.set_xlabel(LON_DIM)
    ax.set_ylabel(LEVEL_DIM)
    add_colorbar(ax.figure, ax, cf, cb_label)


def plot_panel_sn(ax, fld2d, z2d, lat_used, lon_used, norm, cmap, cb_label, v, w, terrain_line):
    x = fld2d[LAT_DIM]
    y = fld2d[LEVEL_DIM]

    add_background(ax, x, y, z2d)
    cf = ax.contourf(x, y, fld2d, levels=NLEVELS_FILL, cmap=cmap, norm=norm)

    if v is not None and w is not None:
        v2 = to_2d(v.sel({LON_DIM: lon_used}, method="nearest"))
        w2 = to_2d(w.sel({LON_DIM: lon_used}, method="nearest"))
        add_quiver(ax, LAT_DIM, v2, w2)

    ax.invert_yaxis()

    if terrain_line is not None:
        mask_terrain_white(ax, x, terrain_line)
        ax.plot(terrain_line[LAT_DIM], terrain_line.values, color="k", linewidth=1.3, zorder=11)

    ax.axvline(lat_used, color="k", linestyle=":", linewidth=1.1, alpha=0.7)
    ax.set_title(f"S–N at {LON_DIM}≈{lon_used:.2f}")
    ax.set_xlabel(LAT_DIM)
    ax.set_ylabel(LEVEL_DIM)
    add_colorbar(ax.figure, ax, cf, cb_label)
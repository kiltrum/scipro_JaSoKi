"""
Helper functions for ERA5 cross-section plotting.

Contents
--------
- Dataset utilities: drop_time, get_case_month_year, to_2d
- Metadata helpers: pretty_var_name
- Plotting helpers: background, colorbar, quiver, terrain masking
- Panel plotting: W–E and S–N cross-sections

Notes
-----
- Assumes ERA5-style dimensions (pressure_level, latitude, longitude).
- Terrain is provided in pressure coordinates (hPa).
- Wind arrows are horizontal only (u or v; vertical set to zero).
"""

from __future__ import annotations

import numpy as np
import xarray as xr

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
    """
    Drops single dimensions so that
    """
    return da.squeeze(drop=True)


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


TERRAIN_VAR = "p_sfc"

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
"""

Created by Jakob Werkgarner, Jannuary 2026


Tests for required ERA5 input and output files.


- Required static data files exist.
- Required PNGs exist before HTML generation.
"""

from __future__ import annotations

from pathlib import Path


def test_required_data_files_exist():
    """
    Ensure that all mandatory static ERA5 input files are present.

    These files are required for climatology-based plotting and
    must exist before any analysis or visualization is performed.
    """
    # Resolve path of this test file
    here = Path(__file__).resolve()

    # Navigate to repository root (tests/ is nested several levels deep)
    repo_root = here.parents[3]

    # Base directory containing static ERA5 data files
    base = repo_root / "era5vis-main" / "era5vis" / "data"

    # List of required static NetCDF input files
    required_files = [
        base / "model_clim.nc",            # ERA5 model climatology
        base / "model_topo_pressure.nc",   # Model topography on pressure levels
    ]

    # Check that each required file exists
    for file in required_files:
        assert file.exists(), f"Missing required file: {file}"


# List of PNG files that must be generated before HTML output
REQUIRED_PNGS = [
    "ERA5_crosssection.png",
    "ERA5_map_anomaly.png",
    "ERA5_sounding.png",
]


def test_required_pngs_exist_before_html():
    """
    Verify that all expected plot images are created before HTML generation.

    This ensures that the plotting pipeline completed successfully
    and that the HTML report will not reference missing figures.
    """
    # Resolve path of this test file
    here = Path(__file__).resolve()

    # Navigate to repository root
    repo_root = here.parents[3]

    # Directory where generated PNGs are stored
    tmp_png = repo_root / "era5vis-main" / "tmp_png"

    # Ensure the output directory exists
    assert tmp_png.is_dir(), f"Missing output directory: {tmp_png}"

    # Identify any required PNGs that are missing
    missing = [name for name in REQUIRED_PNGS if not (tmp_png / name).is_file()]

    # Fail test if any expected figures are missing
    assert not missing, (
        f"Missing required PNG(s): {', '.join(missing)} "
        f"(looked in {tmp_png})"
    )
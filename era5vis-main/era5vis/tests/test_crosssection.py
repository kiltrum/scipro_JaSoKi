"""
Tests for required ERA5 input and output files.

- Required static data files exist.
- Required PNGs exist before HTML generation.
"""

from __future__ import annotations

from pathlib import Path


def test_required_data_files_exist():
    here = Path(__file__).resolve()
    repo_root = here.parents[3]  # tests/ is inside era5vis-main/era5vis/tests
    base = repo_root / "era5vis-main" / "era5vis" / "data"

    required_files = [
        base / "model_clim.nc",
        base / "model_topo_pressure.nc",
    ]

    for file in required_files:
        assert file.exists(), f"Missing required file: {file}"


REQUIRED_PNGS = [
    "ERA5_crosssection.png",
    "ERA5_map_anomaly.png",
    "ERA5_sounding.png",
]


def test_required_pngs_exist_before_html():
    here = Path(__file__).resolve()
    repo_root = here.parents[3]
    tmp_png = repo_root / "era5vis-main" / "tmp_png"

    assert tmp_png.is_dir(), f"Missing output directory: {tmp_png}"

    missing = [name for name in REQUIRED_PNGS if not (tmp_png / name).is_file()]
    assert not missing, f"Missing required PNG(s): {', '.join(missing)} (looked in {tmp_png})"
from pathlib import Path


def test_plot_map_anomaly_required_files_exist():
    here = Path(__file__).resolve()
    repo_root = here.parents[2]   # ggf. anpassen
    base = repo_root / "era5vis" / "data"

    required_files = [
        base / "model_clim.nc",
    ]

    for file in required_files:
        assert file.exists(), f"Missing required file: {file}"

"""
Tests for Plot_map_anomaly
"""

from pathlib import Path
import matplotlib.pyplot as plt
import pytest

from era5vis.Plot_map_anomaly import Plot_map_anomaly


def test_plot_map_anomaly_creates_png(
    era5_test_file,
    monkeypatch,
    tmp_path,
):
    pytest.importorskip("cartopy")

    # GUI unterdrücken
    monkeypatch.setattr(plt, "show", lambda: None)

    # Output in temp dir
    monkeypatch.chdir(tmp_path)

    fname = Plot_map_anomaly(
        pathfile=era5_test_file,
        param="t",
        pressure_level=500,
        lat_pt=50,
        lon_pt=10,
    )

    outpath = Path("tmp_png") / fname

    assert outpath.exists()
    assert outpath.stat().st_size > 0

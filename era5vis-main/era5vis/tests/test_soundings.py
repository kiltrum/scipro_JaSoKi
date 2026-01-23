from pathlib import Path
import matplotlib.pyplot as plt
import pytest
from era5vis.Soundings import plot_sounding

"""
Test if function is plot_soundings running and creates a PNG file
"""
def test_plot_sounding_creates_png(
    era5_test_file,
    monkeypatch,
    tmp_path,
):
    pytest.importorskip("cartopy")
    pytest.importorskip("metpy")
    monkeypatch.setattr(plt, "show", lambda: None)

    # Output in temp dir
    monkeypatch.chdir(tmp_path)

    fname = plot_sounding(
        pathfile=era5_test_file,
        lat_pt=50,
        lon_pt=10,
    )

    outpath = Path("PNG") / fname

    assert outpath.exists()
    assert outpath.stat().st_size > 0

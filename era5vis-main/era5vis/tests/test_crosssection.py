from pathlib import Path


def test_required_data_files_exist():
    """Check that required data files are present in the repository."""

    base = Path("era5vis/data")

    required_files = [
        base / "model_clim" / "model_clim.nc",
        base / "model_terrain" / "DEM.nc",
        base / "tmp" / "test_tmp_with_wind.nc",
    ]

    for file in required_files:
        assert file.exists(), f"Missing required file: {file}"
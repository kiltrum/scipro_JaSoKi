from pathlib import Path

def test_required_data_files_exist():
    here = Path(__file__).resolve()
    repo_root = here.parents[2]        # adjust if needed
    base = repo_root / "era5vis" / "data"

    required_files = [
        base / "model_clim.nc",
        base / "model_topo_pressure.nc",
    ]

    for file in required_files:
        assert file.exists(), f"Missing required file: {file}"
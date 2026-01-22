#created and edited by Kilian
import os

def test_model_clim_exists():
    file_path = os.path.join(os.path.dirname(__file__), '../data/model_clim.nc')
    assert os.path.isfile(file_path), f"File not found: {file_path}"

def test_model_clim_dimensions():
    import xarray as xr
    file_path = os.path.join(os.path.dirname(__file__), '../data/model_clim.nc')
    ds = xr.open_dataset(file_path)
    expected_dims = {
        'month': 12,
        'pressure_level': 13,
        'latitude': 221,
        'longitude': 401
    }
    actual_dims = dict(ds.sizes)
    assert actual_dims == expected_dims, f"Expected dimensions {expected_dims}, got {actual_dims}"
    ds.close()

def test_model_clim_variables():
    import xarray as xr
    file_path = os.path.join(os.path.dirname(__file__), '../data/model_clim.nc')
    ds = xr.open_dataset(file_path)
    expected_vars = ['z', 'q', 'crwc', 't', 'u', 'v', 'wspd', 'wdir']
    actual_vars = list(ds.data_vars)
    for var in expected_vars:
        assert var in actual_vars, f"Variable '{var}' not found in dataset"
    ds.close()
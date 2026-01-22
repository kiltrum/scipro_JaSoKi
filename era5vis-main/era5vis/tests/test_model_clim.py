#created and edited by Kilian
import os

def test_model_clim_exists():
    file_path = os.path.join(os.path.dirname(__file__), '../data/model_clim.nc')
    assert os.path.isfile(file_path), f"File not found: {file_path}"

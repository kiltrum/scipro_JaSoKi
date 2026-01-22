#implemented by Kilian(with help from ChatGPT)

import os
import urllib.request

def download_model_clim():
    '''Downloads the model_clim.nc file if it does not exist.
     The file is downloaded from a Uibk fileshare and saved in the data directory.'''
    
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'era5vis', 'data')
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, 'model_clim.nc')
    url = 'https://fileshare.uibk.ac.at/d/c4c3ef46072448109590/files/?p=%2Fmodel_clim.nc&dl=1'
    if not os.path.isfile(file_path):
        print(f"Downloading model_clim.nc to {file_path}...")
        urllib.request.urlretrieve(url, file_path)
        print("Download complete.")
    else:
        print("model_clim.nc already exists at:", file_path)


def main():
    download_model_clim()
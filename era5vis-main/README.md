# A visualization package for ERA5 data

**era5vis** offers command line tools to display ERA5 data in your browser.

It was written for the University of Innsbruck's
[scientific programming](https://manuelalehner.github.io/scientific_programming)
course as a package template for the semester project and is based on the 
example packages [scispack](https://github.com/fmaussion/scispack) and
[climvis](https://github.com/fmaussion/climvis) written by
[Fabien Maussion](https://fabienmaussion.info).

It was edited and extended by Jakob, Kilian and Simon as their semester project.

## HowTo (edited by Kilian)

Make sure you have all dependencies installed. These are:
- numpy
- xarray
- netcdf4
- matplotlib
- pytest
- cdsapi
- cartopy
- metpy

Download the package and install it in development mode. In the root directory
type:

    $ pip install -e .

## Copernicus API setup (required) (edited by Kilian)

To download ERA5 data, you need a Copernicus Climate Data Store account.

Register at: https://cds.climate.copernicus.eu

Create an API key

Store your credentials in ~/.cdsapirc:

    $ url: https://cds.climate.copernicus.eu/api/v2
    $ key: <UID>:<API_KEY>

## Climate model data setup (requiered) (edited by Kilian)
After installing the package, run the following command in your terminal:

    $ era5vis_download_model_clim

This will automatically download the required model_clim.nc file and store it in the data folder (/era5vis-main/era5vis/data), if not yet present.This can take a while depending on your internet connection.

## Command line interface (edited by Kilian)

``setup.py`` defines an "entry point" for a script to be used as a
command line program.

After installation, just type

    $ era5vis_modellevel --help

or

    $ era5vis_clim --help

to see what the tools can do.

## Testing

I recommend to use [pytest](https://docs.pytest.org) for testing. To test
the package, run

    $ pytest .

in the package's root directory. If all tests pass, you should see something like

    $ ============== 18 passed, 1 warning in 4.57s =================


## Author Contributions

- **tests/test_model_clim.py** – Kilian
- **tests/test_api.py** – Kilian
- **init_download_model_clim.py** – Kilian
- **download_era5.py** – Kilian
- **README.md** – Mainly adapted by Kilian
- **Plot_map_anomaly** - Simon
- **Soundgings** - Simon
- **cli.py** – Mainly written by Kilian; edited by Jakob and Simon
- **build_html.py** – First draft by Simon; current version by Jakob  
- **helpers.py** – Jakob  
- **helpers_crosssection.py** – Jakob  
- **graphics.py** – Original package authors; `plot_crosssection` added by Jakob


## License

With the exception of the ``setup.py`` file, which was adapted from the
[sampleproject](https://github.com/pypa/sampleproject) package, all the
code in this repository is dedicated to the public domain.

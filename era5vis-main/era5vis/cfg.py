""" Configuration module containing settings and constants. """

from pathlib import Path

datafile = '/home/kili/Dokumente/MA/program/project/era5_example_dataset.nc'

# location of data directory containing html template
pkgdir = Path(__file__).parents[0]
html_template = Path(pkgdir) / 'data' / 'template.html'
""" Configuration module containing settings and constants. """

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
datafile = BASE_DIR / "era5_example_dataset.nc"
#datafile = r"C:\Users\User\Documents\Master\Scientific programming\Project\scipro_JaSoKi\era5_example_dataset.nc"
# location of data directory containing html template
pkgdir = Path(__file__).parents[0]
html_template = Path(pkgdir) / 'data' / 'template.html'
#Pressure level 3 hPa not found in dataset. Available levels: [925. 850. 700. 500. 300.]
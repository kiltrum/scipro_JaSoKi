from pathlib import Path
import cdsapi

# Fixed configuration
VARIABLES = [
    'geopotential',
    'specific_humidity',
    'specific_rain_water_content',
    'temperature',
    'u_component_of_wind',
    'v_component_of_wind'
]
PRESSURE_LEVELS = ['1000', '950', '900', '850', '800', '750', '700', '600', '500', '400', '300', '200', '100']
AREA = [90, -55, 35, 35]  # [North, West, South, East]
TIME = "00:00"
TARGET = Path("./era5_data.nc")


def download_era5(year: str, month: str, day: str) -> Path:
    """
    Download ERA5 pressure level data from the Copernicus Climate Data Store.

    Args:
        year: Year to download (e.g., "2024").
        month: Month to download (e.g., "03").
        day: Day to download (e.g., "01").

    Returns:
        Path to the downloaded NetCDF file.
    """
    request = {
        'product_type': ['reanalysis'],
        'variable': VARIABLES,
        'year': [year],
        'month': [month],
        'day': [day],
        'time': [TIME],
        'pressure_level': PRESSURE_LEVELS,
        'data_format': 'netcdf',
        'area': AREA,
    }

    client = cdsapi.Client()
    client.retrieve('reanalysis-era5-pressure-levels', request, TARGET)

    return TARGET


if __name__ == "__main__":
    download_era5(year="2024", month="03", day="01")
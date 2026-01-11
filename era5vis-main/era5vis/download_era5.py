#This file was created by Kilian

from pathlib import Path
import cdsapi

# Month name to number mapping (English and German) and therefore allow more input options
MONTH_NAMES = {
    # English
    'january': '01', 'february': '02', 'march': '03', 'april': '04',
    'may': '05', 'june': '06', 'july': '07', 'august': '08',
    'september': '09', 'october': '10', 'november': '11', 'december': '12',
    # English short
    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
    'jun': '06', 'jul': '07', 'aug': '08',
    'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
    # German
    'januar': '01', 'februar': '02', 'märz': '03', 'maerz': '03',
    'mai': '05', 'juni': '06', 'juli': '07',
    'oktober': '10', 'dezember': '12',
}


def parse_month(month_input: str) -> str:
    """Convert month name or number to two-digit month string.
    
    Args:
        month_input: Month as name (e.g., 'January', 'Mai') or number (e.g., '3', '03')
    
    Returns:
        Two-digit month string (e.g., '01', '03', '12')
    
    Raises:
        ValueError: If month cannot be parsed
    """
    # Try as number first
    try:
        month_num = int(month_input)
        if 1 <= month_num <= 12:
            return f'{month_num:02d}'
        else:
            raise ValueError(f"Month number must be 1-12, got {month_num}")
    except ValueError:
        pass
    
    # Try as month name
    month_lower = month_input.lower()
    if month_lower in MONTH_NAMES:
        return MONTH_NAMES[month_lower]
    
    raise ValueError(
        f"Could not parse month '{month_input}'. "
        "Use a number (1-12) or name (e.g., 'January', 'März')."
    )


# Fixed variables and "settings"
DATASET = 'reanalysis-era5-pressure-levels-monthly-means'
PRODUCT_TYPE = 'monthly_averaged_reanalysis_by_hour_of_day'
VARIABLES = [
    'geopotential',
    'specific_humidity',
    'specific_rain_water_content',
    'temperature',
    'u_component_of_wind',
    'v_component_of_wind'
]
PRESSURE_LEVELS = ['1000', '950', '900', '850', '800', '750',
                   '700', '600', '500', '400', '300', '200', '100']
AREA = [90, -55, 35, 35]  # [North, West, South, East]
TIME = "00:00"
TARGET = Path("./era5_data.nc")


def download_era5(year: str, month: str) -> Path:
    """
    Download ERA5 monthly mean pressure level data from the Copernicus Climate Data Store.
    The the fixed variables and configurations are defined above the function definition 

    Args:
        year: Year to download (e.g., "2024").
        month: Month to download (e.g., "03").

    Returns:
        Path to the downloaded NetCDF file.
    """
    request = {
        'product_type': [PRODUCT_TYPE],
        'variable': VARIABLES,
        'year': [year],
        'month': [month],
        'time': [TIME],
        'pressure_level': PRESSURE_LEVELS,
        'data_format': 'netcdf',
        'area': AREA,
    }

    client = cdsapi.Client()
    client.retrieve(DATASET, request, TARGET)

    return TARGET


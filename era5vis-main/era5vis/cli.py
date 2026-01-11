""" contains command line tools of ERA5vis

Manuela Lehner
November 2025

Modified by Kilian Trummer Jannuary 2026
"""

import sys
import webbrowser
import era5vis

HELP = """era5vis_modellevel: Visualization of ERA5 at a given model level.

Usage:
   -h, --help                       : print the help
   -v, --version                    : print the installed version
   -p, --parameter [PARAM]          : ERA5 variable to plot, mandatory
   -lvl, --level [LEVEL]            : pressure level to plot (hPa), mandatory
   -t, --time [TIME]                : time to plot (YYYYmmddHHMM)
   -ti, --time_index [TIME_IND]     : time index within dataset to plot (--time takes 
                                      precedence of both --time and --time_index are specified
                                      (default=0)
   --no-browser                     : the default behavior is to open a browser with the
                                      newly generated visualisation. Set to ignore
                                      and print the path to the html file instead
"""


def modellevel(args):
    """The actual era5vis_modellevel command line tool.

    Parameters
    ----------
    args: list
        output of sys.args[1:]
    """

    if '--parameter' in args:
        args[args.index('--parameter')] = '-p'
    if '--level' in args:
        args[args.index('--level')] = '-lvl'
    if '--time' in args:
        args[args.index('--time')] = '-t'
    if '--time_index' in args:
        args[args.index('--time_index')] = '-ti'

    if len(args) == 0:
        print(HELP)
    elif args[0] in ['-h', '--help']:
        print(HELP)
    elif args[0] in ['-v', '--version']:
        print('era5vis_modellevel: ' + era5vis.__version__)
        print('Licence: public domain')
        print('era5vis_modellevel is provided "as is", without warranty of any kind')
    # parameter and level must be provided, time/time_ind are optional
    elif ('-p' in args) and ('-lvl' in args):
        param = args[args.index('-p') + 1]
        level = int(args[args.index('-lvl') + 1])
        if ('-t' in args):
            time = args[args.index('-t') + 1]
            html_path = era5vis.write_html(param, level=level, time=time)
        elif ('-ti' in args):
            time = int(args[args.index('-ti') + 1])
            html_path = era5vis.write_html(param, level=level, time_ind=time)
        else:
            print('No time provided, using default (first time in the file)')
            html_path = era5vis.write_html(param, level=level, time_ind=0)
        if '--no-browser' in args:
            print('File successfully generated at: ' + str(html_path))
        else:
            webbrowser.get().open_new_tab('file://' + str(html_path))
    else:
        print('era5vis_modellevel: command not understood. '
              'Type "era5vis_modellevel --help" for usage information.')


def era5vis_modellevel():
    """Entry point for the era5vis_modellevel application script"""
    modellevel(sys.argv[1:])


HELP_CLIM = """era5vis_clim: Download and visualize ERA5 monthly mean climatology data.

Usage:
   -h, --help                       : print the help
   -v, --version                    : print the installed version
   -y, --year [YEAR]                : year to download (e.g., 2024), mandatory
   -m, --month [MONTH]              : month to download (e.g., 03), mandatory
   -p, --parameter [PARAM]          : ERA5 variable to plot
   -lvl, --level [LEVEL]            : pressure level to plot (hPa)
   --no-browser                     : the default behavior is to open a browser with the
                                      newly generated visualisation. Set to ignore
                                      and print the path to the html file instead
"""


def clim(args):
    """The actual era5vis_clim command line tool.

    Parameters
    ----------
    args: list
        output of sys.args[1:]
    """
    from era5vis.download_era5 import download_era5, parse_month

    if '--year' in args:
        args[args.index('--year')] = '-y'
    if '--month' in args:
        args[args.index('--month')] = '-m'
    if '--parameter' in args:
        args[args.index('--parameter')] = '-p'
    if '--level' in args:
        args[args.index('--level')] = '-lvl'

    if len(args) == 0:
        print(HELP_CLIM)
    elif args[0] in ['-h', '--help']:
        print(HELP_CLIM)
    elif args[0] in ['-v', '--version']:
        print('era5vis_clim: ' + era5vis.__version__)
        print('Licence: public domain')
        print('era5vis_clim is provided "as is", without warranty of any kind')
    elif ('-y' in args) and ('-m' in args):
        year = args[args.index('-y') + 1]  # getting the year from user input
        month_input = args[args.index('-m') + 1]  # getting the month from user input
        
        # Convert month name to number if needed
        try:
            month = parse_month(month_input)
        except ValueError as e:
            print(f'Error: {e}')
            return
        
        # Download the data 
        print(f'Downloading ERA5 monthly mean data for {year}-{month}...')
        filepath = download_era5(year=year, month=month)
        print(f'Data downloaded to: {filepath}')
    
    else:
        print('era5vis_clim: command not understood. '
              'Type "era5vis_clim --help" for usage information.')


def era5vis_clim():
    """Entry point for the era5vis_clim application script"""
    clim(sys.argv[1:])

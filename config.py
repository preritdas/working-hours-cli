"""
Read the config.ini and parse values into their appropriate types.
"""
# Local imports
import configparser
import os  # join paths
import datetime as dt

# Project modules
import keys


# Initialize config
class Config:
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    config.read(config_path)

    dt_format = config['General']['dt_format']

    # Show most recent tasks at the top or at the bottom. Influences _reorder_dicts
    if config['General']['most_recent_bottom'].lower() == 'false':
        reverse_sort = True
    else:
        reverse_sort = False

    # Colors
    colors = {key: color for key, color in config['Colors'].items()}

    # Ideal order
    ideal_order = config['General']['column_order'].split(',')

    # Center table?
    if config['General']['center_table'].lower() == 'true':
        center_table = True
    else:
        center_table = False

    # Database name by month
    db_basename = config['General']['database_name']
    month, year = dt.datetime.now().month, dt.datetime.now().year
    current_db = db_basename + f"_{month}_{year}"

    # Report
    report_font = config['Report']['font']
    report_char_cutoff = int(config['Report']['char_length_cutoff'])

    # Smart capitalization - RapidAPI
    smart_cap_preference = config['General']['smart_capitalization'].lower()
    if smart_cap_preference == 'true' and not keys.RapidAPI.api_key:
        raise Exception(
            "If you have smart capitalization enabled, you must "
            "provide your RapidAPI API key and subscribe to the "
            "Capitalize My Title app, as documented in the README."
        )
    smart_cap_preference = True if smart_cap_preference == 'true' else False
    
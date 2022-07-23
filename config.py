import configparser
import os  # join paths
import datetime as dt


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

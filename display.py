# Non-local imports
from rich.table import Table
from rich.console import Console; console = Console()

# Local imports
from datetime import datetime as dt

# Project modules
from config import Config 


def _reorder_dicts(tasks: dict | list[dict]) -> list[dict]:
    """`tasks` can be a single dict or list of dicts."""
    if isinstance(tasks, dict):
        tasks = [tasks]
    
    # Sort the list by date
    dates = [(idx, dt.strptime(task["Date"], Config.dt_format)) for idx, task in enumerate(tasks)]
    sorted_dates = sorted(dates, key=lambda x: x[1], reverse=Config.reverse_sort)
    sorted_idx = (tup[0] for tup in sorted_dates)

    # Store the results
    new_tasks = []
    for idx in sorted_idx:
        new_tasks.append(tasks[idx])

    tasks = new_tasks  # overwrite the old tasks

    # Reorder keys in all the dicts
    return_tasks = []
    for task in tasks:
        # Check that it has all the keys
        if any([True for key in Config.ideal_order if key not in task]):
            return_tasks.append(task)
            continue

        return_tasks.append({k: task[k] for k in Config.ideal_order}) 

    return return_tasks


def display_tasks(tasks: dict | list[dict]):
    """Uses rich to print a table."""
    full_log_title = True
    if isinstance(tasks, dict):
        tasks = [tasks]
        full_log_title = False

    # Re-order tasks
    tasks = _reorder_dicts(tasks)

    if not tasks[0]:
        console.print("Empty log.")
        return
    
    table = Table(title="Log of Working Hours" if full_log_title else "Single Task View")
    for key in tasks[0].keys():
        if key.lower() in Config.colors:  # color the columns
            color = Config.colors[key.lower()]
        else:
            color = 'white'

        table.add_column(key, style=color)
    
    for task in tasks:
        str_vals = (str(val) for val in task.values())
        table.add_row(*str_vals)
    
    console.print(table)

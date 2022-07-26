# Non-local imports
from rich.table import Table
from rich.console import Console; console = Console()

# Local imports
from datetime import datetime as dt

# Project modules
from config import Config 


def _reorder_dicts(tasks: dict | list[dict]) -> list[dict]:
    """
    `tasks` can be a single dict or list of dicts. But, regardless
    of whether a dict or list of dicts was passed, a list of dicts is returned.
    So, if you pass in a single dict, a list is returned containing one dict.
    """
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


def display_tasks(tasks: dict | list[dict], space_above: bool = True) -> None:
    """
    Uses rich to print a table of tasks. If `space_above` is not passed in as 
    `True`, doesn't prints a blank line before printing the table to provide room.

    Reads the first task in the list of tasks to determine what month is being displayed.
    """
    full_log_title = True
    if isinstance(tasks, dict):
        tasks = [tasks]
        full_log_title = False

    # Re-order tasks
    tasks = _reorder_dicts(tasks)

    if len(tasks) == 0:  # this should never actually trigger but just in case.
        return

    # Construct title with month and year
    if full_log_title:
        date = dt.strptime(tasks[0]['Date'], Config.dt_format)
        month, year = date.month, date.year
        title = f"Log of Working Hours for {month}-{year}"
    else:
        title = "Single Task View"
    
    table = Table(title=title)

    for key in tasks[0].keys():
        if key.lower() in Config.colors:  # color the columns
            color = Config.colors[key.lower()]
        else:
            color = 'white'

        table.add_column(key, style=color)
    
    for task in tasks:
        # Add emojis to none objects
        if not task['Hours']:
            task['Hours'] = ':clock1:'
        if not task['Deliverable']:
            task['Deliverable'] = ':x:'

        str_vals = (str(val) for val in task.values())
        table.add_row(*str_vals)
    
    # Display the results
    if space_above:
        console.print('')

    console.print(table, justify="center" if Config.center_table else "default")

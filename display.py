from rich.table import Table
from rich.console import Console

console = Console()

# Params
colors = {
    'Date': '#1C96BA',
    'Deliverable': '#EAE1C8',
    'Hours': '#3CBCC7',
    'Task': '#DFC39D',
    'key': '#0C73B2'
}

ideal_order = ['Date', 'Task', 'Hours', 'Deliverable', 'key']


def _reorder_dicts(tasks: dict | list[dict]):
    """`tasks` can be a single dict or list of dicts."""
    if isinstance(tasks, dict):
        tasks = [tasks]

    return_tasks = []
    for task in tasks:
        # Check that it has all the keys
        if any([True for key in ideal_order if key not in task]):
            return_tasks.append(task)
            continue

        return_tasks.append({k: task[k] for k in ideal_order}) 

    return return_tasks[0] if len(return_tasks) == 1 else return_tasks


def display_tasks(tasks: dict | list[dict]):
    """Uses rich to print a table."""
    if isinstance(tasks, dict):
        tasks = [tasks]

    # Re-order tasks
    tasks = _reorder_dicts(tasks)

    if not tasks[0]:
        console.print("Empty log.")
        return
    
    table = Table(title="Log of Working Hours")
    for key in tasks[0].keys():
        print("KEY", key)
        if key in colors:
            color = colors[key]
        else:
            color = 'white'

        table.add_column(key, style=color)
    
    for task in tasks:
        str_vals = (str(val) for val in task.values())
        table.add_row(*str_vals)
    
    console.print(table)

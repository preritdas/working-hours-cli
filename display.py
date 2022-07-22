from rich.table import Table
from rich.console import Console

console = Console()

def display_tasks(tasks: dict | list[dict]):
    if isinstance(tasks, dict):
        tasks = [tasks]

    if not tasks[0]:
        console.print("Empty log.")
        return
    
    table = Table()
    for key in tasks[0].keys():
        table.add_column(key)
    
    for task in tasks:
        str_vals = (str(val) for val in task.values())
        table.add_row(*str_vals)
    
    console.print(table)

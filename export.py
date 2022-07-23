# Non-local imports
import pandas as pd

# Local imports
import datetime as dt
import os


def export_tasks(tasks: list[dict]) -> str:
    """
    Takes a list of tasks (dicts) and exports them to a CSV.
    
    The resulting file is stored in the current working directory of the terminal.
    So, the user should be instructed to navigate to the output directory of choice
    using cd in their shell, and then execute the command using the CLI.
    """
    df = pd.DataFrame(tasks)

    month, year = dt.datetime.now().month, dt.datetime.now().year
    path = os.path.join(os.getcwd(), f"Work Log {month}-{year}.csv")
    df.to_csv(path)

    return path

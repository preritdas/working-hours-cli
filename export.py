# Non-local imports
import pandas as pd

# Local imports
import os

# Project modules
from config import Config
from pdfclass import PDF
from display import _reorder_dicts


def export_tasks(tasks: list[dict], monthyear: str) -> str:
    """
    Takes a list of tasks (dicts) and exports them to a CSV.

    `monthyear` is in the format 7-2022. This is provided by the user when
    invoking the export command from the CLI.
    
    The resulting file is stored in the current working directory of the terminal.
    So, the user should be instructed to navigate to the output directory of choice
    using cd in their shell, and then execute the command using the CLI.
    """
    # Remove key and convert everything to string and shorten long values
    tasks = _reorder_dicts(tasks)

    for task in tasks:
        del task['key']
    
    # Store CSV before changing values
    path = os.path.join(os.getcwd(), f"Work Log {monthyear}")
    pd.DataFrame(tasks).to_csv(path+'.csv')


    create_pdf(tasks, monthyear, path+'.pdf')

    return path


def create_pdf(tasks: list[dict], monthyear: str, path: str):
    """Testing."""
    data = [list(tasks[0].keys())]
    appendix_count = 0
    appendix = {}
    for task in tasks:
        # Stringify and shorten length items
        for key, val in task.items():
            str_val = str(val)
            if len(str_val) > 50:
                appendix_count += 1
                appendix[appendix_count] = str_val
                str_val = f"A{appendix_count}: " + str_val[:50] + '...'
            task[key] = str_val

        data.append(list(task.values()))


    pdf = PDF()
    pdf.add_page()
    pdf.set_font(Config.report_font, size=15)

    # Titles
    pdf.cell(200, 10, f"Log of Working Hours {monthyear}", align='C')
    pdf.ln()
    pdf.ln()

    # Body
    pdf.set_font("Times", size=11)

    pdf.cell(
        200, 
        10,
        f"The following is a report of all hours logged in the month of {monthyear}. "
    )
    pdf.ln()

    pdf.cell(
        200, 
        10, 
        "Any deliverables cut off for length reasons can be seen in full in the appendix."
    )
    pdf.ln()

    pdf.ln()
    pdf.create_table(data, "Hours Logged", cell_width='uneven')
    pdf.ln()

    # Deliverables appendix
    pdf.set_font(Config.report_font, size = 13)
    pdf.cell(
        200,
        10,
        "Appendix of Deliverables",
        align='L' 
    )
    pdf.ln()

    for idx, deliverable in appendix.items():
        pass
    

    pdf.output(path)

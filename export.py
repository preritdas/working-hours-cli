# Non-local imports
import pandas as pd

# Local imports
import os

# Project modules
from config import Config
from pdfclass import PDF
from display import _reorder_dicts
from bitly import bitly


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

        # Mark all unfinished tasks as 0 hours
        if not task['Hours']:
            task['Hours'] = 0
    
    # Store CSV before changing values
    path = os.path.join(os.getcwd(), f"Work Log {monthyear}")
    pd.DataFrame(tasks).to_csv(path+'.csv')


    create_pdf(tasks, monthyear, path+'.pdf')

    return path


def create_pdf(tasks: list[dict], monthyear: str, path: str):
    """
    Generate a full PDF report, shortening links with Bitly, 
    and including an appendix.
    """
    data = [list(tasks[0].keys())]
    appendix_count = 0
    appendix = {}
    hours_total = 0
    for task in tasks:
        # Stringify and shorten length items
        for key, val in task.items():
            if key == 'Hours':
                hours_total += val
            str_val = str(val)
            if len(str_val) > Config.report_char_cutoff:
                appendix_count += 1
                appendix[appendix_count] = str_val
                str_val = f"A{appendix_count}: " + str_val[:Config.report_char_cutoff] + '...'
            task[key] = str_val

        data.append(list(task.values()))


    pdf = PDF(format='letter')
    pdf.add_page()
    pdf.set_font(Config.report_font, size=16)

    # Titles
    pdf.cell(200, 10, txt=f"Log of Working Hours {monthyear}", align='C')
    pdf.ln()
    pdf.ln()

    # Body
    pdf.set_font("Times", size=11)

    pdf.cell(
        txt = (
            "The following is an automatically generated report of all hours logged "
            f"in the month of {monthyear}. "
        )
    )
    pdf.ln()

    pdf.cell(
        txt = "Any items cut off for lack of space can be seen in full in the appendix."
    )
    pdf.ln()

    pdf.ln()
    pdf.create_table(
        table_data = data, 
        title = f"Total Hours Logged: {hours_total:,.2f}",
        cell_width = [30, 50, 15, 93]
    )
    pdf.ln()

    # Deliverables appendix
    if appendix:
        pdf.set_font(Config.report_font, size = 14)
        pdf.cell(
            txt = "Appendix of Deliverables",
            align = 'L' 
        )
        pdf.ln()
        pdf.ln()

        pdf.set_font(Config.report_font, size = 10)

        pdf.cell(txt="Some of the following items have been interpreted as links.")
        pdf.cell(txt="They've been shortened below using bit.ly.")
        pdf.ln()
        pdf.ln()
        pdf.ln()

        pdf.set_font(Config.report_font, size = 11)
        # Links
        for idx, deliverable in appendix.items():
            pdf.cell(txt=f"Item A{idx}")

            if 'http' in deliverable:
                pdf.ln()
                pdf.cell(txt=bitly(deliverable))
            else:
                if len(deliverable) < 100:
                    pdf.ln()
                    pdf.cell(txt=deliverable)
                else:
                    pdf.set_font(Config.report_font, size = 9)
                    pdf.cell(txt="(The full deliverable is too long to be displayed. Part of it is shown below.)")
                    pdf.set_font(Config.report_font, size = 11)
                    pdf.ln()
                    pdf.cell(txt=deliverable[:100]+'...')

            pdf.ln()
            pdf.ln()

    pdf.output(path)

"""
Define the CLI.
"""
# Non-local imports
import typer # cli
import deta  # database 

# local imports
import datetime as dt  # current time and time calculations

# Project modules
import keys  # deta auth
from display import display_tasks, console  # printing tasks
from config import Config
from export import export_tasks  # exporting tasks to csv
import utils  # title capitalization

# Debugging with the Rich traceback
from rich import traceback; traceback.install()


# Deta
deta_client = deta.Deta(keys.Deta.project_key)
work_log = deta_client.Base(Config.current_db)


# Item types
database_types: dict[str, type] = {
    'Date': str,
    'Task': str,
    'Hours': float,
    'Deliverable': str,
    'key': str
}


# CLI
app = typer.Typer(
    name = "loghours",
    no_args_is_help = True,
    add_completion = False,
    help = (
        "A simple-to-use command-line interface built to remove the stress of logging "
        "working hours, keeping track of completed payable tasks, "
        "and referencing deliverables." 
    )
)


def _query_db(
    task: str = None, 
    key: str = None, 
    only_unfinished: bool = False,
    prioritize_undelivered: bool = False,
    prioritize_delivered: bool = False
) -> dict | bool:
    """
    Checks the database for an item matching the task name, the task title,
    or using the key directly if it's provided. 

    If there was an error finding the item due to an invalid task name or invalid key,
    prints the error using click. 

    If `prioritize_undelivered` is `True`, if there are multiple occurrences of the same 
    task name, but only one has no delivery, the single undelivered task will be 
    returned without causing an error. 

    Returns the item if it was found, or `False` if it wasn't, so functinos calling it
    can use `if not` syntax to determine if they should themselves `return`. 
    """
    # Ensure either task or only unfinished is given
    if not task and not only_unfinished and not key:
        raise Exception(
            "Neither task, only_unfinished, nor key were given. "
            "You must provide one of these for the database to be queried."
        )

    if prioritize_delivered and prioritize_undelivered:
        raise Exception(
            "You cannot prioritize both delivered and undelivered tasks."
        )

    # Key is given
    if key is not None:
        db_item = work_log.get(key)
        if not db_item:
            console.print(
                f"Invalid [{Config.colors['key']}]key[/{Config.colors['key']}]. "
                "Try again."
            )
            return False
        else:
            return db_item

    # Clockout - only find the single unfinished task
    if only_unfinished:
        items = work_log.fetch(
            {
                'Hours': None
            }
        ).items

        if len(items) == 1:
            return items[0]
        elif len(items) == 0:
            console.print("")
            console.print(
                f"There are no unfinished "
                f"[{Config.colors['task']}]items[/{Config.colors['task']}]."
            )
            console.print("")
            return False

    fetch_title = False
    items = work_log.fetch(
        {
            'Task': task
        }
    ).items

    # Try looking for tasks with title case
    if len(items) == 0:
        items = work_log.fetch(
            {
                'Task': utils.capitalize_title(task)
            }
        ).items
        fetch_title = True

    if len(items) == 0:  # if none were found after trying title case
        console.print("")
        console.print(
            "No items found. "
            f"Correct the [{Config.colors['task']}]query[/{Config.colors['task']}] "
            f"or specify the [{Config.colors['key']}]key[/{Config.colors['key']}]."
        )
        display_tasks(work_log.fetch().items)
        return False

    if len(items) > 1:
        if prioritize_undelivered:
            # Check if only one is undelivered
            query_undelivered = work_log.fetch(
                {
                    'Task': utils.capitalize_title(task) if fetch_title else task,
                    'Deliverable': None
                }
            ).items
            if len(query_undelivered) == 1:
                return query_undelivered[0]

        if prioritize_delivered:
            delivered_items = []
            for item in items:
                if item['Deliverable']:
                    delivered_items.append(item)
            if len(delivered_items) == 1:
                return delivered_items[0]

        console.print("")
        console.print(
            "Multiple items found. "
            f"Please specify the [{Config.colors['key']}]key[/{Config.colors['key']}]."
        )
        display_tasks(work_log.fetch().items)
        return False

    db_item = items[0]
    return db_item


@app.command()
def log():
    """Displays a full log of all work hours. Is this in?"""
    items = work_log.fetch().items
    if len(items) == 0:
        console.print("")
        console.print(
            f"No [{Config.colors['task']}]tasks[/{Config.colors['task']}] "
            "exist in the log yet."
        )
        console.print("")
        return

    display_tasks(items)


@app.command()
def clockin(
    task: str = typer.Argument(
        default = ...,
        help = "Name of the task you want to clock in."
    ), 
    hours: float = typer.Option(
        ...,
        help = "Log a completed task that took this many hours."
    ), 
    date: str = typer.Option(
        ...,
        help = "Force date. Use this is if you started but forgot to clock in."
    ), 
    titlecase: bool = typer.Option(
        ...,
        help = "Override auto titlecasing. Makes future reference harder."
    )
):
    """
    Create a new task and clock in. 

    If you provide `hours`, the task will be marked as completed with `hours` hours.
    The date will be set to `hours` hours before the current moment, as if you forgot to
    clock in then and are doing so after the fact.

    If you provide `date`, you will override the date calculations and forcibly 
    insert `date`. The only reason to do this is if you're working on a task currently
    and forgot to clock in when you started. You can clock in, pass in the properly 
    formatted date representing the time you started, and then clock out whenever 
    you're finished.

    If you set `titlecase` as `False`, it becomes harder to reference the task in 
    future commands. For example, if you create a task with the name "hEllo" and try 
    to execute `deliver "hello" "deliverable"`, you'll get an error. If "hEllo" was 
    instead automatically or manually set as "Hello", the previous command would work.
    """
    # If not explicitly false, use title case
    task = utils.capitalize_title(task) if titlecase else task

    # Check for multiple unfinished tasks
    tasks = work_log.fetch(
        {
            "Hours": None
        }
    ).items

    if len(tasks) > 0:
        console.print("")
        console.print(
            "You cannot start multiple unfinished "
            f"[{Config.colors['task']}]tasks[/{Config.colors['task']}]."
        )
        console.print("")
        return

    # Store the task
    if hours is None:
        console.print("")
        console.print(
            f"Clocking in and starting the clock. "
            f"Clockout with task "
            f"'[{Config.colors['task']}]{task}[/{Config.colors['task']}]' "
            "to close this task."
        )
    elif hours is not None and date is None:
        console.print("")
        console.print(
            f"Logging [{Config.colors['task']}]{task}[/{Config.colors['task']}] for "
            f"[{Config.colors['hours']}]{hours}[/{Config.colors['hours']}] hours, "
            f"starting [{Config.colors['hours']}]{hours}[/{Config.colors['hours']}] "
            "hours ago."
        )
    elif hours is not None and date is not None:
        console.print("")
        console.print(
            f"Logging [{Config.colors['task']}]{task}[/{Config.colors['task']}] for "
            f"[{Config.colors['hours']}]{hours}[/{Config.colors['hours']}] hours, "
            f"starting at [{Config.colors['date']}]{date}[/{Config.colors['date']}]. "
        )
    else:
        raise Exception("Don't know what to do in this case.")

    # Determine date
    if date is None:
        date = dt.datetime.now().strftime(Config.dt_format)

    # Push time backward if hours is given without a date
    if hours is not None and date is None:
        time_started = dt.datetime.now() - dt.timedelta(hours=hours)
        date = time_started.strftime(Config.dt_format)

    work_log.put(
        {
            "Date": date,
            "Task": task,
            "Hours": hours,
            "Deliverable": None
        }
    )

    console.print("")


@app.command()
def clockout(
    hours: float = typer.Option(
        ...,
        help = "Force the number of hours worked."
    ), 
    deliver: str = typer.Option(
        ...,
        help = "Add a deliverable item."
    ),
    key: str = typer.Option(
        ...,
        help = "Unique database key if prompted by CLI."
    ), 
):
    """
    Clock out of an unfinished task.

    Does not work on finished tasks; i.e. tasks with a finite `Hours` value. Therefore,
    does not accept a positional 'task' parameter like most other commands. This command
    can only be used to clock out of the single unfinished task, if it exists (you cannot 
    have multiple unfinished tasks in the log).

    Deliver a task directly while clocking out with --deliver. If you use --hours, the 
    `hours` value provided is used instead of a standard calculation involving the 
    current time.
    """
    db_task = _query_db(key=key, only_unfinished=True)
    if not db_task:
        return

    # Disallow if task has been completed
    if db_task['Hours'] is not None:
        console.print("")
        console.print(
            "You cannot clock out of a "
            f"[{Config.colors['task']}]task[/{Config.colors['task']}] "
            "that has already been completed."
        )
        return

    # Hours
    if hours is None:
        time_delta = (
            dt.datetime.now() - \
                dt.datetime.strptime(db_task['Date'], Config.dt_format)
        )
        hours_delta = time_delta.total_seconds() / 3600
        hours = round(hours_delta, 2)
    db_task['Hours'] = hours

    # Deliverable
    if deliver is not None:
        db_task['Deliverable'] = deliver

    console.print("")
    console.print(
        f"Clocking out of "
        f"[{Config.colors['task']}]{db_task['Task']}[/{Config.colors['task']}] "
        f"for [{Config.colors['hours']}]{hours}[/{Config.colors['hours']}] hours.")

    work_log.put(db_task)

    console.print("")


@app.command()
def pickup(
    task: str = typer.Argument(
        ...,
        help = "Name of the task you want to pick up."
    ), 
    key: str = typer.Option(
        ...,
        help = "Unique database key, if prompted by the CLI."
    )
):
    """
    Continue working on a pre-existing task.

    Finds a _completed_ task from the database, resets its date to `hours` hours ago,
    and removes its `hours` value to indicate that it's unfinished. That way you 
    can continue working and clock out as normal. The resulting behavior is that you 
    add on the extra time between when you picked up the task and when you 
    clock out again.
    """
    db_item = _query_db(task, key)
    if not db_item:
        return

    new_start = dt.datetime.now() - dt.timedelta(hours=db_item['Hours'])
    db_item['Date'] = new_start.strftime(Config.dt_format)
    db_item['Hours'] = None

    work_log.put(db_item)
    console.print("")
    console.print(
        f"Continuing work on "
        f"[{Config.colors['task']}]{db_item['Task']}[/{Config.colors['task']}]."
    )

    console.print("")


@app.command()
def removetask(key: str = typer.Argument(..., help="Task unique database key.")):
    """
    Removes task with `key`.
    
    You cannot remove tasks by name; only by key, for security.
    """
    task = _query_db("", key)
    if not task:
        return

    work_log.delete(key)
    console.print("")
    console.print(
        f"Removed task with key [{Config.colors['key']}]{key}[/{Config.colors['key']}]."
    )
    display_tasks(task)


@app.command()
def totalhours(payrate: float = typer.Option(..., help="Your hourly wage.")):
    """
    Calculates the total hours worked on all tasks.

    Proviate `payrate` to calculate your monthly pay.
    """
    tasks = work_log.fetch().items

    hours = 0
    for task in tasks:
        for key, val in task.items():
            if key == 'Hours' and val is not None:
                hours += val

    console.print("")
    console.print(
        f"You've worked a total of "
        f"[{Config.colors['hours']}]{hours:,.2f}[/{Config.colors['hours']}] hours "
        "this month."
    )
    if payrate is not None:
        console.print(
            f"Your work has earned you "
            f"[green]${(hours*payrate):,.2f}[/green]."  # no need to source config
        )

    console.print("")


@app.command()
def deliver(
    task: str = typer.Argument(
        ...,
        help = "Name of the task you wish to add a deliverable for."
    ), 
    item: str = typer.Argument(
        ...,
        help = "Note, result, reference, or link to the deliverable."
    ), 
    key: str = typer.Option(
        ...,
        help = "Unique database key, if prompted by the CLI."
    )
):
    """
    Stores a deliverable item after you've clocked out.

    Note that you don't technically have to clock out to add a deliverable.
    And, deliverables can also be added directly when clocking out. See clockout
    help to learn more.
    """
    db_item = _query_db(task, key, prioritize_undelivered=True)
    if not db_item:
        return

    db_item['Deliverable'] = item
    work_log.put(db_item)

    console.print("")
    console.print(
        f"Added deliverable "
        f"[{Config.colors['deliverable']}]{item}[/{Config.colors['deliverable']}] "
        f"to [{Config.colors['task']}]{db_item['Task']}[/{Config.colors['task']}]."
    )
    display_tasks(db_item)


@app.command()
def deliverable(
    task: str = typer.Argument(
        ...,
        help = "Name of the task whose deliverable you wish to view."
    ), 
    key: str = typer.Option(
        ...,
        help = "Unique database key, if prompted by the CLI."
    )
):
    """
    View a tasks's deliverable. 

    If the deliverable is determined to be a link, the link is automatically opened
    in your default browser.
    """
    db_item = _query_db(task, key, prioritize_delivered=True)
    if not db_item: return

    deliverable_item: str = db_item['Deliverable']

    if deliverable_item is None:
        console.print("")
        console.print(
            "There is no "
            f"[{Config.colors['deliverable']}]deliverable[/{Config.colors['deliverable']}] "
            "for "
            f"[{Config.colors['task']}]{task}[/{Config.colors['task']}]."
        )
        return

    console.print("")
    console.print(
        f"[{Config.colors['deliverable']}]{deliverable_item}"
        f"[/{Config.colors['deliverable']}]"  # end the rich color tag
    )
    console.print("")

    if "http" in deliverable_item:
        typer.launch(deliverable_item)


@app.command()
def previewmonth(
    monthyear: str = typer.Argument(
        ..., 
        help = "Month to preview, ex. '7-2022'."
    )
):
    """
    Displays all tasks of a given month. This is useful when previewing the 
    contents of an export before exporting to a PDF. 
    See the section on `export` (or run `export --help`) to learn more 
    about why you'd ever want to do that.

    Automatically generates an appendix of deliverables that were too long
    to be fully displayed in the list of tasks. If links were detected, they're 
    automatically shortened using bitly. Shortened links are then displayed
    in the appendix. 
    
    The required `monthyear` parameter takes the format "7-2022" where 
    7 is July and 2022 is the year. No leading zeroes here. 
    """
    # If user provides a leading 0
    if monthyear[0] == '0':
        monthyear = monthyear[1:]

    month, year = monthyear.split('-')
    items = deta_client.Base(Config.db_basename + f"_{month}_{year}").fetch().items

    if len(items) == 0:
        console.print("")
        console.print(f"No database was found for '{monthyear}'.")
        console.print("")
        return

    display_tasks(items)


@app.command()
def export(
    monthyear: str = typer.Argument(
        ..., 
        help = "Month to preview, ex. '7-2022'."
    )
):
    """
    Create a PDF report of the provided month's work log. This is useful for 
    exporting a report of all work completed once the month is over. 
    For example, it's August 1st and you'd like a report of all the work you 
    completed in July to send to your employer. 
    Execute `export 7-2022` and you will have a properly formatted PDF document 
    to forward on. Create a PDF report of the provided month's work log.
    
    Exports the provided month's tasks in PDF and CSV formats.
    The file is automatically stored in your current directory; i.e.
    where your terminal/shell is navigated upon executing the command.

    The required `monthyear` parameter takes the format "7-2022" where 
    7 is July and 2022 is the year. No leading zeroes here.

    Output files are automatically zipped together into a .zip archive called 
    "Work Log 7-2022.zip" if the month is July, 2022. This is a single file
    that can be forwarded to anyone. When unzipped, it contains all export files,
    including the PDF report and CSV full list of all logged tasks.
    """
    with console.status(f"Generating a report for {monthyear}."):
        # If user provides a leading 0
        if monthyear[0] == '0':
            monthyear = monthyear[1:]

        # Parse the input
        month, year = monthyear.split('-')

        db_lookup = Config.db_basename + f"_{month}_{year}"
        db = deta_client.Base(db_lookup)

        items = db.fetch().items
        if len(items) == 0:
            console.print("")
            console.print(f"No database was found for '{monthyear}'.")
            console.print("")
            return

        path = export_tasks(items, monthyear=monthyear)

    console.print(
        f"\nYour log has been exported to the current directory in PDF and CSV, "
        "and zipped format. "
    )
    console.print(
        f"'{path}.csv'\n'{path}.pdf'\n'{path}.zip'"
    )
    console.print("")


@app.command()
def modify(
    task: str = typer.Argument(
        ...,
        help = "Name of the task whose property you wish to modify."
    ), 
    item: str = typer.Argument(
        ...,
        help = "Name of the property you wish to modify, ex. 'task' or 'hours'."
    ), 
    value: str = typer.Argument(
        ...,
        help = "Value to which the property should be set."
    ), 
    key: str = typer.Option(
        ...,
        help = "Unique database key, if prompted by the CLI."
    )
):
    """
    Change an attribute of a logged item.

    Automatically tries to convert the value provided to the appropriate type,
    depending on the attribute. For example, if the user requests to change the
    'hours' attribute of an item, the value is automatically converted to a float.
    If this operation fails, the user is notified that their provided value is
    unacceptable.

    This command is only meant to be used to correct errors. To update the delivery
    of a task, it is much safer to use the `deliver` command.
    """
    item = utils.capitalize_title(item)
    try: value = float(value)
    except ValueError: pass

    task = _query_db(task, key)
    if not task:
        return

    # Check if the requested attribute is available
    if not item in database_types:
        console.print("")
        console.print(
            f"'{item}' is not a valid attribute of any "
            f"[{Config.colors['task']}]item[/{Config.colors['task']}] "
            "in the database."
        )
        console.print("")
        return

    # Check if the correct value type can be used
    if not isinstance(value, database_types[item]):
        try:
            value = database_types[item](value)
        except ValueError:
            console.print("")
            console.print(
                f"{value} is an unacceptable type for the attribute "
                f"'{item}'."
            )
            console.print("")
            return

    # Update the database
    task[item] = value
    work_log.put(task)

    # Report back to the user
    console.print("")
    console.print(
        f"The [{Config.colors['task']}]{task['Task']}[/{Config.colors['task']}] "
        f"'{item}' attribute has been set to "
        f"[{Config.colors['deliverable']}]{value}[/{Config.colors['deliverable']}]. "
    )
    console.print("")
    display_tasks(task)

# Non-local imports
import click  # cli
import deta  # database 

# local imports
import datetime as dt  # current time and time calculations
import webbrowser  # auto open deliverable links

# Project modules
import _keys  # deta auth
from display import display_tasks, console  # printing tasks
from config import Config
from export import export_tasks  # exporting tasks to csv


# Deta
deta_client = deta.Deta(_keys.Deta.project_key)
work_log = deta_client.Base(Config.current_db)


def _query_db(
    task: str, 
    key: str = None, 
    prioritize_unfinished: bool = False,
    prioritize_undelivered: bool = False
) -> dict | bool:
    """
    Checks the database for an item matching the task name, the task title,
    or using the key directly if it's provided. 

    If there was an error finding the item due to an invalid task name or invalid key,
    prints the error using click. 

    If `prioritize_unfinished` is `True`, if there are multiple occurrences of the same 
    task name, but only one is unfinsihed, the single unfinished task will be 
    returned without causing an error. The same is true for `allow_underlivered`,
    designed to enable prioritizing the delivery of the instance of duplicate tasks
    who has not yet been delivered. 

    `prioritize_unfinished` and `prioritize_undelivered` are mutually exclusive.

    Returns the item if it was found, or `False` if it wasn't, so functinos calling it
    can use `if not` syntax to determine if they should themselves `return`. 
    """
    # Ensure mutual exclusivity
    if prioritize_unfinished and prioritize_undelivered:
        raise Exception(
            "prioritize_unfinished and prioritize_undelivered are mutually exclusive. "
            "See docs to learn more."
        )

    if key is not None:
        db_item = work_log.get(key)
        if not db_item:
            click.echo("Invalid key. Try again.")
            return False
        else:
            return db_item

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
                'Task': task.title()
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
        if prioritize_unfinished:
            # Check if only one is unfinished
            query_unfinished = work_log.fetch(
                {
                    'Task': task.title() if fetch_title else task,
                    'Hours': None
                }
            ).items
            if len(query_unfinished) == 1:
                return query_unfinished[0]
        elif prioritize_undelivered:
            # Check if only one is undelivered
            query_undelivered = work_log.fetch(
                {
                    'Task': task.title() if fetch_title else task,
                    'Deliverable': None
                }
            ).items
            if len(query_undelivered) == 1:
                return query_undelivered[0]

        console.print("")
        console.print(
            "Multiple items found. "
            f"Please specify the [{Config.colors['key']}]key[/{Config.colors['key']}]."
        )
        display_tasks(work_log.fetch().items)
        return False

    db_item = items[0]

    return db_item


@click.group
def cli():
    pass


@click.command()
def log():
    """Displays a full log of all work hours."""
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


@click.command()
@click.argument("task", type=str)
@click.option(
    '--hours', 
    type = float, 
    help = "Log a completed task that took this many hours."
)
@click.option(
    '--date', 
    type = str, 
    help = "Force date. Use this is if you started but forgot to clock in."
)
@click.option(
    '--titlecase', 
    type = bool, 
    default = True, 
    help="Override auto titlecasing. Makes future reference harder."
)
def clockin(task: str, hours: float, date: str, titlecase: bool):
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
    task = task.title() if titlecase else task

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


@click.command()
@click.argument("task")
@click.option('--key', type=str, help="Unique database key if prompted by CLI.")
@click.option('--hours', type=float, help="Force the number of hours worked.")
@click.option('--deliver', type=str, help="Add a deliverable item.")
def clockout(task: str, key: str, hours: float, deliver: str):
    """
    Clock out of an unfinished task.

    Does not work on finished tasks; i.e. tasks with a finite `Hours` value.
    
    If you have multiple tasks of the same name, and only one of them is unfinished, 
    clocks out of the unfinished task. 

    Deliver a task directly while clocking out with --deliver. If you use --hours, the 
    `hours` value provided is used instead of a standard calculation involving the 
    current time.
    """
    db_task = _query_db(task, key, prioritize_unfinished=True)
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


@click.command()
@click.argument("task", type=str)
@click.option("--key", type=str, help="Unique database key for use if prompted by CLI.")
def pickup(task: str, key: str):
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


@click.command()
@click.argument("key", type=str)
def removetask(key):
    """Removes task with `key`."""
    task = _query_db("", key)
    if not task:
        return

    work_log.delete(key)
    console.print("")
    console.print(
        f"Removed task with key [{Config.colors['key']}]{key}[/{Config.colors['key']}]."
    )
    display_tasks(task)


@click.command()
@click.option('--payrate', type=float, help="Your hourly wage.")
def totalhours(payrate: float):
    """
    Calculates the total hours worked on all tasks.
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
        f"[{Config.colors['hours']}]{hours:,.2f}[/{Config.colors['hours']}] hours."
    )
    if payrate is not None:
        console.print(
            f"Your work has earned you "
            f"[green]${(hours*payrate):,.2f}[/green]."  # no need to source config
        )

    console.print("")


@click.command()
@click.argument("task", type=str)
@click.argument("item", type=str)
@click.option('--key', type=str, help="Unique database key for use if prompted by CLI.")
def deliver(task: str, item: str, key: str):
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


@click.command()
@click.argument("task", type=str)
@click.option('--key', type=str, help="Unique database key, for use if prompted by CLI.")
def deliverable(task: str, key: str):
    """
    View a tasks's deliverable. 

    If the deliverable is determined to be a link, the link is automatically opened
    in your default browser.
    """
    db_item = _query_db(task, key)
    if not db_item:
        return

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

    if 'http' in deliverable_item:
        webbrowser.open(deliverable_item)


@click.command()
@click.argument('monthyear', type=str)
def previewmonth(monthyear: str):
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
    7 is July and 2022 is the year. 
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


@click.command()
@click.argument('monthyear', type=str)
def export(monthyear: str):
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
    7 is July and 2022 is the year. 
    """
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
    console.print("")
    console.print(
        f"Your log has been exported to the current directory in PDF and CSV foramt. "
        f"See '{path}.csv' and '{path}.pdf'."
    )
    console.print("Execute 'ls' to view the contents of your current directory.")
    console.print(
        "Navigate to this directory in a file browser and "
        "open the CSV in Excel to view it properly formatted."
    )
    console.print("")


# Register the commands
cli.add_command(log)  # print log
cli.add_command(clockin)  
cli.add_command(clockout)
cli.add_command(pickup)  # continue finished tasks
cli.add_command(removetask)
cli.add_command(totalhours)
cli.add_command(deliver)  # add deliverable
cli.add_command(deliverable)  # view deliverable
cli.add_command(previewmonth)  # view the tasks of a given month's db
cli.add_command(export)  # exporting tasks


if __name__ == '__main__':
    cli()

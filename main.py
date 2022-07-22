# Non-local imports
import click  # cli
import deta  # database 

# local imports
import datetime as dt  # current time and time calculations
import pytz  # future - make timezone specific

# Project modules
import _keys  # deta auth
from display import display_tasks  # printing tasks


# Params
dt_format = '%Y-%m-%d %H-%M'
timezone = pytz.timezone('US/Eastern')  # doesn't do anything yet


# Deta
work_log = deta.Deta(_keys.Deta.project_key).Base('work_log')


def _query_db(task: str, key: str = None, allow_unfinished: bool = True) -> dict | bool:
    """
    Checks the database for an item matching the task name, the task title,
    or using the key directly if it's provided. 

    If there was an error finding the item due to an invalid task name or invalid key,
    prints the error using click. 

    If `allow_unfinished` is `True`, if there are multiple occurrences of the same task name,
    but only one is unfinsihed, the single unfinished task will be returned without causing 
    an error.

    Returns the item if it was found, or `False` if it wasn't, so functinos calling it
    can use `if not` syntax to determine if they should themselves `return`. 
    """
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
        click.echo("No items found. Correct the query or specify the key.")
        display_tasks(work_log.fetch().items)
        return False

    if len(items) > 1:
        if allow_unfinished:
            # Check if only one is unfinished
            query_unfinished = work_log.fetch(
                {
                    'Task': task.title() if fetch_title else task,
                    'Hours': None
                }
            ).items
            if len(query_unfinished) == 1:
                return query_unfinished[0]

        click.echo("Multiple items found. Please specify the key.")
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
    display_tasks(work_log.fetch().items)


@click.command()
@click.argument("task", type=str)
@click.option('--hours', type=float, help="Log a completed task that took this many hours.")
@click.option('--date', type=str, help="Force date. Use this is if you started but forgot to clock in.")
@click.option('--titlecase', type=bool, default=True, help="Override auto titlecasing. Makes future reference harder.")
def clockin(task: str, hours: float, date: str, titlecase: bool):
    """
    Create a new task and clock in. 

    If you provide `hours`, the task will be marked as completed with `hours` hours.
    The date will be set to `hours` hours before the current moment, as if you forgot to
    clock in then and are doing so after the fact.

    If you provide `date`, you will override the date calculations and forcibly insert `date`.
    The only reason to do this is if you're working on a task currently and forgot to clock in when
    you started. You can clock in, pass in the properly formatted date representing the time you started,
    and then clock out whenever you're finished.

    If you set `titlecase` as `False`, it becomes harder to reference the task in future commands. For example,
    if you create a task with the name "hEllo" and try to execute `deliver "hello" "deliverable"`, you'll get an error.
    If "hEllo" was instead automatically or manually set as "Hello", the previous command would work.
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
        click.echo("You cannot start multiple unfinished tasks.")
        return

    # Store the task
    if hours is None:
        click.echo(f"Clocking in and starting the clock. Clockout with task '{task}' to close this task.")
    else:
        click.echo(f"Logging {task} for {hours} hours, starting {hours} hours ago.")

    # Determine date
    if hours is not None and date is None:
        time_started = dt.datetime.now() - dt.timedelta(hours=hours)
        date = time_started.strftime(dt_format)
    else:
        date = dt.datetime.now().strftime(dt_format)


    work_log.put(
        {
            "Date": date,
            "Task": task,
            "Hours": hours,
            "Deliverable": None
        }
    )


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
    `hours` value provided is used instead of a standard calculation involving the current time.
    """
    db_task = _query_db(task, key, allow_unfinished=True)
    if not db_task:
        return

    # Disallow if task has been completed
    if db_task['Hours'] is not None:
        click.echo("You cannot clock out of a task that's been already completed.")
        return

    # Hours
    if hours is None:
        time_delta = dt.datetime.now() - dt.datetime.strptime(db_task['Date'], dt_format)
        hours_delta = time_delta.total_seconds() / 3600
        hours = round(hours_delta, 2)
    db_task['Hours'] = hours

    # Deliverable
    if deliver is not None:
        db_task['Deliverable'] = deliver

    click.echo(f"Clocking out of {db_task['Task']} for {hours} hours.")
    work_log.put(db_task)


@click.command()
@click.argument("task", type=str)
@click.option("--key", type=str, help="Unique database key, for use if prompted by CLI.")
def pickup(task: str, key: str):
    """
    Continue working on a pre-existing task.

    Finds a _completed_ task from the database, resets its date to `hours` hours ago,
    and removes its `hours` value to indicate that it's unfinished. That way you can continue
    working and clock out as normal. The resulting behavior is that you add on the extra time
    between when you picked up the task and when you clock out again.
    """
    db_item = _query_db(task, key)
    if not db_item:
        return

    new_start = dt.datetime.now() - dt.timedelta(hours=db_item['Hours'])
    db_item['Date'] = new_start.strftime(dt_format)
    db_item['Hours'] = None

    work_log.put(db_item)
    click.echo(f"Continuing work on {db_item['Task']}.")


@click.command()
@click.argument("key", type=str)
def removetask(key):
    """Removes task with `key`."""
    task = _query_db("", key)
    if not task:
        return

    work_log.delete(key)
    click.echo(f"Removed task with key {key}.")
    display_tasks(task)


@click.command()
def totalhours():
    """
    Calculates the total hours worked on all tasks.
    """
    tasks = work_log.fetch().items

    hours = 0
    for task in tasks:
        for key, val in task.items():
            if key == 'Hours' and val is not None:
                hours += val

    click.echo(f"You've worked a total of {hours} hours.")


@click.command()
@click.argument("task", type=str)
@click.argument("item", type=str)
@click.option('--key', type=str, help="Unique database key, for use if prompted by CLI.")
def deliver(task: str, item: str, key: str):
    """
    Stores a deliverable item after you've clocked out.

    Note that you don't technically have to clock out to add a deliverable.
    And, deliverables can also be added directly when clocking out. See clockout
    help to learn more.
    """
    db_item = _query_db(task, key)
    if not db_item:
        return

    db_item['Deliverable'] = item

    work_log.put(db_item)
    click.echo(f"Added deliverable {item} to {db_item['Task']}.")
    display_tasks(db_item)


@click.command()
@click.argument("task", type=str)
@click.option('--key', type=str, help="Unique database key, for use if prompted by CLI.")
def deliverable(task: str, key: str):
    """
    View a tasks's deliverable. 
    """
    db_item = _query_db(task, key)
    if not db_item:
        return

    deliverable_item = db_item['Deliverable']

    if deliverable_item is None:
        click.echo(f"There is no deliverable for {task}.")
        return

    click.echo(deliverable_item)


# Register the commands
cli.add_command(log)  # print log
cli.add_command(clockin)  
cli.add_command(clockout)
cli.add_command(pickup)  # continue finished tasks
cli.add_command(removetask)
cli.add_command(totalhours)
cli.add_command(deliver)  # add deliverable
cli.add_command(deliverable)  # view deliverable


if __name__ == '__main__':
    cli()

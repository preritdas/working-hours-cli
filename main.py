# Non-local imports
import click
import pandas as pd
import deta

# local imports
import datetime as dt
import pytz

# Project modules
import _keys


# Params
dt_format = '%Y-%m-%d %H-%M'
EST = pytz.timezone('US/Eastern')


# Deta
work_log = deta.Deta(_keys.Deta.project_key).Base('work_log')


def _query_db(task: str, key: str = None) -> dict | bool:
    """
    Checks the database for an item matching the task name, the task title,
    or using the key directly if it's provided. 

    If there was an error finding the item due to an invalid task name or invalid key,
    prints the error using click. 

    Returns the item if it was found, or `False` if it wasn't, so functinos calling it
    can use `if not` syntax to determine if they should themselves `return`. 
    """
    if key is not None:
        db_item = work_log.get(key)
        if not db_item:
            click.echo("Invalid key. Try again.")
            return False
    else:
        items = work_log.fetch(
            {
                'Task': task
            }
        ).items

        if len(items) != 0:
            # Try looking for tasks with title case
            items = work_log.fetch(
                {
                    'Task': task.title()
                }
            ).items

            if len(items) == 0:  # if none were found after trying title case
                click.echo("No items found. Correct the query or specify the key.")
                click.echo(pd.DataFrame(work_log.fetch().items))
                return False

        elif len(items) > 1:
            click.echo("Multiple items found. Please specify the key.")
            click.echo(pd.DataFrame(work_log.fetch().items))
            return False

        db_item = items[0]

    return db_item


@click.group
def cli():
    pass


@click.command()
def log():
    """Prints the log."""
    print(pd.DataFrame(work_log.fetch().items))


@click.command()
@click.argument("task")
@click.option('--hours', type=float)
@click.option('--date', type=str)
@click.option('--titlecase', type=bool, default=True)
def clockin(task: str, hours: float, date: str, titlecase: bool):
    """
    Clock in.
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
        time_started = dt.datetime.now(EST) - dt.timedelta(hours=hours)
        date = time_started.strftime(dt_format)
    else:
        date = dt.datetime.now(EST).strftime(dt_format)


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
@click.option('--key', type=str)
@click.option('--hours', type=float)
@click.option('--deliverable', type=str)
def clockout(task: str, key: str, hours: float, deliverable: str):
    """
    Clock out.
    """
    db_task = _query_db(task, key)
    if not db_task:
        return

    # Hours
    if hours is None:
        time_delta = dt.datetime.now(EST) - dt.datetime.strptime(db_task['Date'], dt_format)
        hours_delta = time_delta.total_seconds() / 3600
        hours = round(hours_delta, 2)
    db_task['Hours'] = hours

    # Deliverable
    if deliverable is not None:
        db_task['Deliverable'] = deliverable

    click.echo(f"Clocking out of {db_task['Task']} for {hours} hours.")
    work_log.put(db_task)


@click.command()
@click.argument("key")
def removetask(key):
    """Removes task with `key`."""
    task = _query_db("", key)
    if not task:
        return

    work_log.delete(key)
    click.echo(f"Removed task with key {key}.")
    click.echo(task)


@click.command()
def totalhours():
    tasks = work_log.fetch().items

    hours = 0
    for task in tasks:
        for key, val in task.items():
            if key == 'Hours' and val is not None:
                hours += val

    click.echo(f"You've worked a total of {hours} hours.")


@click.command()
@click.argument("task")
@click.argument("item")
@click.option('--key', type=str)
def deliver(task, item, key):
    db_item = _query_db(task, key)
    if not db_item:
        return

    db_item['Deliverable'] = item

    work_log.put(db_item)
    click.echo(f"Added deliverable {item} to {db_item['Task']}.")
    click.echo(pd.DataFrame(db_item, index=[0]))


@click.command()
@click.argument("task", type=str)
@click.option('--key', type=str)
def deliverable(task, key):
    db_item = _query_db(task, key)
    if not db_item:
        return

    deliverable_item = db_item['Deliverable']

    if deliverable_item is None:
        click.echo(f"There is no deliverable for {task}.")
        return

    click.echo(deliverable_item)


# Register the commands
cli.add_command(log)
cli.add_command(clockin)
cli.add_command(clockout)
cli.add_command(removetask)
cli.add_command(totalhours)
cli.add_command(deliver)
cli.add_command(deliverable)


if __name__ == '__main__':
    cli()

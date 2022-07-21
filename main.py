# Non-local imports
import click
import pandas as pd
import deta

# local imports
import datetime as dt

# Project modules
import _keys


# Params
dt_format = '%Y-%m-%d %H-%M'


# Deta
work_log = deta.Deta(_keys.Deta.project_key).Base('work_log')


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
@click.option('--titlecase', type=bool)
def clockin(task, hours, date, titlecase):
    """
    Clock in.
    """
    if titlecase is None:
        titlecase == True

    task = task.title() if titlecase else task

    # Check for multiple unfinished tasks
    tasks = work_log.fetch(
        {
            "Hours": None
        }
    ).items

    if len(tasks) > 1:
        click.echo("You cannot start multiple unfinished tasks.")
        return

    # Store the task
    if hours is None:
        click.echo(f"Clocking in and starting the clock. Clockout with task '{task}' to close this task.")
    else:
        click.echo(f"Logging {task} for {hours} hours.")

    work_log.put(
        {
            "Date": dt.datetime.now().strftime(dt_format) if date is None else date,
            "Task": task,
            "Hours": hours
        }
    )


@click.command()
@click.argument("task")
@click.option('--key', type=str)
@click.option('--hours', type=float)
def clockout(task: str, key: str, hours: float):
    """
    Clock out.
    """
    tasks = work_log.fetch(
        {
            'Task': task
        }
    ).items

    if key is not None:
        db_task = work_log.get(key)
    else:
        if len(tasks) < 1:
            click.echo("Task not found.")
            return
        elif len(tasks) > 1:
            # Try to look for unfinished tasks
            tasks = work_log.fetch(
                {
                    'Task': task,
                    'Hours': None
                }
            ).items

            if len(tasks) >= 0:
                click.echo("Too many tasks found. Specify the key.")
                print(pd.DataFrame(work_log.fetch().items))
                return

            task = tasks[0]

    db_task = tasks[0] if key is None else db_task

    # Hours
    if hours is None:
        time_delta = dt.datetime.now() - dt.datetime.strptime(db_task['Date'], dt_format)
        hours_delta = time_delta.total_seconds() / 3600
        hours = round(hours_delta, 2)
    db_task['Hours'] = hours

    click.echo(f"Clocking out of {db_task['Task']} for {hours} hours.")
    work_log.put(db_task)


@click.command()
@click.argument("key")
def removetask(key):
    """Removes task with `key`."""
    task = work_log.get(key)
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


# Register the commands
cli.add_command(log)
cli.add_command(clockin)
cli.add_command(clockout)
cli.add_command(removetask)
cli.add_command(totalhours)


if __name__ == '__main__':
    cli()

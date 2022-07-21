# Non-local imports
import click
import pandas as pd; pd.options.mode.chained_assignment = None
import numpy as np  # checking NaN values

# local imports
import datetime as dt


# Params
log_file = 'work_log.csv'
dt_format = '%Y-%m-%d %H-%M'


@click.group
def cli():
    pass


@click.command()
def log():
    """Prints the log."""
    click.echo(pd.read_csv(log_file))


@click.command()
@click.argument("task")
@click.option('--hours', type=float)
def clockin(task, hours):
    """
    Clock in.
    """
    task = task.lower()

    if hours is None:
        click.echo(f"Clocking in and starting the clock. Clockout with task '{task}' to close this task.")
    else:
        click.echo(f"Logging {task} for {hours} hours.")

    new_df = pd.DataFrame(
        {
            "Date": [dt.datetime.now().strftime(dt_format)],
            "Task": [task],
            "Hours": [hours]
        }
    )

    # Write to the file 
    pd.concat((pd.read_csv(log_file), new_df)).to_csv(log_file, index=False)


@click.command()
@click.argument("task")
@click.option('--index', type=int)
def clockout(task: str, index: int):
    """
    Clock out.
    """
    click.echo(f"Clocking out of {task}.")

    work_log = pd.read_csv(log_file)
    if index is not None:
        work_log['Hours'][index] = (dt.datetime.now() - work_log['Date'][index]).hours
        work_log.to_csv(log_file, index=False)
        return

    if len(work_log[work_log['Task'] == task]) > 1:
        click.echo("Multiple tasks with that name were found. Specify the index and rerun the command.")
        click.echo(work_log)
        return
    elif len(work_log[work_log['Task'] == task]) == 1:
        idx = work_log.index[work_log['Task'] == task]
        idx = idx[0]

        if not np.isnan(work_log['Hours'][idx]):
            click.echo(f"Hours for {task} have already been logged.")
            click.echo(work_log)
            return

        work_log['Hours'][idx] = f"{((dt.datetime.now() - dt.datetime.strptime(work_log['Date'][idx], dt_format)).total_seconds() / 3600):.2f}"
        work_log.to_csv(log_file, index=False)


# Register the commands
cli.add_command(log)
cli.add_command(clockin)
cli.add_command(clockout)


if __name__ == '__main__':
    cli()

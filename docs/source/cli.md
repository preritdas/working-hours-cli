# CLI Reference

A simple-to-use command-line interface built to remove the stress of logging working hours, keeping track of completed payable tasks, and referencing deliverables.

**Usage**:

```console
$ loghours [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `clockin`: Create a new task and clock in.
* `clockout`: Clock out of an unfinished task.
* `deliver`: Stores a deliverable item after you've...
* `deliverable`: View a tasks's deliverable.
* `export`: Create a PDF report of the provided month's...
* `log`: Displays a full log of all work hours.
* `modify`: Change an attribute of a logged item.
* `pickup`: Continue working on a pre-existing task.
* `previewmonth`: Displays all tasks of a given month.
* `removetask`: Removes task with `key`.
* `totalhours`: Calculates the total hours worked on all...

## `loghours clockin`

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

**Usage**:

```console
$ loghours clockin [OPTIONS] TASK
```

**Arguments**:

* `TASK`: Name of the task you want to clock in.  [required]

**Options**:

* `--hours FLOAT`: Log a completed task that took this many hours.  [required]
* `--date TEXT`: Force date. Use this is if you started but forgot to clock in.  [required]
* `--titlecase / --no-titlecase`: Override auto titlecasing. Makes future reference harder.  [required]
* `--help`: Show this message and exit.

## `loghours clockout`

Clock out of an unfinished task.

Does not work on finished tasks; i.e. tasks with a finite `Hours` value. Therefore,
does not accept a positional 'task' parameter like most other commands. This command
can only be used to clock out of the single unfinished task, if it exists (you cannot 
have multiple unfinished tasks in the log).

Deliver a task directly while clocking out with --deliver. If you use --hours, the 
`hours` value provided is used instead of a standard calculation involving the 
current time.

**Usage**:

```console
$ loghours clockout [OPTIONS]
```

**Options**:

* `--hours FLOAT`: Force the number of hours worked.  [required]
* `--deliver TEXT`: Add a deliverable item.  [required]
* `--key TEXT`: Unique database key if prompted by CLI.  [required]
* `--help`: Show this message and exit.

## `loghours deliver`

Stores a deliverable item after you've clocked out.

Note that you don't technically have to clock out to add a deliverable.
And, deliverables can also be added directly when clocking out. See clockout
help to learn more.

**Usage**:

```console
$ loghours deliver [OPTIONS] TASK ITEM
```

**Arguments**:

* `TASK`: Name of the task you wish to add a deliverable for.  [required]
* `ITEM`: Note, result, reference, or link to the deliverable.  [required]

**Options**:

* `--key TEXT`: Unique database key, if prompted by the CLI.  [required]
* `--help`: Show this message and exit.

## `loghours deliverable`

View a tasks's deliverable. 

If the deliverable is determined to be a link, the link is automatically opened
in your default browser.

**Usage**:

```console
$ loghours deliverable [OPTIONS] TASK
```

**Arguments**:

* `TASK`: Name of the task whose deliverable you wish to view.  [required]

**Options**:

* `--key TEXT`: Unique database key, if prompted by the CLI.  [required]
* `--help`: Show this message and exit.

## `loghours export`

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

If no optional path is provided, the files are exported to the current working
directory (of your console session).

**Usage**:

```console
$ loghours export [OPTIONS] MONTHYEAR
```

**Arguments**:

* `MONTHYEAR`: Month to preview, ex. '7-2022'.  [required]

**Options**:

* `--path TEXT`: Absolute path to the folder in which to export your documents.  [required]
* `--help`: Show this message and exit.

## `loghours log`

Displays a full log of all work hours. Is this in?

**Usage**:

```console
$ loghours log [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `loghours modify`

Change an attribute of a logged item.

Automatically tries to convert the value provided to the appropriate type,
depending on the attribute. For example, if the user requests to change the
'hours' attribute of an item, the value is automatically converted to a float.
If this operation fails, the user is notified that their provided value is
unacceptable.

This command is only meant to be used to correct errors. To update the delivery
of a task, it is much safer to use the `deliver` command.

**Usage**:

```console
$ loghours modify [OPTIONS] TASK ITEM VALUE
```

**Arguments**:

* `TASK`: Name of the task whose property you wish to modify.  [required]
* `ITEM`: Name of the property you wish to modify, ex. 'task' or 'hours'.  [required]
* `VALUE`: Value to which the property should be set.  [required]

**Options**:

* `--key TEXT`: Unique database key, if prompted by the CLI.  [required]
* `--help`: Show this message and exit.

## `loghours pickup`

Continue working on a pre-existing task.

Finds a _completed_ task from the database, resets its date to `hours` hours ago,
and removes its `hours` value to indicate that it's unfinished. That way you 
can continue working and clock out as normal. The resulting behavior is that you 
add on the extra time between when you picked up the task and when you 
clock out again.

**Usage**:

```console
$ loghours pickup [OPTIONS] TASK
```

**Arguments**:

* `TASK`: Name of the task you want to pick up.  [required]

**Options**:

* `--key TEXT`: Unique database key, if prompted by the CLI.  [required]
* `--help`: Show this message and exit.

## `loghours previewmonth`

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

**Usage**:

```console
$ loghours previewmonth [OPTIONS] MONTHYEAR
```

**Arguments**:

* `MONTHYEAR`: Month to preview, ex. '7-2022'.  [required]

**Options**:

* `--help`: Show this message and exit.

## `loghours removetask`

Removes task with `key`.

You cannot remove tasks by name; only by key, for security.

**Usage**:

```console
$ loghours removetask [OPTIONS] KEY
```

**Arguments**:

* `KEY`: Task unique database key.  [required]

**Options**:

* `--help`: Show this message and exit.

## `loghours totalhours`

Calculates the total hours worked on all tasks.

Proviate `payrate` to calculate your monthly pay.

**Usage**:

```console
$ loghours totalhours [OPTIONS]
```

**Options**:

* `--payrate FLOAT`: Your hourly wage.  [required]
* `--help`: Show this message and exit.

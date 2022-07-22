# Working Hours CLI

An extremely simple-to-use command-line interface built to remove the stress of logging working hours, keeping track of completed payable tasks, and referencing deliverables. Simply `clockin` to your task, complete it, and `clockout`, and the rest is taken care of. Of course, that's just the bare-bones functionality... A heap of features await you.


See the CLI in action...

[![asciicast](https://asciinema.org/a/r2nB2goFnWbXVCgZdNz58tOca.svg)](https://asciinema.org/a/r2nB2goFnWbXVCgZdNz58tOca)

## Deployment

I deployed the CLI above using a script called `loghours`...

```bash
#!/bin/bash

python3.10 "/home/path/to/Working Hours CLI/main.py" "$@"
```

I then added the script's directory to $PATH, and gave it executable permissions with `chmod +x loghours`. This allows me to call it like a professional CLI application from anywhere in the system, with the `loghours` command. All arguments passed to `loghours`, such as `loghours clockin "this or that" --hours 2`, are passed individually to the Python script thanks to the script above.


## Usage and Behavior

The CLI interacts with a Deta database whose credentials are supplied by a project key provided in `_keys.py` (see [`_keys (sample).py`](_keys%20(sample).py)), in the same directory as `main.py`. 

Whenever a new item is added to the database, using `clockin`, the item is assigned a completely unique random string `key`. If you try to run a command (ex. `deliverable "a task"` to view the deliverable of task "a task," and there are multiple tasks named "a task," the CLI will print all items (including their keys) and prompt you to rerun the command but append `--key KEY`, where KEY is the key printed beside the name of an item. 

In the specific circumstance that you're clocking out of a task whose name is shared by other tasks, if only one occurrence of all the tasks with that name is _unfinished_, you'll automatically be clocked out of that unfinished task, without the need for manually providing a `key` as explained above. 


## Commands

The following is a list of all commands with their behavior summarized.

| Command | Behavior| 
| --- | --- |
| clockin | Create a new task and clock in. |
| clockout | Clock out of an unfinished task. |
| deliver | Stores a deliverable item after you've clocked out. |
| deliverable | View a tasks's deliverable. |
| log | Displays a full log of all work hours. |
| pickup | Continue working on a pre-existing task. |
| removetask | Removes task with `key`. |
| totalhours | Calculates the total hours worked on all tasks. |

### clockin

Create a new task and clock in.

If you provide `hours`, the task will be marked as completed with `hours` hours. The date will be set to `hours` hours before the current moment, as if you forgot to clock in then and are doing so after the fact.

If you provide `date`, you will override the date calculations and forcibly insert `date`. The only reason to do this is if you're working on a task currently and forgot to clock in when you started. You can clock in, pass in the properly formatted date representing the time you started, and then clock out whenever you're finished.

If you set `titlecase` as `False`, it becomes harder to reference the task in future commands. For example, if you create a task with the name "hEllo" and try to execute `deliver "hello" "deliverable"`, you'll get an error. If "hEllo" was instead automatically or manually set as "Hello", the previous command would work.

| Option | Type | Note |
| --- | --- | --- |
| --hours | float | Log a completed task that took this many hours. |
| --date | string | Force date. Use this is if you started but forgot to clock in. |
| --titlecase | bool | Override auto titlecasing. Makes future reference harder. |

### clockout 

Clock out of an unfinished task.

Does not work on finished tasks; i.e. tasks with a finite `Hours` value.

If you have multiple tasks of the same name, and only one of them is unfinished,  clocks out of the unfinished task.

Deliver a task directly while clocking out with --deliver. If you use --hours, the  `hours` value provided is used instead of a standard calculation involving the current time.

| Option | Type | Note |
| --- | --- | --- |
| --key | string | Unique database key, for use if prompted by CLI. |
| --hours | float | Force the number of hours worked. |
| --deliver | string | Add a deliverable item. |

### deliver 

Stores a deliverable item after you've clocked out.

Note that you don't technically have to clock out to add a deliverable. And, deliverables can also be added directly when clocking out. See `clockout --help` to learn more.

| Option | Type | Note |
| --- | --- | --- |
| --key | stirng | Unique database key, for use if prompted by CLI. |

### deliverable

View a task's deliverable.

| Option | Type | Note |
| --- | --- | --- |
| --key | string | Unique database key, for use if prompted by CLI. |

### log

Displays a full log of all work hours.

### pickup 

Continue working on a pre-existing task.

Finds a _completed_ task from the database, resets its date to `hours` hours ago, and removes its `hours` value to indicate that it's unfinished. That way you can continue working and clock out as normal. The resulting behavior is that you add on the extra time between when you picked up the task and when you clock out again.

| Option | Type | Note |
| --- | --- | --- |
| --key | stirng | Unique database key, for use if prompted by CLI. || Option | Type | Note |

### removetasks

Removes task with `key`.

### totalhours

Calculates and displays the total hours worked on all tasks.